from models.user import User


def get_module(call):
    return call.data.split('_')[0]


def get_id(call):
    return call.data.split('_')[1]


class Modules:
    CATEGORY = 'category'
    SUBCATEGORY = 'subcategory'
    PRODUCT = 'product'
    ADD_TO_CART = 'addtocart'


def get_user(message) -> User:
    return User.objects(telegram_id=message.chat.id).first()


def delete_last_message(bot, call):
    bot.delete_message(call.message.chat.id, call.message.message_id)