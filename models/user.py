from mongoengine import Document, StringField, IntField


# class Cart(Document):
#     ...


class User(Document):
    telegram_id = IntField(max_value=9999999999999)
    name = StringField(max_length=255)
    surname = StringField(max_length=255)
    nickname = StringField(max_length=255)
    user_state = IntField(min_value=0)
    language = StringField(max_length=2)
    # user_cart = ReferenceField(Cart)
