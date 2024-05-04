from django.urls import path
from .views import (
    ContractClassNameAjaxViewPermanent, TraderSalesContractView, TraderPurchasesContractView, HallSalesContractView, HallPurchasesContractView,
    TraderSalesValidateAjaxView, TraderPurchasesValidateAjaxView, HallSalesValidateAjaxView, HallPurchasesValidateAjaxView,
    ContractShippingLabelAjaxView, ContractManagerAjaxView, ContractClassNameAjaxView, CheckTaxableAjaxView,
    InvoiceContractView, InvoiceClassNameAjaxView,
    EstimateContractView,EstimateClassNameAjaxView,
    DeliveryContractView,DeliveryClassNameAjaxView,
)
from .update_views import (
    TraderSalesContractUpdateView, TraderPurchasesContractUpdateView, HallSalesContractUpdateView, HallPurchasesContractUpdateView,
    InvoiceContractUpdateView, EstimateContractUpdateView, DeliveryContractUpdateView 
)
from .invoice_views import (
    TraderSalesInvoiceView, TraderPurchasesInvoiceView, HallSalesInvoiceView, HallPurchasesInvoiceView, TraderSalesInvoiceViewOnly
)

app_name = 'contract'
urlpatterns = [
    path('trader-sales/', TraderSalesContractView.as_view(), name='trader-sales'),
    path('trader-purchases/', TraderPurchasesContractView.as_view(), name='trader-purchases'),
    path('hall-sales/', HallSalesContractView.as_view(), name='hall-sales'),
    path('hall-purchases/', HallPurchasesContractView.as_view(), name='hall-purchases'),
    
    path('estimate/', EstimateContractView.as_view(), name='estimate'),
    path('invoice/', InvoiceContractView.as_view(), name='invoice'),
    path('delivery/', DeliveryContractView.as_view(), name='delivery'),
    
    path('invoice/trader-sales/', TraderSalesInvoiceView.as_view(), name='trader-sales-invoice'),
    path('invoice/trader-sales-only/', TraderSalesInvoiceViewOnly.as_view(), name='trader-sales-invoice-only'),
    path('invoice/trader-purchases/', TraderPurchasesInvoiceView.as_view(), name='trader-purchases-invoice'),
    path('invoice/hall-sales/', HallSalesInvoiceView.as_view(), name='hall-sales-invoice'),
    path('invoice/hall-purchases/', HallPurchasesInvoiceView.as_view(), name='hall-purchases-invoice'),

    path('trader-sales/<int:pk>/update/', TraderSalesContractUpdateView.as_view(), name='tradersalescontract-update'),
    path('trader-purchases/<int:pk>/update/', TraderPurchasesContractUpdateView.as_view(), name='traderpurchasescontract-update'),
    path('hall-sales/<int:pk>/update/', HallSalesContractUpdateView.as_view(), name='hallsalescontract-update'),
    path('hall-purchases/<int:pk>/update/', HallPurchasesContractUpdateView.as_view(), name='hallpurchasescontract-update'),
    
    path('estimate/<int:pk>/update/', EstimateContractUpdateView.as_view(), name='estimatecontract-update'),
    path('invoice/<int:pk>/update/', InvoiceContractUpdateView.as_view(), name='invoicecontract-update'),
    path('delivery/<int:pk>/update/', DeliveryContractUpdateView.as_view(), name='deliverycontract-update'),

    path('validate/trader-sales/', TraderSalesValidateAjaxView.as_view(), name='trader-sales-validate'),
    path('validate/trader-purchases/', TraderPurchasesValidateAjaxView.as_view(), name='trader-purchases-validate'),
    path('validate/hall-sales/', HallSalesValidateAjaxView.as_view(), name='hall-sales-validate'),
    path('validate/hall-purchases/', HallPurchasesValidateAjaxView.as_view(), name='hall-purchases-validate'),

    path('shipping-label/', ContractShippingLabelAjaxView.as_view(), name='shipping-label'),
    path('manager/', ContractManagerAjaxView.as_view(), name='manager-list'),
    path('contract-update-path/', ContractClassNameAjaxView.as_view(), name='contract-update-path'),
    
    path('estimate-update-path/', EstimateClassNameAjaxView.as_view(), name='estimate-update-path'),
    path('invoice-update-path/', InvoiceClassNameAjaxView.as_view(), name='invoice-update-path'),
    path('delivery-update-path/', DeliveryClassNameAjaxView.as_view(), name='delivery-update-path'),

    path('contract-update-path-permanent/', ContractClassNameAjaxViewPermanent.as_view(), name='contract-update-path-permanent'),
    path('check-taxable/', CheckTaxableAjaxView.as_view(), name='check-taxable'),
]
