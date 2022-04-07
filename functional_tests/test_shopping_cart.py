
from .base import BasketTestingMixin, FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import datetime, random, re, time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select


class NewShoppingCartTest(FunctionalTest, BasketTestingMixin):

	def test_can_add_random_items_to_basket(self):
		self.add_random_items_to_basket()
