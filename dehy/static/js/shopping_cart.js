$(document).ready(function() {
	variant_size_selection_handler()
});

function variant_size_selection_handler() {
	var size_selector = document.getElementById('size_selector');
	size_selector.addEventListener('change', e=> {
		var select_container = document.querySelector('.variant-select-container')
		select_container.dataset.text = e.target.value;
	});
}
