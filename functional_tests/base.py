

import os, random, sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time
from pathlib import Path
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from django.test.testcases import SerializeMixin

MAX_WAIT = 10
BASE_DIR = Path(__file__).resolve().parent


from django.core.management import call_command
from django.test import TestCase as BaseTestCase


class FunctionalTest(StaticLiveServerTestCase):
	fixtures = [BASE_DIR / 'fixtures.json']
	# @classmethod
	# def setUpTestData(cls):
	#

	# @classmethod
	# def setUpClass(cls):
	# 	print('setUpClass')
	# 	super().setUpClass()
	# 	fixture_filename = BASE_DIR / 'fixtures.json'
	# 	# call_command('dumpdata', output=fixture_filepath, verbosity=0)
	# 	print('loading data')
	# 	call_command('loaddata', fixture_filename, verbosity=0)


	def setUp(self):
		self.browser = webdriver.Chrome(BASE_DIR / 'chromedriver')
		self.browser.maximize_window()
		self.wait = WebDriverWait(self.browser, 10)

		staging_server = os.environ.get('STAGING_SERVER')
		if staging_server:
			self.live_server_url = 'http://' + staging_server


	def tearDown(self):
		self.browser.quit()

	def wait_for(self, fn):
		start_time = time.time()
		while True:
			try:
				return fn()
			except (AssertionError, WebDriverException) as e:
				if time.time() - start_time > MAX_WAIT:
					raise e
				time.sleep(0.5)



	def wait_for_row_in_list_table(self, row_text):
		start_time = time.time()
		while True:
			try:
				table = self.browser.find_element_by_id('id_list_table')
				rows = table.find_elements_by_tag_name('tr')
				self.assertIn(row_text, [row.text for row in rows])
				return
			except (AssertionError, WebDriverException) as e:
				if time.time() - start_time > MAX_WAIT:
					raise e
				time.sleep(0.5)



class BasketTestingMixin(FunctionalTest, SerializeMixin):
	lockfile = __file__

	def setUp(self):
		super().setUp()
		self.add_random_items_to_basket()


	def loading_modal_displayed(self):
		return lambda: self.browser.find_element(By.ID, 'loading_modal').is_displayed()

	def add_random_items_to_basket(self):
		product_info = {'url':'', 'name':'', 'price':None, 'variant':None}
		self.browser.get(self.live_server_url)

		# wait for shop link, then click it
		self.wait_for(lambda: self.browser.find_element(By.LINK_TEXT, 'Shop'))
		shop_link = self.browser.find_element(By.LINK_TEXT, 'Shop')
		shop_link.click()

		# wait for the pagination container
		self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, 'div.pagination-container'))

		products = self.browser.find_elements(By.CSS_SELECTOR, 'section.product-info')
		product = random.choice(products)
		product_link = product.find_element(By.TAG_NAME, "a")

		href = product_link.get_attribute('href')
		self.browser.get(href)

		self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, 'select#size_selector'))
		product_info['url'] = self.browser.current_url
		product_info['name'] = self.browser.find_element(By.CSS_SELECTOR, 'div.product_main h1')

		size_selector = self.browser.find_element(By.CSS_SELECTOR, 'select#size_selector')
		options = size_selector.find_elements(By.CSS_SELECTOR, 'option')

		selected_option = options[random.randint(1, len(size_selector.find_elements(By.CSS_SELECTOR, 'option'))-1)]

		product_info['variant'] = selected_option.text
		selected_option.click()

		product_info['price'] = self.browser.find_element(By.CSS_SELECTOR, 'span.variant_price')
		add_to_cart =  self.browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
		add_to_cart.click()
		# add an explicit wait since this is an ajax function
		time.sleep(0.5)

		# click cart container
		cart_container = self.browser.find_element(By.CSS_SELECTOR, "div.cart-container")
		cart_container.click()

		# wait for checkout button to be visible on page
		self.wait_for(lambda: self.browser.find_element(By.LINK_TEXT, 'CHECKOUT'))
		checkout_button = self.browser.find_element(By.LINK_TEXT, 'CHECKOUT')

		# NOTE: add a check that:
		# makes sure item is on page using gathered info