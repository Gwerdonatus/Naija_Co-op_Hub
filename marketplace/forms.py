from django import forms
from .models import Product
from .models import SellerProfile


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'image', 'category']




from django import forms
from .models import SellerProfile

BANK_CHOICES = [
    ("044", "Access Bank Nigeria Plc"),
    ("050", "Ecobank Nigeria"),
    ("084", "Enterprise Bank Plc"),
    ("070", "Fidelity Bank Plc"),
    ("011", "First Bank of Nigeria Plc"),
    ("214", "First City Monument Bank"),
    ("058", "Guaranty Trust Bank Plc"),
    ("301", "Jaiz Bank"),
    ("082", "Keystone Bank Ltd"),
    ("014", "Mainstreet Bank Plc"),
    ("076", "Skye Bank Plc"),
    ("039", "Stanbic IBTC Plc"),
    ("232", "Sterling Bank Plc"),
    ("032", "Union Bank Nigeria Plc"),
    ("033", "United Bank for Africa Plc"),
    ("215", "Unity Bank Plc"),
    ("035", "WEMA Bank Plc"),
    ("057", "Zenith Bank International"),
    ("101", "Providus Bank"),
    ("104", "PARALLEX BANK LIMITED"),
    ("303", "LOTUS BANK LIMITED"),
    ("105", "PREMIUM TRUST BANK LTD"),
    ("106", "SIGNATURE BANK LTD"),
    ("103", "GLOBUS BANK"),
    ("102", "TITAN TRUST BANK"),
    ("067", "Polaris Bank"),
    ("107", "OPTIMUS BANK LTD"),
    ("068", "Standard Chartered Bank"),
    ("100", "Suntrust Bank"),
]

class SellerProfileForm(forms.ModelForm):
    # Replace the free-text bank_name with a ChoiceField returning the bank code.
    bank_name = forms.ChoiceField(choices=BANK_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = SellerProfile
        fields = [
            'business_name', 
            'bank_name',          
            'account_number', 
            'account_holder_name'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'account_holder_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
