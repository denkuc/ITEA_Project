import time

from bson import ObjectId
from flask import Flask, request, abort
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, Update

from config import TOKEN, START_KEYBOARD
from common import Modules, delete_last_message
from config import SHOP_URL
from models.product import Category, Product
from models.cart import Cart, OrdersHistory
from models.texts import Texts
from models.user import User
from webhook import WEBHOOK_URL_BASE, WEBHOOK_URL_PATH, WEBHOOK_SSL_CERT, \
    WEBHOOK_LISTEN, WEBHOOK_PORT, WEBHOOK_SSL_PRIV

bot = TeleBot(TOKEN)
app = Flask(__name__)


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


main_menu_keyboard = ReplyKeyboardMarkup(one_time_keyboard=True,
                                         resize_keyboard=True)
RU_MENU = ["Категории", "Новости", "Информация для покупателя", "Корзина"]
UA_MENU = ["Категорії", "Новини", "Інформація для покупця", "Корзина"]


@bot.message_handler(commands=['start'])
def greetings(message):
    user = User.get_or_create_user(message)

    if user.language == 'ru':
        main_menu_keyboard.add(*RU_MENU)
    else:
        main_menu_keyboard.add(*UA_MENU)

    bot.send_message(user.user_id,
                     text=Texts.get_text('greetings', user.language),
                     reply_markup=main_menu_keyboard)


@bot.message_handler(func=lambda m: m.text in START_KEYBOARD['news'])
def news(message):
    user = User.get_or_create_user(message)
    bot.send_message(user.user_id,
                     Texts.get_text('news', user.language),
                     reply_markup=main_menu_keyboard)


@bot.message_handler(func=lambda m: m.text in START_KEYBOARD['info'])
def info(message):
    user = User.get_or_create_user(message)
    bot.send_message(user.user_id,
                     Texts.get_text('information_for_user', user.language),
                     reply_markup=main_menu_keyboard)


@bot.message_handler(func=lambda m: m.text in START_KEYBOARD['categories'])
def categories_from_menu(message):
    categories_common(message)


@bot.message_handler(func=lambda message: message.text == START_KEYBOARD['cart'])
def show_cart(message):
    user = User.get_or_create_user(message)
    current_user = User.objects.get(user_id=message.chat.id)
    cart = Cart.objects.filter(user=current_user, is_archived=False).first()

    if not cart:
        bot.send_message(message.chat.id,
                         text=Texts.get_text('empty_cart', user.language))
        return

    if not cart.products:
        bot.send_message(message.chat.id,
                         text=Texts.get_text('empty_cart', user.language))
        return

    for product in cart.products:
        remove_keyboard = InlineKeyboardMarkup()
        remove_button = InlineKeyboardButton(
            text=Texts.get_text('remove_product', user.language),
            callback_data='rmproduct_' + str(product.id)
        )
        remove_keyboard.add(remove_button)
        bot.send_message(message.chat.id,
                         text=f'{product.title} {product.price} грн.',
                         reply_markup=remove_keyboard)

    submit_keyboard = InlineKeyboardMarkup()
    submit_button = InlineKeyboardButton(
        text=Texts.get_text('submit', user.language),
        callback_data='submit'
    )
    submit_keyboard.add(submit_button)
    bot.send_message(message.chat.id,
                     text=Texts.get_text('ask_to_submit', user.language),
                     reply_markup=submit_keyboard)


@bot.callback_query_handler(func=lambda call: call.data == Modules.CATEGORY)
def categories_from_inline(call):
    delete_last_message(bot, call)
    categories_common(call.message)


def categories_common(message):
    user = User.get_or_create_user(message)
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
    bot.send_message(message.chat.id,
                     text=Texts.get_text('categories', user.language),
                     reply_markup=categories_keyboard)


@bot.callback_query_handler(
    func=lambda call: Modules.get_module(call) == Modules.CATEGORY)
def subcategories_by_cat(call):
    user = User.get_or_create_user(call.message)
    delete_last_message(bot, call)
    category = Category.objects.get(id=Modules.get_id(call))
    subcategories = category.sub_categories
    subcategories_kb = InlineKeyboardMarkup(row_width=2)

    buttons = []
    for subcategory in subcategories:
        if subcategory.is_parent:
            callback_data = f'{Modules.CATEGORY}_{subcategory.id}'
        else:
            callback_data = f'{Modules.SUBCATEGORY}_{subcategory.id}'
        buttons.append(InlineKeyboardButton(text=subcategory.title,
                                            callback_data=callback_data))
    subcategories_kb.add(*buttons)
    subcategories_kb.add(InlineKeyboardButton(
        text=Texts.get_text('back_to_categories', user.language),
        callback_data=f'{Modules.CATEGORY}'
    ))
    bot.send_message(call.message.chat.id,
                     text=Texts.get_text('subcategory', user.language),
                     reply_markup=subcategories_kb)


@bot.callback_query_handler(
    func=lambda call: Modules.get_module(call) == Modules.SUBCATEGORY)
def products_by_cat(call):
    user = User.get_or_create_user(call.message)
    category = Category.objects.filter(id=Modules.get_id(call)).first()
    products = category.category_products[:5]
    for product in products:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton(
                text=Texts.get_text('add_to_cart', user.language),
                callback_data=f'{Modules.ADD_TO_CART}_{product.id}'),
            InlineKeyboardButton(
                text=Texts.get_text('more_info', user.language),
                callback_data=f'{Modules.PRODUCT}_{product.id}'))
        bot.send_photo(call.message.chat.id,
                       photo=SHOP_URL+product.image_url,
                       caption=product.title,
                       reply_markup=keyboard)


@bot.callback_query_handler(
    func=lambda call: Modules.get_module(call) == Modules.PRODUCT)
def product(call):
    product = Product.objects.get(id=Modules.get_id(call))
    discount = '-{}%' if product.discount else ''
    product_text = f'*{product.title}*\n_{product.price}_ {discount}'
    bot.send_message(call.message.chat.id,
                     text=product_text,
                     parse_mode='MARKDOWN')


@bot.callback_query_handler(
    func=lambda call: Modules.get_module(call) == Modules.ADD_TO_CART)
def add_to_card(call):
    Cart.create_or_append_to_cart(product_id=Modules.get_id(call),
                                  user_id=call.message.chat.id)
    cart = Cart.objects.all().first()


@bot.callback_query_handler(
    func=lambda call: Modules.get_module(call) == Modules.REMOVE_PRODUCT)
def rm_product_from_cart(call):
    user = User.get_or_create_user(call.message)
    cart = Cart.objects.get(user=user)
    cart.update(pull__products=ObjectId(Modules.get_id(call)))
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(
    func=lambda call: Modules.get_module(call) == Modules.SUBMIT)
def submit_cart(call):
    user = User.get_or_create_user(call.message)
    current_user = User.objects.get(user_id=call.message.chat.id)
    cart = Cart.objects.filter(user=current_user, is_archived=False).first()
    cart.is_archived = True

    order_history = OrdersHistory.get_or_create(current_user)
    order_history.orders.append(cart)
    bot.send_message(call.message.chat.id,
                     text=Texts.get_text('thank_you', user.language))
    cart.save()
    order_history.save()


bot.remove_webhook()

time.sleep(0.1)

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Start flask server
app.run(host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
        debug=True)
