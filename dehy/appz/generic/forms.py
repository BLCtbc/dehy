from django import forms
from django.utils.translation import gettext_lazy as _

class ContactForm(forms.Form):
	email = forms.EmailField(required=True, label=_("Email"))
	first_name = forms.CharField(required=False, label=_('First Name'))
	last_name = forms.CharField(required=False, label=_('Last Name'))
	message = forms.CharField(required=True, label=_('Message'), widget=forms.Textarea(attrs={'cols': 40, 'rows': 10}))

	class Meta:
		fields = [
			'first_name', 'last_name', 'email',
			'message',
		]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		print(dir(self))
		# for field in self.fields:
		# 	field.widget.attrs.update()
		#
		# 	self.fields['ingredients'].widget.attrs.update({'placeholder': 'special'})
		self.fields['email'].widget.attrs.update({'placeholder': 'Email'})
		self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name'})
		self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name'})
		self.fields['message'].widget.attrs.update({'placeholder': 'Message'})

	def send_email(self):
		# send email using the self.cleaned_data dictionary
		pass