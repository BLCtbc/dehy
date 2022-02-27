default_app_config = 'dehy.appz.checkout.apps.CheckoutConfig'
PAYMENT_EVENT_PURCHASE = 'Purchase'
PAYMENT_METHOD_STRIPE = 'Stripe'
STRIPE_EMAIL = 'stripeEmail'
STRIPE_TOKEN = 'stripeToken'

class FORM_STRUCTURES:
	address = [
		{
			'tag': 'div',
			'classes': 'address-container',
			'elems': [
				{	## first and last name
					'tag':'div',
					'classes':'form-group row',
					'elems': [
						{
							'tag':'input',
							'classes': 'required col',
							'attrs': {'name':'first_name', 'required':'', 'maxlength': '50', 'type': 'text', 'id':'id_first_name', 'placeholder':"First Name", 'aria-label':"First Name"}
						},
						{
							'tag':'input',
							'classes': 'required col',
							'attrs': {'name':'last_name', 'required':'', 'maxlength': '50', 'type': 'text', 'id':'id_last_name', 'placeholder':"Last Name", 'aria-label':"Last Name"}
						}
					]
				},
				{ ## address 1
					'tag':'div',
					'classes':'form-group row',
					'elems': [
						{
							'tag':'input',
							'classes': 'required',
							'attrs': {'name':'line1', 'required':'', 'maxlength': '70', 'type': 'text', 'id':'id_line1', 'placeholder':"Address 1", 'aria-label':"Address 1"}
						}
					]
				},
				{ ## address 2
					'tag':'div',
					'classes':'form-group row',
					'elems': [
						{
							'tag':'input',
							'attrs': {'name':'line2','maxlength': '70', 'type': 'text', 'id':'id_line2', 'placeholder':"Address 2", 'aria-label':"Address 2"}
						}
					]
				},
				{ ## country select
					'tag':'div',
					'classes':'form-group row',
					'elems': [
						{
							'tag':'select',
							'classes': 'required',
							'attrs': {'name':'country', 'required':'', 'maxlength': '70', 'type': 'text', 'id':'id_country', 'aria-label':"Country"},
							'elems': [
								{
									'tag': 'option',
									'text': 'United States',
									'attrs': {'value': 'US', 'selected':True}
								},
								{
									'tag': 'option',
									'text': 'Canada',
									'attrs': {'value': 'CA'}
								},
							],
						},
					],
				},
				{ ## zip, city, state
					'tag':'div',
					'classes':'form-group row',
					'elems': [
						{	## zip
							'tag':'input',
							'classes': 'required col',
							'attrs': {'required':'', 'name':'postcode', 'maxlength': '30', 'type': 'text', 'id':'id_postcode', 'placeholder':"ZIP Code", 'aria-label':"Zip Code"}
						},
						{	## city
							'tag':'input',
							'classes': 'required col',
							'attrs': {'required':'', 'name':'line4','maxlength': '70', 'type': 'text', 'id':'id_line4', 'placeholder':"City", 'aria-label':"City"}
						},
						{	## state
							'tag':'input',
							'classes': 'required col',
							'attrs': {'required':'', 'name':'state', 'maxlength': '70', 'type': 'text', 'id':'id_state', 'placeholder':"State", 'aria-label':"State"}
						},
					]
				},
				{ ## phone number
					'tag':'div',
					'classes':'form-group row',
					'elems': [
						{
							'tag':'input',
							'attrs': {'name':'phone_number', 'maxlength': '40', 'type': 'tel', 'id':'id_phone_number', 'placeholder':"Phone Number", 'aria-label':"Phone Number"}
						}
					]
				},
			]
		},

		{
			'tag': 'div',
			'classes': 'error-container button-container',
			'elems': [{
				'tag':'div',
				'classes':'form-group row',
				'attrs': {'id': 'error_container'},
				'elems': [
					{
						'tag':'div',
						'classes': 'col-12 errors',
						'attrs': {
							'id': 'errors',
						}
					}]
				},
				{
					'tag':'div',
					'classes':'form-group row',
					'elems': [
						{
							'tag':'button',
							'text': 'Continue',
							'classes': 'col-12',
							'attrs': {
								'type': 'submit', 'hidden': '', 'aria-label':'Continue'
							}
						}
					],
				},
			],
		}]

	shipping_methods = [{
		'tag': 'div',
		'classes': 'shipping-methods-container',
		'elems': [{

		}]
	}]
