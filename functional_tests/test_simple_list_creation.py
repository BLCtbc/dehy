from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import random, re
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

		self.browser.get(product_link.href)
		
		self.wait_for(lambda: self.browser.find_element_by_css_selector('select#size_selector'))
		product_info['url'] = self.browser.current_url
		product_info['name'] = self.browser.find_element_by_css_selector('div.product_main h1')

		size_selector = self.browser.find_element_by_css_selector('select#size_selector')
		options = size_selector.find_elements_by_css_selector('option')
		selected_option = options[random.choice(1, len(size_selector.find_elements_by_css_selector('option')))]
		product_info['variant'] = selected_option.text
		selected_option.click()

		product_info['price'] = self.browser.find_element_by_css_selector('span.variant_price')
		add_to_cart =  self.browser.find_element_by_css_selector("button[type='submit']")
		add_to_cart.click()

		# click cart container
		cart_container = self.browser.find_element_by_css_selector("div.cart-container")
		cart_container.click()

		# wait for checkout button to be visible on page
		self.wait_for(lambda: self.browser.find_element_by_link_text('Proceed to checkout'))
		checkout_button = self.browser.find_element_by_link_text('Proceed to checkout')

		# make sure item is on page using gathered info

		# proceed to checkout

	def test_can_user_can_checkout_as_guest(self):

		self.test_can_add_random_items_to_basket()


#
# class NewVisitorTest(FunctionalTest):
#
#     def test_can_start_a_list_for_one_user(self):
#         # Edith has heard about a cool new online to-do app. She goes
#         # to check out its homepage
#         self.browser.get(self.live_server_url)
#
#         # She notices the page title and header mention to-do lists
#         self.assertIn('To-Do', self.browser.title)
#         header_text = self.browser.find_element_by_tag_name('h1').text
#         self.assertIn('To-Do', header_text)
#
#         # She is invited to enter a to-do item straight away
#         inputbox = self.browser.find_element_by_id('id_new_item')
#         self.assertEqual(
#             inputbox.get_attribute('placeholder'),
#             'Enter a to-do item'
#         )
#
#         # She types "Buy peacock feathers" into a text box (Edith's hobby
#         # is tying fly-fishing lures)
#         inputbox.send_keys('Buy peacock feathers')
#
#         # When she hits enter, the page updates, and now the page lists
#         # "1: Buy peacock feathers" as an item in a to-do list table
#         inputbox.send_keys(Keys.ENTER)
#         self.wait_for_row_in_list_table('1: Buy peacock feathers')
#
#         # There is still a text box inviting her to add another item. She
#         # enters "Use peacock feathers to make a fly" (Edith is very
#         # methodical)
#         inputbox = self.browser.find_element_by_id('id_new_item')
#         inputbox.send_keys('Use peacock feathers to make a fly')
#         inputbox.send_keys(Keys.ENTER)
#
#         # The page updates again, and now shows both items on her list
#         self.wait_for_row_in_list_table('2: Use peacock feathers to make a fly')
#         self.wait_for_row_in_list_table('1: Buy peacock feathers')
#
#         # Satisfied, she goes back to sleep
#
#
#     def test_multiple_users_can_start_lists_at_different_urls(self):
#         # Edith starts a new to-do list
#         self.browser.get(self.live_server_url)
#         inputbox = self.browser.find_element_by_id('id_new_item')
#
#         inputbox.send_keys('Buy peacock feathers')
#         inputbox.send_keys(Keys.ENTER)
#         self.wait_for_row_in_list_table('1: Buy peacock feathers')
#
#         # She notices that her list has a unique URL
#         edith_list_url = self.browser.current_url
#         self.assertRegex(edith_list_url, '/lists/.+')
#
#         # Now a new user, Francis, comes along to the site.
#
#         ## We use a new browser session to make sure that no information
#         ## of Edith's is coming through from cookies etc
#         self.browser.quit()
#         self.browser = webdriver.Firefox()
#
#         # Francis visits the home page.  There is no sign of Edith's
#         # list
#         self.browser.get(self.live_server_url)
#         page_text = self.browser.find_element_by_tag_name('body').text
#         self.assertNotIn('Buy peacock feathers', page_text)
#         self.assertNotIn('make a fly', page_text)
#
#         # Francis starts a new list by entering a new item. He
#         # is less interesting than Edith...
#         inputbox = self.browser.find_element_by_id('id_new_item')
#         inputbox.send_keys('Buy milk')
#         inputbox.send_keys(Keys.ENTER)
#         self.wait_for_row_in_list_table('1: Buy milk')
#
#         # Francis gets his own unique URL
#         francis_list_url = self.browser.current_url
#         self.assertRegex(francis_list_url, '/lists/.+')
#         self.assertNotEqual(francis_list_url, edith_list_url)
#
#         # Again, there is no trace of Edith's list
#         page_text = self.browser.find_element_by_tag_name('body').text
#         self.assertNotIn('Buy peacock feathers', page_text)
#         self.assertIn('Buy milk', page_text)
#
#         # Satisfied, they both go back to sleep
#

