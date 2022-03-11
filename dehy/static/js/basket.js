// DEHY.basket namespace
dehy.basket = {
	currency_symbol: "",
	init(currency_symbol="$") {
		dehy.basket.currency_symbol = currency_symbol;
		dehy.basket.remove_oscar_basket_event_listeners();
		var basket_formset = document.querySelector('.basket_summary');

		basket_formset.querySelectorAll('.product-quantity').forEach(function(elem) {
		    elem.addEventListener('blur', dehy.basket.update_product_quantity_handler);
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
	update_product_quantity_handler(e) {
		console.log('blur')
		if (e.target.value==0) {
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

			dehy.utils.update_cart_quantity(response.basket_num_items);

		},
		error(error, xhr, status) {
			console.log('error: ', error)
			console.log('xhr: ', xhr)

		}
	}
}