import telebot as tb

from lesson12.task_with_telegram.config import TOKEN
from lesson12.task_with_telegram.models.user import User

from mongoengine import connect
connect("tg_shop")

bot = tb.TeleBot(TOKEN)

main_menu_keyboard = tb.types.ReplyKeyboardMarkup(one_time_keyboard=True)
main_menu_keyboard.add("Ввести ФИО",
                       "Ввести почту",
                       "Ввести адрес",
                       "Ввести номер телефона",
                       "Предложить что-то")


def get_user(message):
    return User.objects(telegram_id=message.chat.id)[0]


@bot.message_handler(commands=['start', 'menu'])
def main_menu(message):
    user_id = message.chat.id
    try:
        get_user(message)
    except IndexError:
        user = User()
        user.telegram_id = user_id
        user.save()

    bot.send_message(user_id,
                     "Добро пожаловать. Введите информацию о себе",
                     reply_markup=main_menu_keyboard)


@bot.message_handler(func=lambda m: m.text == "Ввести ФИО")
def enter_name(message):
    user = get_user(message)
    user.state = "entering_name"
    user.save()
    bot.send_message(user.telegram_id, "Введите ФИО:")


@bot.message_handler(func=lambda m: m.text == "Ввести номер телефона")
def enter_phone_number(message):
    user = get_user(message)
    user.state = "entering_phone_number"
    user.save()
    bot.send_message(user.telegram_id, "Введите номер телефона цифрами:")


@bot.message_handler(func=lambda m: m.text == "Ввести адрес")
def enter_address(message):
    user = get_user(message)
    user.state = "entering_address"
    user.save()
    bot.send_message(user.telegram_id, "Введите адрес:")


@bot.message_handler(func=lambda m: m.text == "Ввести почту")
def enter_email(message):
    user = get_user(message)
    user.state = "entering_email"
    user.save()
    bot.send_message(user.telegram_id, "Введите почту:")


@bot.message_handler(func=lambda m: m.text == "Предложить что-то")
def add_suggestion(message):
    user = get_user(message)
    user.state = "entering_suggestion"
    user.save()
    bot.send_message(user.telegram_id, "Введите предложение:")


@bot.message_handler(func=lambda m: get_user(m).state == "entering_name")
def entered_name(message):
    user = get_user(message)
    user.name = message.text
    user.state = None
    user.save()
    bot.send_message(user.telegram_id,
                     "ФИО введены. Выберите пункт главного меню.",
                     reply_markup=main_menu_keyboard)


@bot.message_handler(func=lambda m: get_user(m).state == "entering_phone_number")
def entered_phone_number(message):
    user = get_user(message)
    user.phone_number = message.text
    user.state = None
    user.save()
    bot.send_message(user.telegram_id,
                     "Номер телефона введен. Выберите пункт главного меню.",
                     reply_markup=main_menu_keyboard)


@bot.message_handler(func=lambda m: get_user(m).state == "entering_address")
def entered_address(message):
    user = get_user(message)
    user.address = message.text
    user.state = None
    user.save()
    bot.send_message(user.telegram_id,
                     "Адрес введен. Выберите пункт главного меню.",
                     reply_markup=main_menu_keyboard)


@bot.message_handler(func=lambda m: get_user(m).state == "entering_email")
def entered_email(message):
    user = get_user(message)
    user.email = message.text
    user.state = None
    user.save()
    bot.send_message(user.telegram_id,
                     "Почта введена. Выберите пункт главного меню.",
                     reply_markup=main_menu_keyboard)


@bot.message_handler(func=lambda m: get_user(m).state == "entering_suggestion")
def added_suggestion(message):
    user = get_user(message)
    if user.suggestions:
        user.suggestions.append(message.text)
    else:
        user.suggestions = [message.text]
    user.state = None
    user.save()
    bot.send_message(user.telegram_id,
                     "Предложение добавлено. Выберите пункт главного меню.",
                     reply_markup=main_menu_keyboard)


if __name__ == '__main__':
    bot.polling()
