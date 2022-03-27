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
		dehy.basket.remove_oscar_basket_event_listeners();
		var basket_formset = document.querySelector('.basket_summary');

		basket_formset.querySelectorAll('.product-quantity').forEach(function(elem) {
			dehy.basket.utils.set_product_quantity_width(elem);
		    elem.addEventListener('change', dehy.basket.update_product_quantity_handler);
		});
		basket_formset.querySelectorAll('.remove-basket-item').forEach(function(elem) {
		    elem.addEventListener('click', e=>{dehy.basket.update_product_quantity_handler(e, 0)});
		});
		basket_formset.addEventListener('submit', e=>{
			e.preventDefault();
		});
	},
	remove_oscar_basket_event_listeners() {
		document.querySelectorAll("#content_inner, .order-contents").forEach(function(elem) {
			dehy.utils.remove_event_listeners(elem);
		})
	},
	update_product_quantity(e, n=0) {
		var form = e.target.closest('form');
		var form_data = new FormData(form);
		if (window.location.pathname.includes("checkout")) {
			var section = document.querySelector('section.active');
			if (section && section.id=='shipping') {
				var shipping_form = new FormData(section.querySelector('form'))

				var shipping_data = {};
				for (let[k, val] of shipping_form.entries()) {
					if (val) {
						shipping_data[k] = val;
					}
				};
				form_data.append('shipping_addr', JSON.stringify(shipping_data));
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
				dehy.basket.basket_updated_handlers.success(data);
				if (data.hasOwnProperty('shipping_methods') && window.location.pathname.includes("checkout")) {
					// update shipping methods
					dehy.ch.shipping.display_shipping_methods(data);
				}
			},
			error: dehy.basket.basket_updated_handlers.error
		});
	},
	update_product_quantity_handler(e, n=null) {
		var n = (n != null) ? n: e.target.value;
		if (n==0) {
			const modal = new Promise(function(resolve, reject){
				$('#confirm_item_removal').modal('show');
				$('#confirm_remove_btn').click(function(){
					resolve("user clicked");
				});
				$('#cancel_remove_btn').click(function(){
					reject("user clicked cancel");
				});
			}).then(function(val){
				//val is your returned value. argument called with resolve.
				dehy.basket.update_product_quantity(e)
				e.target.closest('.basket-items').remove()

			}).catch(function(err){
				//user clicked cancel
				console.log("user clicked cancel", err)
				e.target.value = n;
			});
		} else {
			dehy.basket.update_product_quantity(e)
		}
	},
	basket_updated_handlers: {
		success(response, xhr, status) {
			console.log('response: ', response)
			console.log('xhr: ', xhr)
			var subtotal = `${dehy.basket.currency_symbol}${response.subtotal}`;
			var subtotal_container = document.querySelector('span#subtotal');
			subtotal_container.textContent = subtotal;

			if (window.location.pathname.includes("checkout")) {

				var shipping_charge = (response.hasOwnProperty('shipping_charge')) ? `${dehy.basket.currency_symbol}${response.shipping_charge}` : "--";
				var shipping_charge_container = document.querySelector('#shipping_charge');
				if (shipping_charge_container) {
					shipping_charge_container.textContent = shipping_charge;
					if (response.hasOwnProperty('shipping_postcode')) {
						var shipping_postcode_container = document.querySelector('#shipping_postcode');
						if (shipping_postcode_container) {
							shipping_postcode_container.textContent = `(${response.shipping_postcode})`
						}
					}
				};

				var total_tax = (response.hasOwnProperty('total_tax')) ? response.total_tax : "0.00";
				total_tax = `${dehy.basket.currency_symbol}${total_tax}`
				var total_tax_container = document.querySelector('#total_tax');
				if (total_tax_container) {
					total_tax_container.textContent = total_tax;
				};

				var order_total = (response.hasOwnProperty('order_total')) ? `${dehy.basket.currency_symbol}${response.order_total}` : subtotal;
				var order_total_container = document.querySelector('#order_total');
				if (order_total_container) {
					order_total_container.textContent = order_total;
				};
			}


			var form_count = document.querySelectorAll('.basket-items').length
			dehy.utils.update_cart_quantity(response.basket_num_items);
			document.querySelector('#id_form-TOTAL_FORMS').value = form_count
			document.querySelector('#id_form-INITIAL_FORMS').value = form_count

			if (response.object_list) {
				for (let [k,v] of Object.entries(response.object_list)) {
					var basket_item_element = document.querySelector(`.basket-items[data-product-id='${k}']`);
					var quantity_container = basket_item_element.querySelector('.product-quantity');
					dehy.basket.utils.set_product_quantity_width(quantity_container);
					basket_item_element.querySelector('.price-text').textContent = `${dehy.basket.currency_symbol}${v.price}`;
				}
			}

		},
		error(error, xhr, status) {
			console.log('error: ', error)
			console.log('xhr: ', xhr)
		}
	}
}