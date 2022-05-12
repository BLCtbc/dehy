dehy.accounts = {
	init() {
		dehy.accounts.handlers.set_card_as_default_handler();
		dehy.accounts.handlers.remove_card_handler();
	},
	handlers: {
		remove_card_handler() {
			var remove_card_buttons = document.querySelectorAll('.delete-card');
			console.log('remove_card_handler: ', remove_card_buttons)

			remove_card_buttons.forEach(btn=>{
				btn.addEventListener('click', dehy.accounts.handlers.remove_card);
			})
		},
		remove_card(e) {
			var card_id = e.target.closest('tr').dataset.cardid;
			var data = {'card_id': card_id};

			$.ajax({
				method: "POST",
				url: '/accounts/billing/remove-card/',
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
				url: '/accounts/billing/set-default/',
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
		set_card_as_default_handler() {

			var default_buttons = document.querySelectorAll('.set-card-default');
			console.log('set_card_as_default: ', default_buttons)

			default_buttons.forEach(btn=> {
				btn.addEventListener('click', dehy.accounts.handlers.set_card_as_default);
			});

		}
	}
}