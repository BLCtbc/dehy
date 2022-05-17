dehy.accounts = {
	init() {
		dehy.utils.generic_handler_setup(".password-toggle", "click", dehy.accounts.handlers.toggle_password_visibility);
		dehy.utils.generic_handler_setup(".set-card-default", "click", dehy.accounts.handlers.set_card_as_default);
		dehy.utils.generic_handler_setup(".delete-card", "click", dehy.accounts.handlers.remove_card);
		dehy.accounts.handlers.initialize_stripe_card();


		// dehy.accounts.handlers.set_card_as_default_handler();
	},
	handlers: {
		initialize_stripe_card() {
			var stripe_payment_container = document.getElementById('stripe_payment_container');
			if (stripe_payment_container) {
				//
			}
		}
		toggle_password_visibility(e) {
			e.preventDefault();
			var password_field = document.getElementById(e.target.dataset.for);
			if (password_field) {
				if (password_field.type=='password') {
					password_field.type = 'text';
					e.target.textContent = dehy.translations.hide_password
				} else {
					password_field.type = 'password';
					e.target.textContent = dehy.translations.show_password
				}
			}
		},
		remove_card(e) {
			var card_id = e.target.closest('tr').dataset.cardid;
			var data = {'card_id': card_id};

			$.ajax({
				method: "POST",
				url: '/accounts/payment/remove-card/',
				data: data,
				success: function(data) {
					let row = document.querySelector(`tr[data-cardid='${data.card_id}']`);
					row.remove();
					dehy.utils.notify_user(data.message);
				},
				error: function(data) {
					let message = `${data.error_code} ${data.message}`;
					dehy.utils.notify_user(message);
				},
			});
		},
		set_card_as_default(e) {

			var card_id = e.target.closest('tr').dataset.cardid;
			var data = {'card_id': card_id};

			$.ajax({
				method: "POST",
				url: '/accounts/payment/set-default/',
				data: data,
				success: function(data) {
					var old_badges = document.querySelectorAll('.badge-success');
					old_badges.forEach(elem=>{
						let tr = elem.closest('tr')
						let button = dehy.utils.create_element(
							{
								tag:'button', classes:'set-card-default btn btn-primary w-100',
								text: data.button_text,
								attrs:{'role':'button', 'type':'button'}
							}
						);
						button.addEventListener('click', dehy.accounts.handlers.set_card_as_default);
						tr.querySelector("tr > td:nth-child(2) .col").append(button);
						elem.remove();
					});
					let row = document.querySelector(`tr[data-cardid='${data.card_id}']`);
					row.querySelector('.set-card-default').remove();
					let td = row.querySelector('td');
					td.insertBefore(dehy.utils.create_element({tag:'span', classes:'badge badge-success', text: data.badge_text}), td.firstChild);
					dehy.utils.notify_user(data.message);
				},
				error: function(data) {
					let message = `${data.error_code} ${data.message}`;
					dehy.utils.notify_user(message);
				},
			});
		},
	}
}