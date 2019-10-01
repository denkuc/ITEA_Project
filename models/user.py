from mongoengine import Document, StringField, IntField


# class Cart(Document):
#     ...


class User(Document):
    user_id = IntField(max_value=9999999999999)
    language = StringField(max_length=2)
    name = StringField()
    surname = StringField()
    nickname = StringField()
    user_state = IntField()

    @classmethod
    def get_or_create_user(cls, message):
        user = cls.objects.filter(user_id=message.from_user.id).first()
        if user:
            return user
        else:
            return cls(user_id=message.from_user.id,
                       language=message.from_user.language_code,
                       name=message.from_user.first_name,
                       surname=message.from_user.last_name,
                       nickname=message.from_user.username).save()
