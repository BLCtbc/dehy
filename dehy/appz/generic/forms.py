from django import forms
from django.utils.translation import gettext_lazy as _
from dehy.appz.generic.models import Message, MessageUser

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

		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'

		self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name'})
		self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name'})
		self.fields['email'].widget.attrs.update({'placeholder': 'Email'})
		self.fields['subject'].widget.attrs.update({'placeholder': 'Subject'})
		self.fields['message'].widget.attrs.update({'placeholder': 'Message'})

# this version saves message and the associated email address to the database
# useful if you want to reference message from admin or dashboard panels...
# will definitely need some form of rate limiting and spam control if we use this version


class MailingListUserForm(forms.ModelForm):
	email = forms.EmailField(required=True, label=_("Email"), error_messages={'unique': _("That email is already on our mailing list!")})

	class Meta:
		model = MessageUser
		fields = ['email']
		# error_messages = {
        #     'email': {
        #         'unique': ,
        #     },
        # }

class ContactFormV2(forms.ModelForm):
	email = forms.EmailField(required=True, label=_("Email"))

	class Meta:
		model = Message
		fields = '__all__'

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


	def clean(self):

		cleaned_data = super().clean()
		email = cleaned_data.get('email')
		message = cleaned_data.get('message')

		if email and message:
			user,_ = MessageUser.objects.get_or_create(email=email, defaults={'email': email})
			if user:
				cleaned_data['email'] = user

		return cleaned_data
