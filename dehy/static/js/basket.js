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
		$.ajax({
			method: "POST",
			dataType: 'json',
			url: '/basket/',
			contentType: false,
			processData: false,
			data: form_data,
			success: dehy.basket.basket_updated_handlers.success,
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
			// set the subtotal
			var subtotal = document.querySelector('span#subtotal')
			subtotal.textContent = `${dehy.basket.currency_symbol}${response.order_total}`

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

					// console.log(k);
					// console.log(v.quantity);
					// console.log(v.price);
				}
			}

		},
		error(error, xhr, status) {
			console.log('error: ', error)
			console.log('xhr: ', xhr)

		}
	}
}