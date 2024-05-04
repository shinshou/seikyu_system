import xlwt
from django.views.generic.base import View
from django.http import HttpResponse, FileResponse
from io import BytesIO
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from users.views import AdminLoginRequiredMixin
from contracts.models import ContractProduct,InvoiceContract,EstimateContract,DeliveryContract
from masterdata.models import (
    Customer, Hall, Sender, Product, Document, DocumentFee,
    PRODUCT_TYPE_CHOICES, SHIPPING_METHOD_CHOICES, PAYMENT_METHOD_CHOICES, CATEGORY_CHOICES,
    COMPANY_NAME, ADDRESS, TEL, POSTAL_CODE, CEO
)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import cidfonts
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus.frames import Frame
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
import os
from datetime import datetime

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='p_style', fontName='HeiseiMin-W3', fontSize=12, leading=18,))
styles.add(ParagraphStyle(name='p_align_right_style', fontName='HeiseiMin-W3', fontSize=12, alignment=TA_RIGHT, leading=18,))
styles.add(ParagraphStyle(name='h3_style', fontName='HeiseiMin-W3', fontSize=16, leading=21,))
styles.add(ParagraphStyle(name='h1_style', fontName='HeiseiMin-W3', fontSize=24, alignment=1, leading=36,))
pdfmetrics.registerFont(cidfonts.UnicodeCIDFont("HeiseiMin-W3"))


def getDate(date): 
    result = None
    try: 
        try:
            result = datetime.strptime(date, '%m/%d/%Y')
        except:
            try:
                result = datetime.strptime(date, '%Y/%m/%d')
            except:
                try:
                    result = datetime.strptime(date, '%m-%d-%Y')
                except:
                    result = datetime.strptime(date, '%Y-%m-%d')
    except:
        result = None

    return result

def get_product_list(products):
    product_list = []
    for product in products:
        product_info = {
            'name': product.product.name,
            'quantity': product.quantity,
            'price': product.price,
            'amount': product.amount,
            'tax': product.tax,
            'total': product.amount + product.tax 
        }
        product_list.append(product_info)
    return  product_list

def get_document_list(documents):
    document_list = []
    for document in documents:
        document_info = {
            'name': document.document.name,
            'quantity': document.quantity,
            'price': document.price,
            'amount': document.amount,
            'tax': document.tax,
            'total': document.amount + document.tax 
        }
        document_list.append(document_info)
    return  document_list

# 見積書PDF
class EstimateDownloadPdfView(AdminLoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        contract_id = self.request.GET.get('contract_id')
        object_id = self.request.GET.get('object_id')
        contract = EstimateContract.objects.get(id=object_id)
        estimate_id = contract.estimate_id
        created_at = contract.created_at
        customer = contract.customer
        issue_date = contract.issue_date
        expiry_date = contract.expiry_date
        estimate_no = contract.estimate_no
        remarks = contract.remarks
        subject = contract.subject
        fee = contract.fee
        payment_method = contract.payment_method
        transfer_account = contract.transfer_account
        person_in_charge = contract.person_in_charge
        tax = contract.tax
        sub_total = contract.sub_total
        total_price = contract.total_price
        own_company_name = contract.own_company_name
        own_company_postal_code = contract.own_company_postal_code
        own_company_address = contract.own_company_address
        own_company_tel = contract.own_company_tel
        own_company_mailaddress = contract.own_company_mailaddress
        own_company_invoice_no = contract.own_company_invoice_no
        products = contract.products.all()
        documents = contract.documents.all()
        product_list = get_product_list(products)
        document_list = get_document_list(documents)
        
        # buf = os.path.join(settings.BASE_DIR, 'pdffiles', 'test.pdf')
        buf = BytesIO()

        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=10*mm, bottomMargin=10*mm)
        
        # 要素リスト
        elements = []
        # 納品書情報
        formatted_date = issue_date.strftime('%Y年%m月%d日')
        elements.append(Paragraph(formatted_date, styles['p_align_right_style']))
        elements.append(Paragraph('見積番号: '+ estimate_id, styles['p_align_right_style']))
        elements.append(Paragraph('適格請求書発行事業者番号: '+ own_company_invoice_no, styles['p_align_right_style']))
        elements.append(Spacer(1, 12*mm)) 

        elements.append(Paragraph('見積書', styles['h1_style']))
        elements.append(Spacer(1, 12*mm)) 
        
        # ヘッダー情報
        
        data = [
            [Paragraph(customer.name +' 様', styles['h3_style']), Paragraph(own_company_name, styles['p_style'])],
            [Paragraph('件名 : ' + subject, styles['p_style']), Paragraph('TEL: 080-1472-1277', styles['p_style'])],
            ['', Paragraph(own_company_mailaddress, styles['p_style'])],
            [Paragraph('下記のとおりお見積申し上げます。', styles['p_style']), ''],
            [Paragraph('お見積金額&nbsp;&nbsp;&nbsp;' + f"{total_price:,}円" + ' -', styles['h3_style']), ''],
        ]

        # テーブルスタイルの設定
        table_style = TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (0, 0), 12),  # 最初の行のみ12mm
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),  # 2行目以降は3mm
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ])

        # テーブルを生成
        contact_table = Table(data, colWidths=[90*mm, 90*mm], style=table_style)
        elements.append(contact_table)
        elements.append(Spacer(1, 12*mm)) 

        # 商品リスト
        data = [['品番・品名', '数量', '単価', '金額']]
        
        for product in product_list:
            data.append([product['name'], product['quantity'], f"{product['price']:,}円", f"{product['amount']:,}円"])
            
        for document in document_list:
            data.append([document['name'], document['quantity'], f"{document['price']:,}円", f"{document['amount']:,}円"])

        current_rows = len(data)  # 総データ数
        max_per_page = 15  # 1ページに表示するデータ数
        page_num = int((current_rows / max_per_page) + 1) # ページ数
        
        while page_num > 1:
            sub_data = data[:15]  
            del data[:15]
            table = Table(sub_data, colWidths=[80*mm, 30*mm, 30*mm, 30*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), "#e5e5e5"),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,-1), 'HeiseiMin-W3'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black), 
            ]))
            elements.append(table)
            elements.append(PageBreak())
            data.insert(0, ['品番・品名', '数量', '単価', '金額'])
            page_num -= 1
        
        current_rows = len(data)  # 残りのデータ数
        min_rows = 10  #最後のページは10行データ + 合計金額
        if current_rows < min_rows:
            for _ in range(min_rows - current_rows):
                data.append(['', '', '', ''])  # 空のデータを追加

        data.append(['', '', '小計', f"{sub_total:,}円"])
        data.append(['', '', '消費税 (10%)', f"{tax:,}円"])
        data.append(['', '', '合計', f"{total_price:,}円"])

        table = Table(data, colWidths=[80*mm, 30*mm, 30*mm, 30*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), "#e5e5e5"),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'HeiseiMin-W3'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('GRID', (0, 0), (-1, min_rows - 1), 1, colors.black),  # 最初の10行に枠線
            ('GRID', (2, min_rows), (-1, -1), 1, colors.black),  # 小計、税、合計の行に枠線
        ]))

        elements.append(table)
        
        elements.append(Spacer(1, 12*mm)) 
        
        long_text = remarks

        # テーブルデータの作成
        data = [
            [Paragraph('備考', styles['p_style']), ''],
            [Paragraph(long_text, styles['p_style']), '']
        ]

        # テーブルの生成
        table = Table(data, colWidths=[130*mm, 50*mm], style=TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ]))
        
        elements.append(table)

        doc.multiBuild(elements)
        
        pdf = buf.getvalue()
        buf.close()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="downloaded_file.pdf"'
        return response

# 請求書PDF
class InvoiceDownloadPdfView(AdminLoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        contract_id = self.request.GET.get('contract_id')
        object_id = self.request.GET.get('object_id')
        contract = InvoiceContract.objects.get(id=object_id)
        invoice_id = contract.invoice_id
        created_at = contract.created_at
        customer = contract.customer
        billing_date = contract.billing_date
        payment_deadline = contract.payment_deadline
        billing_no = contract.billing_no
        remarks = contract.remarks
        subject = contract.subject
        fee = contract.fee
        payment_method = contract.payment_method
        transfer_account = contract.transfer_account
        person_in_charge = contract.person_in_charge
        tax = contract.tax
        sub_total = contract.sub_total
        total_price = contract.total_price
        own_company_name = contract.own_company_name
        own_company_postal_code = contract.own_company_postal_code
        own_company_address = contract.own_company_address
        own_company_tel = contract.own_company_tel
        own_company_mailaddress = contract.own_company_mailaddress
        own_company_invoice_no = contract.own_company_invoice_no
        products = contract.products.all()
        documents = contract.documents.all()
        product_list = get_product_list(products)
        document_list = get_document_list(documents)

        buf = BytesIO()

        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=10*mm, bottomMargin=10*mm)

        # 要素リスト
        elements = []
        # 納品書情報
        formatted_date = billing_date.strftime('%Y年%m月%d日')
        elements.append(Paragraph(formatted_date, styles['p_align_right_style']))
        elements.append(Paragraph('請求番号: '+ invoice_id, styles['p_align_right_style']))
        elements.append(Paragraph('適格請求書発行事業者番号: '+ own_company_invoice_no, styles['p_align_right_style']))
        elements.append(Spacer(1, 12*mm)) 

        elements.append(Paragraph('請求書', styles['h1_style']))
        elements.append(Spacer(1, 12*mm)) 
        
        # ヘッダー情報
        
        data = [
            [Paragraph(customer.name +' 様', styles['h3_style']), Paragraph(own_company_name, styles['p_style'])],
            [Paragraph('件名 : ' + subject, styles['p_style']), Paragraph('TEL: 080-1472-1277', styles['p_style'])],
            ['', Paragraph(own_company_mailaddress, styles['p_style'])],
            [Paragraph('下記のとおりご請求申し上げます', styles['p_style']), ''],
            [Paragraph('ご請求金額&nbsp;&nbsp;&nbsp;' + f"{total_price:,}円" + ' -', styles['h3_style']), ''],
        ]

        # テーブルスタイルの設定
        table_style = TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (0, 0), 12),  # 最初の行のみ12mm
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),  # 2行目以降は3mm
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ])

        # テーブルを生成
        contact_table = Table(data, colWidths=[90*mm, 90*mm], style=table_style)
        elements.append(contact_table)
        elements.append(Spacer(1, 12*mm)) 

        # 商品リスト
        data = [['品番・品名', '数量', '単価', '金額']]
        
        for product in product_list:
            data.append([product['name'], product['quantity'], f"{product['price']:,}円", f"{product['amount']:,}円"])
            
        for document in document_list:
            data.append([document['name'], document['quantity'], f"{document['price']:,}円", f"{document['amount']:,}円"])
        
        current_rows = len(data)  # 総データ数
        max_per_page = 15  # 1ページに表示するデータ数
        page_num = int((current_rows / max_per_page) + 1) # ページ数
        
        while page_num > 1:
            sub_data = data[:15]  
            del data[:15]
            table = Table(sub_data, colWidths=[80*mm, 30*mm, 30*mm, 30*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), "#e5e5e5"),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,-1), 'HeiseiMin-W3'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black), 
            ]))
            elements.append(table)
            elements.append(PageBreak())
            data.insert(0, ['品番・品名', '数量', '単価', '金額'])
            page_num -= 1
        
        current_rows = len(data)  # 残りのデータ数
        min_rows = 10  # 例えば1ページあたり最低10行を保持したい場合
        if current_rows < min_rows:
            for _ in range(min_rows - current_rows):
                data.append(['', '', '', ''])  # 空のデータを追加

        data.append(['', '', '小計', f"{sub_total:,}円"])
        data.append(['', '', '消費税 (10%)', f"{tax:,}円"])
        data.append(['', '', '合計', f"{total_price:,}円"])

        table = Table(data, colWidths=[80*mm, 30*mm, 30*mm, 30*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), "#e5e5e5"),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'HeiseiMin-W3'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('GRID', (0, 0), (-1, min_rows - 1), 1, colors.black),  # 最初の10行に枠線
            ('GRID', (2, min_rows), (-1, -1), 1, colors.black),  # 小計、税、合計の行に枠線
        ]))

        elements.append(table)
        
        elements.append(Spacer(1, 12*mm)) 
        
        long_text = remarks

        # テーブルデータの作成
        data = [
            [Paragraph('備考', styles['p_style']), ''],
            [Paragraph(long_text, styles['p_style']), '']
        ]

        # テーブルの生成
        table = Table(data, colWidths=[130*mm, 50*mm], style=TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ]))
        
        elements.append(table)

        doc.multiBuild(elements)
        
        pdf = buf.getvalue()
        buf.close()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="downloaded_file.pdf"'
        return response


# 納品書PDF
class DeliveryDownloadPdfView(AdminLoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        contract_id = self.request.GET.get('contract_id')
        object_id = self.request.GET.get('object_id')
        contract = DeliveryContract.objects.get(id=object_id)
        delivery_id = contract.delivery_id
        created_at = contract.created_at
        customer = contract.customer
        issue_date = contract.issue_date
        delivery_date = contract.delivery_date
        delivery_no = contract.delivery_no
        remarks = contract.remarks
        subject = contract.subject
        fee = contract.fee
        payment_method = contract.payment_method
        transfer_account = contract.transfer_account
        person_in_charge = contract.person_in_charge
        tax = contract.tax
        sub_total = contract.sub_total
        total_price = contract.total_price
        own_company_name = contract.own_company_name
        own_company_postal_code = contract.own_company_postal_code
        own_company_address = contract.own_company_address
        own_company_tel = contract.own_company_tel
        own_company_mailaddress = contract.own_company_mailaddress
        own_company_invoice_no = contract.own_company_invoice_no
        products = contract.products.all()
        documents = contract.documents.all()
        product_list = get_product_list(products)
        document_list = get_document_list(documents)
        
        # buf = os.path.join(settings.BASE_DIR, 'pdffiles', 'test.pdf')
        buf = BytesIO()

        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=10*mm, bottomMargin=10*mm)
        
        # 要素リスト
        elements = []
        # 納品書情報
        formatted_date = issue_date.strftime('%Y年%m月%d日')
        elements.append(Paragraph(formatted_date, styles['p_align_right_style']))
        elements.append(Paragraph('納品番号: '+ delivery_id, styles['p_align_right_style']))
        elements.append(Paragraph('適格請求書発行事業者番号: '+ own_company_invoice_no, styles['p_align_right_style']))
        elements.append(Spacer(1, 12*mm)) 

        elements.append(Paragraph('納品書', styles['h1_style']))
        elements.append(Spacer(1, 12*mm)) 
        
        # ヘッダー情報
        
        data = [
            [Paragraph(customer.name +' 様', styles['h3_style']), Paragraph(own_company_name, styles['p_style'])],
            [Paragraph('件名 : ' + subject, styles['p_style']), Paragraph('TEL: 080-1472-1277', styles['p_style'])],
            ['', Paragraph(own_company_mailaddress, styles['p_style'])],
            [Paragraph('下記のとおり納品いたしました。', styles['p_style']), ''],
            [Paragraph('合計金額&nbsp;&nbsp;&nbsp;' + f"{total_price:,}円" + ' -', styles['h3_style']), ''],
        ]

        # テーブルスタイルの設定
        table_style = TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (0, 0), 12),  # 最初の行のみ12mm
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),  # 2行目以降は3mm
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ])

        # テーブルを生成
        contact_table = Table(data, colWidths=[90*mm, 90*mm], style=table_style)
        elements.append(contact_table)
        elements.append(Spacer(1, 12*mm)) 

        # 商品リスト
        data = [['品番・品名', '数量', '単価', '金額']]
        
        for product in product_list:
            data.append([product['name'], product['quantity'], f"{product['price']:,}円", f"{product['amount']:,}円"])
            
        for document in document_list:
            data.append([document['name'], document['quantity'], f"{document['price']:,}円", f"{document['amount']:,}円"])

        current_rows = len(data)  # 総データ数
        max_per_page = 15  # 1ページに表示するデータ数
        page_num = int((current_rows / max_per_page) + 1) # ページ数
        
        while page_num > 1:
            sub_data = data[:15]  
            del data[:15]
            table = Table(sub_data, colWidths=[80*mm, 30*mm, 30*mm, 30*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), "#e5e5e5"),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,-1), 'HeiseiMin-W3'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black), 
            ]))
            elements.append(table)
            elements.append(PageBreak())
            data.insert(0, ['品番・品名', '数量', '単価', '金額'])
            page_num -= 1
        
        current_rows = len(data)  # 残りのデータ数
        min_rows = 10  #最後のページは10行データ + 合計金額
        if current_rows < min_rows:
            for _ in range(min_rows - current_rows):
                data.append(['', '', '', ''])  # 空のデータを追加

        data.append(['', '', '小計', f"{sub_total:,}円"])
        data.append(['', '', '消費税 (10%)', f"{tax:,}円"])
        data.append(['', '', '合計', f"{total_price:,}円"])

        table = Table(data, colWidths=[80*mm, 30*mm, 30*mm, 30*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), "#e5e5e5"),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'HeiseiMin-W3'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('GRID', (0, 0), (-1, min_rows - 1), 1, colors.black),  # 最初の10行に枠線
            ('GRID', (2, min_rows), (-1, -1), 1, colors.black),  # 小計、税、合計の行に枠線
        ]))

        elements.append(table)
        
        elements.append(Spacer(1, 12*mm)) 
        
        long_text = remarks

        # テーブルデータの作成
        data = [
            [Paragraph('備考', styles['p_style']), ''],
            [Paragraph(long_text, styles['p_style']), '']
        ]

        # テーブルの生成
        table = Table(data, colWidths=[130*mm, 50*mm], style=TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ]))
        
        elements.append(table)

        doc.multiBuild(elements)
        
        pdf = buf.getvalue()
        buf.close()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="downloaded_file.pdf"'
        return response