import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time
from pathlib import Path

MAX_WAIT = 10
BASE_DIR = Path(__file__).resolve().parent

from django.core.management import call_command
from django.test import TestCase as BaseTestCase

# class TestCase(BaseTestCase):
# 	@classmethod
# 	def setUpClass(cls):
# 		print('setUpClass')
# 		super().setUpClass()
# 		fixture_filename = BASE_DIR / 'fixtures.json'
# 		# call_command('dumpdata', output=fixture_filepath, verbosity=0)
# 		print('loading data')
# 		call_command('loaddata', fixture_filename, verbosity=0)


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
		print('setUp')
		self.browser = webdriver.Chrome(BASE_DIR / 'chromedriver')
		self.browser.maximize_window()
		
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
