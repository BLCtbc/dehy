
import pandas as pd
import json, os, re
from oscar.core.loading import get_model
from deploy_tools.fixture_creator import FixtureCreator
from oscar.apps.catalogue.models import ProductImage
from django.core.files import File

PartnerClass = get_model('partner', 'Partner')
Product = get_model('catalogue', 'Product')

def main():
	product_images_dir = os.path.abspath(os.path.join(os.path.dirname("__file__"), 'dehy/static/img/product'))

	fc = FixtureCreator(os.path.abspath(os.path.join(os.path.dirname("__file__"), 'deploy_tools/DEHY_productlist.xlsx')))
	df = fc.get_dataframe()

	title = df.at[ix,'title']

	for ix, row in df.iterrows():

		product_image_folder_path = os.path.join(product_images_dir, )
		if not row['category']:
			continue

		title = df.at[ix,'title']
		product_entry = Product.objects.get(title=title, structure='parent')

		if not product_entry:
			continue

		product_image = ProductImage()
		primary_image_path = os.path.abspath(os.path.join(product_images_dir, df.at[ix, 'default_image']))
		image = File(open(primary_image_path, 'rb'))
		product_image.original = image
		image_caption = df.at[ix,'default_image'].replace('.jpg', '').replace('_', ' ').replace('-', ' ').title()
		product_image.caption = image_caption
		product_image.product = product_entry
		product_image.save()

		product_entry.primary_image = product_image
		product_entry.save()

		alt_images = [df.at[ix, x] for x in ['alt_image1', 'alt_image2', 'alt_image3'] if df.at[ix, x]]
		for index, img_name in enumerate(alt_images, start=1):

			product_image = ProductImage()
			primary_image_path = os.path.abspath(os.path.join(product_images_dir, df.at[ix, 'default_image']))
			image = File(open(primary_image_path, 'rb'))
			product_image.original = image
			image_caption = df.at[ix,'default_image'].replace('.jpg', '').replace('_', ' ').replace('-', ' ').title()
			product_image.caption = image_caption
			product_image.product = product_entry
			product_image.display_order = index
			product_image.save()



		## testing ##
		row = df.iloc[0]
		title = df.at[0,'title']
		product_entry = Product.objects.get(title=title, structure='parent')

		alt_images = [df.at[0, x] for x in ['alt_image1', 'alt_image2', 'alt_image3'] if df.at[0, x]]
		for index, img_name in enumerate(alt_images):
			pass
		## end testing ##

		if "," in row['category']:
			row['category'] = row['category'].split(", ")[0]



