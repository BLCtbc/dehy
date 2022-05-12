

window.addEventListener('load', function () {
	//
});

// DEHY.checkout namespace
dehy.ch = {
	utils: {
		loading_messages: {
			'user_info':'Loading shipping addresses...',
			'shipping':'Updating shipping info...',
			'additional_info':'Loading billing addresses...',
			'billing':'updating billing info...',
			'place_order':'Placing Order...',
		},
		re: {
			us: '(^[0-9]{5}$)|(^[0-9]{5}-[0-9]{4}$)',
			ca: /^[abceghjklmnprstvxy][0-9][abceghjklmnprstvwxyz]\s?[0-9][abceghjklmnprstvwxyz][0-9]$/i,
			mx: this.us

		},
		// given a list of corrections, attempts to make address corrections in an open form
		make_address_corrections(corrections) {
			console.log('corrections: ', corrections);
			var form = dehy.ch.forms.get();

			for (let [name, val] of Object.entries(corrections)) {
				var elem = form.querySelector(`[name=${name}]`);
				if (elem) {
					console.log('correcting ', elem);
					if (elem.type == 'select-one') {
						elem.selectedIndex = dehy.ch.utils.get_selector_option(elem, val);
					} else {
						elem.value = val;
					}
				}
			}
		},
		get_selector_option(selector, text=null, return_index=true) {
			var text = (text) ? text : selector.value;
			text = text.toUpperCase();
			var options = Array.from(selector.options);
			var selected_index = (text.length==2) ? options.findIndex(option=>option.value==text) : options.findIndex(option=>option.textContent==text);
            console.log('selected option: ', selected_index)
			return (return_index) ? selected_index : options[selected_index].value;
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
		},
		objects_are_same(obj1=null, obj2=null) {
			var is_same = true;
			if (!obj1 || !obj2) {
				is_same = false
			} else {
				for (let [key, val] of Object.entries(obj1)) {
					if (obj2.hasOwnProperty(key) && obj2[key] != val) {
						console.log(`${obj2[key]} != ${val}`);
						is_same = false;
						return is_same;
					}
				}
			}
			return is_same;
		},

	},
	_stripe: null,
	gateway: {
		init: function() {
			var form = dehy.ch.forms.get_or_create('user_info', FormStructures['user_info']);
			document.querySelector('section#user_info').append(form);
			dehy.ch.forms.init();
			// dehy.ch.forms.reverse_form_labels(form);
		}
	},
	shipping: {
		billing_same_as_shipping_handler(checked=true, form=dehy.ch.forms.get()) {
			if (checked) {
				dehy.ch.forms.saved_form_data.billing = dehy.ch.forms.saved_form_data.shipping;
				var saved_address_dropdown = document.getElementById('saved_address_dropdown');
				if (saved_address_dropdown) {
					saved_address_dropdown.selectedIndex = saved_address_dropdown.options.length-1
				}
			}
			var same_as_shipping_elem = document.getElementById('id_same_as_shipping');
			same_as_shipping_elem.checked = checked;

			var selector_string = "input:not([type=hidden], [name='same_as_shipping']), label:not([for='id_same_as_shipping'], [for='saved_address_dropdown']), select:not([id='saved_address_dropdown'])";
			var elems = Array.from(form.querySelector('.form-container').querySelectorAll(selector_string));
			var form_controls = [...new Set(elems.map(function(e) {return e.closest('.row')}))]
			var address = dehy.ch.forms.saved_form_data.billing
			form_controls.forEach(function(row) {
				row.classList.toggle('display-none', checked);
				var inputs_and_labels = row.querySelectorAll(selector_string)
				inputs_and_labels.forEach(function(elem) {
					if (elem.name && address && address.hasOwnProperty(elem.name)) {
						if (elem.type=='select-one') {
							var options = Array.from(elem.options);
							var selected_index = options.findIndex(ele=>ele.textContent==address[elem.name]);
							// elem.selectedIndex = (checked) ? selected_index : 0;
							elem.selectedIndex = selected_index;
						} else {
							// elem.value = (checked) ? address[elem.name] : '';
							elem.value = address[elem.name];

						}
					}
				});
			});
		},
		get_shipping_methods(form_data) {
			var data = {};
			for (let[k, val] of form_data.entries()) {
				if (val) {
					data[k] = val;
				}
			};
			dehy.loading_message = 'Updating shipping methods...';
			$.ajax({
				method: "POST",
				url: '/shipping/location/',
				data: data,
				success: function(data) {
					dehy.ch.forms.errors.hide();
					if (data.order_client_secret) {
						dehy.ch.stripe.order_client_secret = data.order_client_secret;
					}
					dehy.ch.shipping.update_shipping_methods(data);
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
		update_shipping_methods(data) {
			if (data.corrections) {
				dehy.ch.utils.make_address_corrections(data.corrections);
			}

			dehy.ch.shipping.set_city_and_state(data);
			var form = dehy.ch.forms.get('shipping'),
				fieldset = dehy.utils.create_element({tag:'fieldset'});

			var shipping_method_container = form.querySelector('.shipping-method-container');

			if (shipping_method_container) {
				dehy.utils.remove_children(shipping_method_container);
			} else {
				shipping_method_container = dehy.utils.create_element({tag:'div', classes:'shipping-method-container'})
			}

			shipping_method_container.append(fieldset);
			fieldset.append(dehy.utils.create_element({tag:'legend', classes: "required", text:'Shipping Methods'}));
			var prefix = (data.prefix) ? `${data.prefix}-`:'';
			data.shipping_methods.forEach((method, ix) => {
				// create form group
				let id = `id_${prefix}method_code_${ix}`,
					cost = parseFloat(method.cost).toFixed(2);

				var radio_elem = {
					'tag': 'input',
					'classes': 'shipping-method-option',
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

				let elem = dehy.utils.create_elements(method_structure, fieldset);

			})

			dehy.utils.cleanup_temp_containers();
			if (dehy.ch.forms.saved_form_data.shipping && dehy.ch.forms.saved_form_data.shipping.hasOwnProperty('method_code') && shipping_method_container.querySelector(`input[type='radio'][value='${dehy.ch.forms.saved_form_data.shipping.method_code}']`)){
				shipping_method_container.querySelector(`input[type='radio'][value='${dehy.ch.forms.saved_form_data.shipping.method_code}']`).checked = true;

			} else {
				// gets the first option and selects it
				shipping_method_container.querySelector("input[type='radio']").checked = true;
			}

			// if section is active, add form to the page
			if (document.contains(form)) {
				form.insertBefore(shipping_method_container, document.querySelector('.error-container.button-container'))
				dehy.ch.forms.show_submit_button();
			}
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
	payment_confirmed(response, textStatus=null, xhr=null) {
		//
		var elements = dehy.ch.stripe.elements.get();
	},
	order_placed_success(response, textStatus=null, xhr=null) {
		window.location.href = response.redirect;
	},
	payment_intent_client_secret: null,
	order_client_secret: null,
	pkey: null,
	elements: null,
	submit_billing_info(form_data) {


		return new Promise((resolve, reject) => {

			if (dehy.ch.forms.has_changed('billing')) {

				$.ajax({
					method: "POST",
					url: "/checkout/billing/",
					contentType: false,
					processData: false,
					data: form_data,
					success: function(data) {
						resolve(data)
					},
					error: function(error) {
						reject(error)
					},
				});
			} else {
				resolve(form_data)
			}
		});
	},
	payment_element_setup(client_secret, data){

		const old_appearance = {
			theme: 'night',
			labels: 'floating'
		};
		var gold_color = '#bca263',
			dark_hg = '#1c3627';

		const appearance = {
			variables: {
				colorPrimaryText: gold_color,
			    colorPrimary: '#bca263',
			    colorBackground: '#e7f0fe',
			    colorText: '#495057',
			    colorDanger: '#df1b41',
			    fontFamily: 'Ideal Sans, system-ui, sans-serif',
			    spacingUnit: '2px',
			    borderRadius: '5px',
				colorTextPlaceholder: '#495057bf',
				spacingGridColumn: '1rem'
			    // See all possible variables below
			},
			rules: {
				'.Input': {
        			border: `1px solid ${dark_hg}`,
					outline: `2px solid ${gold_color}`,
					outlineOffset: '1px',
					lineHeight: '1.5rem',
					padding: '0.375rem 0.75rem',
					marginBottom: '0.25rem',

      			},
				'.Input:focus': {
					outline: `2px solid ${gold_color}`,
					boxShadow: 'none'
				},
				'.Label': {
					color: gold_color,
					lineHeight: 1.5
				}
			}
		};

		var options = {
			clientSecret: client_secret,
			// Fully customizable with appearance API.
			appearance: appearance,
		};


		const regex = /\_([a-zA-Z0-9]+)\_/g;
		var matched = client_secret.match(regex);
		if (matched) {
			// Could be used as a reference to an order within query parameter in return URL.
			// This could be useful for returning a page to an existing state, with certain information
			// filled in, in case stripe has to return
			dehy.ch.stripe.order_id = matched.toString().replaceAll("_", "");
		}

		var stripe = dehy.ch.stripe.get(),
			form = dehy.ch.forms.get('billing');

		var elements = stripe.elements(options);
		dehy.ch.stripe.elements = elements;
		var stripe_payment_container = document.getElementById("stripe_payment_container") || dehy.utils.create_element({tag:'div', classes: 'form-group row', attrs:{'id':'stripe_payment_container'}});
		var form_container = form.querySelector('.form-container');
		// form.insertBefore(stripe_payment_container, form_container);

		var payment_element = elements.create('payment', {
			fields: {
				billingDetails: {
			  		name: 'never',
			  		email: 'never',
					phone: 'never',
					address: 'never'
				}
			}
		});
		payment_element.mount(stripe_payment_container);

		form.removeEventListener('submit', dehy.ch.forms.submit_handler);

		// New
		form.addEventListener('submit', async (e) => {
			e.preventDefault();

			var form_data = new FormData(form);

			if (!dehy.ch.forms.form_data_matches_saved_address(form)) {
				// check if billing info matches one of the saved_addresses
				form_data.delete("address_id")
			}

			var address = {
				line1: form_data.get('line1'),
				line2: form_data.get('line2'),
				city: form_data.get('line4'),
				state: form_data.get('state'),
				country: form_data.get('country'),
				postal_code: form_data.get('postcode'),
			};
			var billing_details = {
				name: `${form_data.get('first_name')} ${form_data.get('last_name')}`,
				email: dehy.ch.forms.saved_form_data.user_info.username,
				phone: form_data.get('phone_number'),
				address: address
			};

			dehy.ch.stripe.submit_billing_info(form_data)
			.then((data) =>{
				dehy.ch.forms.success_handler({'section': 'billing'});

				var place_order_form = document.querySelector('#place_order_form') || dehy.ch.forms.get();
				place_order_form.removeEventListener('submit', dehy.ch.forms.submit_handler);
				place_order_form.addEventListener('submit', async (e) => {
					dehy.utils.freeze_forms();
					e.preventDefault();
					stripe.processOrder({
						elements,
						confirmParams: {
						// Return URL where the customer should be redirected after the Order's payment is confirmed.
							return_url: new URL('checkout/thank_you/', window.location.origin).toString(),
							payment_method_data: {
								billing_details: billing_details,
							},
						},
					})
					.then(function(result) {
						console.log('stripe.processOrder result: ', result);
						if (result.error) {
						// Inform the customer that there was an error.
						dehy.ch.forms.errors.display(result.error);
						} else {
							// success, do stuff
						}
					})
					.catch(()=>{
						dehy.ch.forms.errors.display(data);
					})
					.finally(()=> {
						dehy.utils.unfreeze_forms();
					})
				})

			}, dehy.ch.forms.errors.display)
		});


		// stripe.retrievePaymentIntent('{PAYMENT_INTENT_CLIENT_SECRET}').then(function(result) {
		//
		// 	// Handle result.error or result.paymentIntent
		// })
		payment_element.on('ready', e=>{
			console.log('ready, e:', e);

			setTimeout(function() {
				payment_element.focus();
			}, 500);
		});

		payment_element.on('change', e=>{
			if (e.error) {
				dehy.ch.forms.errors.display(e.error);
			} else {
				var submit_button = form.querySelector("button[type='submit']");
				dehy.ch.forms.errors.hide(form);
				if (e.complete) {
					// enable the submit button
					submit_button.disabled = false;
				} else {
					// disable the submit button
					submit_button.disabled = true;
				}
			}
		});

		payment_element.on('blur', e=>{
			console.log('blur, e:', e);
		});
		payment_element.on('focus', e=>{
			console.log('focus, e:', e);
		});

		form.prepend(stripe_payment_container)
		dehy.utils.unfreeze_forms();
	},
	set(pkey=null) {
		if (pkey) {
			dehy.ch.stripe.set_pkey(pkey);
		}
		dehy.ch._stripe = Stripe(dehy.ch.stripe.get_pkey(), {betas: ['process_order_beta_1'], apiVersion: '2020-08-27; orders_beta=v2'});
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
	init(pkey=dehy.ch.stripe.pkey, client_secret=dehy.ch.stripe.client_secret, data={}) {

		if (dehy.ch.stripe.get() && document.querySelector("#stripe_payment_container")) {
			// already created, just need to unhide it
			console.log('stripe already created, unhide it');
			var stripe_payment_container = document.getElementById('stripe_payment_container');
			var form = stripe_payment_container.closest('form');
			stripe_payment_container.classList.toggle('display-none', false);
			form.classList.toggle('display-none', false);
			var payment_element = dehy.ch.stripe.elements.getElement('payment');
			payment_element.focus();
		} else {// attempts to set the pkey and add the stripe elements to the page
			dehy.utils.freeze_forms();

			if (pkey) {
				dehy.ch.stripe.set_pkey(pkey)
			}
			if (dehy.ch.stripe.get_pkey()) {
				dehy.ch.stripe.set();
			}

			if (!dehy.ch.stripe.order_client_secret) {
				// if for some reason we dont have the order_client_secret by now, get it
				// make ajax call to server to retrieve order's client_secret
			}

			dehy.ch.stripe.payment_element_setup(dehy.ch.stripe.order_client_secret, data);

			// dehy.ch.stripe.card_setup();
		}
	},
};

dehy.ch.forms = {
	saved_addresses:[],
	form_data_matches_saved_address(form=dehy.ch.forms.get()) {
		if (dehy.ch.forms.saved_addresses.length < 1) {
			return false
		}

		var matches = false,
			saved_address_obj;

		var form_data_obj = dehy.ch.forms.get_form_data_as_object(form, false, false),
			address_id_elem = document.getElementById('id_address_id');

		if (address_id_elem) {
			var saved_address = dehy.ch.forms.saved_addresses.find(elem=>elem.id==address_id_elem.value);

			if (saved_address) {
				saved_address_object = Object.assign({}, saved_address);
			} else {
				return false
			}
			// saved address needs to be copied, then remove the ID
		}

		matches = dehy.ch.utils.objects_are_same(form_data_obj, saved_address_object);
		return matches
		// get the address id from the form
		// then get the saved address using said id
		// remove extra properties from both objects

	},
	// accepts form_data object or creates one, returns an object in standard notation
	get_form_data_as_object(form=dehy.ch.forms.get(), omit_empty_vals=false, expand_select_elems=true) {
		var data = {};
		var form_elements = document.evaluate(".//input[not(@type='hidden' and @name='csrfmiddlewaretoken')] | .//select[not(@id='saved_address_dropdown')]", form, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
		for (var i=0; i<form_elements.snapshotLength;i++) {
			var elem = form_elements.snapshotItem(i);
			if ((elem.type == 'checkbox' || elem.type == 'radio') && elem.checked == false) {
				continue
			}

			if (elem.type == 'select-one') {
				if (expand_select_elems) {
					data[elem.name] = elem.selectedOptions[0].textContent;
				} else {
					data[elem.name] = elem.selectedOptions[0].value;
				}

			} else {
				data[elem.name] = elem.value;
			}

		}

		return data;

	},
	save_form_data(form, section) {
		var data = dehy.ch.forms.get_form_data_as_object(form);
		if (data.hasOwnProperty('csrfmiddlewaretoken')) {
			delete data.csrfmiddlewaretoken;
		}
		dehy.ch.forms.saved_form_data[section] = data;
	},
	save_submitted_form_data(form, section) {
		var data = dehy.ch.forms.get_form_data_as_object(form);
		if (data.hasOwnProperty('csrfmiddlewaretoken')) {
			delete data.csrfmiddlewaretoken;
		}
		dehy.ch.forms.submitted_form_data[section] = data;
	},
	get_saved_form_data(section) {
		return (dehy.ch.forms.saved_form_data.hasOwnProperty(section)) ? dehy.ch.forms.saved_form_data[section] : null;
	},
	get_submitted_form_data(section) {
		return (dehy.ch.forms.submitted_form_data.hasOwnProperty(section)) ? dehy.ch.forms.submitted_form_data[section] : null;
	},
	saved_form_data: {},
	submitted_form_data: {},

	has_changed(section=null, form=dehy.ch.forms.get()) {
		var changed = false;
		var submitted_form_data = dehy.ch.forms.get_submitted_form_data(section);
		// compare current form data with saved info

		if (submitted_form_data) {
			var new_form_data = dehy.ch.forms.get_form_data_as_object(form);
			if (!dehy.ch.utils.objects_are_same(submitted_form_data, new_form_data)) {
				changed = true;
			}
		} else {
			changed = true;
		}
		// if its the same, skip the ajax call and move to the next section

		return changed

	},
	saved: {},
	show_submit_button(form=null) {
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
	submit_handler(e) {
		dehy.ch.forms.save_all();
		var form = e.target.closest('form');
		var section_name = form.closest('section').id
		// var form = e.target();
		e.preventDefault();
		if (!form.checkValidity()) {
			dehy.ch.forms.errors.display({error: {message: 'Enter the required information.'}});
			return false
		} else {
			dehy.ch.forms.errors.hide();
		}

		if (dehy.ch.forms.has_changed(section_name, form)) {
			dehy.ch.forms.submit_form_info(e.target);

		} else {
			dehy.ch.forms.success_handler({'section': section_name});
		}

		// form.reportValidity();
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
		var form = dehy.utils.create_element({tag:'form', classes: 'checkout-form', attrs:{'method':"post", 'id':`${section}_form`, 'action': `/checkout/${section}/`}});
		let csrftoken_elem = dehy.utils.create_element({tag:'input', attrs:{'name':'csrfmiddlewaretoken', 'type': 'hidden', 'value':dehy.utils.getCookie('csrftoken')}})

		form.append(csrftoken_elem)


		form.append(dehy.utils.create_elements(form_structure));

		if (dehy.ch.forms.saved_addresses.length > 0 && (section=='shipping' ||  section=='billing')) {
			// create the dropdown containing the saved_addresses

			var dropdown = dehy.utils.create_element({tag:'select', style:"padding-right:35px" ,classes: 'form-control mb-2', attrs:{'name':'saved_addresses', 'id':'saved_address_dropdown', 'data-required':false}}),
				dropdown_container = dehy.utils.create_element({tag:'div',style:"position:relative;", classes:"mb-2 px-0 dropdown-container"});

			// dropdown_container.append(dehy.utils.create_element({tag:'span', text:"|", classes:"dropdown-spacer"}));
			// dropdown_container.append(dehy.utils.create_element({tag:'i',classes:"fas fa-grip-lines-vertical dropdown-spacer"}));

			dropdown_container.append(dehy.utils.create_element({tag:'i',classes:"fas fa-chevron-down dropdown-arrow"}));

			var dropdown_label = dehy.utils.create_element({tag:'label', classes:"col-form-label", text:'Saved Addresses', attrs:{'for':"saved_address_dropdown"}});
			// var default_option = dehy.utils.create_element({tag:'option', text: '----', attrs:{'value':""}});
			// dropdown.append(default_option);
			dehy.ch.forms.saved_addresses.forEach((address,i) => {
				var address_lines = address.line1;
				if (address.line2) {
					address_lines = address_lines + `, ${address.line2}`
				}
				address_lines = address_lines + `, ${address.line4}`
				if (address.state) {
					address_lines = address_lines + `, ${address.state}`
				}
				address_lines = address_lines + `, ${address.postcode}`

				var address_summary = `${address.first_name} ${address.last_name} (${address_lines}, ${address.country})`
				var attrs = {'value':address_summary};

				var address_option = dehy.utils.create_element({tag:'option', text: address_summary, attrs:attrs});

				dropdown.append(address_option);
			});

			// dropdown.selectedIndex = 0;
			var default_option = dehy.utils.create_element({tag:'option', text: '----', attrs:{'value':""}});
			dropdown.append(default_option);

			dropdown.options[0].selected = true;
			dropdown_container.append(dropdown);

			if (section=='billing') {
				var form_container = form.querySelector(".form-container");
				dropdown_label.classList += " mt-3"
				form_container.insertBefore(dropdown_container, form_container.firstChild);
				form_container.insertBefore(dropdown_label, form_container.firstChild);
			} else {
				form.insertBefore(dropdown_container, form.firstChild);
				form.insertBefore(dropdown_label, form.firstChild);
			}

			// set the value of the form to the first saved address
			dehy.ch.forms.set_form_to_saved_address(null, form, section);
			dehy.ch.forms.saved_address_handler(dropdown);
		}
		dehy.ch.forms.init();
		return form
	},
	saved_address_handler(elem) {
		var saved_address_dropdown = (elem) ? elem : document.getElementById('saved_address_dropdown');
		if (saved_address_dropdown) {
			saved_address_dropdown.addEventListener('change', dehy.ch.forms.set_form_to_saved_address);
		}
	},
	set_form_to_saved_address(e=null, form=dehy.ch.forms.get(), section=null) {
		// if (e) {
		// 	e.stopImmediatePropogation();
		// }
		var section = (section) ? section : form.closest('section').id;
		var saved_address_dropdown = form.querySelector('#saved_address_dropdown');
		var selected_index = (saved_address_dropdown.selectedIndex) ? saved_address_dropdown.selectedIndex: 0;

		if (selected_index != -1) {
			if (selected_index == saved_address_dropdown.options.length-1) {
				// clear the form
				form.reset();
				saved_address_dropdown.selectedIndex = saved_address_dropdown.options.length-1;
			} else {
				var billing_same_as_shipping_input = document.getElementById('id_same_as_shipping');
				if (billing_same_as_shipping_input) {
					if (billing_same_as_shipping_input.checked) {
						billing_same_as_shipping_input.click();
					}
				}
				var address = dehy.ch.forms.saved_addresses[selected_index];
				var selectors = ['state', 'country']
				selectors.forEach(selector_name=>{
					var selector = form.querySelector(`select[name='${selector_name}']`);
					if (selector && address.hasOwnProperty(selector_name)) {
						var options = Array.from(selector.options);
						var selector_index = options.findIndex(ele=>ele.textContent==address[selector_name]);
						if (selector_index == -1) {
							selector_index = options.findIndex(ele=>ele.value==address[selector_name]);
						}
						selector.selectedIndex = selector_index;
					}
				});
				for (let [key, val] of Object.entries(address)) {
					let field = form.querySelector(`[name="${key}"]`);

					if (field && field.type != 'select-one') {
						field.value = val;
					}
				}
				var address_id_elem = form.querySelector("input#id_address_id");
				if (address_id_elem) {
					address_id_elem.value = address.id
				}

				if (e) {
					const change = new Event('change');
					var postcode = document.getElementById('id_postcode');

					postcode.dispatchEvent(change);
					form.dispatchEvent(change);
				}
			}

		}

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
		var section = form.closest('section');
		if (section) {
			dehy.loading_message = dehy.ch.utils.loading_messages[section.id]
		}
		var form_data = new FormData(form);
		form.querySelectorAll("input[type='checkbox']").forEach(function(checkbox) {
			form_data.set(checkbox.name, form_data.has(checkbox.name) ? 'on':'off');
		})

		if (form_data.has('saved_addresses')) {
			form_data.delete('saved_addresses');
		}

		if (form_data.has('address_id')) {
			if (!dehy.ch.forms.form_data_matches_saved_address(form)) {
				// check if billing info matches one of the saved_addresses
				form_data.delete("address_id")
			}
		}

		$.ajax({
			method: "POST",
			url: form.action,
			contentType: false,
			processData: false,
			data: form_data,
			success: dehy.ch.forms.success_handler,
			error: dehy.ch.forms.errors.display,
		});
	},
	success_handler(response, textStatus=null, xhr=null) {

		if (response.corrections) {
			dehy.ch.utils.make_address_corrections(response.corrections);
		}

		if (response.order_client_secret) {
			dehy.ch.stripe.order_client_secret = response.order_client_secret;
		}

		var form = dehy.ch.forms.get();
		dehy.ch.forms.save_submitted_form_data(form, response.section);
		dehy.ch.forms.save_form_data(form, response.section);
		dehy.ch.forms.errors.hide(form);

		if (response.section=='billing') {
			var stripe_payment_container = document.getElementById('stripe_payment_container');
			stripe_payment_container.classList.toggle('display-none', true);
			stripe_payment_container.closest('form').classList.toggle('display-none', true);
		}
		dehy.ch.forms.remove_all(); //1
		var next_section = dehy.ch.utils.get_next_section(response.section);
		// var form = dehy.ch.forms.get_or_create(next_section.id, FormStructures[next_section.id]); //2
		if (response.saved_addresses) {
			dehy.ch.forms.saved_addresses = response.saved_addresses;
		}
		var form = dehy.ch.forms.get_or_create(next_section.id, FormStructures[next_section.id]); //2

		next_section.append(form); //3
		dehy.ch.utils.deactivate_sections();
		next_section.classList.toggle('active', true);
		dehy.ch.forms.disable_edit_buttons(); //4
		dehy.ch.forms.create_preview(response.section);
		dehy.ch.forms.enable_edit_buttons(next_section.id); //6
		dehy.ch.forms.init();
		// dehy.ch.forms.reverse_form_labels(form);

		if (next_section.id=="billing") {
			var checked = true;
			form.classList.toggle('display-none', false);
			// indicates form previously on page
			if (!form.querySelector('.form-container')) {

				var form_elem = next_section.querySelector('form'),
					error_button_container = next_section.querySelector('.error-container.button-container');

				var form_container = next_section.removeChild(next_section.querySelector('.form-container'));
				form_elem.insertBefore(form_container, error_button_container);
				form_elem.classList.toggle('display-none', false);
				checked = form_elem.querySelector('#id_same_as_shipping').checked
			}

			if (response.hasOwnProperty('same_as_shipping')) {
				checked = response.same_as_shipping
			}

			dehy.ch.shipping.billing_same_as_shipping_handler(checked);
			dehy.ch.stripe.init(response.stripe_pkey, response.client_secret, response);
		}

		if (response.hasOwnProperty('shipping_methods')) {
			dehy.ch.shipping.update_shipping_methods(response);
			// response.shipping_charge = response.shipping_methods[0].cost

			dehy.basket.basket_updated_handlers.success(response);
		}

		//dehy.utils.unfreeze_forms();
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
	save_all() {
		var all_checkout_sections = Array.from(document.querySelectorAll('#checkout_flow section'));
		all_checkout_sections.forEach(function(section) {
			if (section.querySelector('form')) {
				var form = section.querySelector('form');
				if (section.id=="billing") {
					// need to leave the stripe form on the page
					if (form.querySelector('.form-container')) {
						form_container = form.querySelector('.form-container');
						var form_copy = form_container.cloneNode(true);
						dehy.ch.forms.saved[section.id] = form_copy;
					}
				} else {
					var form_copy = form.cloneNode(true);
					dehy.ch.forms.saved[section.id] = form_copy;
				}

			}
		});
	},
	save(form, section) {
		dehy.ch.forms.saved[section] = form;
	},
	//removing the form ensures no left over event handlers are attached
	remove_all() {
		var all_checkout_sections = Array.from(document.querySelectorAll('#checkout_flow section'));
		all_checkout_sections.forEach(function(section) {
			if (section.querySelector('form')) {
				var form = section.querySelector('form');
				if (section.id=="billing") {
					// need to leave the stripe form on the page
					if (form.querySelector('.form-container')) {
						form_container = form.querySelector('.form-container');
						var form_copy = form_container.cloneNode(true);
						form_container.remove();
						form.classList.toggle('display-none', true);
					}
				} else {
					var form_copy = form.cloneNode(true);
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

					dehy.ch.forms.save_all(); //1
					dehy.ch.forms.remove_all(); //1
					var form = dehy.ch.forms.get_or_create(section.id, FormStructures[section.id]); //2

					if (section.id=='billing') {
						dehy.ch.stripe.init();
						var form_elem = section.querySelector('form'),
							error_button_container = section.querySelector('.error-container.button-container');

							if (dehy.ch.forms.saved_form_data.hasOwnProperty(section.id)){

								var address = dehy.ch.forms.saved_form_data[section.id][selected_index];
								var selectors = ['state', 'country']
								selectors.forEach(selector_name=>{
									var selector = form.querySelector(`select[name='${selector_name}']`);
									if (selector && address.hasOwnProperty(selector_name)) {
										var options = Array.from(selector.options);
										var selector_index = options.findIndex(ele=>ele.textContent==address[selector_name]);
										if (selector_index == -1) {
											selector_index = options.findIndex(ele=>ele.value==address[selector_name]);
										}
										selector.selectedIndex = selector_index;
									}
								});

								// var country_selector = form.querySelector("select[name='country']");
								// if (country_selector && dehy.ch.forms.saved_form_data[section.id].hasOwnProperty('country')) {
								// 	let options = Array.from(country_selector.options);
								// 	let selected_index = options.findIndex(ele=>ele.textContent==dehy.ch.forms.saved_form_data[section.id].country);
								// 	country_selector.selectedIndex = selected_index;
								// }
								// var state_selector = form.querySelector("select[name='state']");
								//
								// if (state_selector && dehy.ch.forms.saved_form_data[section.id].hasOwnProperty('state')) {
								// 	let options = Array.from(state_selector.options);
								// 	let selected_index = options.findIndex(ele=>ele.textContent==dehy.ch.forms.saved_form_data[section.id].state);
								// 	state_selector.selectedIndex = selected_index;
								// }
							}

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
					// dehy.ch.forms.reverse_form_labels(form);
					// dehy.utils.unfreeze_forms();
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

		var preview_container = dehy.utils.create_element({tag:'div', classes:'preview_container'});
		var preview_elems = FormStructures.previews[section];
		var elem = dehy.utils.create_elements(preview_elems, preview_container);


		var form_data_obj = dehy.ch.forms.get_saved_form_data(section);

		if (section == 'user_info') {
			console.log('user_info section')
			console.log('form_data_obj: ', form_data_obj);
			var username_text = form_data_obj.username;
			if (form_data_obj.hasOwnProperty('name') && form_data_obj.name.length > 1) {
				username_text = `(${username_text})`;
				var name_elem = preview_container.querySelector("*[data-preview='name']");
				if (name_elem) {
					name_elem.textContent = form_data_obj.name;
				}
			}
			var username_elem = preview_container.querySelector("*[data-preview='username']");
			if (username_elem) {
				username_elem.textContent = username_text;
			}
			if (form_data_obj.hasOwnProperty('user_avatar') && form_data_obj.user_avatar.length > 1) {
				var user_avatar_elem = preview_container.querySelector("*[data-preview='user_avatar']");
				if (user_avatar_elem) {
					user_avatar_elem.src = form_data_obj.user_avatar;
					user_avatar_elem.parentElement.classList.remove("d-none");
				}
			}
		} else {
			for (let [key, val] of Object.entries(form_data_obj)) {
				var elem = preview_container.querySelector(`*[data-preview=${key}]`);

				if (elem) {
					var text_content = val;
					if (val && (elem.dataset.preview=='line4' || elem.dataset.preview=='state')) {
						if (elem.dataset.preview=='state') {
							var state = US_States.find(st=>st.text==val);
							if (state) {
								text_content = state.attrs.value
							}
						}
						text_content += ", "
					}
					elem.textContent = text_content;

				}
			}
		}

		if (section=='shipping') {
			var shipping_form = dehy.ch.forms.saved.shipping;
			// shipping_form.querySelector(`.shipping-method-container input[value='${form_data_obj.method_code}']`)
			var label_text = shipping_form.querySelector(`.shipping-method-container input[value='${form_data_obj.method_code}']`).parentNode.querySelector('label').textContent

			var method_name = `${label_text.split('®')[0]}®`,
				method_cost = `$${label_text.split('®')[1].split("$")[1]}`;

			preview_container.querySelector(`span[data-preview='shipping_method']`).textContent = method_name;
			preview_container.querySelector(`span[data-preview='shipping_cost']`).textContent = method_cost;
		}


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
		display(response) {
			var error_text = (response.responseJSON) ? response.responseJSON.errors : response.text || response.message;
			if (response.responseJSON && response.responseJSON.errors) {
				error_text = "";
				if (typeof(response.responseJSON.errors)!='object') {
					response.responseJSON.errors = JSON.parse(response.responseJSON.errors);
				}
				for (let[k, val] of Object.entries(response.responseJSON.errors)) {

					if (val) {
						if (Array.isArray(val)) {
							if (typeof(val[0])=='object') {
								error_text += val[0].message
							} else {
								error_text += val.join(" ")
							}

						}
					}
				};
			}

			console.log('response: ', response);
			console.log('error_text: ', error_text)
			var error_message = `${response.statusText} (${response.status}): ${error_text}`

			console.log('error_message: ', error_message);
			var form = dehy.ch.forms.get();
			var error_container = form.querySelector('#error_container');
			if (error_container) {
				error_container.classList.toggle('hidden', false);
				error_container.querySelector('span').textContent = error_message
			}

			// error_container.append(dehy.utils.create_element({tag:'div', classes:'error', text: error_message, attrs:{'id':'errors'}}));
		},
		hide(form=dehy.ch.forms.get()) {
			var error_container = form.querySelector('#error_container');
			error_container.classList.toggle('hidden', true);
			error_container.querySelector('span').textContent = ''
		},
	},
	// dehy.ch.forms.init()
	init() {
		var form = dehy.ch.forms.get();

		if (form) {
			var section = form.closest('section');
			if (dehy.ch.forms.saved_form_data.hasOwnProperty(section.id)){
				var country_selector = form.querySelector("select[name='country']");
				if (country_selector && dehy.ch.forms.saved_form_data[section.id].hasOwnProperty('country')) {
					let options = Array.from(country_selector.options);
					let selected_index = options.findIndex(ele=>ele.textContent==dehy.ch.forms.saved_form_data[section.id].country);
					country_selector.selectedIndex = selected_index;
				}
				var state_selector = form.querySelector("select[name='state']");
				if (state_selector && dehy.ch.forms.saved_form_data[section.id].hasOwnProperty('state')) {
					let options = Array.from(state_selector.options);
					let selected_index = options.findIndex(ele=>ele.textContent==dehy.ch.forms.saved_form_data[section.id].state);
					state_selector.selectedIndex = selected_index;
				}
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

				var section_name = form.closest('section').id;
				dehy.ch.forms.save_form_data(form, section_name);

				// should prevent race conditions and spam requests
				if (dehy.utils.freeze_submissions) {
					return false;
				}
				// postcode_input.setCustomValidity(validity_message)
				if (section_name == 'shipping' || section_name == 'billing') {
					if (e.target.hasAttribute('name') && e.target.name=='method_code') {
						dehy.ch.shipping.update_shipping_method(e.target);
						return
					}
					var postcode_input = e.target.closest('form').querySelector('#id_postcode');
					if (e.target.matches('#id_country')) {

						var country = document.querySelector('#id_country').value.toLowerCase();
						var validity_message = 'Please enter a proper 5 digit (XXXXX) or 9 digit ZIP code (XXXXX-XXXX).';
						var state_selector = document.querySelector('#id_state');

						if (country == 'ca') {
							validity_message = 'Please enter a proper Canadian postal code';
							state_selector.required = false;
							state_selector.disabled = true;
							state_selector.selectedIndex = 0;
						} else {
							state_selector.required = true;
							state_selector.disabled = false;
						}
						if (postcode_input.validity.patternMismatch) {
							postcode_input.setCustomValidity(validity_message)
						} else {
							postcode_input.setCustomValidity("")
						}

						postcode_input.pattern = dehy.ch.utils.re[country];
					}
					if (e.target.matches('#id_postcode, #id_state, #id_city, #saved_address_dropdown')) {
						// console.log('e.target.reportValidity(): ', e.target.reportValidity());
						if (e.target.matches('#id_postcode')) {
							if (!e.target.checkValidity()) {
								e.target.reportValidity();
								return
							}
						}
						if (!postcode_input.checkValidity()) {
							postcode_input.classList.toggle('invalid', true);
							return
						}
						// get/update the shipping methods
						if (section_name == 'shipping') {
							var data = new FormData(e.target.closest('form'));
							dehy.ch.shipping.get_shipping_methods(data);
							console.log('getting shipping methods');
							dehy.ch.forms.show_submit_button();
							return
						}
					}
				}
				if (e.target.matches("input#id_same_as_shipping")) {
					// set or reset the address elements
					var checked = e.target.checked;

					if (!checked) {
						// clear the form
						form.reset();
						dehy.ch.forms.save_form_data(form, section_name);
						e.target.checked = false;
					}
					dehy.ch.shipping.billing_same_as_shipping_handler(checked);
				}
			});

			var saved_address_dropdown = document.getElementById('saved_address_dropdown');

			if (saved_address_dropdown) {
				var address_id_elem = document.getElementById('id_address_id');
				if (address_id_elem) {
					var saved_address = dehy.ch.forms.saved_addresses.find(elem=>elem.id==address_id_elem.value);
					saved_address_dropdown.selectedIndex = dehy.ch.forms.saved_addresses.indexOf(saved_address);

				}
				saved_address_dropdown.addEventListener('change', dehy.ch.forms.set_form_to_saved_address);
			}

			// dehy.utils.unfreeze_forms();
		}
	},
};