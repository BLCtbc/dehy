from django.utils.translation import gettext_lazy as _
from django_tables2 import A, Column, LinkColumn, TemplateColumn

from oscar.core.loading import get_class, get_model
Recipe = get_model('recipes', 'Recipe')
DashboardTable = get_class('dashboard.tables', 'DashboardTable')

class RecipesTable(DashboardTable):
	name = TemplateColumn(verbose_name=_('Title'), order_by='name', accessor=A('name'), template_name='dehy/dashboard/recipes/partials/recipe_title.html')
	image = TemplateColumn(verbose_name=_('Image'), template_name='dehy/dashboard/recipes/partials/recipe_image.html', orderable=False)
	description = TemplateColumn(template_name='dehy/dashboard/recipes/partials/recipe_description.html', verbose_name=_('Description'), orderable=False)
	created = Column(verbose_name=_('Created'), accessor='date_created')
	last_modified = Column(verbose_name=_('Last Modified'), accessor='last_modified')
	actions = TemplateColumn(verbose_name=_('Actions'), template_name='dehy/dashboard/recipes/partials/recipe_row_actions.html', orderable=False)
	class Meta(DashboardTable.Meta):
		model = Recipe
		fields = ('name', 'image', 'description', 'created', 'last_modified', 'featured')
		# sequence = ('title', 'upc', 'image', 'product_class', 'variants',
		#             'stock_records', '...', 'is_public', 'date_updated', 'actions')
		order_by = '-last_modified'
#
# class UserTable(DashboardTable):
#     check = TemplateColumn(
#         template_name='oscar/dashboard/users/user_row_checkbox.html',
#         verbose_name=' ', orderable=False)
#     email = LinkColumn('dashboard:user-detail', args=[A('id')],
#                        accessor='email')
#     name = Column(accessor='get_full_name',
#                   order_by=('last_name', 'first_name'))
#     active = Column(accessor='is_active')
#     staff = Column(accessor='is_staff')
#     date_registered = Column(accessor='date_joined')
#     num_orders = Column(accessor='orders__count', orderable=False, verbose_name=_('Number of Orders'))
#     actions = TemplateColumn(
#         template_name='oscar/dashboard/users/user_row_actions.html',
#         verbose_name=' ')
#
#     icon = 'fas fa-users'
#
#     class Meta(DashboardTable.Meta):
#         template_name = 'oscar/dashboard/users/table.html'
#
# class ProductTable(DashboardTable):
#     title = TemplateColumn(
#         verbose_name=_('Title'),
#         template_name='oscar/dashboard/catalogue/product_row_title.html',
#         order_by='title', accessor=A('title'))
#     image = TemplateColumn(
#         verbose_name=_('Image'),
#         template_name='oscar/dashboard/catalogue/product_row_image.html',
#         orderable=False)
#     product_class = Column(
#         verbose_name=_('Product type'),
#         accessor=A('product_class'),
#         order_by='product_class__name')
#     variants = TemplateColumn(
#         verbose_name=_("Variants"),
#         template_name='oscar/dashboard/catalogue/product_row_variants.html',
#         orderable=False
#     )
#     stock_records = TemplateColumn(
#         verbose_name=_('Stock records'),
#         template_name='oscar/dashboard/catalogue/product_row_stockrecords.html',
#         orderable=False)
#     actions = TemplateColumn(
#         verbose_name=_('Actions'),
#         template_name='oscar/dashboard/catalogue/product_row_actions.html',
#         orderable=False)
#
#     icon = 'fas fa-sitemap'
#
#     class Meta(DashboardTable.Meta):
#         model = Product
#         fields = ('upc', 'is_public', 'date_updated')
#         sequence = ('title', 'upc', 'image', 'product_class', 'variants',
#                     'stock_records', '...', 'is_public', 'date_updated', 'actions')
#         order_by = '-date_updated'
