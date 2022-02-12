# from oscar.apps.basket.views import BasketView as CoreBasketView

# class BasketView(CoreBasketView):
# 	template_name = 'basket/basket.html'
#
# 	def formset_valid(self, formset):
# 		# Store offers before any changes are made so we can inform the user of
# 		# any changes
# 		offers_before = self.request.basket.applied_offers()
# 		save_for_later = False
#
# 		# Keep a list of messages - we don't immediately call
# 		# django.contrib.messages as we may be returning an AJAX response in
# 		# which case we pass the messages back in a JSON payload.
# 		flash_messages = ajax.FlashMessages()
#
# 		for form in formset:
# 		    if (hasattr(form, 'cleaned_data')
# 		            and form.cleaned_data.get('save_for_later', False)):
# 		        line = form.instance
# 		        if self.request.user.is_authenticated:
# 		            self.move_line_to_saved_basket(line)
#
# 		            msg = render_to_string(
# 		                'basket/messages/line_saved.html',
# 		                {'line': line})
# 		            flash_messages.info(msg)
#
# 		            save_for_later = True
# 		        else:
# 		            msg = _("You can't save an item for later if you're "
# 		                    "not logged in!")
# 		            flash_messages.error(msg)
# 		            return redirect(self.get_success_url())
#
# 		if save_for_later:
# 		    # No need to call super if we're moving lines to the saved basket
# 		    response = redirect(self.get_success_url())
# 		else:
# 		    # Save changes to basket as per normal
# 		    response = super().formset_valid(formset)