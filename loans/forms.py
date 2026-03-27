from django import forms
from django.contrib.auth.models import User
from .models import LoanApplication, UserProfile, OCCUPATION_CHOICES, LOAN_AMOUNT_CHOICES, DURATION_CHOICES, LOAN_PURPOSE_CHOICES, PAYMENT_METHOD_CHOICES


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'আপনার ইউজার নেম লিখুন', 'class': 'form-input'})
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'placeholder': '01XXXXXXXXX', 'class': 'form-input'})
    )
    occupation = forms.ChoiceField(
        choices=OCCUPATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'পাসওয়ার্ড দিন', 'class': 'form-input'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'পাসওয়ার্ড পুনরায় লিখুন', 'class': 'form-input'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('এই ইউজার নেমটি ইতিমধ্যে ব্যবহৃত হয়েছে।')
        return username

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if UserProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError('এই নম্বরটি ইতিমধ্যে নিবন্ধিত।')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('পাসওয়ার্ড মিলছে না।')
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'ইউজার নেম লিখুন', 'class': 'form-input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'পাসওয়ার্ড দিন', 'class': 'form-input'})
    )


class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['applicant_name', 'amount', 'duration_months', 'purpose']
        widgets = {
            'applicant_name': forms.TextInput(attrs={'placeholder': 'Enter your name', 'class': 'form-input'}),
            'amount': forms.Select(attrs={'class': 'form-input'}),
            'duration_months': forms.Select(attrs={'class': 'form-input'}),
            'purpose': forms.Select(attrs={'class': 'form-input'}),
        }
        labels = {
            'applicant_name': 'আপনার নাম:',
            'amount': 'লোনের পরিমাণ:',
            'duration_months': 'মেয়াদ (মাস):',
            'purpose': 'লোনের কারণ:',
        }


class NIDUploadForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['nid_front', 'nid_back']
        widgets = {
            'nid_front': forms.FileInput(attrs={'accept': 'image/*', 'class': 'nid-input'}),
            'nid_back': forms.FileInput(attrs={'accept': 'image/*', 'class': 'nid-input'}),
        }


class WithdrawForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'payment-radio'})
    )
    amount = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'টাকা লিখুন', 'class': 'form-input'})
    )
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'আপনার নাম্বার লিখুন', 'class': 'form-input'})
    )


class PasswordChangeForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'নতুন পাসওয়ার্ড লিখুন', 'class': 'form-input'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'পুনরায় পাসওয়ার্ড লিখুন', 'class': 'form-input'})
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password')
        p2 = cleaned.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('পাসওয়ার্ড মিলছে না।')
        return cleaned
