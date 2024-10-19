from django import forms
from .models import Product,Category

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class ProductForm(forms.ModelForm):
    images = MultipleFileField()

    class Meta:
        model = Product
        fields = ["name", "description", "category","price", "stock", "category", "images", "available"]

class CategoryForm(forms.ModelForm):
    base_choices = [
        ("Mens Clothing", "Men's Clothing"),
        ("Womens Clothing", "Women's Clothing"),
        ("Kids Clothing", "Kids' Clothing"),
        ("Unisex Clothing", "Unisex Clothing"),
    ]
    choices=forms.MultipleChoiceField(choices=base_choices,required=True,widget=forms.CheckboxSelectMultiple())
    class Meta:
        model=Category
        fields=["name","choices"]