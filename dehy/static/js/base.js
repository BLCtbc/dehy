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
			$( "#loading_modal" ).show();
			dehy.utils.freeze_forms();
			dehy.loadStart = window.performance.now();
		});

		$( document ).ajaxStop(function(xhr, settings) {
			if (window.performance.now() - dehy.loadStart < 500) {
				setTimeout(function() {
					dehy.utils.unfreeze_forms();
					$( "#loading_modal" ).hide();
				}, (dehy.loadStart + 500) - window.performance.now());
			} else {
				dehy.utils.unfreeze_forms();
				$( "#loading_modal" ).hide();
			}
		});

		$.ajaxSetup({
			beforeSend: function(xhr, settings) {

				console.log('beforeSend xhr: ', xhr);
				console.log('beforeSend settings: ', settings);

				if (!dehy.utils.csrfSafeMethod(settings.type) && !this.crossDomain) {
					xhr.setRequestHeader("X-CSRFToken", dehy.utils.getCookie('csrftoken'));
				}
			},
			complete: function(e, xhr, status) {
				console.log('ajax complete');
				console.log('e: ', e);
				console.log('xhr: ', xhr);
				console.log('status: ', status);

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
				console.log('success response: ', response);
				console.log('success xhr: ', xhr);
				console.log('success status: ', status);
			},
			item_added_to_cart_error(error, xhr, status) {
				console.log('error: ', error);
				console.log('xhr: ', xhr);
				console.log('status: ', status);

				var error_container = document.querySelector('#error_container');
				error_container.classList.toggle('hide', false);
				error_container.textContent = error
				// error_container.append(dehy.utils.create_element({tag:'div', classes:'error', text: error_message, attrs:{'id':'errors'}}));
			},
			variant_size_selection_handler() {
				var size_selectors = document.querySelectorAll('.variant-size-selector');
				size_selectors.forEach(function(select_elem) {
					select_elem.addEventListener('change', e=> {
						var variant_select_container = e.target.closest('.variant-select-container'),
							not_price_selector = e.target.closest('.product_main').querySelector('span.not_price_color'),
							variant_price = e.target.closest('.product_main').querySelector('span.variant_price'),
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
		update_cart_quantity(basket_items=0) {

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
			var forms = document.querySelectorAll('form');
			forms.forEach(function(form) {
				form.querySelectorAll("input, select, button").forEach(function(elem) {
					elem.disabled = force
				})
			})
		},
		unfreeze_forms() {
			this.freeze_forms(false);
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
		serialize: function(form) {

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




