// DEHY.basket namespace
dehy.basket = {
	currency_symbol: "",
	utils: {
		set_product_quantity_width(elem) {
			elem.style.width = `${Math.max(2, elem.value.length+0.5)}rem`;
		}
	},
	init(currency_symbol="$") {
		dehy.basket.currency_symbol = currency_symbol;
		// dehy.basket.remove_oscar_basket_event_listeners();
		var basket_formset = document.querySelector('form.basket_summary');

		if (basket_formset) {

			basket_formset.querySelectorAll('.product-quantity').forEach(elem=> {

				elem.addEventListener('change', dehy.basket.update_product_quantity_handler);
			});

			basket_formset.addEventListener('submit', e=>{
				e.preventDefault();
			});

			basket_formset.querySelectorAll('.remove-basket-item').forEach(elem=> {
				elem.addEventListener('click', dehy.basket.remove_basket_item_handler);
			});

		} else {
			// console.log('no basket form found');
		}

	},
	remove_basket_item_handler(e) {
		dehy.basket.product_quantity_update_confirmation(e, 0)
		.then((input)=>{
			const change = new Event('change');
			input.dispatchEvent(change);
			return input
		}, (msg)=>{throw msg})
		.then((input)=>{
			input.closest('.basket-items').remove();
		})
		.catch(err=>{
			console.error(err);
		});
	},
	remove_oscar_basket_event_listeners() {
		document.querySelectorAll("#content_inner, .order-contents").forEach(function(elem) {
			dehy.utils.remove_event_listeners(elem);
		});
	},
	update_product_quantity(e) {
		return new Promise((resolve, reject) => {
			var form = e.target.closest('form');
			var form_data = new FormData(form);
			if (window.location.pathname.includes("checkout")) {
				var section = document.querySelector('section.active');
				if (dehy.ch.forms.saved_form_data.hasOwnProperty('shipping') && dehy.ch.forms.saved_form_data.shipping.postcode) {
					form_data.append('update_shipping', JSON.stringify(true));
				}
			}
			$.ajax({
				method: "POST",
				dataType: 'json',
				url: form.action,
				contentType: false,
				processData: false,
				data: form_data,
				success: function(data) {
					resolve(data)
				},
				error: function(error) {
					reject(error)
				}
			});
		});
	},
	update_product_quantity_handler(e) {
		dehy.basket.product_quantity_update_confirmation(e)
		.then(dehy.basket.update_product_quantity, dehy.basket.basket_updated_handlers.error)
		.then((data)=> {
			dehy.basket.basket_updated_handlers.success(data);
			if (data.hasOwnProperty('shipping_methods') && window.location.pathname.includes("checkout")) {
				// update shipping methods
				dehy.ch.shipping.update_shipping_methods(data);
			}
		}, (data)=> {dehy.basket.basket_updated_handlers.error(data) })
		.catch(dehy.basket.basket_updated_handlers.error)
	},
	product_quantity_update_confirmation(e, n=null) {
		const modal = new Promise((resolve, reject) => {

			if (n != null) {

				var name = `form-${e.target.dataset.id}-quantity`;
				var input = document.querySelector(`input[name='${name}']`);
				$('#confirm_item_removal').modal('show');
				$('#confirm_remove_btn').click(function(){
					input.value = 0;
					resolve(input)
				});
				$('#cancel_remove_btn').click(function(){
					input.value = 1;
					reject("user clicked cancel");
				});
			} else {
				resolve(e)
			}
		});
		return modal
	},
	create_basket_item(product) {

		var form = document.getElementById('basket_formset');
		if (!form) {
			form = dehy.basket.create_mini_basket_formset();

			let mini_basket_form_container = document.getElementById('mini_basket_form_container');
			mini_basket_form_container.append(form);
		}
		var	basket_row = dehy.utils.create_element({tag:'div', classes: 'basket-items row', attrs: {'data-product-id': product.id}}),
			form_number = document.querySelectorAll('.basket-items.row').length;

		form.append(basket_row);
		var input_name = `form-${form_number}-id`;

		var form_identifier = dehy.utils.create_element({tag:'input', attrs: {'value':product.line_id, 'name': input_name, 'id':`id_${input_name}`, 'type':'hidden'}}),
			image_col = dehy.utils.create_element({tag:'div', classes: 'col-3 px-0'}),
			title_col = dehy.utils.create_element({tag:'div', classes: 'col-6 col-md-5 mt-3'}),
			price_col = dehy.utils.create_element({tag:'div', classes: 'col-3'});

		basket_row.append(form_identifier, image_col, title_col, price_col);


		var image_container = dehy.utils.create_element({tag:'div', classes: 'image-container'});

		if (product.img_url) {
			let img = dehy.utils.create_element({tag:'img', attrs:{'src': window.location.origin+product.img_url, 'alt':product.title}});
			image_container.append(img);
		}

		image_col.append(image_container);


		var h3 = dehy.utils.create_element({tag:'h3'}),
			link = dehy.utils.create_element({tag:'a', text:product.title, attrs:{'href':window.location.origin+product.url}});

		h3.append(link);
		title_col.append(h3);

		if (product.size) {
			let size = dehy.utils.create_element({tag:'p', classes: 'size-variant', text: `${dehy.translations.size}: ${product.size}`});
			title_col.append(size);
		}

		let price_text = dehy.utils.create_element({tag:'p', classes: 'price-text', text: `${dehy.basket.currency_symbol}${product.price}`});

		var quantity_select_container = dehy.utils.create_element({tag:'div', classes: 'quantity-select-container row'}),
			minus_container = dehy.utils.create_element({tag:'div', classes: 'plus-minus-container minus-container col-3 p-0'}),
			input_label = dehy.utils.create_element({tag:'label', classes:'sr-only', text:'Quantity', attrs:{'for':'quantity'}}),
			input_container = dehy.utils.create_element({tag:'div', classes: 'input-quantity-container px-0 col-6'}),
			plus_container = dehy.utils.create_element({tag:'div', classes: 'plus-minus-container plus-container col-3 p-0'});

		let minus_button_attrs = {
			'aria-controls': "#id_quantity",
			'role':"button",
			'aria-label':"Decrement",
			"data-product_id":product.id
		};
		let minus_button = dehy.utils.create_element({tag:'button', classes: 'plus-minus-btn minus-btn', attrs:minus_button_attrs});
		minus_container.append(minus_button);

		let minus_i = dehy.utils.create_element({tag:'i', classes:'fas fa-minus', attrs:{'aria-hidden': true}});
		minus_button.append(minus_i);
		minus_button.addEventListener('click', dehy.handlers.shop.plus_minus_button_handler);

		let input_attrs = {
			"type": "number",
			"pattern": "[0-9]*",
			"name": `form-${form_number}-quantity`,
			"id": `id_form-${form_number}-quantity`,
			"value": product.quantity,
			"min": 1,
			"max": 99,
			"data-product_id": product.id
		};
		let quantity_input = dehy.utils.create_element({tag:'input', classes: 'product-quantity quantity', attrs:input_attrs});
		quantity_input.addEventListener('change', dehy.basket.update_product_quantity_handler);
		input_container.append(quantity_input);

		let plus_button = dehy.utils.create_element({tag:'button', classes: 'plus-minus-btn plus-btn', attrs:{'aria-controls': "#id_quantity", 'role':"button", 'aria-label':"Increment", "data-product_id":product.id}});

		plus_container.append(plus_button);
		let plus_i = dehy.utils.create_element({tag:'i', classes: 'fas fa-plus', attrs:{'aria-hidden': true}});
		plus_button.append(plus_i);
		plus_button.addEventListener('click', dehy.handlers.shop.plus_minus_button_handler);

		quantity_select_container.append(minus_container, input_label, input_container, plus_container);
		let remove_container = dehy.utils.create_element({tag:'p', classes: 'remove-container'}),
			remove_button = dehy.utils.create_element({tag:'a', classes: 'remove-basket-item', text:"Remove", attrs:{"role":"button", "data-id":form_number, "data-behaviors":"remove"}});

		remove_container.append(remove_button);
		price_col.append(price_text, quantity_select_container, remove_container);
		remove_button.addEventListener("click", dehy.basket.remove_basket_item_handler);

		return basket_row

	},
	create_mini_basket_formset() {
		var form_attrs = {
			"method": "post",
			"action": "/basket/",
			"id": "basket_formset",
		};
		var form = dehy.utils.create_element({tag:'form', classes:'basket_summary col-12 compact', attrs:form_attrs});

		var csrftoken_elem = dehy.utils.create_element({tag:'input', attrs:{'name':'csrfmiddlewaretoken', 'type': 'hidden', 'value':dehy.utils.getCookie('csrftoken')}});
		var total_forms = dehy.utils.create_element({tag:'input', attrs:{'id': 'id_form-TOTAL_FORMS', 'name':'form-TOTAL_FORMS', 'type': 'hidden', 'value':0}});
		var initial_forms = dehy.utils.create_element({tag:'input', attrs:{'id': 'id_form-INITIAL_FORMS', 'name':'form-INITIAL_FORMS', 'type': 'hidden', 'value':0}});
		var min_forms = dehy.utils.create_element({tag:'input', attrs:{'id': 'id_form-MIN_NUM_FORMS', 'name':'form-MIN_NUM_FORMS', 'type': 'hidden', 'value':0}});
		var max_forms = dehy.utils.create_element({tag:'input', attrs:{'id': 'id_form-MAX_NUM_FORMS', 'name':'form-MAX_NUM_FORMS', 'type': 'hidden', 'value':1000}});
		form.append(csrftoken_elem, total_forms, initial_forms, min_forms, max_forms);
		return form

	},
	basket_updated_handlers: {
		success(response, xhr, status) {

			var subtotal = (response.hasOwnProperty('subtotal')) ? response.subtotal: null;
			var subtotal_container = document.querySelector('span#subtotal');

			if (subtotal && subtotal_container) {
				subtotal_container.textContent =  `${dehy.basket.currency_symbol}${response.subtotal}`;
				var free_shipping_bar = document.querySelector(".free-shipping-bar");
				var free_shipping_container = document.querySelector('.free-shipping-container');
				if (parseFloat(subtotal) < 50) {
					free_shipping_container.firstChild.textContent = `Spend $${50-parseFloat(subtotal)} or more to get FREE SHIPPING!`

					var delta = parseInt(100*(parseFloat(subtotal)/50));
					free_shipping_bar.classList.toggle('d-none', false);
					free_shipping_bar.firstElementChild.style.width = `${delta}%`;
				} else {
					free_shipping_container.firstChild.textContent = `You've unlocked FREE SHIPPING!`
					free_shipping_bar.classList.toggle('d-none', true);
					free_shipping_bar.firstElementChild.style.width = "100%";

				}
			} else {
				// create subtotal container?
			}

			if (window.location.pathname.includes("checkout")) {

				var shipping_charge = (response.hasOwnProperty('shipping_charge')) ? `${dehy.basket.currency_symbol}${response.shipping_charge}` : "--";
				var shipping_charge_container = document.getElementById('shipping_charge');
				if (shipping_charge_container) {
					shipping_charge_container.textContent = shipping_charge;
					if (response.hasOwnProperty('shipping_postcode')) {
						var shipping_postcode_container = document.querySelector('#shipping_postcode');
						if (shipping_postcode_container) {
							shipping_postcode_container.textContent = ` (${response.shipping_postcode})`
						}
					}
				};

				var total_tax = (response.hasOwnProperty('total_tax')) ? response.total_tax : "0.00";
				total_tax = `${dehy.basket.currency_symbol}${total_tax}`
				var total_tax_container = document.getElementById('total_tax');
				if (total_tax_container) {
					total_tax_container.textContent = total_tax;
				};

				var discounts = (response.hasOwnProperty('discounts')) ? response.discounts : null;
				var discounts_container = document.getElementById('discounts_container');
				if (discounts_container) {
					dehy.utils.remove_children(discounts_container);
					if (discounts && discounts.total>0) {
						var total_discount = `${dehy.basket.currency_symbol}${discounts.total}`;
						var col1 = dehy.utils.create_element({tag:'div', classes:'col'}),
							disc_span = dehy.utils.create_element({tag:'span', text:dehy.translations.discounts}),
							col2 = dehy.utils.create_element({tag:'div', classes:'col text-right'}),
							price_span = dehy.utils.create_element({tag:'span', classes:'price-text', text: `-${total_discount}`, attrs:{'id':'discounts'}});

						col1.append(disc_span);
						col2.append(price_span);
						discounts_container.append(col1, col2);
						if (discounts.hasOwnProperty('shipping')) {
							shipping_charge_container.textContent = `${dehy.basket.currency_symbol}${discounts.shipping}`;
						}
					}
				}


				var order_total = (response.hasOwnProperty('order_total')) ? `${dehy.basket.currency_symbol}${response.order_total}` : subtotal;
				var order_total_container = document.getElementById('order_total');
				if (order_total && order_total_container) {
					order_total_container.textContent = order_total;
				};
			}

			if (response.hasOwnProperty('object_list')) {
				for (let [k,v] of Object.entries(response.object_list)) {
					var basket_item_element = document.querySelector(`.basket-items[data-product-id='${k}']`);
					if (!basket_item_element) {
						dehy.basket.create_basket_item(v);
					} else {
						var quantity_container = basket_item_element.querySelector('.product-quantity');
						quantity_container.value = v.quantity;
						basket_item_element.querySelector('.price-text').textContent = `${dehy.basket.currency_symbol}${v.price}`;
					}
				}
			}
			var form_count = document.querySelectorAll('.basket-items').length;

			let total_forms = document.getElementById('id_form-TOTAL_FORMS'),
				initial_forms = document.getElementById('id_form-INITIAL_FORMS');

			total_forms.value = form_count
			initial_forms.value = form_count

			var basket_status_container = document.getElementById('basket_status_container');
			if (basket_status_container && !window.location.pathname.includes("checkout")) {
				dehy.utils.remove_children(basket_status_container);
				if (form_count == 0) {
					// create
					var p_elem = dehy.utils.create_element({tag:'p', text:dehy.translations.basket_empty, attrs:{id:'basket_empty_container'}}),
						a_elem = dehy.utils.create_element({tag:'a', text:dehy.translations.continue_shopping, attrs:{'href':"/shop/"}});
					p_elem.append(a_elem);
					basket_status_container.append(p_elem);
				} else {
					// var h2_elem = dehy.utils.create_element({tag:'h2', text:dehy.translations.order_summary});
					// basket_status_container.append(h2_elem);
				}
			}
			if (response.hasOwnProperty('basket_num_items')) {
				dehy.utils.update_cart_quantity(response.basket_num_items);
			}

		},
		error(error, xhr, status) {
			console.error('Uncaught Exception: ', error);
			console.log('xhr: ', xhr);
		}
	}
}