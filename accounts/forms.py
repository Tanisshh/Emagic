from django import forms
from .models import Accounts, UserProfile

class RegistrationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'confirm Password',
        'class': 'form-control',
    }))
    class Meta:
        model = Accounts
        fields =['first_name', 'last_name', 'email', 'phone_number', 'password']


    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder']= 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder']= 'Enter Last Name'
        for field in self.fields:
            self.fields[field].widget.attrs['class']= 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError(
                "Password Does not Match"
            )
class UserForm(forms.ModelForm):

    class Meta:
        model= Accounts
        fields = ['first_name', 'last_name', 'phone_number']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']= 'form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture=forms.ImageField(required=False, error_messages={'invalid':("Image Files Only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ['address', 'city', 'country', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']= 'form-control'
