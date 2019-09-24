from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from config import TOKEN
from common import get_module, get_id, Modules, get_user, \
    delete_last_message
from config import SHOP_URL
from models.product import Category, Product
from models.texts import Texts
from models.user import User

bot = TeleBot(TOKEN)

main_menu_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True,
                                                  resize_keyboard=True)
RU_MENU = ["Категории", "Новости", "Информация для покупателя"]
UA_MENU = ["Категорії", "Новини", "Інформація для покупця"]


@bot.message_handler(commands=['start'])
def greetings(message):
    user_id = message.chat.id
    user = get_user(message)
    if not user:
        user = User()
        user.telegram_id = user_id
        user.language = message.from_user.language_code
        user.save()

    if user.language == 'ru':
        main_menu_keyboard.add(*RU_MENU)
    else:
        main_menu_keyboard.add(*UA_MENU)

    bot.send_message(user_id,
                     Texts.get_text('greetings', user.language),
                     reply_markup=main_menu_keyboard)


@bot.message_handler(func=lambda m: m.text in ["Новости", "Новини"])
def news(message):
    user = get_user(message)
    bot.send_message(user.telegram_id,
                     Texts.get_text('news', user.language),
                     reply_markup=main_menu_keyboard)


@bot.message_handler(func=lambda m: m.text in ["Информация для покупателя",
                                               "Інформація для покупця"])
def info(message):
    user = get_user(message)
    bot.send_message(user.telegram_id,
                     Texts.get_text('information_for_user', user.language),
                     reply_markup=main_menu_keyboard)


@bot.message_handler(func=lambda m: m.text in ["Категорії", "Категории"])
def categories_from_menu(message):
    categories_common(message)


@bot.callback_query_handler(func=lambda call: call.data == Modules.CATEGORY)
def categories_from_inline(call):
    delete_last_message(bot, call)
    categories_common(call.message)


def categories_common(message):
    user = get_user(message)
    categories_keyboard = InlineKeyboardMarkup(row_width=2)
    categories_objects = Category.objects(main=True)

    buttons = []
    for c in categories_objects:
        if c.is_parent:
            callback_data = f'{Modules.CATEGORY}_{c.id}'
        else:
            callback_data = f'{Modules.SUBCATEGORY}_{c.id}'
        buttons.append(InlineKeyboardButton(text=c.title,
                                            callback_data=callback_data))

    categories_keyboard.add(*buttons)
    bot.send_message(user.telegram_id,
                     Texts.get_text('categories', user.language),
                     reply_markup=categories_keyboard)


@bot.callback_query_handler(func=lambda call: get_module(call) == Modules.CATEGORY)
def subcategories_by_cat(call):
    user = get_user(call.message)
    delete_last_message(bot, call)
    category = Category.objects.get(id=get_id(call))
    subcategories = category.sub_categories
    subcategories_kb = InlineKeyboardMarkup(row_width=2)

    buttons = []
    for sc in subcategories:
        if sc.is_parent:
            callback_data = f'{Modules.CATEGORY}_{sc.id}'
        else:
            callback_data = f'{Modules.SUBCATEGORY}_{sc.id}'
        buttons.append(InlineKeyboardButton(text=sc.title,
                                            callback_data=callback_data))
    subcategories_kb.add(*buttons)
    subcategories_kb.add(InlineKeyboardButton(
        text=Texts.get_text('back_to_categories', user.language),
        callback_data=f'{Modules.CATEGORY}')
    )
    bot.send_message(user.telegram_id,
                     text=Texts.get_text('subcategory', user.language),
                     reply_markup=subcategories_kb)


@bot.callback_query_handler(func=lambda call: get_module(call) == Modules.SUBCATEGORY)
def products_by_cat(call):
    user = get_user(call.message)
    category = Category.objects.filter(id=get_id(call)).first()
    products = category.category_products[:5]
    for p in products:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton(
                text=Texts.get_text('add_to_cart', user.language),
                callback_data=f'{Modules.ADD_TO_CART}_{p.id}'),
            InlineKeyboardButton(
                text=Texts.get_text('more_info', user.language),
                callback_data=f'{Modules.PRODUCT}_{p.id}')
        )
        bot.send_photo(user.telegram_id,
                       photo=SHOP_URL+p.image_url,
                       caption=p.title,
                       reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: get_module(call) == Modules.PRODUCT)
def product(call):
    product = Product.objects.get(id=get_id(call))
    discount = '-{}%' if product.discount else ''
    product_text = f'*{product.title}*\n_{product.price}_'
    bot.send_message(call.message.chat.id, text=product_text, parse_mode='MARKDOWN')


@bot.callback_query_handler(func=lambda call: get_module(call) == Modules.ADD_TO_CART)
def add_to_cart(call):
    # cart = Cart.objects.get(id=get_id(call))
    bot.send_message(call.message.chat.id, text='Добавлено')


if __name__ == '__main__':
    bot.polling()
