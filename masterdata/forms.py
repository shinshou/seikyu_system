from django import forms
from django.core.validators import MinValueValidator
from django.forms import ModelForm
from .models import (
    Customer, Hall, Sender, Product, Document,
    PersonInCharge,InventoryProduct, INPUT_FORMATS,
)
import datetime


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'


class HallForm(ModelForm):
    class Meta:
        model = Hall
        fields = '__all__'


class SenderForm(ModelForm):
    class Meta:
        model = Sender
        fields = '__all__'


class ProductForm(ModelForm):
    purchase_date = forms.DateField(input_formats=INPUT_FORMATS, required=False)
    class Meta:
        model = Product
        fields = '__all__'

    def save(self, commit=True):
        product = super().save(commit=commit)

        now = datetime.datetime.now()

        # Productが保存された後、InventoryProductを作成または更新
        InventoryProduct.objects.update_or_create(
            product=product,
            defaults={
                'updated_date': now,
                'quantity': 0,  # 初期値として0を設定
                'price': 0,    # 初期値として0を設定
            }
        )


class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = '__all__'


class PersonInChargeForm(ModelForm):
    class Meta:
        model = PersonInCharge
        fields = '__all__'

class InventoryProductForm(ModelForm):
    quantity = forms.IntegerField(
        validators=[MinValueValidator(0)],  # 数量は0以上の整数
        required=True 
    )
    
    class Meta:
        model = InventoryProduct
        fields = ['quantity']