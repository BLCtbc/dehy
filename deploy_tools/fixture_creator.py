from django.core.management import call_command
import pandas as pd
import json, os, re
from datetime import datetime as dt
from oscar.core.loading import get_model

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dehy.settings")
# from django.conf import settings
# settings.configure()
django.setup()

# from APP_NAME.models import *

class FixtureCreator(object):
	def __init__(self, df_file_location=""):
		self.file_location = df_file_location
		ProductTypeClass = get_model('catalogue', 'ProductClass')
		# ProductTypeClass = models.ProductClass
		PartnerClass = get_model('partner', 'Partner')
		self.partner = PartnerClass.objects.get_or_create(name='DEHY', code='dehy')

		# create the product classes: merch, garnish
		self.garnish_product_class = ProductTypeClass.objects.get_or_create(name='Garnish', slug="garnish", requires_shipping=True, track_stock=False)
		self.merch_product_class = ProductTypeClass.objects.get_or_create(name='Merchandise', slug="merchandise", requires_shipping=True, track_stock=True)

	# get current pk
	def get_model_count(self, all_fixtures, model=""):
		model_test = lambda x: ('model' in x.keys() and x['model'] == model)
		return(list(map(model_test, all_fixtures)).count(True))

	def get_parent_pk(self, upc, fixtures):
		upc_test = lambda x: ('upc' in x['fields'].keys() and x['fields']['upc'] == upc)
		ix = list(map(upc_test, fixtures)).index(True)
		return fixtures[ix]['pk']

	def set_file_location(self, df_file_location):
		self.file_location = df_file_location
		self.df = self.get_dataframe(self.file_location)

	class re:
		img_name = re.compile(r'\/[\w\+\-\.\%]*?\.jpg')
		# useless = re.compile("(DEHY(DRATED)*|fruit|garnish)+", re.I) ## remove non-descriptive words
		useless = re.compile("(DEHY(DRATED)*|(?<!agon|star)fruit|garnish)+", re.I) ## remove non-descriptive words
		nope = re.compile(r"[\-\+\%]")
		forbidden = re.compile(r"[\/\:\'\(\)]")
		repeated = re.compile(r"[\-\+\_\s]{2,}")
		slug_matcher = re.compile(r'(https\:\/{2}w{3}\.dehygarnish\.com\/shop\/p\/)?(?P<slug>[\w\- ]+)', re.I)

	class category:
		# create the various Categories: Citrus, Seasonal, etc.
		CategoryClass = get_model('catalogue', 'Category')
		# CategoryClass = models.Category

		flowers = CategoryClass.objects.get_or_create(name='Flowers', slug="flowers",  defaults={'depth':1, 'path':"0002"})
		seasonal = CategoryClass.objects.get_or_create(name='Seasonal', depth=1, defaults={'path':"0003", 'slug':"seasonal"})
		exotic = CategoryClass.objects.get_or_create(name='Exotic', depth=1, defaults={'path':"0005", 'slug':"exotic"})
		citrus = CategoryClass.objects.get_or_create(name='Citrus', depth=1, defaults={'path':"0001", 'slug':"citrus"})
		sets = CategoryClass.objects.get_or_create(name='Sets', depth=1, defaults={'path':"0006", 'slug':"sets"})
		merch = CategoryClass.objects.get_or_create(name='Merch', depth=1, defaults={'path':"0004", 'slug':"merch"})
		pks = {
			'citrus': citrus[0].pk, 'flowers':flowers[0].pk, 'seasonal':seasonal[0].pk, 'exotic': exotic[0].pk, 'merch':merch[0].pk
		}

	def get_product_class_pk(self, category):
		return self.merch_product_class[0].pk if category=="merch" else self.garnish_product_class[0].pk

	def get_category_pk(self, c):
		return self.category.pks[c]



	def extract_float(self, s):
		m = re.match(r'(\d+\.\d+)', s)
		if m:
			return float(m.group())

	def create_img_name(self, img_url):

		match = self.re.img_name.search(img_url)
		if match:
			img_subpath = match.group()
			s = self.re.useless.sub('', img_subpath)
			s = re.sub(r'([\+\-]*?)(?:\.jpg)', '.jpg', s)
			s = self.sanitize(s)
			return s

	def sanitize(self, s):
		a = self.re.forbidden.sub('', s)
		a = self.re.nope.sub(' ', a).strip().replace(' ', '_').lower()
		a = self.re.repeated.sub('_', a)
		return(a)

	def get_slug(self, url):
		match = self.re.slug_matcher.search(url)
		# match = re.search(r'\/p\/(?P<slug>[\w\-]+)', url)
		if match and match.groupdict().get('slug', None):
			match = match.groupdict()['slug'].lower().replace(" ", "")
			return match


	def get_dataframe(self):
		self.df = self._get_dataframe()
		return self.df

	def _get_dataframe(self):

		df = pd.read_excel(os.path.abspath(self.file_location))
		df.price = df.price.apply(self.extract_float)

		df.rename(columns={'link':'url'}, inplace=True)
		df = df.assign(default_image="")
		# df = df[df['category'].notna()] ## removes variants

		df['all_image_links'] = df['all_image_links'].str.strip("[]").str.replace("'","").str.split(',') ## changes all_image_links column: str -> lists

		df['group_id'] = df.title.apply(self.sanitize) ## create new column 'group_id' out of sanitizing 'name' column
		df['slug'] = df.url.apply(self.get_slug)
		# remove duplicate photos from alt images
		for index, row in df.iterrows():
			df.at[index, 'default_image'] = self.create_img_name(df.at[index, 'image_link'])

			# if row['default_image'] in row["all_image_links"]:
			# 	all_image_links = df.at[index, "all_image_links"]
			# 	all_image_links.remove(df.at[index, 'default_image'])
			# 	df.at[index, "all_image_links"] = all_image_links

		df = df.assign(alt_image1="", alt_image2="", alt_image3="")
		for index, row in df.iterrows():
			for img_num, img in enumerate(df.at[index, 'all_image_links'], start=1):
				## add alt image columns
				df.at[index, f'alt_image{img_num}'] = self.create_img_name(img)
		# df.drop(axis=1, columns='all_image_links', inplace=True)
		df.category.fillna(value=0, inplace=True)
		return df



def main():

	# steps:

	# create the partner
	PartnerClass = get_model('partner', 'Partner')
	dehy = PartnerClass.objects.get_or_create(name='DEHY', code='dehy')

	# create the product classes: merch, garnish
	ProductTypeClass = get_model('catalogue', 'ProductClass')

	garnish_product_class = ProductTypeClass.objects.get_or_create(name='Garnish', slug="garnish", requires_shipping=True, track_stock=False)
	merch_product_class = ProductTypeClass.objects.get_or_create(name='Merchandise', slug="merchandise", requires_shipping=True, track_stock=True)

	fc = FixtureCreator(os.path.abspath(os.path.join(os.path.dirname(__file__), 'deploy_tools/DEHY_productlist.xlsx')))
	df = fc.get_dataframe()

	## finalizing the data:
	all_fixtures = []

	counter = 1
	for ix, row in df.iterrows():
		fields,has_child = {},True

		if row['category']:
			if "," in row['category']:
				row['category'] = row['category'].split(", ")[0]

			# create the parent
			fields = {
				"structure": "parent",
				"is_public": True,
				"upc": row["item_group_id"],
				"title": row['title'],
				"slug": fc.get_slug(row["url"]),
				"description": row["description"],
				"product_class": fc.get_product_class_pk(row["category"]),
				"date_created": f"{dt.now().isoformat(timespec='milliseconds')}Z",
				"date_updated": f"{dt.now().isoformat(timespec='milliseconds')}Z"
			}

			if row['category'] == "merch":
				has_child = False
				# if product is standalone, don't create child
				fields.update({
					"structure": "standalone",
					"length": row["length"],
					"width": row["width"],
					"height": row["height"],
					"weight":row["shipping_weight"]
				})

			product_pk = fc.get_model_count(all_fixtures, "catalogue.product")+1
			all_fixtures.append({
				'model':"catalogue.product",
				'pk': product_pk,
				'fields':fields
			})


			### create the productcategory
			# only done for parents and standalones
			all_fixtures.append({
				'model':"catalogue.productcategory",
				'pk': fc.get_model_count(all_fixtures, "catalogue.productcategory")+1,
				'fields': {
					'product': product_pk,
					'category': fc.get_category_pk(row['category'])
				}
			})

			### create and upload the product images
			# images = [x for x in [row["default_image"], row["alt_image1"], row["alt_image2"], row["alt_image3"]] if x]
			# for image_num,image in enumerate([images]):
			# 	image_fields = {
			# 		"product": product_pk,
			# 		"original": f'media/images/{fc.create_img_name(row["url"])}',
			# 		"caption": row["name"],
			# 		"display_order": image_num,
			# 		"date_created": f"{dt.now().isoformat(timespec='milliseconds')}Z",
			# 	}
			# 	all_fixtures.append({
			# 		"model":"catalogue.productimage",
			# 		"pk": fc.get_model_count(all_fixtures, "catalogue.productimage")+1,
			# 		"fields":image_fields
			# 	})

		if has_child:
			# create the child
			parent_ix = fc.get_parent_pk(row['item_group_id'], all_fixtures)
			fields = {
				"structure": "child",
				"title": row['size'],
				"is_public": True,
				"parent": parent_ix,
				"upc": row["id"],
				"slug": f'{fc.get_slug(row["url"])}-{fc.get_slug(row["size"])}',
				"length": row["length"],
				"width": row["width"],
				"height": row["height"],
				"weight":row["shipping_weight"],
				"date_created": f"{dt.now().isoformat(timespec='milliseconds')}Z",
				"date_updated": f"{dt.now().isoformat(timespec='milliseconds')}Z"
			}

			product_pk = fc.get_model_count(all_fixtures, "catalogue.product")+1
			# append the child
			all_fixtures.append({
				'model':"catalogue.product",
				'pk': product_pk,
				'fields':fields
			})


		### create the stock record

		product_sku = row['id']

		# how to find product # for use stockrecord?
		# product_pk = [x['pk'] for x in all_fixtures if x['fields']['upc']==row['id']][0]

		fields = {
			"product": product_pk,
			"partner": 1,
			"partner_sku": product_sku,
			"price_currency": "USD",
			"price": row["price"],
			"date_created": f"{dt.now().isoformat(timespec='milliseconds')}Z",
			"date_updated": f"{dt.now().isoformat(timespec='milliseconds')}Z"
		}

		if row['category'] == "merch" and row['Stock'] != "Unlimited":
			fields.update({
				"num_in_stock": row['Stock'],
				"low_stock_threshold": 5,
			})

		all_fixtures.append({
			'model':"partner.stockrecord",
			'pk': fc.get_model_count(all_fixtures, "partner.stockrecord")+1,
			'fields':fields
		})

	print('saving file')

	fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), './dehy/fixtures'))

	fixture_filename = f'{dt.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'
	fixture_file = os.path.join(fixture_dir, fixture_filename)

	with open(fixture_file, 'w+') as f:
		json.dump(all_fixtures, f, indent=4)

	print(f'successfully dumped file to: {fixture_filename}')

	call_command('loaddata', fixture_file, app_label='dehy')


if __name__ == "__main__":
	main()


