from mongoengine import Document, StringField, IntField, BooleanField, \
    ReferenceField, ListField

from models.product import Product
from models.user import User


class Cart(Document):
    user = ReferenceField(User, required=True)
    products = ListField(ReferenceField(Product))
    is_archived = BooleanField(default=False)

    @property
    def get_sum(self):
        cart_sum = 0
        for p in self.products:
            cart_sum += p.price

        return cart_sum/100

    @classmethod
    def create_or_append_to_cart(cls, product_id, user_id):
        user = User.objects.get(user_id=user_id)
        user_cart = cls.objects.filter(user=user).first()
        product = Product.objects.get(id=product_id)

        if user_cart and not user_cart.is_archived:
            user_cart.products.append(product)
            user_cart.save()
        else:
            cls(dict(user=user, products=[product])).save()

    def clean_cart(self):
        self.products = []
        self.save()


class OrdersHistory(Document):
    user = ReferenceField(User)
    orders = ListField(ReferenceField(Cart))

    @classmethod
    def get_or_create(cls, user):
        history = cls.objects.filter(user=user).first()
        if history:
            return history
        else:
            return cls(user)