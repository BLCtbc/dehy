from django import forms
from django.utils.translation import gettext_lazy as _

class ContactForm(forms.Form):
	email = forms.EmailField(required=True, label=_("Email"))
	subject = forms.CharField(required=False, label=_('Subject'), help_text=_("What is the nature if your inquiry?"))
	first_name = forms.CharField(required=False, label=_('First Name'))
	last_name = forms.CharField(required=False, label=_('Last Name'))
	message = forms.CharField(required=True, label=_('Message'), widget=forms.Textarea(attrs={'cols': 30, 'rows': 4}))

	class Meta:
		fields = [
			'first_name', 'last_name', 'email', 'subject',
			'message',
		]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# for field in self.fields:
		# 	field.widget.attrs.update()
		#
		# 	self.fields['ingredients'].widget.attrs.update({'placeholder': 'special'})
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'

		self.fields['email'].widget.attrs.update({'placeholder': 'Email'})
		self.fields['subject'].widget.attrs.update({'placeholder': 'Subject'})

		self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name'})
		self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name'})
		self.fields['message'].widget.attrs.update({'placeholder': 'Message'})

	def send_email(self):
		# send email using the self.cleaned_data dictionary
		pass