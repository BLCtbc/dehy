$(document).ready(function() {
	dehy.shop.variant_size_selection_handler();
	dehy.shop.add_item_to_cart_handler();

});

dehy.shop = {
	variant_size_selection_handler() {
		var size_selector = document.getElementById('size_selector');
		size_selector.addEventListener('change', e=> {
			var select_container = document.querySelector('.variant-select-container')
			select_container.dataset.text = e.target.value;
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

