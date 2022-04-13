from django import template
from django.template.loader import select_template
from oscar.templatetags import product_tags

register = template.Library()

def render_product(context, product):
	"""
	Render a product snippet as you would see in a browsing display.
	This templatetag looks for different templates depending on the UPC and
	product class of the passed product.  This allows alternative templates to
	be used for different product classes.
	"""
	if not product:
		# Search index is returning products that don't exist in the
		# database...
		return ''

	names = [
		'dehy/shop/partials/product/upc-%s.html' % product.upc,
		'dehy/shop/partials/product/class-%s.html' % product.get_product_class().slug,
		'dehy/shop/partials/product.html'
	]

	template_ = select_template(names)
	context = context.flatten()

	# Ensure the passed product is in the context as 'product'
	context['product'] = product
	return template_.render(context)


product_tags.render_product = render_product
register.simple_tag(takes_context=True, name="render_product")(product_tags.render_product)