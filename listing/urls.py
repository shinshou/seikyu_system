from django.urls import path
from .views import (
    SalesListView, PurchasesListView, LinkListView, LinkListShowView, ExportHistoryListView, DeletedListView,
    SalesProductUpdateView, PurchasesProductUpdateView, LinkProductsAjaxView,
    SalesProductDetailAjaxView, PurchasesProductDetailAjaxView,
    InventoryProductDetailAjaxView, InventoryProductCreateView, InventoryProductUpdateView, InventoryProductDeleteView,
    LinkProductReportDateUpdate,
    InvoiceListView,InvoicesProductDetailAjaxView,
    EstimateListView,EstimatesProductDetailAjaxView,
    DeliveryListView,DeliverysProductDetailAjaxView
)

from .pdf_download_views import (
    EstimateDownloadPdfView, InvoiceDownloadPdfView, DeliveryDownloadPdfView
)

app_name = 'listing'
urlpatterns = [
    path('sales/', SalesListView.as_view(), name='sales-list'),
    
    path('estimates/', EstimateListView.as_view(), name='estimates-list'),
    path('invoices/', InvoiceListView.as_view(), name='invoices-list'),
    path('deliverys/', DeliveryListView.as_view(), name='deliverys-list'),

    path('estimates/pdf-download/', EstimateDownloadPdfView.as_view(), name='estimate-pdf-download'),
    path('invoices/pdf-download/', InvoiceDownloadPdfView.as_view(), name='invoice-pdf-download'),
    path('deliverys/pdf-download/', DeliveryDownloadPdfView.as_view(), name='delivery-pdf-download'),
    
    path('purchases/', PurchasesListView.as_view(), name='purchases-list'),
    path('deleted/', DeletedListView.as_view(), name='deleted-list'),
    path('link-list/', LinkListView.as_view(), name='link-list'),
    path('link-list-report-update', LinkProductReportDateUpdate.as_view(), name='link-list-report-update'),
    path('link-list-show/', LinkListShowView.as_view(), name='link-list-show'),
    path('link-list-ajax/', LinkProductsAjaxView.as_view(), name='link-list-ajax'),
    # path('inventory/', InventoryListView.as_view(), name='inventory-list'),
    path('history/', ExportHistoryListView.as_view(), name='history-list'),
    path('sales-product/update/', SalesProductUpdateView.as_view(), name='sales-product-update'),
    path('purchases-product/update/', PurchasesProductUpdateView.as_view(), name='purchases-product-update'),
    path('sales-product/detail/', SalesProductDetailAjaxView.as_view(), name='sales-product-detail'),
    
    path('estimates-product/detail/', EstimatesProductDetailAjaxView.as_view(), name='estimates-product-detail'),
    path('invoices-product/detail/', InvoicesProductDetailAjaxView.as_view(), name='invoices-product-detail'),
    path('deliverys-product/detail/', DeliverysProductDetailAjaxView.as_view(), name='deliverys-product-detail'),
    
    path('purchases-product/detail/', PurchasesProductDetailAjaxView.as_view(), name='purchases-product-detail'),
    path('inventory-product/detail/', InventoryProductDetailAjaxView.as_view(), name='inventory-product-detail'),
    path('inventory-product/create/', InventoryProductCreateView.as_view(), name='inventory-product-create'),
    path('inventory-product/update/', InventoryProductUpdateView.as_view(), name='inventory-product-update'),
    path('inventory-product/delete/', InventoryProductDeleteView.as_view(), name='inventory-product-delete'),
]
