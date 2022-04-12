$(document).ready(function() {
	dehy.shop.variant_size_selection_handler();
	dehy.shop.add_item_to_cart_handler();
	dehy.shop.plus_minus_button_handler();
});

dehy.shop = {
	increment_quantity(elem, n=1) {
		var input = document.querySelector(`input[data-product-id='${elem.dataset.product_id}']`);
		input.value = (n < 0) ? Math.max((input.value - n), input.min) : Math.min((input.value + n), input.max);
	}
	plus_minus_button_handler() {
		var plus_minus_buttons = document.querySelectorAll('.plus-minus-btn');
		plus_minus_buttons.forEach(elem=>{
			var n = 1;
			if (elem.matches('.minus-btn')) {
				n *= -1;
			}
			elem.addEventListener(e=>{
				console.log('elem clicked: ', e.target);
				dehy.shop.increment_quantity(e.target, n);
			})
		})
	},
	variant_size_selection_handler() {
		var size_selectors = document.querySelectorAll('select.variant-size-selector')
		size_selectors.forEach(elem=>{
			elem.addEventListener('change', e=> {
				var select_container = elem.closest('.variant-select-container')
				select_container.dataset.text = e.target.value;
			});
		});
	},
	add_item_to_cart_handler() {
		var forms = document.querySelectorAll('form.add-to-basket');
		forms.forEach(function(form) {
			form.addEventListener('submit', e=> {
				e.preventDefault();
				var form_data = new FormData(e.target);
				$.ajax({
					method: "POST",
					dataType: 'json',
					url: form.action,
					contentType: false,
					processData: false,
					data: form_data,
					success: dehy.shop.item_added_to_cart_success,
					error: dehy.ch.forms.error,
					complete: function() {
						console.log('completed!!!')
						return
					}
				});
			});
		})

	},
	item_added_to_cart_success(response, xhr, status) {
		console.log('success response: ', response);
		console.log('success xhr: ', xhr);
		console.log('success status: ', status);
	},
	item_added_to_cart_error(response, xhr, status) {
		console.log('error: ', error_message);
		var form = dehy.ch.forms.get();
		var error_container = form.querySelector('#error_container');
		error_container.classList.toggle('hide', false);
		error_container.textContent = error_message
		// error_container.append(dehy.utils.create_element({tag:'div', classes:'error', text: error_message, attrs:{'id':'errors'}}));
	}
}

