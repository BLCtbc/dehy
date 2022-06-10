dehy.home = {
	init() {
		// carousel handler
		dehy.utils.generic_handler_setup('.carousel-control', "click", dehy.home.handlers.carousel_scroll_handler);
	},
	handlers: {
		carousel_scroll_handler(e) {
			var mini_shop = document.getElementById('mini_shop');
			var product_card = mini_shop.querySelector('.product-card');
			const gridComputedStyle = window.getComputedStyle(mini_shop);
			var card_gap_total = product_card.offsetWidth + parseFloat(gridComputedStyle.gridColumnGap.replace('px', ''));
			var num_scrolls = Math.max(1, Math.floor(mini_shop.offsetWidth / card_gap_total));
			var total_scroll = card_gap_total*num_scrolls;
			if (e.target.matches('.carousel-control-prev, .carousel-scroll-left')) {
				total_scroll *= -1
			};
			mini_shop.closest('section').scrollBy({left: total_scroll, top: 0, behavior: 'smooth'});
		}
	}
}