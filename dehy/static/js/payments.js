window.addEventListener('load', function () {
	same_as_shipping_handler();
}

function same_as_shipping_handler() {
	var same_as_shipping_checkbox = document.querySelector("input[name=same_as_shipping]");

	if (same_as_shipping_checkbox) {
		same_as_shipping_checkbox.addEventListener('change', e=>{
			// list of elements that need to be changed:
			// first_name, last_name, addr1, addr2(optional), city, state, postcode, phone(optional), country
			if (e.target.checked) {
				// fill in the values
			} else {
				// first_name, last_name,
			}
		})
	}
}