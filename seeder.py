from mongoengine import connect

from models.texts import Texts

connect('bot_shop')


def seed_texts():
    texts_dict = {
        'greetings': {'ru': "Приветствую в нашем магазине! Выбери действие:",
                      'ua': "Вітаю в нашому магазині! Обери дію:"},
        'news': {'ru': 'Новостей нет.',
                 'ua': 'Новин немає'},
        'information_for_user': {'ru': 'Здесь может быть ваша реклама.',
                                 'ua': "Тут може бути ваша реклама."},
        'categories': {'ru': 'Выберите категорию товара:',
                       'ua': "Оберіть категорію товару:"},
        'back_to_categories': {'ru': "<< Ко всем категориям",
                               'ua': "<< До всіх категорій"},
        'add_to_cart': {'ru': 'В корзину 🛒',
                        'ua': 'В корзину 🛒'},
        'more_info': {'ru': 'Подробнее 📝',
                      'ua': 'Детальніше 📝'},
        'subcategory': {'ru': 'Выберите подкатегорию товара:',
                        'ua': 'Оберіть підкатегорію товару:'},
        'empty_cart': {'ru': 'Корзина пустая!',
                       'ua': 'Корзина порожня!'},
        'remove_product': {'ru': 'Удалить продукт с корзины',
                           'ua': 'Видалити продукт з корзини'},
        'submit': {'ru': 'Оформить заказ',
                   'ua': 'Оформити замовлення'},
        'ask_to_submit': {'ru': 'Подтвердите Ваш заказ',
                          'ua': 'Підтвердіть Ваше замовлення'},
        'thank_you': {'ru': 'Благодарим за ваш заказ',
                      'ua': 'Дякуємо за ваше замовлення'},
    }
    for key, value in texts_dict.items():
        texts = Texts()
        texts.title = key
        texts.text_ru = value['ru']
        texts.text_ua = value['ua']
        texts.save()


if __name__ == '__main__':
    connect("bot_shop")
    # seed_products(50, 10)
    seed_texts()

