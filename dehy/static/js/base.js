var dehy = {
	loadStart: '',
	loading_message: 'Loading...',
	init(choice='') {
		dehy.handlers.all();
		$( document ).ajaxStart(function(xhr, settings) {
			var modal_text = document.querySelector('#modal_text')
			if (modal_text) {
				modal_text.textContent = dehy.loading_message
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
			if (window.performance.now() - dehy.loadStart < 500) {
				setTimeout(function() {
					dehy.utils.unfreeze_forms();
				}, (dehy.loadStart + 500) - window.performance.now());
			} else {
				dehy.utils.unfreeze_forms();
			}
			dehy.loading_message = 'Loading...';

		});

		$.ajaxSetup({
			beforeSend: function(xhr, settings) {

				if (!dehy.utils.csrfSafeMethod(settings.type) && !this.crossDomain) {
					xhr.setRequestHeader("X-CSRFToken", dehy.utils.getCookie('csrftoken'));
				}
			},
			complete: function(xhr, status) {
				console.log('ajax complete, xhr: ', xhr);
				console.log('ajax complete, status: ', status);
			},
		});
	},
	handlers: {
		all() {
			dehy.handlers.shop.all();
		},
		shop: {
			all() {
				dehy.handlers.shop.add_item_to_cart_handler();
				dehy.handlers.shop.variant_size_selection_handler();
				dehy.handlers.shop.activate_plus_minus_buttons();
				dehy.handlers.shop.show_active_input_handler();
				dehy.handlers.shop.toggle_mini_basket_handler();
			},
			add_item_to_cart_handler() {
				var forms = document.querySelectorAll('form.add-to-basket');
				forms.forEach(function(form) {
					form.addEventListener('submit', e=> {
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
				} catch {
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
				size_selectors.forEach(function(select_elem) {
					select_elem.addEventListener('change', e=> {
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
				quantity_selects.forEach(elem=> {
					elem.addEventListener('click', e=>{
						// e.stopImmediatePropogation();
						var closest_input = elem.querySelector("input[name='quantity']");
						if (closest_input) {
							closest_input.focus();
						}
					})
				}, true);

				var quantity_inputs = document.querySelectorAll("input[name='quantity']");
				quantity_inputs.forEach(elem=>{
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
					})
				})
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
			// increment_input_quantity(elem, n=1) {
			//
			// 	var input = document.querySelector(`input[data-product_id='${elem.dataset.product_id}']`);
			// 	let v = parseInt(input.value) + n;
			// 	input.value = (n < 0) ? Math.max(v, input.min) : Math.min(v, input.max);
			//
			// 	const change = new Event('change');
			// 	input.dispatchEvent(change);
			//
			// 	// input.value = (n < 0) ? Math.max((input.value - n), input.min) : Math.min((input.value + n), input.max);
			// },
			// activate_plus_minus_buttons() {
			// 	var plus_minus_buttons = document.querySelectorAll('.plus-minus-btn');
			// 	plus_minus_buttons.forEach(elem =>{
			//
			// 		var n = 1;
			// 		if (elem.matches('.minus-btn')) {
			// 			n *= -1;
			// 		}
			// 		elem.addEventListener('click', e=>{
			// 			e.preventDefault();
			// 			dehy.handlers.shop.increment_input_quantity(e.target, n);
			// 		});
			// 	})
			// },
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
							}
						}
					});

					if (close_button && mini_basket_container) {
						close_button.addEventListener("click", e=>{
							e.stopPropagation();
							document.body.classList.toggle("modal-open", false);
							mini_basket_container.classList.toggle("show", false);
						});

						cart_icon.addEventListener("click", e=>{
							e.stopPropagation();
							mini_basket_container.classList.toggle("show");
							document.body.classList.toggle("modal-open");
						});
					}

					document.body.addEventListener("click", e=>{
						var loading_modal = document.getElementById("loading_modal"),
							confirm_item_removal =  document.getElementById("confirm_item_removal");

						if (mini_basket_container && !e.path.includes(mini_basket) && !e.path.includes(confirm_item_removal) && !e.path.includes(loading_modal)) {
							document.body.classList.toggle("modal-open", false);
							mini_basket_container.classList.toggle("show", false);
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
		freeze_submissions: false,
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
		notifyUser(message) {
			let notificationContainer = ($("<div/>", {
				class: "notification-container",
				text: message,
			}));
			$("body").append(notificationContainer)
			setTimeout(() => {
				$(".notification-container").remove()
			}, 4500);
		},
		freeze_forms(force=true) {
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
		unfreeze_forms() {
			this.freeze_forms(false);
			dehy.utils.freeze_submissions = false;
			$( "#loading_modal" ).hide();

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

			// Setup our serialized data
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
		}
	}
}




