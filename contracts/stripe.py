import stripe
from decouple import config

class create_stripe_item:
    def __init__(self, data):
        # Stripeの秘密鍵を設定
        stripe.api_key = config('STRIPE_API_KEY')
        self.data = data
        
    def create_payment_link(self):
        # 商品を作成
        product = stripe.Product.create(
            name=self.data['invoice_id'],
            description='作成日：' + str(self.data['created_at']) + '、' + '請求書番号：' + self.data['billing_no'] + '、' + '件名：' + self.data['subject'],
            active=True
        )

        # 商品に価格を設定
        if isinstance(self.data['total'], str):
            amount = int(self.data['total'].replace(',', ''))
        else:
            amount = int(self.data['total'])
        price = stripe.Price.create(
            product=product.id,
            unit_amount=amount,
            currency='jpy'
        )
        
        payment_link = create_checkout_session(price.id)
        return payment_link

        print("商品が作成されました:", product.id)
        print("価格設定が完了しました:", price.id)
        print("支払いリンクが作成されました:", payment_link)


def create_checkout_session(price_id):
    try:
        # Checkout Sessionの作成
        session = stripe.PaymentLink.create(
            payment_method_types=['card'],  # 支払い方法をカードに設定
            line_items=[{
                'price': price_id,  # Stripe価格オブジェクトID
                'quantity': 1,  # 数量
            }],
            # mode='payment',  # 単一の支払い
            # success_url='https://example.com/success',  # 支払い成功時のURL
            # cancel_url='https://example.com/cancel',  # 支払いキャンセル時のURL
        )
        return session.url  # 支払いページのURLを返す
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None