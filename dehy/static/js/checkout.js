

window.addEventListener('load', function () {
	//
});



function payment_element_setup() {
	const stripe_data = JSON.parse(document.getElementById('stripe-data').textContent);

	var stripe = Stripe(stripe_data.publishable_key);
	var payment_form = document.getElementById('billing-form');

	if (payment_form) {

		const appearance = {
  			theme: 'night',
			labels: 'floating'
		};
		const options = {
		  clientSecret: stripe_data.client_secret,
		  // Fully customizable with appearance API.
		  appearance: appearance,
		};

		// Set up Stripe.js and Elements to use in checkout form, passing the client secret obtained in step 2
		const elements = stripe.elements(options);

		// Create and mount the Payment Element
		const paymentElement = elements.create('payment');
		paymentElement.mount('#payment-element');

		// var style = {
		//   base: {
		//     // Add your base input styles here. For example:
		//     fontSize: '16px',
		//     color: '#32325d',
		// 	fontSmoothing: 'antialiased',
      	// 	':-webkit-autofill': {
        // 		color: '#fce883',
      	// 	},
		// 	'::placeholder': {
        // 		color: '#87BBFD',
      	// 	},
		// 	// padding: '0.75rem',
		// 	backgroundColor: '#30313d',
		// 	// borderRadius: '5px',
		// 	// transition: 'background 0.15s ease, border 0.15s ease, box-shadow 0.15s ease, color 0.15s ease',
		// 	// border: `1px solid #424353`,
		// 	// boxShadow: "0px 2px 4px rgb(0 0 0 / 50%), 0px 1px 6px rgb(0 0 0 / 25%)"
		// }};

		// var elements = stripe.elements();
		// var card = elements.create('card');
		// var cardContainer = document.getElementById('card-element')
		// card.mount(cardContainer);

		// var cardNumber = elements.create('cardNumber');
		// var cardExpiry = elements.create('cardExpiry');
		// var cardCvc = elements.create('cardCvc');
		//
		// cardNumber.mount("#card-element-new")
		// cardExpiry.mount("#card-element-new")
		// cardCvc.mount("#card-element-new")


	}
}

// function same_as_shipping_handler() {
// 	var same_as_shipping_checkbox = document.querySelector("input[name=same_as_shipping]");
//
// 	if (same_as_shipping_checkbox) {
// 		same_as_shipping_checkbox.addEventListener('change', e=>{
// 			var billing_address_container = document.querySelector('form.billing-form .billing-address-container');
//
// 			billing_address_container.querySelectorAll('.form-group').forEach(function(elem) {
// 				elem.classList.toggle('hide', e.target.checked)
// 			})
//
// 			for (let [key, val] of Object.entries(SHIPPING.ADDRESS)) {
// 				if (val) {
// 					let elem = billing_address_container.querySelector(`input[name=${key}]`);
// 					if (elem) {
// 						if (e.target.checked) {
// 							elem.value = val
// 						} else {
// 							elem.value = ''
// 						}
// 					}
// 				}
// 			}
//
// 			var country_selector = billing_address_container.querySelector("select[name='country']");
// 			if (country_selector) {
// 				if (e.target.checked) {
// 					country_selector.value = SHIPPING.ADDRESS['country']
// 				} else {
// 					country_selector.selectedIndex = 0
// 				}
// 			}
// 		})
// 	}
// }

function redirectToCheckoutHandler() {
	var stripe_redirect_btn = document.getElementById('stripe_redirect');

	if (stripe_redirect_btn) {
		stripe_redirect_btn.addEventListener('submit', e=>{
			e.preventDefault();
			var stripe = Stripe('pk_test_51KTDOrLpSVHc8H4yhmmmivcD8wYAIH7WzoslAGkQPCZ0iGQVWIsPsskwa5f4TSRoh42mg9gLKS0txZuZxzTAnYLh00K6pki08H');

			stripe.redirectToCheckout({
			  lineItems: [{
			    price: 'price_1KUEr3LpSVHc8H4yVn96Typb', // Replace with the ID of your price
			    quantity: 1,
			  }],
			  mode: 'payment',
			  successUrl: 'https://127.0.0.1/',
			  cancelUrl: 'https://127.0.0.1/',
			}).then(function (result) {
				document.querySelector("#error-message").innerText = result.error.message;
			  // If `redirectToCheckout` fails due to a browser or network
			  // error, display the localized error message to your customer
			  // using `result.error.message`.
			});
		})
		return false;
	}
}


DEHY.checkout = {
	_stripe: null,
	stripe: {
		client_secret: null,
		pkey: null,
		elements_setup(client_secret=DEHY.checkout.stripe.client_secret) {
			var stripe = DEHY.checkout.stripe.get();

			const appearance = {
	  			theme: 'night',
				labels: 'floating'
			};
			const options = {
			  clientSecret: this.client_secret,
			  // Fully customizable with appearance API.
			  appearance: appearance,
			};

			// Set up Stripe.js and Elements to use in checkout form, passing the client secret obtained in step 2
			const elements = stripe.elements(options);

			// Create and mount the Payment Element
			// const paymentElement = elements.create('payment');
			// paymentElement.mount('#payment-element');

			// Create and mount the Payment Element
			const paymentElement = elements.create('payment');
			var stripe_payment_container = document.getElementById("stripe_payment_container") || DEHY.utils.create_element({tag:'div', attrs:{'id':'stripe_payment_container'}})
			var form = DEHY.checkout.forms.get();
			var form_container = form.querySelector('.form-container');
			form.insertBefore(stripe_payment_container, form_container)
			paymentElement.mount(stripe_payment_container);
		},
		set(pkey=null) {
			if (pkey) {
				DEHY.checkout.stripe.set_pkey(pkey);
			}
			DEHY.checkout._stripe = Stripe(DEHY.checkout.stripe.get_pkey());
		},
		get() {
			return DEHY.checkout._stripe;
		},
		set_pkey(pkey) {
			DEHY.checkout.stripe.pkey = pkey;
		},
		get_pkey() {
			return DEHY.checkout.stripe.pkey;
		},
		init(pkey=null, client_secret=null) {
			// attempts to set the pkey and add the stripe elements to the page
			if (pkey) {
				DEHY.checkout.stripe.set_pkey(pkey)
			}
			if (DEHY.checkout.stripe.get_pkey()) {
				DEHY.checkout.stripe.set();
			}
			if (client_secret) {
				DEHY.checkout.stripe.client_secret = client_secret;
				DEHY.checkout.stripe.elements_setup(client_secret);
			}
		},
	},
	gateway: {
		init: function() {
			DEHY.checkout.forms.init();
		}
	},
	forms: {
		show_submit_button: function(form=null) {
			var form = form || DEHY.checkout.forms.get(),
				hidden = true;

			if (form.closest('section').id=='shipping') {
				if (DEHY.checkout.shipping.check_if_shipping_methods_displayed()) {
					hidden = false;
				}
			} else {
				hidden = false
			}
			form.querySelector("button[type='submit']").hidden = hidden;
			return hidden;

		},
		submit_handler: function(e, form=DEHY.checkout.forms.get()) {
			console.log('submit_handler');
			e.preventDefault();
			if (!form.checkValidity()) {
				document.getElementById('error_container').classList.toggle('hidden', false);
				return false
			} else {
				document.getElementById('error_container').classList.toggle('hidden', true)
			}

			DEHY.checkout.forms.submit_form_info(e.target);
			form.reportValidity();
		},
		get: function() {
			return document.getElementById('checkout')
		},
		create: function(data) {
			// create the form

			var form = DEHY.utils.create_element({tag:'form', classes: 'card card-body checkout-form', attrs:{'method':"post", 'id':'checkout', 'action': `/checkout/${data.next_section}/`}});
			let csrftoken_elem = DEHY.utils.create_element({tag:'input', attrs:{'name':'csrfmiddlewaretoken', 'type': 'hidden', 'value':DEHY.utils.getCookie('csrftoken')}})
			form.append(csrftoken_elem)

			form.append(DEHY.utils.create_elements(data.form_structure))

			DEHY.checkout.forms.init();

			return form
		},
		submit_form_info: function(form) {

			var data = {}
			if (form.closest('section').id == '___shipping') {
				// create two different forms
				data['shipping_address'] = DEHY.utils.serialize(form.querySelector('.address-container'));
				data['shipping_method'] = DEHY.utils.serialize(form.querySelector('.shipping-method-container'));
			} else {
				data = DEHY.utils.serialize(form)
			}
			console.log('form data: ', data)
			$.ajax({
				method: "POST",
				url: form.action,
				data: data,
				success: DEHY.checkout.forms.success_handler,
				error: DEHY.checkout.forms.error,
				complete: function() {
					return
				}
			});
		},
		success_handler: function(response) {
			function get_preview_section(elems, section) {

				switch(section) {
					case 'user_info':
						console.log('user_info');
						let elem = DEHY.utils.create_element({tag:'div', classes:'email', text:elems['email']})
						return elem;
					case 'shipping':
						// do stuff
						for (let [key, val] of Object.entries(response.preview_elems)) {
							let elem = DEHY.utils.create_element({tag:'div', classes:key, text:val})
							preview_container.append(elem)
						}
						return ;
					case 'additional_info':
						return ;
					case 'billing':
						return ;
					case 'review_and_purchase':
						return ;

					default:
						console.log(`no match for switch statement found with section=${section}.`);
				}
			}

			console.log('success response: ', response);

			var next_section = response.next_section
			var checkout_sections = Array.from(document.querySelectorAll('#checkout_flow section'));
			var previous_sections = checkout_sections.slice(0,checkout_sections.indexOf(document.querySelector(`section#${next_section}`)))

			console.log('previous_sections: ', previous_sections)
			previous_sections.forEach(function(elem) {
				// set all other sections to preview mode
				elem.classList.toggle('preview', true);
				elem.querySelectorAll('form').forEach(function(form) {
					form.remove()
				});
			});

			var preview_container = DEHY.utils.create_element({tag:'div', classes:'preview_container'});
			preview_container.append(get_preview_section(response.preview_elems, response.section));
			var next_section_elem = document.querySelector(`section#${next_section}`);

			next_section_elem.append(DEHY.checkout.forms.create(response));
			document.getElementById(response.section).append(preview_container);
			DEHY.checkout.forms.init();
			if (response.stripe_pkey && response.client_secret && response.next_section=="billing") {
				DEHY.checkout.stripe.init(response.stripe_pkey, response.client_secret)
			}

		},
		error: function(response) {
			// add errors to the error element
			console.log('error: ', response);
			document.getElementById('error_container').append(DEHY.utils.create_element({tag:'div', classes:'error', text: response.statusText, attrs:{'id':'errors'}}))

		},
		init: function() {

			// debounceBtn.addEventListener("click", debounce(this, function () {displayDebounce.textContent = "Today is: " + new Date().toUTCString();}, 1000));

			var form = document.querySelector('form.checkout-form');
			if (form) {
				/******
					debounce testing
				*****/
				// form.addEventListener('submit', DEHY.utils.debounce(this, DEHY.checkout.forms.submit_handler, 500));
				// form.addEventListener('submit', e=> {
				// 	e.preventDefault();
				// 	DEHY.utils.debounce(e, DEHY.checkout.forms.submit_handler(e), 500);
				// });

				DEHY.utils.cleanup_temp_containers();
				DEHY.checkout.forms.show_submit_button();
				DEHY.checkout.shipping.billing_same_as_shipping_handler();

				form.addEventListener('submit', e=>{
					DEHY.checkout.forms.submit_handler(e);
				});
				form.addEventListener('change', e=> {
					console.log('form changed')
					if (form.closest('section').id == 'shipping') {
						DEHY.checkout.shipping.ADDRESS.set();

						if (e.target.matches('#id_postcode, #id_state, #id_city')) {
							// get/update the shipping methods
							var data = {[`${e.target.id}`]: e.target.value, 'action': e.target.closest('form').action}
							DEHY.checkout.shipping.get_shipping_methods(data)
							console.log('matched')
							DEHY.checkout.forms.show_submit_button();
						}
					}
					if (e.target.matches("input#id_same_as_shipping")) {
						// set or reset the address elements
						DEHY.checkout.shipping.billing_same_as_shipping_handler(e.target.checked);
					}
				});
			}
		},
	},
	shipping: {
		billing_same_as_shipping_handler(checked=true, form=DEHY.checkout.forms.get()) {

			for (let [key, val] of Object.entries(DEHY.checkout.shipping.ADDRESS.get())) {
				let inputElem = form.querySelector(`input[name=${key}]`);
				if (inputElem) {
					inputElem.classList.toggle('hidden', checked)
					inputElem.value = (checked) ? val : '';
				}
				var country_selector = form.querySelector("select[name='country']");
				if (country_selector) {
					country_selector.value = (checked) ? val : '';
					country_selector.classList.toggle('hidden', checked);
				}
			}
		},
		ADDRESS: {
			_address: {},
			get() {
				return this._address;
			},
			set(address=null) {
				var form = DEHY.checkout.forms.get();
				form.querySelectorAll("input[type='text'], input[type='number'], input[type='tel']").forEach(function(elem) {
					DEHY.checkout.shipping.ADDRESS._address[elem.name] = elem.value;
				});
				var country_selector = form.querySelector("select[name='country']");
				if (country_selector) {
					DEHY.checkout.shipping.ADDRESS._address['country'] = country_selector.value;
				}
			},
		},
		METHOD: {
			_method: {},
			get() {
				return this._method;
			},
			set() {
				return false;
			}
		},
		address_is_valid: function() {
			//
		},
		// set_address: function() {
		// 	var billing_address_container = document.querySelector('form.billing-form .billing-address-container');
		// 	if (billing_address_container) {
		// 		billing_address_container.querySelectorAll("input[type='text'], input[type='number']").forEach(function(elem) {
		// 			DEHY.checkout.shipping.ADDRESS[elem.name] = elem.value;
		// 		});
		// 		var country_selector = billing_address_container.querySelector("select[name='country']");
		// 		if (country_selector) {
		// 			DEHY.checkout.shipping.ADDRESS['country'] = country_selector.value;
		// 		}
		// 	}
		// },
		init: function() {
			DEHY.checkout.shipping.ADDRESS.set();

			var same_as_shipping_checkbox = document.querySelector("input[name=same_as_shipping]");

			if (same_as_shipping_checkbox) {
				same_as_shipping_checkbox.addEventListener('change', e=>{
					var billing_address_container = document.querySelector('form.billing-form .billing-address-container');

					billing_address_container.querySelectorAll('.form-group').forEach(function(elem) {
						elem.classList.toggle('hide', e.target.checked)
					})

					for (let [key, val] of Object.entries(DEHY.checkout.shiping.ADDRESS)) {
						if (val) {
							let elem = billing_address_container.querySelector(`input[name=${key}]`);
							if (elem) {
								if (e.target.checked) {
									elem.value = val
								} else {
									elem.value = ''
								}
							}
						}
					}

					var country_selector = billing_address_container.querySelector("select[name='country']");
					if (country_selector) {
						if (e.target.checked) {
							country_selector.value = DEHY.checkout.shipping.ADDRESS['country']
						} else {
							country_selector.selectedIndex = 0
						}
					}
				})
			}
		},
		get_shipping_methods: function(data) {
			//
			$.ajax({
				method: "GET",
				url: data.action,
				data: data,
				success: DEHY.checkout.shipping.display_shipping_methods,
				error: DEHY.checkout.forms.error,
				complete: function() {
					return
				}
			});
		},
		display_shipping_methods: function(data) {
			console.log('display_shipping_methods: ', data);
			// add the shipping methods to the existing form
			var form = DEHY.checkout.forms.get(),
				fieldset = DEHY.utils.create_element({tag:'fieldset'});

			var shipping_method_container = document.querySelector('.shipping-method-container');

			if (shipping_method_container) {
				DEHY.utils.remove_children(shipping_method_container);
			} else {
				shipping_method_container = DEHY.utils.create_element({tag:'div', classes:'shipping-method-container'})
			}


			shipping_method_container.append(fieldset)
			fieldset.append(DEHY.utils.create_element({tag:'legend', classes: "required", text:'Shipping Methods'}))
			var prefix = (data.prefix) ? `${data.prefix}-`:'';
			data.shipping_methods.forEach((method, ix) => {
				// create form group
				let id = `id_${prefix}method_code_${ix}`;
				var method_structure = [{
					'tag': 'div',
					'classes': 'form-group form-check row',
					'elems': [{
						'tag': 'input',
						'classes':'form-check-input',
						'attrs': {
							'type':'radio', 'name':'method_code', 'id':id, 'value': method.code
						}
					},
					{
						'tag': 'label',
						'classes': 'form-check-label',
						'text': `${method.name} — $${method.cost}`,
						'attrs': {
							'for': id,
						}
					}]
				}]
				let elem = DEHY.utils.create_elements(method_structure, fieldset)
				elem.querySelector
				// append it to the shipping_method_container

			})

			DEHY.utils.cleanup_temp_containers()

			shipping_method_container.querySelector("input[type='radio']").checked = true;
			form.insertBefore(shipping_method_container, document.querySelector('.error-container.button-container'))
			DEHY.checkout.forms.show_submit_button();

			console.log('display_shipping_methods: ', data);
		},
		// check if shipping methods are on the page
		check_if_shipping_methods_displayed: function() {
			var displayed = false;
			if (document.querySelector(".shipping-method-container")) {
				var fieldset = document.querySelector(".shipping-method-container fieldset");
				if (fieldset && fieldset.querySelectorAll('input').length > 0) {
					displayed = true;
				}
			}
			return displayed;
		}
	}
}

