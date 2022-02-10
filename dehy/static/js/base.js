var DEHY = {
	init: function(choice='') {
		this.handler_choice(choice);
	},
	handler_choice: function(choice='') {
		switch (choice) {
			case 'detail':
				DEHY.handlers.cart();
				break;
			case 'index':
				DEHY.handlers.shop();
				break;
			default:
				DEHY.handlers.all();
		}
	},
	handlers: {
		all: function() {
			DEHY.handlers.cart();
			DEHY.handlers.shop();
		},
		shop: function() {
			// DEHY.handlers.cart();
		},
		cart: function() {
			var size_selector = document.getElementById('size_selector');
			size_selector.addEventListener('change', e=> {
				var variant_select_container = document.querySelector('.variant-select-container'),
					not_price_selector = document.querySelector('span.not_price_color'),
					variant_price = document.querySelector('span.variant_price');
					console.log(e.target.selectedOptions[0].dataset.price)
					var option_price = e.target.selectedOptions[0].dataset.price
				if (e.target.selectedOptions[0].dataset.price) {
					not_price_selector.innerText = "";
					variant_select_container.dataset.text = e.target.value
					variant_price.innerText = `$${option_price}`
				} else {
					not_price_selector.innerText = 'from ';
					console.log(e.target)
					console.log(e.target.options)

					variant_price.innerText = `$${e.target.options[1].dataset.price}`;
					variant_select_container.dataset.text = e.target.options[0].text;
				}
			});
		},
	},
	ajax: {
		get_cart_quantity: function(data) {
			$.ajax({
		         method: "GET",
		         url: "ajax/get_cart_quantity/",
		         dataType: "json",
		         cache: false,
		         success: DEHY.ajax.update_cart_quantity
		     });
		},
		update_cart_quantity: function(data) {
			var cart = document.getElementById("cart-quantity");
			cart.innerText = data.num_cart_items
		}
	}
}

// function handlers() {
// 	console.log('handlers')
// 	var product_list = document.getElementById("product_list");
// 	var body = document.querySelector('body');
// 	console.log('body: ', body)
// 	console.log('product_list: ', product_list)
// }

function ajax_update_basket_mini(data){
   $.ajax({
        method: "GET",
        url: "ajax/update_cart_quantity/",
        dataType: "json",
        cache: false,
        success: update_cart_quantity
    });
}


function update_cart_quantity(data) {
	var cart = document.getElementById("cart-quantity");
	cart.innerText = data.num_cart_items
}