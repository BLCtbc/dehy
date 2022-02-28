from oscar.apps.checkout import utils

class CheckoutSessionData(utils.CheckoutSessionData):
	def set_additional_info(self, additional_info):
		self._set('additional_info', 'additional_info_id', additional_info.id)

	def get_additional_info_id(self):
		return self._get('additional_info', 'additional_info_id')

	def is_additional_info_set(self, basket):
		"""
		Test if additional info object id is stored in the session
		"""
		return self.get_additional_info_id() is not None