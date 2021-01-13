from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Review


class UserCreationEmailForm(UserCreationForm):
    email = forms.EmailField()
    username = forms.CharField(max_length=50)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ('username','email','first_name','last_name',)

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email')

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=50, required=True)
    name = forms.CharField(max_length=20, required=True)
    from_email = forms.EmailField(max_length=50, required=True)
    message = forms.CharField(max_length=500,widget=forms.Textarea(),help_text='Write here your message!')

class ReviewEditForm(forms.ModelForm):
    content = forms.CharField(max_length=500,widget=forms.Textarea())
    class Meta:
        model = Review
        fields = ('content',)