from mongoengine import Document, StringField, connect

connect('bot_shop')


class Texts(Document):
    RU_LANGUAGE = 'ru'

    title = StringField()
    text_ru = StringField(max_length=4096)
    text_ua = StringField(max_length=4096)

    @classmethod
    def get_text(cls, title, language):
        if language == cls.RU_LANGUAGE:
            return cls.objects.filter(title=title).first().text_ru
        else:
            return cls.objects.filter(title=title).first().text_ua
