var dehy = {
	loadStart: '',
	loading_message: 'Loading...',
	unfreeze_timeout_id: null,
	keep_frozen: false,
	recaptcha_version: 2,
	init(choice='') {
		dehy.handlers.init();
		$( document ).ajaxStart(function(xhr, settings) {
			var modal_text = document.querySelector('#modal_text');
			if (modal_text) {
				modal_text.textContent = dehy.loading_message;
			}
			dehy.utils.freeze_submissions = true;
			dehy.utils.freeze_forms();
			dehy.loadStart = window.performance.now();
			// unfreeze after 20s, just incase
			setTimeout(function() {
				dehy.utils.unfreeze_forms();
			}, 20000);
		});

		$( document ).ajaxStop(function(xhr, settings) {
			if (!dehy.keep_frozen) {

				var request_time = window.performance.now() - dehy.loadStart;
				if (request_time < 500) { // the request took less than half a second
					dehy.unfreeze_timeout_id = setTimeout(function() {
						dehy.utils.unfreeze_forms();
					}, (dehy.loadStart + 500) - window.performance.now());
				} else {
					dehy.utils.unfreeze_forms();
				}
			}
		});

		$.ajaxSetup({
			beforeSend: function(xhr, settings) {
				if (!dehy.utils.csrfSafeMethod(settings.type) && !this.crossDomain) {
					xhr.setRequestHeader("X-CSRFToken", dehy.utils.getCookie('csrftoken'));
				}
			},
			complete: function(xhr, status) {
				console.info('ajax complete, xhr: ', xhr);
				console.info('ajax complete, status: ', status);
			},
		});
	},
	handlers: {
		init() {
			dehy.handlers.shop.init();
			dehy.handlers.home.init();
			dehy.handlers.spam_filter()
		},
		spam_filter() {
			var forms = document.querySelectorAll('form:not(.basket_summary)');
			forms.forEach(form=>{
				form.addEventListener('click', e=>{
					if (form.dataset.action) {
						form.action = form.dataset.action;
						delete form.dataset.action;
					}
				});
			})
		},
		home: {
			init() {
				dehy.handlers.home.add_user_to_mailing_list_handler();
			},
			add_user_to_mailing_list(e) {
				e.preventDefault();
				var form = e.target.closest('form');
				var form_data = new FormData(form);
				$.ajax({
					method: "POST",
					dataType: 'json',
					url: form.action,
					contentType: false,
					processData: false,
					data: form_data,
					success: function(response) {

						dehy.utils.update_loading_modal(response.message, "#status_success", 2000);
					},
					error: function(response) {
						console.log('error response: ', response);
						$( "#loading_modal" ).show();
						dehy.utils.update_loading_modal(response.responseJSON.message, "#status_error", 2000);
					}
				});
			},
			add_user_to_mailing_list_handler() {
				var forms = document.querySelectorAll("form#mailing_list");
				forms.forEach(form => {
					form.addEventListener('submit', dehy.handlers.home.add_user_to_mailing_list);
				});
			},
		},
		shop: {
			init() {
				dehy.handlers.shop.add_item_to_cart_handler();
				dehy.handlers.shop.variant_size_selection_handler();
				dehy.handlers.shop.activate_plus_minus_buttons();
				dehy.handlers.shop.show_active_input_handler();
				dehy.handlers.shop.toggle_mini_basket_handler();
			},
			add_item_to_cart_handler() {
				var forms = document.querySelectorAll('form.add-to-basket');
				forms.forEach(form => {
					form.addEventListener('submit', e => {
						e.preventDefault();
						var form_data = new FormData(e.target);
						$.ajax({
							method: "POST",
							dataType: 'json',
							url: form.action,
							contentType: false,
							processData: false,
							data: form_data,
							success: dehy.handlers.shop.item_added_to_cart_success,
							error: dehy.handlers.shop.item_added_to_cart_error,
						});
					});
				})

			},
			item_added_to_cart_success(response, xhr, status) {
				dehy.utils.update_cart_quantity(response.basket_items);
				try {
					dehy.basket.basket_updated_handlers.success(response);
				} catch(error) {
					console.error(error);
					return false
				};
			},
			item_added_to_cart_error(error, xhr, status) {

				var error_container = document.querySelector('#error_container');
				error_container.classList.toggle('hide', false);
				error_container.textContent = error
				// error_container.append(dehy.utils.create_element({tag:'div', classes:'error', text: error_message, attrs:{'id':'errors'}}));
			},
			variant_size_selection_handler() {
				var size_selectors = document.querySelectorAll('.variant-size-selector');
				size_selectors.forEach(select_elem => {
					select_elem.addEventListener('change', e => {
						var variant_select_container = e.target.closest('.variant-select-container');
						var product_price_container = e.target.closest('.product_price');

						var not_price_selector = product_price_container.querySelector('span.not_price_color'),
							variant_price = product_price_container.querySelector('span.variant_price'),
							option_price = e.target.selectedOptions[0].dataset.price,
							variant_id = e.target.selectedOptions[0].dataset.id,
							form = e.target.closest('form');

							if (e.target.selectedOptions[0].dataset.price) {
								not_price_selector.innerText = "";
								variant_select_container.dataset.text = e.target.value
								variant_price.innerText = `$${option_price}`
								form.action = `/basket/add/${variant_id}/`

							} else {
								not_price_selector.innerText = 'from ';
								variant_price.innerText = `$${e.target.options[1].dataset.price}`;
								variant_select_container.dataset.text = e.target.options[0].text;
								form.action = "/basket/"
							}

					})
				})
			},
			show_active_input_handler() {
				var quantity_selects = document.querySelectorAll('.quantity-select-container');
				quantity_selects.forEach(elem => {
					elem.addEventListener('click', e => {
						// e.stopImmediatePropogation();
						var closest_input = elem.querySelector("input[name='quantity']");
						if (closest_input) {
							closest_input.focus();
						}
					})
				}, true);

				var quantity_inputs = document.querySelectorAll("input[name='quantity']");
				quantity_inputs.forEach(elem =>{
					elem.addEventListener('focus', e=>{
						var qty_select_container = e.target.closest('.quantity-select-container');
						if (qty_select_container) {
							qty_select_container.classList.toggle('active', true);
						}
					})
					elem.addEventListener('blur', e=>{

						var qty_select_container = e.target.closest('.quantity-select-container');
						if (qty_select_container) {
							qty_select_container.classList.toggle('active', false);
						}
					});
				});
			},
			plus_minus_button_handler(e) {
				e.preventDefault();
				var input = document.querySelector(`input[data-product_id='${e.target.dataset.product_id}']`);
				if (input) {
					var n = 1;

					if (e.target.matches('.minus-btn')) {
						n *= -1;
					}
					let v = parseInt(input.value) + n;

					var min = (input.closest("#basket_formset")) ? 0 : input.min;
					input.value = (n < 0) ? Math.max(v, min) : Math.min(v, input.max);
					if (v==0 && min==0) {
						var qty_select = input.closest(".quantity-select-container");
						qty_select.parentNode.querySelector('.remove-basket-item').click();
					} else {
						const change = new Event('change');
						input.dispatchEvent(change);
					}
				}
			},
			activate_plus_minus_buttons() {
				var plus_minus_buttons = document.querySelectorAll('.plus-minus-btn');
				plus_minus_buttons.forEach(elem =>{
					elem.addEventListener('click', dehy.handlers.shop.plus_minus_button_handler);
				})
			},
			toggle_mini_basket_handler() {
				var cart_icon = document.getElementById("cart_icon");
				if (cart_icon) {
					var close_button = document.getElementById("close_mini_basket"),
						mini_basket = document.getElementById("mini_basket"),
						mini_basket_container = document.getElementById("mini_basket_container");

					document.addEventListener("keydown", e=>{
						if (e.which===27) {
							document.body.classList.toggle("modal-open", false);
							if (mini_basket_container) {
								mini_basket_container.classList.toggle("show", false);
								setTimeout(function(){
									mini_basket_container.classList.toggle("d-none", true);
								}, 500);
							}
						}
					});

					if (close_button && mini_basket_container) {
						close_button.addEventListener("click", e=>{
							e.stopPropagation();
							document.body.classList.toggle("modal-open", false);
							mini_basket_container.classList.toggle("show", false);
							setTimeout(function(){
								mini_basket_container.classList.toggle("d-none", true);
							}, 500);
						});

						cart_icon.addEventListener("click", e=>{
							e.stopPropagation();
							mini_basket_container.classList.toggle("d-none", false);
							setTimeout(function(){
								mini_basket_container.classList.toggle("show");
								document.body.classList.toggle("modal-open");
							}, 100);
						});
					}

					document.body.addEventListener("click", e=>{
						var loading_modal = document.getElementById("loading_modal"),
							confirm_item_removal =  document.getElementById("confirm_item_removal");

						if (mini_basket_container && !e.path.includes(mini_basket) && !e.path.includes(confirm_item_removal) && !e.path.includes(loading_modal)) {
							document.body.classList.toggle("modal-open", false);
							mini_basket_container.classList.toggle("show", false);
							setTimeout(function(){
								mini_basket_container.classList.toggle("d-none", true);
							}, 500);
						}
					});
				}
			}
		},
	},

	ajax: {
		get_cart_quantity(data) {
			$.ajax({
		         method: "GET",
		         url: "ajax/get_cart_quantity/",
		         dataType: "json",
		         cache: false,
		         success: function(response) {
					 dehy.utils.update_cart_quantity(response.basket_items);
				 }
		     });
		},
	},
	utils: {
		generic_handler_setup(selector, event_type="click", callback_fn) {
			var elems = document.querySelectorAll(selector);
			elems.forEach(ele=>{
				ele.addEventListener(event_type, callback_fn);
			});
		},
		freeze_submissions: false,
		get_sitekey(version=dehy.recaptcha_version) {
			return dehy[`recaptcha_sitekey_v${version}`]
		},
		recaptcha_form_intercept_handler() {
			var requires_recaptcha = document.querySelectorAll(".requires-recaptcha");

			requires_recaptcha.forEach(elem=>{

				var form = elem.closest('form');
				if (form) {
					form.addEventListener('submit', dehy.utils.recaptcha_form_intercept);
				}
			});
		},
		recaptcha_form_intercept(e) {
			e.preventDefault();
			let form = e.target.closest('form');
			let recaptcha_elem = form.querySelector(".requires-recaptcha");

			grecaptcha.render(recaptcha_elem, {
				'sitekey' : dehy.utils.get_sitekey(version=2),
				'callback': function(data) {
					dehy.utils.recaptcha_verify(data, form);
				}
			});

		},
		recaptcha_verify(token, form) {
			fetch(`/recaptcha_verify/?version=${dehy.recaptcha_version}&token=`+token).then(function(response) {
                response.json().then(function(data) {
					if (data.success) {
						form.submit();
					}
                });
        	});
		},
		keep_forms_frozen(tf=true) {
			dehy.keep_frozen = tf;
		},
		//
		update_loading_modal(message="Success...", icon_selector="#status_loading", delay=1000) {
			dehy.utils.keep_forms_frozen();

			if (!message) {
				return
			}
			var loading_modal = document.getElementById('loading_modal');
			var modal_text = loading_modal.querySelector('#loading_modal_text');
			var icon = loading_modal.querySelector(icon_selector);
			var unused_icons = loading_modal.querySelectorAll(`#loading_status_icon_container .status-icon:not(${icon_selector})`);

			setTimeout(function() {
				modal_text.textContent = message;
				icon.classList.toggle('d-none', false);

				unused_icons.forEach(elem=>{
					elem.classList.toggle('d-none', true);
				});
			}, 500);


			setTimeout(function() {
				dehy.utils.unfreeze_forms();
				dehy.utils.keep_forms_frozen(false);
			}, delay+500);

		},
		update_cart_quantity(basket_items=0) {

			var navbar = document.getElementById('navbar');
			if (navbar) {
				navbar.classList.toggle('scrolled-up', true);
				setTimeout(function() {
					navbar.classList.toggle('scrolled-up', false);
					navbar.classList.toggle('scrolled-down', true);
				}, 3000);
			}

			var cart_container = document.querySelector('.cart-container');
			if (cart_container) {
				cart_container.querySelector('a.icon-cart').ariaLabel = `${basket_items} items in cart`;
			}

			var cart_quantity_span = document.querySelector("#cart-quantity");
			if (cart_quantity_span) {
				cart_quantity_span.textContent = basket_items
			}

		},
		freeze_forms(force=true) {
			document.body.classList.toggle('modal-open', force);
			if (force) {
				$( "#loading_modal" ).show();

			}
			var forms = document.querySelectorAll('form');
			forms.forEach(function(form) {
				form.querySelectorAll("input, select, button").forEach(function(elem) {
					elem.disabled = force
				});
			});
		},
		reset_loading_modal() {
			var loading_modal_text = document.getElementById('loading_modal_text');
			if (loading_modal_text) {
				loading_modal_text.textContent = dehy.loading_message;
			}
			var loading_status_icon_container = document.getElementById('loading_status_icon_container');
			if (loading_status_icon_container) {
				var children = Array.from(loading_status_icon_container.children);
				children.forEach(elem=>{
					elem.classList.toggle('d-none', true);
				});
				var loading_status_icon = document.getElementById('status_loading');
				loading_status_icon.classList.toggle('d-none', false);
			}
		},
		unfreeze_forms() {
			dehy.loading_message = 'Loading...';
			this.freeze_forms(false);
			dehy.utils.freeze_submissions = false;
			$( "#loading_modal" ).hide();
			dehy.utils.reset_loading_modal();

		},
		remove_event_listeners(elem) {
			var copy = elem.cloneNode(true);
			elem.parentNode.replaceChild(copy, elem)
		},
		debug(fn=null, ...args) {
			// to call: dehy.utils.debug(this, response);
			console.log('function name: ', fn.name);
			console.log('return value: ', fn.call(null, args));
		},
		debounce(context, func, delay) {
			console.log('debouncing')
			console.log('context: ', context)
			console.log('func: ', func)

			if (context && context.preventDefault) {
				context.preventDefault();
			}

			let timeout;
			return (...args) => {
				if (timeout) {
					clearTimeout(timeout);
				}
				timeout = setTimeout(() => {
					func.apply(context, args);
				}, delay);
			}
		},
		serialize(form) {
			var serialized = [];
			var elements = (form.elements) ? form.elements: form.querySelectorAll('input, select, fieldset, button');
			// Loop through each field in the form
			for (var i = 0; i < elements.length; i++) {

				var field = elements[i];

				// Don't serialize fields without a name, submits, buttons, file and reset inputs, and disabled fields
				if (!field.name || field.disabled || field.type === 'file' || field.type === 'reset' || field.type === 'submit' || field.type === 'button') continue;

				// If a multi-select, get all selections
				if (field.type === 'select-multiple') {
					for (var n = 0; n < field.options.length; n++) {
						if (!field.options[n].selected) continue;
						serialized.push(encodeURIComponent(field.name) + "=" + encodeURIComponent(field.options[n].value));
					}
				}

				// Convert field data to a query string
				else if ((field.type !== 'checkbox' && field.type !== 'radio') || field.checked) {
					serialized.push(encodeURIComponent(field.name) + "=" + encodeURIComponent(field.value));
				}
			}

			return serialized.join('&');

		},
		getCookie(name) {
			var cookieValue = null;
			if (document.cookie && document.cookie !== '') {
				var cookies = document.cookie.split(';');
				for (var i = 0; i < cookies.length; i++) {
					var cookie = cookies[i].trim();
					if (cookie.substring(0, name.length + 1) === (name + '=')) {
						cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
						break;
					}
				}
			}
			return cookieValue;
		},

		csrfSafeMethod(method) {
			return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
		},
		create_element({tag, classes, style, text, attrs} = {}) {
			var elem = document.createElement(`${tag}`)
			if (classes) {
				elem.className = classes
			}

			if (style) {
				elem.style.cssText = style
			}

			if (text) {
				var content = document.createTextNode(`${text}`);
				elem.appendChild(content)
			}

			if (attrs) {
				for (let [key, val] of Object.entries(attrs)) {
					var dataItem = document.createAttribute(`${key}`);
					dataItem.value = val
					elem.setAttributeNode(dataItem)
				}
			}
			return elem
		},
		/*********************************************
		Given an array of objects, attempts to recursively create elements using the following format:
		elems = [{
			'tag': 'div','classes': 'shipping-address-container', 'elems': [
				{'tag':'div', 'classes':'form-group row' 'elems': [
					{'tag':'input','attrs': {'required':'', 'maxlength': '50', 'type': 'text', 'id_first_name', 'placeholder':"First Name", 'aria-label':"First Name"}},
				}]
			}]
		}]
		*********************************************/
		create_elements(elems, parent) {
			var container = parent || dehy.utils.create_element({tag:'div', classes:'temp-container'});
			for (let i = 0; i < elems.length; i++) {
				var elem = dehy.utils.create_element(elems[i]);
				container.appendChild(elem);
				if (elems[i].elems) {
					elem.replaceWith(dehy.utils.create_elements(elems[i].elems, elem));
				}
			}
			return container
		},
		cleanup_temp_containers(container=document) {
			container.querySelectorAll('div.temp-container').forEach(function(elem){
				if (elem.hasChildNodes()) {
					elem.replaceWith(...elem.childNodes)
				}
			})
			if (container.matches && container.matches('div.temp-container')) {
				container.replaceWith(...container.childNodes)
			}
			return container
		},
		remove_children(elem) {
			if (elem && elem.hasChildNodes && elem.hasChildNodes()) {
				while (elem.firstChild) {
  					elem.removeChild(elem.firstChild);
				}
			}
		},
		notify_user(message, delay=4500) {
			let notification_container = dehy.utils.create_element({tag:'div', classes:'notification-container', text:message});

			document.body.append(notification_container);
			setTimeout(() => {
				notification_container.remove()
			}, delay);
		},
	}
}

window.recaptcha_onload = dehy.utils.recaptcha_form_intercept_handler;
window.recaptcha_verify = dehy.utils.recaptcha_verify;