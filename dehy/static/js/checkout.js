

window.addEventListener('load', function () {
	DEHY.checkout.shipping.set_address();

	// DEHY.handlers.checkout.forms = checkout_flow_handler()
	// DEHY.handlers.checkout.shipping = same_as_shipping_handler()
	// DEHY.handlers.checkout.init = function() {
	// 	DEHY.handlers.checkout.forms()
	// 	DEHY.handlers.checkout.shipping()
	// }
	// same_as_shipping_handler();
	// payment_element_setup();
	// checkout_flow_handler();
});


// function checkout_flow_handler() {
// 	var form = document.querySelector('form.checkout-form');
// 	if (form) {
// 		form.addEventListener('submit', e=>{
// 			e.preventDefault();
// 			submit_form_info(e.target);
// 			// get form data
// 			// do ajax post request
// 			//
// 		});
// 	}
// }

// function submit_form_info(form) {
//
// 	// var data = {
// 	// 	'checkout_step': form.closest('section').id,
// 	// 	'form': 'aaaaaaaaaa'
// 	// }
//
// 	var data = DEHY.utils.serialize(form)
// 	console.log('form data: ', data)
//
//
// 	$.ajax({
// 		method: "POST",
// 		url: form.action,
// 		data: data,
// 		success: form_validation_success,
// 		error: form_validation_error,
// 		complete: function() {
// 			return
// 		}
// 	});
// }

// function form_validation_error(response) {
// 	console.log('error: ', response);
// }

// function form_validation_success(response) {
// 	console.log('success: ', response);
//
// 	var next_section = response.next_section
// 	var previous_sections = document.querySelectorAll(`section:not(.${next_section})`);
// 	previous_sections.forEach(function(elem) {
// 		elem.classList.toggle('preview', true);
// 	});
// 	// set all previous sections to preview mode
//
// 	// paint the next form
// }


// var SHIPPING = {
// 	ADDRESS: {},
// 	set_address: function() {
// 		var billing_address_container = document.querySelector('form.billing-form .billing-address-container');
// 		if (billing_address_container) {
// 			billing_address_container.querySelectorAll("input[type='text'], input[type='number']").forEach(function(elem) {
// 				SHIPPING.ADDRESS[elem.name] = elem.value;
// 			});
// 			var country_selector = billing_address_container.querySelector("select[name='country']");
// 			if (country_selector) {
// 				SHIPPING.ADDRESS['country'] = country_selector.value;
// 			}
// 		}
// 	}
// }

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
	gateway: {
		init: function() {
			DEHY.checkout.forms.init();
		}
	},
	forms: {
		create: function(action) {
			// create the form
			var form = DEHY.utils.create_element({tag:'form', attrs:{'action': action}});
			return form
		},
		submit_form_info: function(form) {

			var data = DEHY.utils.serialize(form)
			console.log('form data: ', data)
			$.ajax({
				method: "POST",
				url: form.action,
				data: data,
				success: DEHY.checkout.forms.success,
				error: DEHY.checkout.forms.error,
				complete: function() {
					return
				}
			});
		},
		success: function(response) {
			function get_preview_section(elems, section) {

				switch(section) {
					case 'user_info':
						console.log('user_info');
						let elem = DEHY.utils.create_element({tag:'div', classes:'email', text:elems['email']})
						return elem;
					case 'shipping':
						// do stuff
						return ;
					case 'additional_info':
						return ;
					case 'billing':
						return ;
					case 'review_and_purchase':
						return ;

					default:
						console.log(`Sorry, we are out of ${section}.`);
				}
			}

			console.log('success: ', response);

			var next_section = response.next_section
			var previous_sections = document.querySelectorAll(`section:not(.${next_section})`);
			previous_sections.forEach(function(elem) {
				// set all other sections to preview mode
				elem.classList.toggle('preview', true);
				elem.querySelectorAll('form').forEach(function(form) {
					form.remove()
				});
			});

			// create the elements we're going to reserve, retrieving necessary info from the pageNav
			// paint the elements

			var preview_container = DEHY.utils.create_element({tag:'div', classes:'preview_container'});

			preview_container.appendChild(get_preview_section(response.preview_elems, response.section))

			var next_section_elem = document.querySelector(`section.${next_section}`)


			next_section_elem.appendChild(DEHY.checkout.forms.create(action=`/${next_section}/`))

			// if (response.preview_elems) {
			// 	for (let [tag, val] of Object.entries(response.preview_elems)) {
			// 		let elem = DEHY.utils.create_element({tag:tag, classes:key, text:val['text']})
			// 		preview_container.appendChild(elem)
			// 	}
			// }
			document.getElementById(response.section).appendChild(preview_container)





		},
		error: function(response) {
			console.log('error: ', response);

		},
		init: function() {
			var form = document.querySelector('form.checkout-form');
			if (form) {
				form.addEventListener('submit', e=>{
					e.preventDefault();
					DEHY.checkout.forms.submit_form_info(e.target);
					// get form data
					// do ajax post request
					//
				});
			}
		},
	},
	shipping: {
		ADDRESS: {},
		set_address: function() {
			var billing_address_container = document.querySelector('form.billing-form .billing-address-container');
			if (billing_address_container) {
				billing_address_container.querySelectorAll("input[type='text'], input[type='number']").forEach(function(elem) {
					DEHY.checkout.shipping.ADDRESS[elem.name] = elem.value;
				});
				var country_selector = billing_address_container.querySelector("select[name='country']");
				if (country_selector) {
					DEHY.checkout.shipping.ADDRESS['country'] = country_selector.value;
				}
			}
		},
		init: function() {
			DEHY.checkout.shipping.set_address();

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
	}
}