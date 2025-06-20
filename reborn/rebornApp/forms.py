# rebornApp/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, Seller, Buyer, Item, Rating
from .factories import UserFactory

class CustomUserCreationForm(UserCreationForm):
    # Define registration role choices (excluding admin)
    REGISTRATION_ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    role = forms.ChoiceField(
        choices=REGISTRATION_ROLE_CHOICES,  # Changed from User.USER_ROLES to filtered choices
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already in use.")
        return email

    def clean_role(self):
        """Prevent admin registration even if form is tampered with"""
        role = self.cleaned_data.get('role')
        if role == 'admin':
            raise ValidationError("Admin registration is not allowed through this form.")
        return role

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Cannot create user with commit=False")

        user = UserFactory.create_user(
            role=self.cleaned_data['role'],
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password2']
        )
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'price', 'condition', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Item title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your item...'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Price in Malaysia Ringgit'
            }),
            'condition': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError("Price must be greater than zero.")
        return price

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['store_name', 'phone_number', 'bio']
        widgets = {
            'store_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your store name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact number'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tell buyers about yourself...'
            }),
        }

class CheckoutForm(forms.Form):
    """
    Form for collecting shipping and payment information during checkout.
    """
    PAYMENT_CHOICES = (
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
    )
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 3,
        'placeholder': 'Your shipping address'
    }))
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.RadioSelect)
    
    credit_card_number = forms.CharField(max_length=16, required=False, widget=forms.TextInput(attrs={'placeholder': '16-digit card number'}))
    paypal_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'placeholder': 'your@paypal.email'}))

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get("payment_method")

        if payment_method == 'credit_card' and not cleaned_data.get('credit_card_number'):
            self.add_error('credit_card_number', 'This field is required for credit card payments.')
        
        if payment_method == 'paypal' and not cleaned_data.get('paypal_email'):
            self.add_error('paypal_email', 'This field is required for PayPal payments.')

        return cleaned_data

class RatingForm(forms.ModelForm):
    """
    Form for a buyer to rate a seller for a specific order.
    """
    class Meta:
        model = Rating
        fields = ['score', 'comment']
        widgets = {
            'score': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)], attrs={
                'class': 'form-control'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Leave a comment (optional)'
            }),
        }