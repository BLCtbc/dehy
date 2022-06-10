# from oscar.apps.order.utils import OrderCreator as CoreOrderCreator
#
# class OrderCreator(CoreOrderCreator):
# 	"""
# 	Places the order by writing out the various models
# 	"""
# 	def create_order_model(self,user,basket,shipping_address,shipping_method,shipping_charge,billing_address,total, order_number, status, request=None, surcharges=None, **extra_order_fields):
# 		order = super().create_order_model(user,basket,shipping_address,shipping_method,shipping_charge,billing_address,total,order_number,status,request=None,surcharges=None,**extra_order_fields)
# 		if order.basket.questionnaire:
# 			order.questionnaire = order.basket.questionnaire
# 			order.save()
#
# 		return order
#
#
