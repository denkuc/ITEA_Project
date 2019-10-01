from models.user import User


class Modules:
    CATEGORY = 'category'
    SUBCATEGORY = 'subcategory'
    PRODUCT = 'product'
    ADD_TO_CART = 'addtocart'
    SUBMIT = 'submit'
    REMOVE_PRODUCT = 'rmproduct'

    @classmethod
    def get_module(cls, call):
        return call.data.split('_')[0]

    @classmethod
    def get_id(cls, call):
        return call.data.split('_')[1]

    @classmethod
    def get_user(cls, message) -> User:
        return User.objects(telegram_id=message.chat.id).first()


def delete_last_message(bot, call):
    bot.delete_message(call.message.chat.id, call.message.message_id)