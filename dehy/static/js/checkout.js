

window.addEventListener('load', function () {
	//
});

// DEHY.checkout namespace
dehy.ch = {
	utils: {
		re: {
			us: '(^[0-9]{5}$)|(^[0-9]{5}-[0-9]{4}$)',
			ca: /^[abceghjklmnprstvxy][0-9][abceghjklmnprstvwxyz]\s?[0-9][abceghjklmnprstvwxyz][0-9]$/i,
			mx: this.us

		},
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
		deactivate_sections() {
			document.querySelectorAll('#checkout_flow section').forEach(function(section) {
				section.classList.toggle('active', false);
			})
		}

	},
	_stripe: null,
	gateway: {
		init: function() {
			var form = dehy.ch.forms.get_or_create('user_info', FormStructures['user_info']);
			document.querySelector('section#user_info').append(form);
			dehy.ch.forms.init();
			dehy.ch.forms.reverse_form_labels(form);
			dehy.ch.forms.signin_button_handler();
		}
	},
	shipping: {
		billing_same_as_shipping_handler(checked=true, form=dehy.ch.forms.get()) {
			var elems = Array.from(form.querySelector('.form-container').querySelectorAll("input:not([type=hidden], [name='same_as_shipping']), label:not([for='id_same_as_shipping']), select"));
			var form_controls = [...new Set(elems.map(function(e) {return e.closest('.row')}))]
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

				var state_selector = form.querySelector("select[name='state']");
				if (state_selector) {
					dehy.ch.shipping.ADDRESS._address['state'] = state_selector.value;
				}
			}
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
		init() {
			console.log("dehy.ch.shipping.init()");
			dehy.ch.shipping.ADDRESS.set();

			var same_as_shipping_checkbox = document.querySelector("input[name=same_as_shipping]");

			if (same_as_shipping_checkbox) {
				same_as_shipping_checkbox.addEventListener('change', e=>{
					var billing_address_container = document.querySelector('form.billing-form .billing-address-container');

					billing_address_container.querySelectorAll('.form-group').forEach(function(elem) {
						elem.classList.toggle('hide', e.target.checked);
					});

					for (let [key, val] of Object.entries(dehy.ch.shiping.ADDRESS)) {
						if (val) {
							let elem = billing_address_container.querySelector(`input[name=${key}]`);
							if (elem) {
								if (e.target.checked) {
									elem.value = val;
								} else {
									elem.value = '';
								}
							}
						}
					};

					var country_selector = billing_address_container.querySelector("select[name='country']");
					if (country_selector) {
						console.log('found country_selector');
						if (e.target.checked) {
							country_selector.value = dehy.ch.shipping.ADDRESS._address.country;
						} else {
							country_selector.selectedIndex = 0;
						}
					}

					var state_selector = billing_address_container.querySelector("select[name='state']");
					console.log('found state_selector');
					if (state_selector) {
						if (e.target.checked) {
							state_selector.value = dehy.ch.shipping.ADDRESS._address.state;
						} else {
							state_selector.selectedIndex = 0;
						}
					}
				})
			}
		},
		get_shipping_methods(form_data) {
			var data = {};
			for (let[k, val] of form_data.entries()) {
				if (val) {
					data[k] = val;
				}
			};
			console.log('data: ', data);
			$.ajax({
				method: "POST",
				url: '/shipping/location/',
				data: data,
				// contentType: false,
				// processData: false,
				success: function(data) {
					console.log('data: ', data);
					dehy.ch.shipping.display_shipping_methods(data);
					dehy.basket.basket_updated_handlers.success(data);
				},
				error: dehy.ch.forms.errors.display,
			});
		},
		get_city_and_state(postcode) {
			var data = {'postcode': postcode};
			$.ajax({
				method: "GET",
				url: '/shipping/postcode/',
				data: data,
				// contentType: false,
				// processData: false,
				success: dehy.ch.shipping.set_city_and_state,
				error: dehy.ch.forms.errors.display
			});
		},
		update_shipping_method(elem) {
			var data = {[elem.name]: elem.value};

			$.ajax({
				method: "POST",
				url: '/shipping/set_method/',
				data: data,
				// contentType: false,
				// processData: false,
				success: dehy.basket.basket_updated_handlers.success,
				error: dehy.basket.basket_updated_handlers.error
			});
		},
		set_city_and_state(response) {
			var city_container = document.querySelector('#id_line4');
			if (city_container) {
				if (response.hasOwnProperty('city')) {
					city_container.value = response.city;
				}

			}
			var state_container = document.querySelector('#id_state');
			if (state_container) {
				if (response.hasOwnProperty('state')) {
					state_container.value = response.state;
				}
			}
		},
		// add the shipping methods to the existing form
		display_shipping_methods(data) {

			dehy.ch.shipping.set_city_and_state(data);
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
				let id = `id_${prefix}method_code_${ix}`,
					cost = parseFloat(method.cost).toFixed(2);

				var radio_elem = {
					'tag': 'input',
					'attrs': {
						'type':'radio', 'name':'method_code', 'id':id, 'value': method.code, 'data-cost':cost
					}
				}

				if (method.code==data.method_code) {
					radio_elem.attrs.checked = ""
				}

				var method_structure = [{
					'tag': 'div',
					'classes': 'row',
					'elems': [
						{
							'tag': 'div',
							'classes': 'input-group col',
							'elems': [
								radio_elem,
								{
									'tag': 'label',
									'text': `${method.name} — $${cost}`,
									'attrs': {
										'for': id,
									}
								}
							]
						}
				]
				}]

				let elem = dehy.utils.create_elements(method_structure, fieldset)
				// append it to the shipping_method_container

			})

			dehy.utils.cleanup_temp_containers();
			if (!data.method_code) {
				shipping_method_container.querySelector("input[type='radio']").checked = true;
			}
			form.insertBefore(shipping_method_container, document.querySelector('.error-container.button-container'))
			dehy.ch.forms.show_submit_button();

		},
		// check if shipping methods are on the page
		check_if_shipping_methods_displayed() {
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


dehy.ch.stripe = {
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
		var form = dehy.ch.forms.get('billing');
		var form_container = form.querySelector('.form-container');
		form.insertBefore(stripe_payment_container, form_container)
		paymentElement.mount(stripe_payment_container);

		form.removeEventListener('submit', dehy.ch.forms.submit_handler);
		form.addEventListener('submit', function(e) {
			e.preventDefault();
			// If the client secret was rendered server-side as a data-secret attribute
			// on the <form> element, you can retrieve it here by calling `form.dataset.secret`
			stripe.confirmCardPayment(clientSecret, {
				payment_method: {
					card: card,
				}
			}).then(function(result) {
				if (result.error) {
					// Show error to your customer (for example, insufficient funds)
					console.log(result.error.message);
				} else {
					// The payment has been processed!
					if (result.paymentIntent.status === 'succeeded') {
						// Show a success message to your customer
						// There's a risk of the customer closing the window before callback
						// execution. Set up a webhook or plugin to listen for the
						// payment_intent.succeeded event that handles any business critical
						// post-payment actions.
					}
				}
			});
		});
	},
	card_setup(style=null) {
		console.log('called card setup');
		// dehy.utils.remove_event_listeners(form);
		var cardClasses = {
			base: 'testicles',
			focus: 'focused',
			empty: 'empty',
			invalid: 'invalid',
		};
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
		var options = {style: style, classes: cardClasses, hidePostalCode:true};

		var form = dehy.ch.forms.get(),
			stripe = dehy.ch.stripe.get(),
			elements = dehy.ch.stripe.elements.get();

		var stripe_payment_container = document.getElementById("stripe_payment_container") || dehy.utils.create_element({tag:'div', classes: 'form-group row', attrs:{'id':'stripe_payment_container'}});
		var form_container = form.querySelector('.form-container');
		form.insertBefore(stripe_payment_container, form_container);

		var cardElement = (elements.getElement('card')) ? elements.getElement('card') : elements.create('card', options);
		cardElement.mount(stripe_payment_container)
		cardElement.on('change', function(event) {
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
		//
		form.addEventListener('submit', e=> {
			// We don't want to let default form submission happen here,
			// which would refresh the page.
			e.preventDefault();
			var form_data = new FormData(form);
			stripe.createPaymentMethod({
				type: 'card',
				card: cardElement,
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

			// save the billing info
			var billing_data = {
				'address': {},
				'card':{
					'last4':response.paymentMethod.card.last4,
					'brand':response.paymentMethod.card.brand,
					'country':response.paymentMethod.card.country,
					'exp': `${response.paymentMethod.card.exp_month}/${response.paymentMethod.card.exp_year}`,
				},
				'name': response.paymentMethod.billing_details.name,
				'phone': response.paymentMethod.billing_details.phone

			};

			billing_data.address = response.paymentMethod.billing_details.address;
			dehy.ch.forms.saved_info.billing = billing_data;

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
			});

			form_data.set('payment_intent_id', result.paymentIntent.id);
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
			var form = stripe_payment_container.closest('form');
			stripe_payment_container.classList.toggle('display-none', false);
			form.classList.toggle('display-none', false);
			// form.removeEventListener('submit', dehy.ch.forms.submit_handler);

		} else {// attempts to set the pkey and add the stripe elements to the page
			if (pkey) {
				dehy.ch.stripe.set_pkey(pkey)
			}
			if (dehy.ch.stripe.get_pkey()) {
				dehy.ch.stripe.set();
			}
			// will never be true
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
				dehy.ch.stripe.elements.set();
				dehy.ch.stripe.card_setup();
			}
		}
	},
};

dehy.ch.forms = {
	signin_button_handler() {
		//
	},
	get_form_data_as_object(form=dehy.ch.forms.get(), omit_empty_vals=false) { // accepts form_data object or creates one
		var data = {};
		var form_elements = form.querySelectorAll("input:not([type='hidden'], [type='password']), select");
		form_elements.forEach(function(elem) {
			if ((elem.type == 'checkbox' || elem.type == 'radio') && elem.checked == false) {
				return;
			}

			if (elem.type == 'select-one') {
				data[elem.name] = elem.selectedOptions[0].textContent
			} else {
				data[elem.name] = elem.value;
			}
		})

		return data;

	},
	save_info(form, section) {
		var data = dehy.ch.forms.get_form_data_as_object(form);
		if (data.hasOwnProperty('csrfmiddlewaretoken')) {
			delete data.csrfmiddlewaretoken;
		}
		dehy.ch.forms.saved_info[section] = data;
	},
	get_saved_info(section) {
		return (dehy.ch.forms.saved_info.hasOwnProperty(section)) ? dehy.ch.forms.saved_info[section] : null;
	},
	saved_info: {},
	has_changed(form=dehy.ch.forms.get(), section) {
		var changed = false;
		var current_saved_form_data = dehy.ch.forms.get_saved_info(section);
		// compare current form data with saved info
		if (current_saved_form_data) {
			var new_form_data = dehy.ch.forms.get_form_data_as_object(form);
			for (let [key, val] of Object.entries(new_form_data)) {
				if (current_saved_form_data.hasOwnProperty(key)) {
					if (current_saved_form_data[key] != val) {
						changed = true;
						return changed;
					}
				}
			}
		} else {
			changed = true;
		}
		// if its the same, skip the ajax call and move to the next section
		return changed

	},
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
		var form = e.target.closest('form');
		var section_name = form.closest('section').id
		// var form = e.target();
		e.preventDefault();
		if (!form.checkValidity()) {
			document.getElementById('error_container').classList.toggle('hidden', false);
			return false
		} else {
			document.getElementById('error_container').classList.toggle('hidden', true);
		}


		if (dehy.ch.forms.has_changed(form, section_name)) {
			dehy.ch.forms.submit_form_info(e.target);

		} else {
			dehy.ch.forms.success_handler({'section': section_name});
		}

		form.reportValidity();
	},
	get(name) {
		var form = document.querySelectorAll('#checkout_flow form:not(.display-none)')[0];
		if (name && dehy.ch.forms.saved.hasOwnProperty(name)) {
			form = dehy.ch.forms.saved[name];
		}
		return form
	},
	create(section, form_structure) {
		// create the form
		var form = dehy.utils.create_element({tag:'form', classes: 'card card-body checkout-form', attrs:{'method':"post", 'id':`${section}_form`, 'action': `/checkout/${section}/`}});
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
		});
	},
	submit_form_info(form) {
		var form_data = new FormData(form);
		form.querySelectorAll("input[type='checkbox']").forEach(function(checkbox) {
			form_data.set(checkbox.name, form_data.has(checkbox.name) ? 'on':'off');
		})

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
	success_handler(response, textStatus=null, xhr=null) {
		console.log('success response: ', response);

		var form = dehy.ch.forms.get();
		dehy.ch.forms.save_info(form, response.section);
		dehy.ch.forms.errors.hide();


		if (response.section=='billing') {
			var stripe_payment_container = document.getElementById('stripe_payment_container');
			stripe_payment_container.classList.toggle('display-none', true);
			stripe_payment_container.closest('form').classList.toggle('display-none', true);
		}
		dehy.ch.forms.save_and_remove(); //1
		var next_section = dehy.ch.utils.get_next_section(response.section);
		// var form = dehy.ch.forms.get_or_create(next_section.id, FormStructures[next_section.id]); //2
		var form = dehy.ch.forms.get_or_create(next_section.id, FormStructures[next_section.id]); //2

		next_section.append(form); //3
		dehy.ch.utils.deactivate_sections()
		next_section.classList.toggle('active', true);
		dehy.ch.forms.disable_edit_buttons(); //4
		let previous_section = dehy.ch.utils.get_previous_section(response.section);
		// if (response.preview_elems) {
		// 	dehy.ch.forms.create_preview(response.section, response.preview_elems); //5
		// }
		dehy.ch.forms.create_preview(response.section);
		dehy.ch.forms.enable_edit_buttons(next_section.id); //6
		dehy.ch.forms.init();
		dehy.ch.forms.reverse_form_labels(form);

		console.log('next_section.id', next_section.id)

		if (next_section.id=="billing") {
			form.classList.toggle('display-none', false);
			if (!form.querySelector('.form-container')) {
				var form_elem = next_section.querySelector('form'),
					error_button_container = next_section.querySelector('.error-container.button-container');

				var form_container = next_section.removeChild(next_section.querySelector('.form-container'));
				form_elem.insertBefore(form_container, error_button_container);
				form_elem.classList.toggle('display-none', false);
			}
			dehy.ch.shipping.billing_same_as_shipping_handler();
			if (response.stripe_pkey) {
				dehy.ch.stripe.init(response.stripe_pkey, response.client_secret);
			}
		}

		dehy.utils.unfreeze_forms();
	},
	// Attempts to get a previously saved form, or create one if it doesn't exist
	// If a form isnt saved under the section name, creates a new one from given form structure (required)
	// If no form structure given, falls back to the current form using the get() method
	get_or_create(section=null, form_structure=null) {
		var form;
		if (section && dehy.ch.forms.saved.hasOwnProperty(section)) {
			form = dehy.ch.forms.saved[section];
		} else {
			form = dehy.ch.forms.create(section, form_structure);
		}
		return form;
	},

	save(form, section) {
		dehy.ch.forms.saved[section] = form;
	},
	//removing the form ensures no left over event handlers are attached
	save_and_remove() {
		var all_checkout_sections = Array.from(document.querySelectorAll('#checkout_flow section'));
		all_checkout_sections.forEach(function(section) {
			if (section.querySelector('form')) {
				var form = section.querySelector('form');
				if (section.id=="billing") {
					// need to leave the stripe form on the page
					if (form.querySelector('.form-container')) {

						form_container = form.querySelector('.form-container');
						var form_copy = form_container.cloneNode(true);
						dehy.ch.forms.save(form_copy, section.id);
						form_container.remove();
						form.classList.toggle('display-none', true);
					}
				} else {
					var form_copy = form.cloneNode(true);
					dehy.ch.forms.save(form_copy, section.id);
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
						preview_container.remove();
					}

					dehy.ch.forms.save_and_remove(); //1
					var form = dehy.ch.forms.get_or_create(section.id, FormStructures[section.id]); //2

					if (section.id=='billing') {
						dehy.ch.stripe.init();
						var form_elem = section.querySelector('form'),
							error_button_container = section.querySelector('.error-container.button-container');

						form_elem.insertBefore(form, error_button_container);
						form.classList.toggle('display-none', false);

					} else {
						section.append(form); //3
					}

					var submit_btn = form.querySelector("button[type='submit']");

					if (submit_btn) {
						submit_btn.disabled = false;
					}

					dehy.ch.forms.disable_edit_buttons(); //4
					dehy.ch.forms.clear_previews(section.id) //5
					// let previous_section = dehy.ch.utils.get_previous_section(section.id);
					dehy.ch.forms.enable_edit_buttons(dehy.ch.utils.get_previous_section(section.id).id) //6

					if (section.id != 'billing') {
						dehy.ch.forms.init();
					}

					dehy.ch.forms.reverse_form_labels(form);
					dehy.utils.unfreeze_forms();
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
	create_preview(section, elems=null) {
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
		// get the object and compare it to
		var preview_elems = FormStructures.preview[section];
		var form_data_obj = dehy.ch.forms.get_saved_info(section);
		if (Array.prototype.isPrototypeOf(preview_elems)) {
			preview_elems.forEach(function(ele) {
				preview_container.append(dehy.utils.create_element({tag: 'div', classes: 'preview-item', text: form_data_obj[ele]}))
			});
		} else {
			for (let [key, val] of Object.entries(form_data_obj)) {
				let elem = dehy.utils.create_element({tag:'div', classes:key, text:val})
				preview_container.append(elem)
			}
		}

		// preview_container.append(get_preview_section(elems, section));
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
		display(error) {
			var error_message = error.statusText

			console.log('error: ', error);
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
		console.log('init forms');
		var form = dehy.ch.forms.get();

		if (form) {
			var country_selector = form.querySelector("select[name='country']");
			if (country_selector && dehy.ch.shipping.ADDRESS._address.country) {
				country_selector.value = dehy.ch.shipping.ADDRESS._address.country;
			}

			var state_selector = form.querySelector("select[name='state']");
			if (state_selector && dehy.ch.shipping.ADDRESS._address.state) {
				state_selector.value = dehy.ch.shipping.ADDRESS._address.state;
			}

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

			form.addEventListener('submit', dehy.ch.forms.submit_handler);
			form.addEventListener('change', e=> {
				console.log('form changed');
				// e.target.setCustomValidity('');

				if (form.closest('section').id == 'shipping' || form.closest('section').id == 'billing') {
					if (e.target.hasAttribute('name') && e.target.name=='method_code') {
						dehy.ch.shipping.update_shipping_method(e.target);
						return false
					}
					dehy.ch.shipping.ADDRESS.set();
					var postcode_input = e.target.closest('form').querySelector('#id_postcode');
					if (e.target.matches('#id_country')) {

						var country = document.querySelector('#id_country').value.toLowerCase();
						var validity_message = 'Please enter a proper 5 digit (XXXXX) or 9 digit ZIP code (XXXXX-XXXX).';
						var state_selector = document.querySelector('#id_state');

						if (country == 'ca') {
							validity_message= 'Please enter a proper Canadian postal code';
							state_selector.required = false;
							state_selector.disabled = true;
							state_selector.selectedIndex = 0;
						} else {
							state_selector.required = true;
							state_selector.disabled = false;
						}
						postcode_input.setCustomValidity(validity_message)
						postcode_input.pattern = dehy.ch.utils.re[country];
						return false
					}
					if (e.target.matches('#id_postcode, #id_state, #id_city')) {
						if (e.target.matches('#id_postcode')) {
							if (!e.target.checkValidity()) {
								e.target.reportValidity();
								return false;
							}
						}
						if (!postcode_input.checkValidity()) {
							postcode_input.classList.toggle('invalid', true);
							return false
						}

						// do input validation here

						// get/update the shipping methods

						// var data = {[`${e.target.id}`]: e.target.value, 'action': e.target.closest('form').action};
						if (form.closest('section').id == 'shipping') {
							var data = new FormData(e.target.closest('form'));
							dehy.ch.shipping.get_shipping_methods(data);
							console.log('getting shipping methods');
							dehy.ch.forms.show_submit_button();
							return false

						}

					}
				}
				if (e.target.matches("input#id_same_as_shipping")) {
					// set or reset the address elements
					dehy.ch.shipping.billing_same_as_shipping_handler(e.target.checked);
					return false
				}
			});

			// dehy.utils.unfreeze_forms();
		}
	},
};