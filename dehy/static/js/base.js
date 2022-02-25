var DEHY = {
	init: function(choice='') {
		this.handler_choice(choice);
		$.ajaxSetup({
			beforeSend: function(xhr, settings) {
				if (!DEHY.utils.csrfSafeMethod(settings.type) && !this.crossDomain) {
					xhr.setRequestHeader("X-CSRFToken", DEHY.utils.getCookie('csrftoken'));
				}
			}
		});
	},
	handler_choice: function(choice='') {
		switch (choice) {
			case 'detail':
				DEHY.handlers.cart();
				break;
			case 'index':
				DEHY.handlers.shop();
				break;
			default:
				DEHY.handlers.all();
		}
	},
	handlers: {
		all: function() {
			DEHY.handlers.cart();
			DEHY.handlers.shop();
		},
		shop: function() {
			// DEHY.handlers.cart();
		},
		cart: function() {
			var size_selector = document.getElementById('size_selector');
			size_selector.addEventListener('change', e=> {

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
			});
		},
	},
	ajax: {
		get_cart_quantity: function(data) {
			$.ajax({
		         method: "GET",
		         url: "ajax/get_cart_quantity/",
		         dataType: "json",
		         cache: false,
		         success: DEHY.ajax.update_cart_quantity
		     });
		},
		update_cart_quantity: function(data) {
			var cart = document.getElementById("cart-quantity");
			cart.innerText = data.num_cart_items
		}
	},
	utils: {
		debounce: function(context, func, delay) {
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
			console.log('elements: ', elements)
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
				console.log('serialized: ', serialized)
			}

			return serialized.join('&');

		},
		getCookie: function(name) {
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

		csrfSafeMethod: function(method) {
			return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
		},
		create_element: function({tag, classes, style, text, attrs} = {}) {
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
		create_elements: function(elems, parent) {
			var container = parent || DEHY.utils.create_element({tag:'div', classes:'temp-container'});
			for (let i = 0; i < elems.length; i++) {
				var elem = DEHY.utils.create_element(elems[i]);
				container.appendChild(elem);
				if (elems[i].elems) {
					elem.replaceWith(DEHY.utils.create_elements(elems[i].elems, elem));
				}
			}
			return container
		},
		cleanup_temp_containers: function(container=document) {
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
		remove_children: function(elem) {
			if (elem && elem.hasChildNodes && elem.hasChildNodes()) {
				while (elem.firstChild) {
  					elem.removeChild(elem.firstChild);
				}
			}
		}
	}
}

let optionSupported = false;

try {
  const options = {
    get once() { // This function will be called when the browser
                    //   attempts to access the passive property.
      optionSupported = true;
      return false;
    }
  };

  window.addEventListener("test", null, options);
  window.removeEventListener("test", null, options);
} catch(err) {
  optionSupported = false;
}


// function handlers() {
// 	console.log('handlers')
// 	var product_list = document.getElementById("product_list");
// 	var body = document.querySelector('body');
// 	console.log('body: ', body)
// 	console.log('product_list: ', product_list)
// }

function ajax_update_basket_mini(data){
   $.ajax({
        method: "GET",
        url: "ajax/update_cart_quantity/",
        dataType: "json",
        cache: false,
        success: update_cart_quantity
    });
}


function update_cart_quantity(data) {
	var cart = document.getElementById("cart-quantity");
	cart.innerText = data.num_cart_items
}

