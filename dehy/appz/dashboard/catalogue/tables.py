from oscar.apps.dashboard.catalogue import tables
from django_tables2 import A, Column, LinkColumn, TemplateColumn
from django.utils.translation import gettext_lazy as _

class ProductTable(tables.ProductTable):

	class Meta(tables.ProductTable.Meta):
		fields = ('upc', 'is_public', 'date_updated', 'featured')
		sequence = (
			'title', 'upc', 'image', 'product_class', 'variants',
			'stock_records', '...', 'is_public', 'featured', 'date_updated', 'actions'
		)