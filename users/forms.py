from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User


def normalize_iin(value):
    return ''.join(char for char in (value or '') if char.isdigit())


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (___) ___-__-__'})
    )
    iin = forms.CharField(
        max_length=12,
        required=True,
        label='ИИН',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12 цифр',
            'inputmode': 'numeric',
            'maxlength': '12',
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'iin', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

        self.fields['username'].widget.attrs.update({'placeholder': 'Логин'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Пароль'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Подтвердите пароль'})

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = ''.join(char for char in phone if char.isdigit() or char == '+')
            if not phone.startswith('+'):
                phone = '+7' + phone.lstrip('8').lstrip('7')
        return phone

    def clean_iin(self):
        iin = normalize_iin(self.cleaned_data.get('iin'))
        if len(iin) != 12:
            raise ValidationError('ИИН должен содержать 12 цифр')
        if User.objects.filter(iin=iin).exists():
            raise ValidationError('Пользователь с таким ИИН уже зарегистрирован')
        return iin

    def save(self, commit=True):
        user = super().save(commit=False)
        user.iin = self.cleaned_data['iin']
        if commit:
            user.save()
        return user
