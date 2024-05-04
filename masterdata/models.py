from django.db import models
from django.utils.translation import gettext_lazy as _

POSTAL_CODE = '000-0000'
ADDRESS = '東京都城東区〇〇-〇〇'
COMPANY_NAME = '株式会社クラウドえびす'
CEO = ''
TEL = '06-1234-5678'
FAX=''
REFAX=''
P_SENSOR_NUMBER=''
MAILADDRESS = 'example@exaple.com'
TRANSFER_ACCOUNT = '三菱UFJ銀行　〇〇支店　口座番号〇〇'
INPUT_FORMATS = ['%Y/%m/%d', '%m/%d/%Y']
THRESHOLD_PRICE = 100000
INVOICE_NO = 'T-000000'

SECURE_PAYMENT = 'あんしん決済'
NO_FEE_SALES = '非課売上'
FEE_SALES = '課税売上10%'
NO_FEE_PURCHASES = '非課仕入'
FEE_PURCHASES = '課対仕入10%'

SHIPPING_METHOD_CHOICES = (
    ('D', _('Delivery')),
    ('R', _('Receipt')),
    ('C', _('ID Change')),
    ('B', _('* Blank')),
)

PAYMENT_METHOD_CHOICES = (
    ('TR', _('Transfer')),
    ('CR', _('Credit')),
)

PRODUCT_TYPE_CHOICES = (
    ('M', _('Main body')),
    ('F', _('Frame')),
    ('C', _('Cell')),
    ('N', _('Nail sheet')),
)

ITEM_CHOICES = (
    ('P', _('Product')),
    ('D', _('Document'))
)

STOCK_CHOICES = (
    ('D', _('Done')),
    ('P', _('Pending'))
)

CATEGORY_CHOICES = (
    ('P', _('Pachinko')),
    ('S', _('Slot')),
    ('categoryA', _('categoryA')),
    ('categoryB', _('categoryB')),
    ('categoryC', _('categoryC')),
    ('categoryD', _('categoryD'))
)


class MasterData(models.Model):
    name = models.CharField(max_length=200)
    customer_name = models.CharField(max_length=200, null=True, blank=True)
    customer_frigana = models.CharField(max_length=200, null=True, blank=True)
    frigana = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=200)
    tel = models.CharField(max_length=100, null=True, blank=True)
    mailaddress = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return self.name


class Customer(MasterData):
    # excel = models.CharField(max_length=200, null=True, blank=True)
    payee = models.CharField(max_length=200)


class Hall(MasterData):
    payee = models.CharField(max_length=200)


class Sender(MasterData):
    payee = models.CharField(max_length=200)


class Product(models.Model):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=200)
    category = models.CharField(max_length=9, choices=CATEGORY_CHOICES, default='categoryA')
    purchase_date = models.DateField(null=True, blank=True)
    supplier = models.CharField(max_length=200, null=True, blank=True)
    person_in_charge = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    # stock = models.IntegerField(null=True, blank=True)
    # amount = models.IntegerField(null=True, blank=True)

    @property
    def amount(self):
        if self.price and self.quantity:
            return self.price * self.quantity
        return None

    def __str__(self):
        return self.name


class Document(models.Model):
    name = models.CharField(max_length=200)
    term = models.CharField(max_length=200)
    taxation = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    @property
    def taxable(self):
        return self.name != SECURE_PAYMENT


class DocumentFee(models.Model):
    type = models.CharField(max_length=9, choices=CATEGORY_CHOICES, default='categoryA')
    model_price = models.IntegerField()
    unit_price = models.IntegerField()
    application_fee = models.IntegerField(default=30000)


class InventoryProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory')
    updated_date = models.DateTimeField(null=True, blank=True)
    supplier = models.CharField(max_length=200, null=True, blank=True)
    person_in_charge = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    # stock = models.IntegerField(null=True, blank=True)
    # amount = models.IntegerField(null=True, blank=True)

    @property
    def amount(self):
        if self.price and self.quantity:
            return self.price * self.quantity
        return None

    def __str__(self):
        return f"{self.product.name}"


class PersonInCharge(models.Model):
    name = models.CharField(max_length=200)
