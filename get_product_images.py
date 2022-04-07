
import django, json, os, re, tempfile, sys
from oscar.core.loading import get_model
from django.core.files import File
from django.core.files.images import ImageFile

from django.conf import settings
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

# settings.configure()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dehy.settings")
django.setup()

from deploy_tools.fixture_creator import FixtureCreator

Product = get_model('catalogue', 'Product')
ProductImage = get_model('catalogue', 'ProductImage')
caption_re = re.compile(r'([\w\+\-]+)\.jpg$')
brand_name_re = re.compile(r'(DEHY)')
# product_images_dir = os.path.abspath(os.path.join(os.path.dirname("__file__"), 'media/images/p'))

fc = FixtureCreator(os.path.abspath(os.path.join(os.path.dirname("__file__"), 'deploy_tools/DEHY_productlist.xlsx')))
df = fc.get_dataframe()

def main():
	for ix, row in df.iterrows():
		product_image_folder_path = settings.BASE_DIR / 'dehy/static/img/p' / row['group_id']

		if not row['category']:
			continue

		title = df.at[ix,'title']
		product = Product.objects.exclude(structure='child').filter(title=title).first()

		if not product:
			print(f'no product found with title: {title}')
			continue

		media_img_path = settings.BASE_DIR / 'media/images/products' / row['group_id'] / df.at[ix, 'default_image']

		image_links = df.at[ix, "all_image_links"]
		alt_images = [df.at[ix, x] for x in ['alt_image1', 'alt_image2', 'alt_image3'] if df.at[ix, x]]
		print(f'\n number of images: {len(alt_images)}')
		print(f'\n alt_images: {alt_images}')
		for index, img_name in enumerate(alt_images):
			image_path = product_image_folder_path / img_name
			media_img_path = settings.BASE_DIR / 'media/images/products' / row['group_id'] / img_name

			if not os.path.exists(image_path):
				print(f'image: {img_name} not found at: {image_path}')
				continue

			elif os.path.exists(media_img_path):
				## need to add another check here for seeing if the image exists in the database also
				# delete it locally
				os.remove(media_img_path)
				# product.images.all().delete()
				existing_product_image = ProductImage.objects.filter(product_id=product.id, original__contains=img_name)
				if existing_product_image:
					existing_product_image.first().delete()
				# delete it from the database


			lf = tempfile.NamedTemporaryFile(dir='media/images')
			f = open(image_path, 'rb')
			lf.write(f.read())
			image_link = image_links[index-1]

			image = ImageFile(lf)

			product_image = ProductImage()
			product_image.caption = get_image_caption(image_link)
			product_image.product = product
			product_image.original = image
			product_image.display_order = index
			product_image.original.save(name=img_name, content=image)
			product_image.save()

			if index == 0:

				product.primary_image = product_image
				product.save()

			lf.close()
			print(f'saved image: {img_name}')

def get_image_caption(url):
	match = caption_re.search(url)
	if match:
		match = match.group()
		s = brand_name_re.sub('', match)
		s = fc.re.nope.sub(' ', s).strip()
		s = fc.re.repeated.sub(' ', s)
		return s.title()


if __name__ == '__main__':
    main()