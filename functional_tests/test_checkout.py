from .base import FunctionalTest
from .test_shopping_cart import BasketTestingMixin

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import datetime, random, re, time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC



class CheckoutTest(FunctionalTest, BasketTestingMixin):

	shipping = subtotal = tax = total = 0.00

	def test_user_cannot_checkout_using_other_users_email(self):
		self.add_random_items_to_basket()

		self.wait_for(lambda: self.browser.find_element(By.LINK_TEXT, 'CHECKOUT'))
		checkout_button = self.browser.find_element(By.LINK_TEXT, 'CHECKOUT')
		checkout_button.click()

		self.wait_for(lambda: self.browser.find_element(By.ID, 'id_username'))
		username = self.browser.find_element(By.ID, 'id_username')
		username.click()

		actions = ActionChains(self.browser)
		actions.move_to_element(username)
		actions.click(username)
		actions.send_keys("kjt1987@gmail.com")
		actions.perform()

		# test for an error on the page
		# self.assertNotIn('Buy peacock feathers', page_text)
		# self.assertIn('Buy milk', page_text)

		# test to see if the next form loaded

	def enter_email_address(self):
		self.wait_for(lambda: self.browser.find_element(By.LINK_TEXT, 'CHECKOUT'))
		checkout_button = self.browser.find_element(By.LINK_TEXT, 'CHECKOUT')
		checkout_button.click()

		self.wait_for(lambda: self.browser.find_element(By.ID, 'id_username'))
		username = self.browser.find_element(By.ID, 'id_username')
		username.click()

		actions = ActionChains(self.browser)
		actions.move_to_element(username)
		actions.click(username)
		# actions.send_keys("kjt1987@gmail.cum")
		actions.send_keys("kjt1987@gmail.cum", Keys.ENTER)
		actions.perform()
		self.wait_for(lambda: self.assertNotEqual(self.loading_modal_displayed(), True))

	def enter_shipping_details(self):
		self.wait_for(lambda: self.browser.find_element(By.ID, 'id_first_name'))
		address_fields = {
			'last_name':'McPoople',
			'first_name':'Bobbert',
			'country': 'US',
			'line4': 'AUSTIN',
			'state': 'TX',
			'line1':'11112 Furrow Hill Dr',
			'phone_number': '+13862668079',
			'postcode': '78761',
		}


		for k,v in address_fields.items():
			ajax_keys = ['country', 'postcode', 'line4', 'state']
			time.sleep(0.2)
			self.wait_for(lambda: self.browser.find_element(By.NAME, k))
			elem = self.browser.find_element(By.NAME, k)
			self.assertIsNotNone(elem.location_once_scrolled_into_view)
			time.sleep(0.2)
			actions = ActionChains(self.browser)
			actions.move_to_element(elem)
			actions.pause(0.2)
			actions.click(elem)

			if elem.get_attribute('tagName') == 'SELECT':
				actions.perform()
				select = Select(elem)
				select.select_by_value(v)
			else:
				actions.pause(0.2)
				actions.send_keys(v)
				actions.pause(0.2)
				actions.perform()

			if k=='postcode':
				postcode_loadstart = datetime.datetime.now()

				first_name = self.browser.find_element(By.NAME, 'first_name')
				ActionChains(self.browser).send_keys(Keys.TAB).perform()
				self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '.shipping-method-container'))
				print(f'\n postcode load time --- {datetime.datetime.now() - postcode_loadstart}')


			if k in ajax_keys:
				# we add an extra sleep here since these fields can cause ajax calls to the server
				load_start = datetime.datetime.now()
				# time.sleep(1.5)
				self.wait_for(lambda: self.assertNotEqual(self.loading_modal_displayed(), True))
				print(f'\n load time --- {datetime.datetime.now() - load_start}')
				# add a small buffer
				time.sleep(0.2)




		# check shipping methods loaded
		self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '.shipping-method-container'))

		# check to see if we have at least one shipping method to choose from
		shipping_methods = self.browser.find_elements(By.CSS_SELECTOR, '.shipping-method-option')
		self.assertIs(len(shipping_methods)>0, True)

		# choose a random shipping method and then wait for the page to load
		selected_shipping_method = random.choice(shipping_methods)

		self.assertIsNotNone(selected_shipping_method.location_once_scrolled_into_view)
		actions = ActionChains(self.browser)
		actions.move_by_offset(0, -50)
		actions.pause(0.2)

		actions.move_to_element(selected_shipping_method)
		actions.pause(0.2)
		actions.click(selected_shipping_method)
		actions.pause(0.2)
		actions.perform()

		self.wait_for(lambda: self.assertNotEqual(self.loading_modal_displayed(), True))

		continue_button = self.browser.find_element(By.XPATH, '//button[text()="Continue"]')
		continue_button.click()
		self.wait_for(lambda: self.assertNotEqual(self.loading_modal_displayed(), True))

		return True

	def complete_additional_info_questionnaire(self):
		self.wait_for(lambda: self.browser.find_element(By.ID, 'id_purchase_business_type'))
		purchase_info_elem = self.browser.find_element(By.ID, 'id_purchase_business_type')

		self.assertIsNotNone(purchase_info_elem.location_once_scrolled_into_view)
		purchase_info_elem_selector = Select(purchase_info_elem)

		option = random.choice(purchase_info_elem_selector.options)
		purchase_info_elem_selector.select_by_value(option.get_attribute('value'))

		business_name_elem = self.browser.find_element(By.NAME, 'business_name')
		self.assertIsNotNone(business_name_elem.location_once_scrolled_into_view)
		actions = ActionChains(self.browser)
		actions.move_to_element(business_name_elem)
		actions.pause(0.2)
		actions.click(business_name_elem)
		actions.pause(0.2)
		actions.send_keys("hello")
		actions.pause(0.1)
		actions.send_keys(Keys.ENTER)
		actions.perform()

		business_name_elem.submit()

		self.wait_for(lambda: self.assertNotEqual(self.loading_modal_displayed(), True))

	def enter_billing_details(self):

		self.wait_for(lambda: self.browser.find_element(By.ID, 'billing_form'))
		billing_form = self.browser.find_element(By.ID, 'billing_form')
		time.sleep(0.5)
		self.wait_for(lambda: self.browser.find_element(By.ID, 'stripe_payment_container'))
		stripe_payment_container = self.browser.find_element(By.ID, 'stripe_payment_container')
		time.sleep(0.5)
		self.assertIsNotNone(billing_form.location_once_scrolled_into_view)

		# fill in card info
		actions = ActionChains(self.browser)
		actions.move_to_element(billing_form)
		actions.click(billing_form)
		# actions.pause(0.2)
		# actions.send_keys(Keys.TAB)
		actions.pause(0.5)
		actions.send_keys("4242424242424242", Keys.TAB)
		actions.pause(0.2)
		actions.send_keys("669", Keys.TAB)
		actions.pause(0.2)
		actions.send_keys("420", Keys.TAB)
		actions.pause(0.2)
		actions.perform()



		submit_button = billing_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
		self.assertIsNotNone(submit_button.location_once_scrolled_into_view)

		ActionChains(self.browser).move_to_element(submit_button).pause(0.1).click(submit_button).pause(0.1).perform()
		self.wait_for(lambda: self.assertNotEqual(self.loading_modal_displayed(), True))

	def record_cost_info(self):

		self.wait_for(lambda: self.browser.find_element(By.ID, 'subtotal'))

		self.subtotal = self.browser.find_element(By.ID, 'subtotal').text
		self.tax = self.browser.find_element(By.ID, 'total_tax').text
		self.shipping = self.browser.find_element(By.ID, 'shipping_charge').text
		self.total = self.browser.find_element(By.ID, 'order_total').text

	def place_order(self):
		time.sleep(0.5)
		self.wait_for(lambda: self.browser.find_element(By.ID, 'place_order_form'))
		place_order_form = self.browser.find_element(By.ID, 'place_order_form')
		self.assertIsNotNone(place_order_form.location_once_scrolled_into_view)
		place_order_form.submit()
		time.sleep(1)


	def test_user_can_checkout_as_guest(self):
		print('dir(self.test_user_can_checkout_as_guest): ', dir(self.test_user_can_checkout_as_guest))
		with self.subTest(fn='add_random_items_to_basket'):
			self.add_random_items_to_basket()

		with self.subTest(fn='enter_email_address()'):
			self.enter_email_address()
			self.wait_for(lambda: self.assertNotEqual(self.loading_modal_displayed(), True))
			self.assertEqual(self.browser.find_element(By.ID, 'user_info_form').is_displayed(), False)

		with self.subTest(fn='enter_shipping_details()'):
			time.sleep(0.5)
			self.enter_shipping_details()
			self.wait_for(lambda: self.assertNotEqual(self.loading_modal_displayed(), True))
			self.assertEqual(self.browser.find_element(By.ID, 'shipping_form').is_displayed(), False)

		with self.subTest(fn='complete_additional_info_questionnaire()'):
			self.complete_additional_info_questionnaire()
			self.wait_for(lambda: self.assertNotEqual(self.loading_modal_displayed(), True))
			self.assertEqual(self.browser.find_element(By.ID, 'additional_info_form').is_displayed(), False)

		with self.subTest(fn='enter_billing_details()'):
			time.sleep(0.5)
			self.wait_for(lambda: self.assertNotEqual(self.loading_modal_displayed(), True))
			self.enter_billing_details()
			self.wait_for(lambda: self.assertNotEqual(self.loading_modal_displayed(), True))
			self.assertEqual(self.browser.find_element(By.CSS_SELECTOR, '#billing_form .form-container').is_displayed(), False)

		self.record_cost_info()

		with self.subTest(fn='place_order()'):
			self.place_order()
			self.wait.until(EC.invisibility_of_element(self.browser.find_element(By.ID, 'loading_modal')))
			# self.wait_for(lambda: self.assertNotEqual(self.loading_modal_displayed(), True))
			# self.assertEqual(self.browser.find_element(By.ID, 'user_info_form').is_displayed(), False)


		url = self.browser.current_url
		self.wait.until(EC.url_changes(url))
		self.wait.until(EC.url_contains('thank_you'))










