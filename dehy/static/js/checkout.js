

window.addEventListener('load', function () {
	//
});

// DEHY.checkout namespace
dehy.ch = {
	utils: {
		get_next_section(section=null) {
			var checkout_sections = Array.from(document.querySelectorAll('#checkout_flow section'));
			var index = checkout_sections.indexOf(document.querySelector(`section#${section}`))
			return checkout_sections[Math.min(4, index+1)];
		},
		get_next_sections(section=null, include_self=0) {
			var checkout_sections = Array.from(document.querySelectorAll('#checkout_flow section'));
			return checkout_sections.slice(checkout_sections.indexOf(dehy.ch.utils.get_next_section(section))+1-include_self, checkout_sections.length);
		},
		get_previous_section(section=null) {
			var checkout_sections = Array.from(document.querySelectorAll('#checkout_flow section'));
			var index = checkout_sections.indexOf(document.querySelector(`section#${section}`));
			return checkout_sections[Math.max(0, index)];
		},
		get_previous_sections(section=null, include_self=0) {
			var checkout_sections = Array.from(document.querySelectorAll('#checkout_flow section'));
			var index = checkout_sections.indexOf(document.querySelector(`section#${section}`))
			return checkout_sections.slice(0, Math.min(4, index+include_self))
		},

	},
	_stripe: null,
	stripe: {
		async confirmSetupHandler() {
			  var stripe = dehy.ch.stripe.get();
			  var elements = dehy.ch.stripe.elements.get();

			  const {error} = await stripe.confirmSetup({
				  //`Elements` instance that was used to create the Payment Element
				  elements,
				  redirect: 'if_required',
				  confirmParams: {
					return_url: '/checkout/thank_you/',
				  },
			});
		},
		client_secret: null,
		pkey: null,
		_elements: null,
		elements: {
			set(options=null) {
				let stripe = dehy.ch.stripe.get();
				dehy.ch.stripe._elements = (options) ? stripe.elements(options) : stripe.elements();
			},
			get(options=null) {
				if (dehy.ch.stripe._elements) {
					return dehy.ch.stripe._elements;
				} else {
					let stripe = dehy.ch.stripe.get();
					dehy.ch.stripe._elements = (options) ? stripe.elements(options) : stripe.elements();
				}
				return dehy.ch.stripe._elements;
			},
		},

		payment_element_setup(client_secret=dehy.ch.stripe.client_secret) {
			var stripe = dehy.ch.stripe.get();
			// Set up Stripe.js and Elements to use in checkout form, passing the client secret obtained in step 2
			const elements = dehy.ch.stripe.elements.get();

			// Create and mount the Payment Element
			// const paymentElement = elements.create('payment');
			// paymentElement.mount('#payment-element');

			// Create and mount the Payment Element
			const paymentElement = elements.create('payment');
			var stripe_payment_container = document.getElementById("stripe_payment_container") || dehy.utils.create_element({tag:'div', attrs:{'id':'stripe_payment_container'}})
			var form = dehy.ch.forms.get();
			var form_container = form.querySelector('.form-container');
			form.insertBefore(stripe_payment_container, form_container)
			paymentElement.mount(stripe_payment_container);
		},
		card_setup(style=null) {
			console.log('called card setup');
			// dehy.utils.remove_event_listeners(form);
			var cardClasses = {
				base: 'testicles',
				focus: 'focused',
				empty: 'empty',
				invalid: 'invalid',
			}
			var style = style || {
				base: {
					color: "#32325d",
					fontFamily: 'Consolas, Menlo, monospace',
					fontSmoothing: "antialiased",
					fontSize: "16px",
					"::placeholder": {
						color: "#aab7c4"
					},
					'::placeholder': {
				        color: '#CFD7DF',
				    },
				    ':-webkit-autofill': {
						color: '#e39f48',
					},
			},
			invalid: {
				color: "#fa755a",
				iconColor: "#fa755a"
				},
			};

			var inputs = document.querySelectorAll('input');
			Array.prototype.forEach.call(inputs, function(input) {
				input.addEventListener('focus', function() {
					input.classList.add('focused');
				});
				input.addEventListener('blur', function() {
					input.classList.remove('focused');
				});
				input.addEventListener('keyup', function() {
					if (input.value.length === 0) {
						input.classList.add('empty');
					} else {
						input.classList.remove('empty');
					}
				});
			});

			var options = {style: style, classes: cardClasses};

			var form = dehy.ch.forms.get(),
				stripe = dehy.ch.stripe.get(),
				elements = dehy.ch.stripe.elements.get();

			var stripe_payment_container = document.getElementById("stripe_payment_container") || dehy.utils.create_element({tag:'div', classes: 'form-group row', attrs:{'id':'stripe_payment_container'}});
			var stripe_cardNumber_container = document.getElementById("stripe_card_number") || dehy.utils.create_element({tag:'label', classes: 'col-7', text:'Card Number', attrs:{'for': 'Card Number', 'id':'stripe_card_number'}});
			var stripe_cardExpiry_container = document.getElementById("stripe_card_expiry") || dehy.utils.create_element({tag:'label', classes: 'col-3', text:'Exp', attrs:{'id':'stripe_card_expiry'}});
			var stripe_cardCvc_container = document.getElementById("stripe_card_cvc") || dehy.utils.create_element({tag:'label', classes: 'col-2', text:'CVC', attrs:{'id':'stripe_card_cvc'}});

			stripe_payment_container.append(stripe_cardNumber_container, stripe_cardExpiry_container, stripe_cardCvc_container);
			var form_container = form.querySelector('.form-container');
			form.insertBefore(stripe_payment_container, form_container);

			// we create the individual card elements since we'll be using our own zipcode element
			// get or create the card element

			var cardNumber = (elements.getElement('cardNumber')) ? elements.getElement('cardNumber') : elements.create('cardNumber', options);
			var cardExpiry = (elements.getElement('cardExpiry')) ? elements.getElement('cardExpiry') : elements.create('cardExpiry', options);
			var cardCvc = (elements.getElement('cardCvc')) ? elements.getElement('cardCvc') : elements.create('cardCvc', options);

			// mount the card elements to the page
			cardNumber.mount(stripe_cardNumber_container);
			cardExpiry.mount(stripe_cardExpiry_container);
			cardCvc.mount(stripe_cardCvc_container);

			cardNumber.on('change', function(event) {
				var displayError = document.getElementById('error_container');
				if (event.error) {
					displayError.classList.toggle('hide', false);
					displayError.textContent = event.error.message;
				} else {
					displayError.classList.toggle('hide', true);
					displayError.textContent = '';
				}
			});

			form.removeEventListener('submit', dehy.ch.forms.submit_handler);

			form.addEventListener('submit', e=> {
				// We don't want to let default form submission happen here,
				// which would refresh the page.
				e.preventDefault();
				var form_data = new FormData(form);
				stripe.createPaymentMethod({
					type: 'card',
					card: cardNumber,
					billing_details: {
						// Include any additional collected billing details.
						name: `${form_data.get('first_name')} ${form_data.get('last_name')}`,
						phone: `${form_data.get('phone_number')}`,
						address: {
							line1: form_data.get('line1'),
							line2: form_data.get('line2'),
							city: form_data.get('line4'),
							state: form_data.get('state'),
							postal_code: form_data.get('postcode'),
							country: form_data.get('country'),
						}
					},
				}).then(dehy.ch.stripe.paymentMethodHandler);
			});

			var myPostalCodeField = document.querySelector('input[name="postcode"]');
			myPostalCodeField.addEventListener('change', function(event) {
				cardElement.update({value: {postalCode: event.target.value}});
			});
		},

		paymentMethodHandler(response) {

			console.log('paymentMethodHandler response: ', response);
			if (response.error) {
				// Show error in payment form
				dehy.ch.forms.errors.display(response.error);
				console.log('ERROR: ', response.error);
  			} else {
				var card = response.paymentMethod.card;
				var form_data = new FormData(dehy.ch.forms.get());
				form_data.set('payment_method_id', response.paymentMethod.id);

				$.ajax({
					method: "POST",
					dataType: 'json',
					url: '/checkout/billing/',
					contentType: false,
					processData: false,
					data: form_data,
					success: dehy.ch.forms.success_handler,
					error: dehy.ch.forms.errors.display,
					complete: function() {
						console.log('completed!!!')
						return
					}
				});



			}
		},
		handleServerResponse(response) {
			console.log('handleServerResponse response: ', response);

			if (response.error) {
				// Show error from server on payment form
				dehy.ch.forms.errors.display(response.error);
				console.log('ERROR: ', response.error);
			} else if (response.requires_action) {
				// Use Stripe.js to handle required card action
				stripe.handleCardAction(
					response.payment_intent_client_secret
				).then(dehy.ch.stripe.handleStripeJsResult);
			} else {
				// Show success message
				dehy.ch.forms.errors.display(response.error);
				console.log('ERROR: ', response.error);
			}
		},
		handleStripeJsResult(result) {
			console.log('handleStripeJsResult result: ', result);

			if (result.error) {
				// Show error in payment form
				console.log('ERROR: ', response.error);
				dehy.ch.forms.errors.display(result.error);
			} else {
				var form_data = new FormData(dehy.ch.forms.get());

				$.ajax({
					method: "POST",
					dataType: 'json',
					url: '/checkout/place_order/',
					contentType: false,
					processData: false,
					data: form_data,
					success: dehy.ch.forms.success_handler,
					error: dehy.ch.forms.errors.display,
					complete: function() {
						console.log('completed!!!')
						return
					}
				});

				form_data.set('payment_intent_id', result.paymentIntent.id);

				// The card action has been handled
				// The PaymentIntent can be confirmed again on the server
				// fetch('/checkout/place_order/', {
				// 	method: 'POST',
				// 	headers: { 'Content-Type': 'application/json' },
				// 	body: JSON.stringify({ form_data })
				// }).then(function(confirmResult) {
				// 	return confirmResult.json();
				// }).then(dehy.ch.stripe.handleServerResponse);
			}
		},
		set(pkey=null) {
			if (pkey) {
				dehy.ch.stripe.set_pkey(pkey);
			}
			dehy.ch._stripe = Stripe(dehy.ch.stripe.get_pkey());
		},
		get() {
			return dehy.ch._stripe;
		},
		set_pkey(pkey) {
			dehy.ch.stripe.pkey = pkey;
		},
		get_pkey() {
			return dehy.ch.stripe.pkey;
		},
		init(pkey=dehy.ch.stripe.pkey, client_secret=dehy.ch.stripe.client_secret) {
			console.log('initiating stripe');
			if (dehy.ch.stripe.get() && dehy.ch.stripe.elements.get()) {
				// already created, just need to unhide it
				var stripe_payment_container = document.getElementById('stripe_payment_container');
				stripe_payment_container.classList.toggle('display-none', false);
				stripe_payment_container.closest('form').classList.toggle('display-none', false);
			} else {// attempts to set the pkey and add the stripe elements to the page
				if (pkey) {
					dehy.ch.stripe.set_pkey(pkey)
				}
				if (dehy.ch.stripe.get_pkey()) {
					dehy.ch.stripe.set();
				}
				// will never be true,
				if (client_secret==false) {
					// var appearance = {
			  		// 	theme: 'night',
					// 	labels: 'floating'
					// };
					// var options = {
					//   clientSecret: client_secret,
					//   // Fully customizable with appearance API.
					//   appearance: appearance,
					// };
					// dehy.ch.stripe.elements.set(options)
					// dehy.ch.stripe.client_secret = client_secret;
					// dehy.ch.stripe.payment_element_setup(client_secret);

				} else {
					dehy.ch.stripe.elements.set()
					dehy.ch.stripe.card_setup()
				}
			}
		},
	},
	gateway: {
		init: function() {
			var form = dehy.ch.forms.get_or_create('user_info', FormStructures['user_info']);
			document.querySelector('section#user_info').append(form);
			dehy.ch.forms.init();
			dehy.ch.forms.reverse_form_labels(form);
		}
	},
	forms: {
		saved: {},
		show_submit_button: function(form=null) {
			var form = form || dehy.ch.forms.get(),
				hidden = true;

			if (form.closest('section').id=='shipping') {
				if (dehy.ch.shipping.check_if_shipping_methods_displayed()) {
					hidden = false;
				}
			} else {
				hidden = false
			}
			form.querySelector("button[type='submit']").hidden = hidden;
			return hidden;

		},
		place_order() {

		},
		submit_handler(e) {
			var form = dehy.ch.forms.get();
			// var form = e.target();
			e.preventDefault();
			if (!form.checkValidity()) {
				document.getElementById('error_container').classList.toggle('hidden', false);
			} else {
				document.getElementById('error_container').classList.toggle('hidden', true);
			}
			// if (form.closest('section').id=='place_order') {
			// 	dehy.ch.stripe.paymentSubmissionHandler();
			// }

			dehy.ch.forms.submit_form_info(e.target);
			form.reportValidity();
		},
		get(name) {
			var form = document.querySelectorAll('#checkout_flow form:not(.display-none)')[0];
			if (name) {
				form = dehy.ch.forms.saved[name];
			}
			return form
		},
		create(section, form_structure) {
			// create the form

			var form = dehy.utils.create_element({tag:'form', classes: 'card card-body checkout-form', attrs:{'method':"post", 'id':'checkout', 'action': `/checkout/${section}/`}});
			let csrftoken_elem = dehy.utils.create_element({tag:'input', attrs:{'name':'csrfmiddlewaretoken', 'type': 'hidden', 'value':dehy.utils.getCookie('csrftoken')}})
			form.append(csrftoken_elem)
			form.append(dehy.utils.create_elements(form_structure))

			dehy.ch.forms.init();
			return form
		},
		// moves the labels to be after their various inputs/selects
		reverse_form_labels(form=dehy.ch.forms.get()) {
			form.querySelectorAll('label').forEach(function(label) {
				var parent = label.parentElement;
				var input = parent.querySelector('input, select');
				if (input) {
					parent.insertBefore(input, label);
				}

				// let label_element = parent.removeChild(label);
				//
				// parent.insertAdjacentElement('beforeend', label);
			});
		},
		submit_form_info(form) {
			var form_data = new FormData(form);
			form.querySelectorAll("input[type='checkbox']").forEach(function(checkbox) {
				form_data.set(checkbox.name, form_data.has(checkbox.name) ? 'on':'off');
			})
			var data = {}

			if (form.closest('section').id == '___shipping') {
				// create two different forms
				data['shipping_address'] = dehy.utils.serialize(form.querySelector('.address-container'));
				data['shipping_method'] = dehy.utils.serialize(form.querySelector('.shipping-method-container'));
			} else {
				data = dehy.utils.serialize(form)
			}
			console.log('form data: ', data)

			$.ajax({
				method: "POST",
				url: form.action,
				contentType: false,
				processData: false,
				data: form_data,
				success: dehy.ch.forms.success_handler,
				error: dehy.ch.forms.error,
			});
		},
		success_handler(response, textStatus, xhr) {
			console.log('success response: ', response);
			console.log('textStatus: ', textStatus);
			console.log('xhr.status: ', xhr.status);


			// if ((response.section=='billing'||response.section=='place_order') && response.status == 'requires_confirmation') {
			// 	console.log('requires_confirmation');
			// 	dehy.ch._stripe.handleCardAction(
			// 		response.payment_intent_client_secret
			// 	).then(dehy.ch.stripe.handleStripeJsResult);
			// }

			if (xhr.status===302) {
				console.log('hi')
			} else {
				if (response.section=='billing') {
					var stripe_payment_container = document.getElementById('stripe_payment_container');
					stripe_payment_container.classList.toggle('display-none', true);
					stripe_payment_container.closest('form').classList.toggle('display-none', true);
				} else {
					dehy.ch.forms.save_and_remove(); //1
				}

				var next_section = dehy.ch.utils.get_next_section(response.section);
				// var form = dehy.ch.forms.get_or_create(next_section.id, FormStructures[next_section.id]); //2
				var form = dehy.ch.forms.get_or_create(next_section.id, FormStructures[next_section.id]); //2

				next_section.append(form); //3
				dehy.ch.forms.disable_edit_buttons(); //4
				let previous_section = dehy.ch.utils.get_previous_section(response.section);
				dehy.ch.forms.create_preview(response.section, response.preview_elems); //5
				dehy.ch.forms.enable_edit_buttons(next_section.id); //6
				dehy.ch.forms.init();
				dehy.ch.forms.reverse_form_labels(form);
			}


			console.log('next_section.id', next_section.id)

			if (next_section.id=="billing") {
				dehy.ch.shipping.billing_same_as_shipping_handler();
				if (response.stripe_pkey) {
					dehy.ch.stripe.init(response.stripe_pkey, response.client_secret);
				}
			}

		},
		// Attempts to get a previously saved form, or create one if it doesn't exist
		// If a form isnt saved under the section name, creates a new one from given form structure (required)
		// If no form structure given, falls back to the current form using the get() method
		get_or_create(section=null, form_structure=null) {
			var form = dehy.ch.forms.create(section, form_structure);
			return form;
		},
		// get_or_create(section=null, form_structure=null) {
		// 	var form = dehy.ch.forms.get();
		//
		// 	if (section && dehy.ch.forms.saved.hasOwnProperty(section)) {
		// 		form = dehy.ch.forms.saved[section]
		// 	} else if (form_structure){
		// 		form = dehy.ch.forms.create(section, form_structure)
		// 	}
		// 	return form;
		// },
		save(form, section) {
			dehy.ch.forms.saved[section] = form;
		},
		save_and_remove() {
			var all_checkout_sections = Array.from(document.querySelectorAll('#checkout_flow section'));

			all_checkout_sections.forEach(function(section) {
				if (section.querySelector('form')) {
					let form = section.querySelector('form')

					let copy = form.cloneNode(true)

					if (section.id=="billing") {

					} else {
						dehy.ch.forms.save(form, section.id);
						form.remove();
					}

				}
			});

		},
		// enables all edit buttons in sections prior to given section
		enable_edit_buttons(section_name) {
			dehy.ch.utils.get_previous_sections(section_name).forEach(function(section) {
				let edit_btn = section.querySelector('button.edit')
				if (edit_btn) {

					edit_btn.hidden = false;
					edit_btn.disabled = false;


					edit_btn.addEventListener('click', e=>{
						var preview_container = section.querySelector('.preview_container');
						if (preview_container) {
							preview_container.remove()
						}
						dehy.ch.forms.save_and_remove(); //1
						var form = dehy.ch.forms.get_or_create(section.id, FormStructures[section.id]); //2
						section.append(form); //3
						if (section.id=='billing') {
							dehy.ch.stripe.init();
						}
						dehy.ch.forms.disable_edit_buttons(); //4
						dehy.ch.forms.clear_previews(section.id) //5
						// let previous_section = dehy.ch.utils.get_previous_section(section.id);
						dehy.ch.forms.enable_edit_buttons(dehy.ch.utils.get_previous_section(section.id).id) //6

						dehy.ch.forms.init();
						dehy.ch.forms.reverse_form_labels(form);
						// dehy.ch.forms.init();
					});
				}
			})
		},
		// disables and hides all edit buttons
		disable_edit_buttons() {
			document.querySelectorAll("button.edit").forEach(function(elem) {
				elem.hidden = true;
				elem.disabled = true;
				dehy.utils.remove_event_listeners(elem);
			});
		},

		// create a preview of a section form and append it to that section
		create_preview(section, elems) {
			function get_preview_section(elems, section) {
				switch(section) {
					case 'user_info':
						console.log('user_info');
						let elem = dehy.utils.create_element({tag:'div', classes:'email', text:elems['email']})
						return elem;
					case 'shipping':
						// do stuff
						for (let [key, val] of Object.entries(elems)) {
							let elem = dehy.utils.create_element({tag:'div', classes:key, text:val})
							preview_container.append(elem)
						}
						return ;
					case 'additional_info':

						for (let [key, val] of Object.entries(elems)) {
							let elem = dehy.utils.create_element({tag:'div', classes:key, text:val})
							preview_container.append(elem)
						}
					case 'billing':
						for (let [key, val] of Object.entries(elems)) {
							let elem = dehy.utils.create_element({tag:'div', classes:key, text:val})
							preview_container.append(elem)
						}
						return ;
					case 'place_order':
						return ;

					default:
						console.log(`no match for switch statement found with section=${section}.`);
				}
			}
			var preview_container = dehy.utils.create_element({tag:'div', classes:'preview_container'});
			preview_container.append(get_preview_section(elems, section));
			document.getElementById(section).append(preview_container);
		},

		clear_previews(section) {

			dehy.ch.utils.get_next_sections(section, 1).forEach(function(section) {
				section.querySelectorAll('.preview_container').forEach(function(elem) {
					elem.remove();
				});
			});
		},
		errors: {
			display(error_message) {
				console.log('error: ', error_message);
				var form = dehy.ch.forms.get();
				var error_container = form.querySelector('#error_container');
				error_container.classList.toggle('hide', false);
				error_container.textContent = error_message
				// error_container.append(dehy.utils.create_element({tag:'div', classes:'error', text: error_message, attrs:{'id':'errors'}}));
			},
			hide() {
				var form = dehy.ch.forms.get();
				var error_container = form.querySelector('#error_container');
				error_container.classList.toggle('hide', true);
				error_container.textContent = ''
			},
		},
		// dehy.ch.forms.init()
		init() {

			var form = dehy.ch.forms.get();
			if (form) {
				/******
					debounce testing
				*****/
				// form.addEventListener('submit', dehy.utils.debounce(this, dehy.ch.forms.submit_handler, 500));
				// form.addEventListener('submit', e=> {
				// 	e.preventDefault();
				// 	dehy.utils.debounce(e, dehy.ch.forms.submit_handler(e), 500);
				// });

				dehy.utils.cleanup_temp_containers();
				dehy.ch.forms.show_submit_button();

				var inputs = document.querySelectorAll('input');
				Array.prototype.forEach.call(inputs, function(input) {
					if (input.value.length === 0) {
					  input.classList.add('empty');
					} else {
					  input.classList.remove('empty');
					}

				    input.addEventListener('focus', function() {
				      input.classList.add('focused');
				    });
				    input.addEventListener('blur', function() {
				      input.classList.remove('focused');
				    });
				    input.addEventListener('keyup', function() {
				      if (input.value.length === 0) {
				        input.classList.add('empty');
				      } else {
				        input.classList.remove('empty');
				      }
				    });
				});

				form.addEventListener('submit', dehy.ch.forms.submit_handler);
				form.addEventListener('blur', e=> {
					if (form.closest('section').id == 'shipping') {
						dehy.ch.shipping.ADDRESS.set();

						if (e.target.matches('#id_postcode, #id_state, #id_city')) {
							// get/update the shipping methods
							var data = {[`${e.target.id}`]: e.target.value, 'action': e.target.closest('form').action};
							dehy.ch.shipping.get_shipping_methods(data);
							console.log('getting shipping methods');
							dehy.ch.forms.show_submit_button();
						}
					}
					if (e.target.matches("input#id_same_as_shipping")) {
						// set or reset the address elements
						dehy.ch.shipping.billing_same_as_shipping_handler(e.target.checked);
					}
				});
			}
		},
	},
	shipping: {
		billing_same_as_shipping_handler(checked=true, form=dehy.ch.forms.get()) {
			var elems = Array.from(form.querySelector('.form-container').querySelectorAll("input:not([type=hidden], [name='same_as_shipping']), label:not([for='id_same_as_shipping']), select"));
			var form_controls = [...new Set(elems.map(function(e) {return e.closest('.form-control')}))]
			var address = dehy.ch.shipping.ADDRESS.get();
			form_controls.forEach(function(row) {
				row.classList.toggle('display-none', checked);
				var inputs_and_labels = row.querySelectorAll("input:not([type=hidden], [name='same_as_shipping']), label:not([for='id_same_as_shipping']), select")
				inputs_and_labels.forEach(function(elem) {
					if (elem.name && address.hasOwnProperty(elem.name)) {
						elem.value = (checked) ? address[elem.name] : '';
					}
				});
			});

			// for (let [key, val] of Object.entries(dehy.ch.shipping.ADDRESS.get())) {
			// 	let inputElem = form.querySelector(`input[name=${key}]`);
			// 	if (inputElem) {
			// 		inputElem.classList.toggle('hidden', checked)
			// 		inputElem.value = (checked) ? val : '';
			// 	}
			// 	var country_selector = form.querySelector("select[name='country']");
			// 	if (country_selector) {
			// 		country_selector.value = (checked) ? val : '';
			// 		country_selector.classList.toggle('hidden', checked);
			// 	}
			// }
		},
		ADDRESS: {
			_address: {},
			get() {
				return this._address;
			},
			set(address=null) {
				var form = dehy.ch.forms.get();
				form.querySelectorAll("input[type='text'], input[type='number'], input[type='tel']").forEach(function(elem) {
					dehy.ch.shipping.ADDRESS._address[elem.name] = elem.value;
				});
				var country_selector = form.querySelector("select[name='country']");
				if (country_selector) {
					dehy.ch.shipping.ADDRESS._address['country'] = country_selector.value;
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
		address_is_valid() {
			//
		},
		// set_address: function() {
		// 	var billing_address_container = document.querySelector('form.billing-form .billing-address-container');
		// 	if (billing_address_container) {
		// 		billing_address_container.querySelectorAll("input[type='text'], input[type='number']").forEach(function(elem) {
		// 			dehy.ch.shipping.ADDRESS[elem.name] = elem.value;
		// 		});
		// 		var country_selector = billing_address_container.querySelector("select[name='country']");
		// 		if (country_selector) {
		// 			dehy.ch.shipping.ADDRESS['country'] = country_selector.value;
		// 		}
		// 	}
		// },
		init() {
			dehy.ch.shipping.ADDRESS.set();

			var same_as_shipping_checkbox = document.querySelector("input[name=same_as_shipping]");

			if (same_as_shipping_checkbox) {
				same_as_shipping_checkbox.addEventListener('change', e=>{
					var billing_address_container = document.querySelector('form.billing-form .billing-address-container');

					billing_address_container.querySelectorAll('.form-group').forEach(function(elem) {
						elem.classList.toggle('hide', e.target.checked)
					})

					for (let [key, val] of Object.entries(dehy.ch.shiping.ADDRESS)) {
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
							country_selector.value = dehy.ch.shipping.ADDRESS['country']
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
				success: dehy.ch.shipping.display_shipping_methods,
				error: dehy.ch.forms.errors.display,
				complete: function() {
					return
				}
			});
		},
		display_shipping_methods: function(data) {
			console.log('display_shipping_methods: ', data);
			// add the shipping methods to the existing form
			var form = dehy.ch.forms.get(),
				fieldset = dehy.utils.create_element({tag:'fieldset'});

			var shipping_method_container = document.querySelector('.shipping-method-container');

			if (shipping_method_container) {
				dehy.utils.remove_children(shipping_method_container);
			} else {
				shipping_method_container = dehy.utils.create_element({tag:'div', classes:'shipping-method-container'})
			}


			shipping_method_container.append(fieldset)
			fieldset.append(dehy.utils.create_element({tag:'legend', classes: "required", text:'Shipping Methods'}))
			var prefix = (data.prefix) ? `${data.prefix}-`:'';
			data.shipping_methods.forEach((method, ix) => {
				// create form group
				let id = `id_${prefix}method_code_${ix}`;
				var method_structure = [{
					'tag': 'div',
					'classes': 'form-control row',
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
				let elem = dehy.utils.create_elements(method_structure, fieldset)
				elem.querySelector
				// append it to the shipping_method_container

			})

			dehy.utils.cleanup_temp_containers()

			shipping_method_container.querySelector("input[type='radio']").checked = true;
			form.insertBefore(shipping_method_container, document.querySelector('.error-container.button-container'))
			dehy.ch.forms.show_submit_button();

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

