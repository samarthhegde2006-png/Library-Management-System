from django import forms
from django.contrib.auth.models import User
from .models import MemberProfile

class MemberRegisterForm(forms.Form):
    ROLE_CHOICES = [('member', 'Library Member'), ('librarian', 'Head Librarian (Admin)')]
    account_role = forms.ChoiceField(choices=ROLE_CHOICES, initial='member', widget=forms.RadioSelect)
    full_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Aarav Sharma'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'aarav_reader'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'aarav@athenaeum.org'}))
    phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': '+91 98765 43210'}))
    department_or_grade = forms.CharField(max_length=100, initial='General Reader', widget=forms.TextInput(attrs={'placeholder': 'Literature / CS / Comic Collector'}))
    password = forms.CharField(min_length=6, widget=forms.PasswordInput(attrs={'placeholder': 'Minimum 6 characters', 'id': 'reg-password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'id': 'reg-confirm-password'}))

    def clean_username(self):
        u = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=u).exists():
            raise forms.ValidationError('Username already exists.')
        return u

    def clean_email(self):
        e = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=e).exists():
            raise forms.ValidationError('Email already registered.')
        return e

    def clean(self):
        cd = super().clean()
        if cd.get('password') != cd.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords do not match.')
        return cd

class MemberLoginForm(forms.Form):
    identifier = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'id': 'login-password'}))
    remember_me = forms.BooleanField(required=False)

class MemberProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = MemberProfile
        fields = ['full_name', 'phone_number', 'department_or_grade', 'avatar', 'bio']
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email
