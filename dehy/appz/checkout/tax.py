from decimal import Decimal as D

def apply_to(submission):
	# Assume 7% sales tax on sales to New Jersey  You could instead use an
	# external service like Avalara to look up the appropriates taxes.
	STATE_TAX_RATES = {
		'NJ': D('0.07')
	}
	shipping_address = submission['shipping_address']
	rate = STATE_TAX_RATES.get(shipping_address.state, D('0.07')) ## defaults to 7% tax rate
	for line in submission['basket'].all_lines():
		line_tax = calculate_tax(
			line.line_price_excl_tax_incl_discounts, rate)
		unit_tax = (line_tax / line.quantity).quantize(D('0.01'))
		line.purchase_info.price.tax = unit_tax

	# Note, we change the submission in place - we don't need to
	# return anything from this function
	shipping_charge = submission['shipping_charge']
	if shipping_charge is not None:
		shipping_charge.tax = calculate_tax(
			shipping_charge.excl_tax, rate)

def calculate_tax(price, rate):
	tax = price * rate
	return tax.quantize(D('0.01'))