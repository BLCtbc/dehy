from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import datetime, random, re, time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select

class BasketTestingMixin(object):

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

		# go to a random page:
		# page_number = 1
		# pagination_container = self.browser.find_element(By.CSS_SELECTOR, 'div.pagination-container')
		# pages_str = pagination_container.find_element(By.CSS_SELECTOR, 'span.page-link').text
		#
		# myre = re.compile('Page (?P<page1>\d+) of (?P<page2>\d+)')
		# match = myre.search(pages_str)
		# if match:
		# 	page_number = random.randint(int(match.groupdict()['page1']), int(match.groupdict()['page2']))
		#
		# self.browser.get(f"{self.browser.current_url}?page={page_number}")
		# self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, 'div.brand-logo.image-container'))

		products = self.browser.find_elements(By.CSS_SELECTOR, 'section.product-info')
		product = random.choice(products)
		product_link = product.find_element(By.TAG_NAME, "a")

		# actions = ActionChains(self.browser)
		# actions.move_to_element(product_link)
		# actions.click(product_link)
		# actions.perform()
		#
		# print(f'\nproduct_link.rect: {product_link.rect}')
		# print(f'\nproduct_link.location: {product_link.rect}')
		# print(f'\nproduct_link.location_once_scrolled_into_view: {product_link.location_once_scrolled_into_view}')

		# product_link.click()
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

class NewShoppingCartTest(FunctionalTest, BasketTestingMixin):

	def test_can_add_random_items_to_basket(self):
		self.add_random_items_to_basket()
