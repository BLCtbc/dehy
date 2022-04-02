from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import random, re, time
from selenium.webdriver.common.action_chains import ActionChains

class NewShoppingCartTest(FunctionalTest):

	def test_can_add_random_items_to_basket(self):
		product_info = {'url':'', 'name':'', 'price':None, 'variant':None}
		self.browser.get(self.live_server_url)

		# wait for shop link, then click it
		self.wait_for(lambda: self.browser.find_element_by_link_text('Shop'))
		shop_link = self.browser.find_element_by_link_text('Shop')
		shop_link.click()

		# wait for the pagination container
		self.wait_for(lambda: self.browser.find_element_by_css_selector('div.pagination-container'))

		# go to a random page:
		# page_number = 1
		# pagination_container = self.browser.find_element_by_css_selector('div.pagination-container')
		# pages_str = pagination_container.find_element_by_css_selector('span.page-link').text
		#
		# myre = re.compile('Page (?P<page1>\d+) of (?P<page2>\d+)')
		# match = myre.search(pages_str)
		# if match:
		# 	page_number = random.randint(int(match.groupdict()['page1']), int(match.groupdict()['page2']))
		#
		# self.browser.get(f"{self.browser.current_url}?page={page_number}")
		# self.wait_for(lambda: self.browser.find_element_by_css_selector('div.brand-logo.image-container'))

		products = self.browser.find_elements_by_css_selector('section.product-info')
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

		self.wait_for(lambda: self.browser.find_element_by_css_selector('select#size_selector'))
		product_info['url'] = self.browser.current_url
		product_info['name'] = self.browser.find_element_by_css_selector('div.product_main h1')

		size_selector = self.browser.find_element_by_css_selector('select#size_selector')
		options = size_selector.find_elements_by_css_selector('option')

		selected_option = options[random.randint(1, len(size_selector.find_elements_by_css_selector('option')))]

		product_info['variant'] = selected_option.text
		selected_option.click()

		product_info['price'] = self.browser.find_element_by_css_selector('span.variant_price')
		add_to_cart =  self.browser.find_element_by_css_selector("button[type='submit']")
		add_to_cart.click()
		# add an explicit wait since this is an ajax function
		time.sleep(0.5)

		# click cart container
		cart_container = self.browser.find_element_by_css_selector("div.cart-container")
		cart_container.click()

		# wait for checkout button to be visible on page
		self.wait_for(lambda: self.browser.find_element_by_link_text('CHECKOUT'))
		checkout_button = self.browser.find_element_by_link_text('CHECKOUT')

		# NOTE: add a check that:
		# makes sure item is on page using gathered info

		# proceed to checkout

	def test_can_user_can_checkout_as_guest(self):
		self.test_can_add_random_items_to_basket()
