from mongoengine import Document, StringField, IntField, BooleanField, \
    ReferenceField, FloatField, ListField, FileField


class Category(Document):
    title = StringField(max_length=64)
    main = BooleanField()
    sub_categories = ListField(ReferenceField('self'))
    href = StringField(max_length=1000)
    description = StringField(max_length=1000)

    @property
    def category_products(self):
        return Product.objects.filter(category=self, is_available=True)

    @property
    def is_parent(self):
        if self.sub_categories:
            return True


class Product(Document):
    title = StringField(max_length=64)
    image_url = StringField(max_length=1000)
    is_available = BooleanField(default=True)
    href = StringField(max_length=1000)
    description = StringField(max_length=4096)
    price = IntField(min_value=0)
    quantity = IntField(min_value=0)
    is_discount = BooleanField()
    discount = IntField(min_value=0, max_value=100)
    category = ReferenceField(Category)
    weight = FloatField(min_value=0, null=True)
    width = FloatField(min_value=0, null=True)
    height = FloatField(min_value=0, null=True)
