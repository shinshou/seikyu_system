from django import forms
from django.forms import formset_factory, BaseFormSet
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from masterdata.models import (
    Product, InventoryProduct, Document, Sender, DocumentFee,
    CATEGORY_CHOICES, INPUT_FORMATS, PRODUCT_TYPE_CHOICES, SHIPPING_METHOD_CHOICES, PAYMENT_METHOD_CHOICES,
)
from .models import (
    TraderSalesContract, TraderPurchasesContract, HallSalesContract, HallPurchasesContract,
    TraderSalesSender, TraderPurchasesSender,
    ContractProduct, ContractDocument, ContractDocumentFee, Milestone,
    InvoiceContract, EstimateContract, DeliveryContract 
)
from .stripe import create_stripe_item
from .utilities import (generate_contract_id, generate_invoice_id)


# Common Forms like Product, Document and Insurance Fee
class ProductForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'true'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'true'}))
    tax = forms.IntegerField(widget=forms.HiddenInput(attrs={'disabled': 'disabled'}), required=False)
    amount = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('invoice_id'):
            self.invoice_id = kwargs.pop('invoice_id')
        if kwargs.get('invoice_class'):
            self.invoice_class = kwargs.pop('invoice_class')
        super().__init__(*args, **kwargs)
    
    def save(self):
        id = self.cleaned_data.get('id')
        if id:
            contract_product = ContractProduct.objects.get(id=id)
            contract_product.quantity = self.cleaned_data.get('quantity')
            contract_product.price = self.cleaned_data.get('price')
            contract_product.save()
        else:
            print(self.cleaned_data.get('product_id'))
            contract_class_name = ContentType.objects.get(model=self.invoice_class)
            contract_class = contract_class_name.model_class()
            contract = contract_class.objects.get(id=self.invoice_id)
            product = Product.objects.get(id=self.cleaned_data.get('product_id'))
            data = {
                'quantity': self.cleaned_data.get('quantity'),
                'price': self.cleaned_data.get('price'),
                'product': product,
                'content_object': contract,
            }
            ContractProduct.objects.create(**data)


class DocumentForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    document_id = forms.IntegerField(widget=forms.HiddenInput())
    taxable = forms.IntegerField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    quantity = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'true'}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'true'}))
    tax = forms.IntegerField(widget=forms.HiddenInput(attrs={'disabled': 'disabled'}), required=False)
    amount = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('invoice_id'):
            self.invoice_id = kwargs.pop('invoice_id')
        if kwargs.get('invoice_class'):
            self.invoice_class = kwargs.pop('invoice_class')
        super().__init__(*args, **kwargs)
    
    def save(self):
        id = self.cleaned_data.get('id')
        if id:
            contract_document = ContractDocument.objects.get(id=id)
            contract_document.quantity = self.cleaned_data.get('quantity')
            contract_document.price = self.cleaned_data.get('price')
            contract_document.save()
        else:
            contract_class_name = ContentType.objects.get(model=self.invoice_class)
            invoice_class = contract_class_name.model_class()
            contract = invoice_class.objects.get(id=self.invoice_id)
            document = Document.objects.get(id=self.cleaned_data.get('document_id'))
            data = {
                'quantity': self.cleaned_data.get('quantity'),
                'price': self.cleaned_data.get('price'),
                'document': document,
                'content_object': contract,
            }
            ContractDocument.objects.create(**data)


class DocumentFeeForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    document_fee_id = forms.IntegerField(widget=forms.HiddenInput())
    model_price = forms.IntegerField(widget=forms.HiddenInput())
    unit_price = forms.IntegerField(widget=forms.HiddenInput())
    application_fee = forms.IntegerField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    model_count = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'true'}))
    unit_count = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'true'}))
    tax = forms.IntegerField(widget=forms.HiddenInput(attrs={'disabled': 'disabled'}), required=False)
    amount = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id'):
            self.contract_id = kwargs.pop('contract_id')
        if kwargs.get('contract_class'):
            self.contract_class = kwargs.pop('contract_class')
        super().__init__(*args, **kwargs)
    
    def save(self):
        id = self.cleaned_data.get('id')
        if id:
            contract_document_fee = ContractDocumentFee.objects.get(id=id)
            contract_document_fee.model_count = self.cleaned_data.get('model_count')
            contract_document_fee.unit_count = self.cleaned_data.get('unit_count')
            contract_document_fee.save()
        else:
            contract_class_name = ContentType.objects.get(model=self.contract_class)
            contract_class = contract_class_name.model_class()
            contract = contract_class.objects.get(id=self.contract_id)
            document_fee = DocumentFee.objects.get(id=self.cleaned_data.get('document_fee_id'))
            data = {
                'model_count': self.cleaned_data.get('model_count'),
                'unit_count': self.cleaned_data.get('unit_count'),
                'document_fee': document_fee,
                'content_object': contract,
            }
            ContractDocumentFee.objects.create(**data)


class MilestoneForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control datepicker-nullable'}),
        input_formats=INPUT_FORMATS,
        required=False
    )
    amount = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id'):
            self.contract_id = kwargs.pop('contract_id')
        if kwargs.get('contract_class'):
            self.contract_class = kwargs.pop('contract_class')
        super().__init__(*args, **kwargs)
    
    def clean_date(self):
        data = self.cleaned_data['date']
        return data
    
    def save(self, amount = None, shipping_date = None):
        id = self.cleaned_data.get('id')
        if id:
            milestone = Milestone.objects.get(id=id)
            milestone.date = self.cleaned_data.get('date') if self.cleaned_data.get('date') else shipping_date
            milestone.amount = self.cleaned_data.get('amount') if self.cleaned_data.get('amount') else amount
            milestone.save()
        else:
            contract_class_name = ContentType.objects.get(model=self.contract_class)
            contract_class = contract_class_name.model_class()
            contract = contract_class.objects.get(id=self.contract_id)
            data = {
                'date': self.cleaned_data.get('date') if self.cleaned_data.get('date') else shipping_date,
                'amount': self.cleaned_data.get('amount') if self.cleaned_data.get('amount') else amount,
                'content_object': contract,
            }
            Milestone.objects.create(**data)
# shipping_date if shipping_date else cleaned_data.get('shipping_date')

class ItemValidationFormSet(BaseFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        invoice_id = kwargs.get('invoice_id')
        invoice_class = kwargs.get('invoice_class')
        
        data = {}
        if invoice_id:
            data['invoice_id'] = invoice_id
        if invoice_class:
            data['invoice_class'] = invoice_class
        return data


class DocumentFeeValidationFormSet(BaseFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        contract_id = kwargs.get('contract_id')
        contract_class = kwargs.get('contract_class')
        
        data = {}
        if contract_id:
            data['contract_id'] = contract_id
        if contract_class:
            data['contract_class'] = contract_class
        return data


class MilestoneValidationFormSet(BaseFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        contract_id = kwargs.get('contract_id')
        contract_class = kwargs.get('contract_class')
        
        data = {}
        if contract_id:
            data['contract_id'] = contract_id
        if contract_class:
            data['contract_class'] = contract_class
        return data


ProductFormSet = formset_factory(ProductForm, formset=ItemValidationFormSet, extra=0)
DocumentFormSet = formset_factory(DocumentForm, formset=ItemValidationFormSet, extra=0)
DocumentFeeFormSet = formset_factory(DocumentFeeForm, formset=DocumentFeeValidationFormSet, extra=0)
MilestoneFormSet = formset_factory(MilestoneForm, formset=MilestoneValidationFormSet, min_num=5, validate_min=True, extra=0)
# End of Common Forms


#===================================#
# Trader Sales Forms
class TraderSalesContractForm(forms.Form):
    contract_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}))
    created_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    updated_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    customer_id = forms.IntegerField(required=False)
    customer_name = forms.CharField(required=False)
    manager = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    frigana = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    postal_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    fax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    person_in_charge = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control person_in_charge'}), required=False)
    remarks = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-140-px'}), required=False)
    sub_total = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    tax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    fee = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), initial=0)
    total = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=True)
    billing_amount = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), initial=0, required=False)
    shipping_method = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices=SHIPPING_METHOD_CHOICES, required=False)
    shipping_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS, required=False)
    payment_method = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices=PAYMENT_METHOD_CHOICES)
    payment_due_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS, required=False)
    memo = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-112-px'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('id'):
            self.id = kwargs.pop('id')
        else:
            self.id = None
        super().__init__(*args, **kwargs)
        self.fields['contract_id'].initial = generate_contract_id('01')

    def save(self):
        if self.id:
            contract = TraderSalesContract.objects.get(id=self.id)
            cleaned_data = self.cleaned_data
            contract.created_at = cleaned_data.get('created_at')
            contract.updated_at = cleaned_data.get('updated_at')
            contract.customer_id = cleaned_data.get('customer_id')
            contract.manager = cleaned_data.get('manager')
            contract.person_in_charge = cleaned_data.get('person_in_charge')
            contract.remarks = cleaned_data.get('remarks')
            contract.shipping_date = cleaned_data.get('shipping_date')
            contract.fee = int(cleaned_data.get('fee').replace(',', ''))
            contract.shipping_method = cleaned_data.get('shipping_method')
            contract.payment_method = cleaned_data.get('payment_method')
            contract.payment_due_date = cleaned_data.get('payment_due_date')
            contract.memo = cleaned_data.get('memo')
            contract.save()
            return contract
        else:
            cleaned_data = self.cleaned_data
            contract_data = {
                'contract_id': cleaned_data.get('contract_id'),
                'created_at': cleaned_data.get('created_at'),
                'updated_at': cleaned_data.get('updated_at'),
                'customer_id': cleaned_data.get('customer_id'),
                'manager': cleaned_data.get('manager'),
                'person_in_charge': cleaned_data.get('person_in_charge'),
                'remarks': cleaned_data.get('remarks'),
                'shipping_date': cleaned_data.get('shipping_date'),
                'fee': int(cleaned_data.get('fee').replace(',', '')),
                'shipping_method': cleaned_data.get('shipping_method'),
                'payment_method': cleaned_data.get('payment_method'),
                'payment_due_date': cleaned_data.get('payment_due_date'),
                'memo': cleaned_data.get('memo')
            }
            return TraderSalesContract.objects.create(**contract_data)


class TraderSalesProductSenderForm(forms.Form):
    p_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    product_sender_id = forms.IntegerField(required=False)
    product_sender_name = forms.CharField(required=False)
    product_sender_postal_code = forms.CharField(required=False)
    product_sender_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-70', 'readonly': 'readonly'}), required=False)
    product_sender_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)
    product_sender_fax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)
    product_expected_arrival_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}),
        input_formats=INPUT_FORMATS,
        required=False
    )

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id'):
            self.contract_id = kwargs.pop('contract_id')
        super().__init__(*args, **kwargs)
    
    def save(self):
        sender = None
        if self.cleaned_data.get('product_sender_id'):
            sender = Sender.objects.get(id=self.cleaned_data.get('product_sender_id'))
        if self.cleaned_data.get('p_id'):
            contract_sender = TraderSalesSender.objects.get(id=self.cleaned_data.get('p_id'))
            contract_sender.sender = sender
            contract_sender.expected_arrival_date = self.cleaned_data.get('product_expected_arrival_date')
            contract_sender.save()
            return contract_sender
        else:
            
            data = {
                'contract': TraderSalesContract.objects.get(id=self.contract_id),
                'type': 'P',
                'sender': sender,
                'expected_arrival_date': self.cleaned_data.get('product_expected_arrival_date'),
            }
            return TraderSalesSender.objects.create(**data)


class TraderSalesDocumentSenderForm(forms.Form):
    d_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    document_sender_id = forms.IntegerField(required=False)
    document_sender_name = forms.CharField(required=False)
    document_sender_postal_code = forms.CharField(required=False)
    document_sender_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-70', 'readonly': 'readonly'}), required=False)
    document_sender_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)
    document_sender_fax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)
    document_expected_arrival_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}),
        input_formats=INPUT_FORMATS,
        required=False
    )

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id'):
            self.contract_id = kwargs.pop('contract_id')
        super().__init__(*args, **kwargs)
    
    def save(self):
        sender = None
        if self.cleaned_data.get('document_sender_id'):
            sender = Sender.objects.get(id=self.cleaned_data.get('document_sender_id'))
        if self.cleaned_data.get('d_id'):
            contract_sender = TraderSalesSender.objects.get(id=self.cleaned_data.get('d_id'))
            contract_sender.sender = sender
            contract_sender.expected_arrival_date = self.cleaned_data.get('document_expected_arrival_date')
            contract_sender.save()
            return contract_sender
        else:
            data = {
                'contract': TraderSalesContract.objects.get(id=self.contract_id),
                'type': 'D',
                'sender': sender,
                'expected_arrival_date': self.cleaned_data.get('document_expected_arrival_date'),
            }
            return TraderSalesSender.objects.create(**data)
# End of Trader Sales Forms


# Trader Purchases Forms
class TraderPurchasesContractForm(forms.Form):
    contract_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}))
    created_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    updated_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    customer_id = forms.IntegerField(required=False)
    customer_name = forms.CharField(required=False)
    manager = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    frigana = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    postal_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    fax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    person_in_charge = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control person_in_charge'}), required=False)
    payment_due_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS, required=False)
    removal_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS, required=False)
    shipping_method = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices=SHIPPING_METHOD_CHOICES, required=False)
    shipping_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS, required=False)
    frame_color = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    receipt = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    remarks = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-70'}), required=False)
    sub_total = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    tax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    fee = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), initial=0)
    total = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    transfer_deadline = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    bank_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    account_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    branch_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    account_holder = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    
    def __init__(self, *args, **kwargs):
        if kwargs.get('id'):
            self.id = kwargs.pop('id')
        else:
            self.id = None
        super().__init__(*args, **kwargs)
        self.fields['contract_id'].initial = generate_contract_id('02')
    
    def save(self):
        if self.id:
            contract = TraderPurchasesContract.objects.get(id=self.id)
            cleaned_data = self.cleaned_data
            contract.created_at = cleaned_data.get('created_at')
            contract.updated_at = cleaned_data.get('updated_at')
            contract.customer_id = cleaned_data.get('customer_id')
            contract.manager = cleaned_data.get('manager')
            contract.person_in_charge = cleaned_data.get('person_in_charge')
            contract.removal_date = cleaned_data.get('removal_date')
            contract.shipping_date = cleaned_data.get('shipping_date')
            contract.frame_color = cleaned_data.get('frame_color')
            contract.receipt = cleaned_data.get('receipt')
            contract.remarks = cleaned_data.get('remarks')
            contract.fee = int(cleaned_data.get('fee').replace(',', ''))
            contract.transfer_deadline = cleaned_data.get('transfer_deadline')
            contract.bank_name = cleaned_data.get('bank_name')
            contract.account_number = cleaned_data.get('account_number')
            contract.branch_name = cleaned_data.get('branch_name')
            contract.account_holder = cleaned_data.get('account_holder')

            contract.shipping_method = cleaned_data.get('shipping_method')
            contract.payment_due_date = cleaned_data.get('payment_due_date')
            contract.save()
            return contract
        else:
            cleaned_data = self.cleaned_data
            contract_data = {
                'contract_id': cleaned_data.get('contract_id'),
                'created_at': cleaned_data.get('created_at'),
                'updated_at': cleaned_data.get('updated_at'),
                'customer_id': cleaned_data.get('customer_id'),
                'manager': cleaned_data.get('manager'),
                'person_in_charge': cleaned_data.get('person_in_charge'),
                'removal_date': cleaned_data.get('removal_date'),
                'shipping_date': cleaned_data.get('shipping_date'),
                'frame_color': cleaned_data.get('frame_color'),
                'receipt': cleaned_data.get('receipt'),
                'remarks': cleaned_data.get('remarks'),
                'fee': int(cleaned_data.get('fee').replace(',', '')),
                'transfer_deadline': cleaned_data.get('transfer_deadline'),
                'bank_name': cleaned_data.get('bank_name'),
                'account_number': cleaned_data.get('account_number'),
                'branch_name': cleaned_data.get('branch_name'),
                'account_holder': cleaned_data.get('account_holder'),

                'shipping_method': cleaned_data.get('shipping_method'),
                'payment_due_date': cleaned_data.get('payment_due_date'),
            }
            return TraderPurchasesContract.objects.create(**contract_data)


class TraderPurchasesProductSenderForm(forms.Form):
    p_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    product_sender_id = forms.IntegerField(required=False)
    product_sender_name = forms.CharField(required=False)
    product_sender_postal_code = forms.CharField(required=False)
    product_sender_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-70', 'readonly': 'readonly'}), required=False)
    product_sender_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)
    product_desired_arrival_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}),
        input_formats=INPUT_FORMATS,
        required=False
    )
    product_shipping_company = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    product_sender_remarks = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id'):
            self.contract_id = kwargs.pop('contract_id')
        super().__init__(*args, **kwargs)
    
    def save(self):
        sender = None
        if self.cleaned_data.get('product_sender_id'):
            sender = Sender.objects.get(id=self.cleaned_data.get('product_sender_id'))
        if self.cleaned_data.get('p_id'):
            contract_sender = TraderPurchasesSender.objects.get(id=self.cleaned_data.get('p_id'))
            contract_sender.sender = sender
            contract_sender.desired_arrival_date = self.cleaned_data.get('product_desired_arrival_date')
            contract_sender.shipping_company = self.cleaned_data.get('product_shipping_company')
            contract_sender.remarks = self.cleaned_data.get('product_sender_remarks')
            contract_sender.save()
            return contract_sender
        else:
            data = {
                'contract': TraderPurchasesContract.objects.get(id=self.contract_id),
                'type': 'P',
                'sender': sender,
                'desired_arrival_date': self.cleaned_data.get('product_desired_arrival_date'),
                'shipping_company': self.cleaned_data.get('product_shipping_company'),
                'remarks': self.cleaned_data.get('product_sender_remarks'),
            }
            return TraderPurchasesSender.objects.create(**data)


class TraderPurchasesDocumentSenderForm(forms.Form):
    d_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    document_sender_id = forms.IntegerField(required=False)
    document_sender_name = forms.CharField(required=False)
    document_sender_postal_code = forms.CharField(required=False)
    document_sender_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-70', 'readonly': 'readonly'}), required=False)
    document_sender_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)
    document_desired_arrival_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}),
        input_formats=INPUT_FORMATS,
        required=False
    )
    document_shipping_company = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    document_sender_remarks = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('contract_id'):
            self.contract_id = kwargs.pop('contract_id')
        super().__init__(*args, **kwargs)
    
    def save(self):
        sender = None
        if self.cleaned_data.get('document_sender_id'):
            sender = Sender.objects.get(id=self.cleaned_data.get('document_sender_id'))
        if self.cleaned_data.get('d_id'):
            contract_sender = TraderPurchasesSender.objects.get(id=self.cleaned_data.get('d_id'))
            contract_sender.sender = sender
            contract_sender.desired_arrival_date = self.cleaned_data.get('document_desired_arrival_date')
            contract_sender.shipping_company = self.cleaned_data.get('document_shipping_company')
            contract_sender.remarks = self.cleaned_data.get('document_sender_remarks')
            contract_sender.save()
            return contract_sender
        else:
            data = {
                'contract': TraderPurchasesContract.objects.get(id=self.contract_id),
                'type': 'D',
                'sender': sender,
                'desired_arrival_date': self.cleaned_data.get('document_desired_arrival_date'),
                'shipping_company': self.cleaned_data.get('document_shipping_company'),
                'remarks': self.cleaned_data.get('document_sender_remarks'),
            }
            return TraderPurchasesSender.objects.create(**data)
# End of trader purchases form


# Hall Sales Forms
class HallSalesContractForm(forms.Form):
    contract_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}))
    created_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    customer_id = forms.IntegerField(required=False)
    customer_name = forms.CharField(required=False)
    hall_id = forms.IntegerField(required=False)
    hall_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    hall_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    hall_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    remarks = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-197-px'}), required=False)
    sub_total = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), required=False)
    tax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), required=False)
    fee = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'data-type': 'hall'}), required=False)
    total = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), required=False)
    shipping_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS, required=False)
    opening_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS, required=False)
    payment_method = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices=PAYMENT_METHOD_CHOICES)
    transfer_account = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "関西みらい銀行 堀江支店(118)普通 0076109 バッジオカブシキガイシャ"}),
        required=False
    )
    person_in_charge = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control person_in_charge'}), required=False)
    confirmor = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('id'):
            self.id = kwargs.pop('id')
        else:
            self.id = None
        super().__init__(*args, **kwargs)
        self.fields['contract_id'].initial = generate_contract_id('03')

        

    def save(self, shipping_date = None):
        if self.id:
            contract = HallSalesContract.objects.get(id=self.id)
            cleaned_data = self.cleaned_data
            contract.created_at = cleaned_data.get('created_at')
            contract.customer_id = cleaned_data.get('customer_id')
            contract.hall_id = cleaned_data.get('hall_id')
            contract.remarks = cleaned_data.get('remarks')
            contract.fee = cleaned_data.get('fee') or 0
            contract.shipping_date = shipping_date if shipping_date else cleaned_data.get('shipping_date')
            contract.opening_date = cleaned_data.get('opening_date')
            contract.payment_method = cleaned_data.get('payment_method')
            contract.transfer_account = cleaned_data.get('transfer_account')
            contract.person_in_charge = cleaned_data.get('person_in_charge')
            contract.confirmor = cleaned_data.get('confirmor')
            contract.save()
            return contract
        else:
            cleaned_data = self.cleaned_data
            contract_data = {
                'contract_id': cleaned_data.get('contract_id'),
                'created_at': cleaned_data.get('created_at'),
                'customer_id': cleaned_data.get('customer_id'),
                'hall_id': cleaned_data.get('hall_id'),
                'remarks': cleaned_data.get('remarks'),
                'fee': cleaned_data.get('fee') or 0,
                'shipping_date': shipping_date if shipping_date else cleaned_data.get('shipping_date'),
                'opening_date': cleaned_data.get('opening_date'),
                'payment_method': cleaned_data.get('payment_method'),
                'transfer_account': cleaned_data.get('transfer_account'),
                'person_in_charge': cleaned_data.get('person_in_charge'),
                'confirmor': cleaned_data.get('confirmor')
            }
            return HallSalesContract.objects.create(**contract_data)
# End of hall sales form


# Hall Purchases Forms
class HallPurchasesContractForm(forms.Form):
    contract_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}))
    created_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS)
    customer_id = forms.IntegerField(required=False)
    customer_name = forms.CharField(required=False)
    hall_id = forms.IntegerField(required=False)
    hall_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    hall_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    hall_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}), required=False)
    remarks = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-197-px'}), required=False)
    sub_total = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    tax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    fee = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'data-type': 'hall'}), initial=0, required=False)
    total = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), initial=0, required=False)
    shipping_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS, required=False)
    opening_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), input_formats=INPUT_FORMATS, required=False)
    payment_method = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices=PAYMENT_METHOD_CHOICES)
    transfer_account = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "関西みらい銀行 堀江支店(118)普通 0076109 バッジオカブシキガイシャ"}),
        required=False
    )
    person_in_charge = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control person_in_charge'}), required=False)
    confirmor = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    memo = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-92-px'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('id'):
            self.id = kwargs.pop('id')
        else:
            self.id = None
        super().__init__(*args, **kwargs)
        self.fields['contract_id'].initial = generate_contract_id('04')

    def save(self, shipping_date = None):
        if self.id:
            contract = HallPurchasesContract.objects.get(id=self.id)
            cleaned_data = self.cleaned_data
            contract.created_at = cleaned_data.get('created_at')
            contract.customer_id = cleaned_data.get('customer_id')
            contract.hall_id = cleaned_data.get('hall_id')
            contract.remarks = cleaned_data.get('remarks')
            contract.fee = cleaned_data.get('fee') or 0
            contract.shipping_date = shipping_date if shipping_date else cleaned_data.get('shipping_date')
            contract.opening_date = cleaned_data.get('opening_date')
            contract.payment_method = cleaned_data.get('payment_method')
            contract.transfer_account = cleaned_data.get('transfer_account')
            contract.person_in_charge = cleaned_data.get('person_in_charge')
            contract.confirmor = cleaned_data.get('confirmor')
            contract.memo = cleaned_data.get('memo')
            contract.save()
            return contract
        else:
            cleaned_data = self.cleaned_data
            contract_data = {
                'contract_id': cleaned_data.get('contract_id'),
                'created_at': cleaned_data.get('created_at'),
                'customer_id': cleaned_data.get('customer_id'),
                'hall_id': cleaned_data.get('hall_id'),
                'remarks': cleaned_data.get('remarks'),
                'fee': cleaned_data.get('fee') or 0,
                'shipping_date': shipping_date if shipping_date else cleaned_data.get('shipping_date'),
                'opening_date': cleaned_data.get('opening_date'),
                'payment_method': cleaned_data.get('payment_method'),
                'transfer_account': cleaned_data.get('transfer_account'),
                'person_in_charge': cleaned_data.get('person_in_charge'),
                'confirmor': cleaned_data.get('confirmor'),
                'memo': cleaned_data.get('memo')
            }
            return HallPurchasesContract.objects.create(**contract_data)
# End of hall purchases form

# 見積書フォーム
class EstimateContractForm(forms.Form):
    estimate_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}))
    created_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}))
    customer_id = forms.IntegerField(required=False)
    customer_name = forms.CharField(required=False)
    issue_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}))
    expiry_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), required=False)
    estimate_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    remarks = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-197-px'}), required=False)
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    sub_total = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), required=False)
    tax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), required=False)
    # fee = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'data-type': 'hall'}), required=False)
    total = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none'}), required=False)
    payment_method = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices=PAYMENT_METHOD_CHOICES)
    person_in_charge = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control person_in_charge'}), required=False)
    transfer_account = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_postal_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_mailaddress = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_invoice_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('id'):
            self.id = kwargs.pop('id')
        else:
            self.id = None
        
        initial = kwargs.pop('initial', {})
        super().__init__(*args, **kwargs)
        self.fields['estimate_id'].initial = generate_invoice_id('01')

        # 更新の場合には初期値を設定
        if initial:
            self.fields['estimate_id'].initial = initial.get('estimate_id')
            self.fields['created_at'].initial = initial.get('created_at').strftime('%Y-%m-%d')
            self.fields['customer_id'].initial = initial.get('customer_id')
            self.fields['issue_date'].initial = initial.get('issue_date').strftime('%Y-%m-%d')
            self.fields['expiry_date'].initial = initial.get('expiry_date').strftime('%Y-%m-%d')
            self.fields['estimate_no'].initial = initial.get('estimate_no')
            self.fields['remarks'].initial = initial.get('remarks')
            self.fields['subject'].initial = initial.get('subject')
            self.fields['sub_total'].initial = initial.get('sub_total')
            self.fields['tax'].initial = initial.get('tax')
            self.fields['total'].initial = initial.get('total')
            self.fields['payment_method'].initial = initial.get('payment_method')
            self.fields['transfer_account'].initial = initial.get('transfer_account')
            self.fields['person_in_charge'].initial = initial.get('person_in_charge')
            self.fields['own_company_name'].initial = initial.get('own_company_name')
            self.fields['own_company_postal_code'].initial = initial.get('own_company_postal_code')
            self.fields['own_company_address'].initial = initial.get('own_company_address')
            self.fields['own_company_tel'].initial = initial.get('own_company_tel')
            self.fields['own_company_mailaddress'].initial = initial.get('own_company_mailaddress')
            self.fields['own_company_invoice_no'].initial = initial.get('own_company_invoice_no')
        
            
        

    def save(self, shipping_date = None):
        if self.id:
            contract = EstimateContract.objects.get(id=self.id)
            cleaned_data = self.cleaned_data
            contract.created_at = cleaned_data.get('created_at')
            contract.customer_id = cleaned_data.get('customer_id')
            contract.issue_date = cleaned_data.get('issue_date')
            contract.expiry_date = cleaned_data.get('expiry_date')
            contract.estimate_no = cleaned_data.get('estimate_no')
            contract.remarks = cleaned_data.get('remarks')
            contract.subject = cleaned_data.get('subject')
            contract.fee = cleaned_data.get('fee') or 0
            contract.payment_method = cleaned_data.get('payment_method')
            contract.transfer_account = cleaned_data.get('transfer_account')
            contract.person_in_charge = cleaned_data.get('person_in_charge')
            contract.total_price = int(cleaned_data.get('total').replace(',', ''))
            contract.own_company_name = cleaned_data.get('own_company_name')
            contract.own_company_postal_code = cleaned_data.get('own_company_postal_code')
            contract.own_company_address = cleaned_data.get('own_company_address')
            contract.own_company_tel = cleaned_data.get('own_company_tel')
            contract.own_company_mailaddress = cleaned_data.get('own_company_mailaddress')
            contract.own_company_invoice_no = cleaned_data.get('own_company_invoice_no')
            contract.save()
            return contract
        else:
            cleaned_data = self.cleaned_data
            contract_data = {
                'estimate_id': cleaned_data.get('estimate_id'),
                'created_at': cleaned_data.get('created_at'),
                'customer_id': cleaned_data.get('customer_id'),
                'issue_date': cleaned_data.get('issue_date'),
                'expiry_date': cleaned_data.get('expiry_date'),
                'estimate_no': cleaned_data.get('estimate_no'),
                'remarks': cleaned_data.get('remarks'),
                'subject': cleaned_data.get('subject'),
                'fee': cleaned_data.get('fee') or 0,
                'payment_method': cleaned_data.get('payment_method'),
                'transfer_account': cleaned_data.get('transfer_account'),
                'person_in_charge': cleaned_data.get('person_in_charge'),
                'total_price': int(cleaned_data.get('total').replace(',', '')),
                'own_company_name': cleaned_data.get('own_company_name'),
                'own_company_postal_code': cleaned_data.get('own_company_postal_code'),
                'own_company_address': cleaned_data.get('own_company_address'),
                'own_company_tel': cleaned_data.get('own_company_tel'),
                'own_company_mailaddress': cleaned_data.get('own_company_mailaddress'),
                'own_company_invoice_no': cleaned_data.get('own_company_invoice_no'),
            }
            return EstimateContract.objects.create(**contract_data)
# End 見積書フォーム

# 請求書フォーム
class InvoiceContractForm(forms.Form):
    invoice_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}))
    created_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}))
    customer_id = forms.IntegerField(required=False)
    customer_name = forms.CharField(required=False)
    billing_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}))
    payment_deadline = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), required=False)
    billing_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    remarks = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-197-px'}), required=False)
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    sub_total = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), required=False)
    tax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), required=False)
    # fee = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'data-type': 'hall'}), required=False)
    total = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none'}), required=False)
    payment_method = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices=PAYMENT_METHOD_CHOICES)
    person_in_charge = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control person_in_charge'}), required=False)
    transfer_account = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_postal_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_mailaddress = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_invoice_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    payment_link = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    
    def __init__(self, *args, **kwargs):
        if kwargs.get('id'):
            self.id = kwargs.pop('id')
        else:
            self.id = None
        
        initial = kwargs.pop('initial', {})
        super().__init__(*args, **kwargs)
        self.fields['invoice_id'].initial = generate_invoice_id('01')

        # 更新の場合には初期値を設定
        if initial:
            self.fields['invoice_id'].initial = initial.get('invoice_id')
            self.fields['created_at'].initial = initial.get('created_at').strftime('%Y-%m-%d')
            self.fields['customer_id'].initial = initial.get('customer_id')
            self.fields['billing_date'].initial = initial.get('billing_date').strftime('%Y-%m-%d')
            self.fields['payment_deadline'].initial = initial.get('payment_deadline').strftime('%Y-%m-%d')
            self.fields['billing_no'].initial = initial.get('billing_no')
            self.fields['remarks'].initial = initial.get('remarks')
            self.fields['subject'].initial = initial.get('subject')
            self.fields['sub_total'].initial = initial.get('sub_total')
            self.fields['tax'].initial = initial.get('tax')
            self.fields['total'].initial = initial.get('total')
            self.fields['payment_method'].initial = initial.get('payment_method')
            self.fields['transfer_account'].initial = initial.get('transfer_account')
            self.fields['person_in_charge'].initial = initial.get('person_in_charge')
            self.fields['own_company_name'].initial = initial.get('own_company_name')
            self.fields['own_company_postal_code'].initial = initial.get('own_company_postal_code')
            self.fields['own_company_address'].initial = initial.get('own_company_address')
            self.fields['own_company_tel'].initial = initial.get('own_company_tel')
            self.fields['own_company_mailaddress'].initial = initial.get('own_company_mailaddress')
            self.fields['own_company_invoice_no'].initial = initial.get('own_company_invoice_no')
        
            
        

    def save(self, shipping_date = None):
        stripe_item = create_stripe_item(self.cleaned_data)
        payment_link = stripe_item.create_payment_link()
        if self.id:
            contract = InvoiceContract.objects.get(id=self.id)
            cleaned_data = self.cleaned_data
            contract.created_at = cleaned_data.get('created_at')
            contract.customer_id = cleaned_data.get('customer_id')
            contract.billing_date = cleaned_data.get('billing_date')
            contract.payment_deadline = cleaned_data.get('payment_deadline')
            contract.billing_no = cleaned_data.get('billing_no')
            contract.remarks = cleaned_data.get('remarks')
            contract.subject = cleaned_data.get('subject')
            contract.fee = cleaned_data.get('fee') or 0
            contract.payment_method = cleaned_data.get('payment_method')
            contract.transfer_account = cleaned_data.get('transfer_account')
            contract.person_in_charge = cleaned_data.get('person_in_charge')
            contract.total_price = int(cleaned_data.get('total').replace(',', ''))
            contract.own_company_name = cleaned_data.get('own_company_name')
            contract.own_company_postal_code = cleaned_data.get('own_company_postal_code')
            contract.own_company_address = cleaned_data.get('own_company_address')
            contract.own_company_tel = cleaned_data.get('own_company_tel')
            contract.own_company_mailaddress = cleaned_data.get('own_company_mailaddress')
            contract.own_company_invoice_no = cleaned_data.get('own_company_invoice_no')
            contract.payment_link = payment_link
            contract.save()
            return contract
        else:
            cleaned_data = self.cleaned_data
            contract_data = {
                'invoice_id': cleaned_data.get('invoice_id'),
                'created_at': cleaned_data.get('created_at'),
                'customer_id': cleaned_data.get('customer_id'),
                'billing_date': cleaned_data.get('billing_date'),
                'payment_deadline': cleaned_data.get('payment_deadline'),
                'billing_no': cleaned_data.get('billing_no'),
                'remarks': cleaned_data.get('remarks'),
                'subject': cleaned_data.get('subject'),
                'fee': cleaned_data.get('fee') or 0,
                'payment_method': cleaned_data.get('payment_method'),
                'transfer_account': cleaned_data.get('transfer_account'),
                'person_in_charge': cleaned_data.get('person_in_charge'),
                'total_price': int(cleaned_data.get('total').replace(',', '')),
                'own_company_name': cleaned_data.get('own_company_name'),
                'own_company_postal_code': cleaned_data.get('own_company_postal_code'),
                'own_company_address': cleaned_data.get('own_company_address'),
                'own_company_tel': cleaned_data.get('own_company_tel'),
                'own_company_mailaddress': cleaned_data.get('own_company_mailaddress'),
                'own_company_invoice_no': cleaned_data.get('own_company_invoice_no'),
                'payment_link': payment_link,
            }
            return InvoiceContract.objects.create(**contract_data)
# End 請求書フォーム


# 納品書フォーム
class DeliveryContractForm(forms.Form):
    delivery_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}))
    created_at = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}))
    customer_id = forms.IntegerField(required=False)
    customer_name = forms.CharField(required=False)
    issue_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}))
    delivery_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control daterange-single'}), required=False)
    delivery_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    remarks = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control h-197-px'}), required=False)
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    sub_total = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), required=False)
    tax = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none', 'readonly': 'readonly'}), required=False)
    # fee = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'data-type': 'hall'}), required=False)
    total = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control border-none'}), required=False)
    payment_method = forms.ChoiceField(widget=forms.Select(attrs={'class': 'selectbox'}), choices=PAYMENT_METHOD_CHOICES)
    person_in_charge = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control person_in_charge'}), required=False)
    transfer_account = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_postal_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_tel = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_mailaddress = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    own_company_invoice_no = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('id'):
            self.id = kwargs.pop('id')
        else:
            self.id = None
        
        initial = kwargs.pop('initial', {})
        super().__init__(*args, **kwargs)
        self.fields['delivery_id'].initial = generate_invoice_id('01')

        # 更新の場合には初期値を設定
        if initial:
            self.fields['delivery_id'].initial = initial.get('delivery_id')
            self.fields['created_at'].initial = initial.get('created_at').strftime('%Y-%m-%d')
            self.fields['customer_id'].initial = initial.get('customer_id')
            self.fields['issue_date'].initial = initial.get('issue_date').strftime('%Y-%m-%d')
            self.fields['delivery_date'].initial = initial.get('delivery_date').strftime('%Y-%m-%d')
            self.fields['delivery_no'].initial = initial.get('delivery_no')
            self.fields['remarks'].initial = initial.get('remarks')
            self.fields['subject'].initial = initial.get('subject')
            self.fields['sub_total'].initial = initial.get('sub_total')
            self.fields['tax'].initial = initial.get('tax')
            self.fields['total'].initial = initial.get('total')
            self.fields['payment_method'].initial = initial.get('payment_method')
            self.fields['transfer_account'].initial = initial.get('transfer_account')
            self.fields['person_in_charge'].initial = initial.get('person_in_charge')
            self.fields['own_company_name'].initial = initial.get('own_company_name')
            self.fields['own_company_postal_code'].initial = initial.get('own_company_postal_code')
            self.fields['own_company_address'].initial = initial.get('own_company_address')
            self.fields['own_company_tel'].initial = initial.get('own_company_tel')
            self.fields['own_company_mailaddress'].initial = initial.get('own_company_mailaddress')
            self.fields['own_company_invoice_no'].initial = initial.get('own_company_invoice_no')
        
            
        

    def save(self, shipping_date = None):
        if self.id:
            contract = DeliveryContract.objects.get(id=self.id)
            cleaned_data = self.cleaned_data
            contract.created_at = cleaned_data.get('created_at')
            contract.customer_id = cleaned_data.get('customer_id')
            contract.issue_date = cleaned_data.get('issue_date')
            contract.delivery_date = cleaned_data.get('delivery_date')
            contract.delivery_no = cleaned_data.get('delivery_no')
            contract.remarks = cleaned_data.get('remarks')
            contract.subject = cleaned_data.get('subject')
            contract.fee = cleaned_data.get('fee') or 0
            contract.payment_method = cleaned_data.get('payment_method')
            contract.transfer_account = cleaned_data.get('transfer_account')
            contract.person_in_charge = cleaned_data.get('person_in_charge')
            contract.total_price = int(cleaned_data.get('total').replace(',', ''))
            contract.own_company_name = cleaned_data.get('own_company_name')
            contract.own_company_postal_code = cleaned_data.get('own_company_postal_code')
            contract.own_company_address = cleaned_data.get('own_company_address')
            contract.own_company_tel = cleaned_data.get('own_company_tel')
            contract.own_company_mailaddress = cleaned_data.get('own_company_mailaddress')
            contract.own_company_invoice_no = cleaned_data.get('own_company_invoice_no')
            contract.save()
            return contract
        else:
            cleaned_data = self.cleaned_data
            contract_data = {
                'delivery_id': cleaned_data.get('delivery_id'),
                'created_at': cleaned_data.get('created_at'),
                'customer_id': cleaned_data.get('customer_id'),
                'issue_date': cleaned_data.get('issue_date'),
                'delivery_date': cleaned_data.get('delivery_date'),
                'delivery_no': cleaned_data.get('delivery_no'),
                'remarks': cleaned_data.get('remarks'),
                'subject': cleaned_data.get('subject'),
                'fee': cleaned_data.get('fee') or 0,
                'payment_method': cleaned_data.get('payment_method'),
                'transfer_account': cleaned_data.get('transfer_account'),
                'person_in_charge': cleaned_data.get('person_in_charge'),
                'total_price': int(cleaned_data.get('total').replace(',', '')),
                'own_company_name': cleaned_data.get('own_company_name'),
                'own_company_postal_code': cleaned_data.get('own_company_postal_code'),
                'own_company_address': cleaned_data.get('own_company_address'),
                'own_company_tel': cleaned_data.get('own_company_tel'),
                'own_company_mailaddress': cleaned_data.get('own_company_mailaddress'),
                'own_company_invoice_no': cleaned_data.get('own_company_invoice_no'),
            }
            return DeliveryContract.objects.create(**contract_data)
# End 納品書フォーム