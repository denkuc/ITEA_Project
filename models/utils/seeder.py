import random
import string

from mongoengine import connect

from models.texts import Texts
from models.product import Product, Category


def random_string(string_length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(string_length))


def random_bool():
    return random.choice([True, False])


def seed_and_get_category(num_of_cats):
    category_list = []
    for i in range(num_of_cats):
        cat = Category()
        cat.title = random_string()
        cat.save()
        category_list.append(cat)
    return category_list


def seed_products(num_of_products, num_of_cats):
    category_list = seed_and_get_category(num_of_cats)
    subcategories = seed_and_get_category(3)

    category_obj = category_list[0]
    for sc in subcategories:
        category_obj.sub_categories.append(sc)

    category_obj.save()

    category_list = category_list + subcategories
    for i in range(num_of_products):
        product = Product()
        product.title = random_string()
        product.description = random_string()
        product.price = random.randint(1000, 100000)
        product.is_available = random_bool()
        product.is_discount = random_bool()
        product.quantity = random.randint(0, 100)
        product.category = random.choice(category_list)
        product.weight = random.uniform(0, 100)
        product.height = random.uniform(0, 100)
        product.width = random.uniform(0, 100)

        product.save()


def seed_texts():
    texts_dict = {
        # 'greetings': {'ru': "Приветствую в нашем магазине! Выбери действие:",
        #               'ua': "Вітаю в нашому магазині! Обери дію:"},
        # 'news': {'ru': 'Новостей нет.',
        #          'ua': 'Новин немає'},
        # 'information_for_user': {'ru': 'Здесь может быть ваша реклама.',
        #                          'ua': "Тут може бути ваша реклама."},
        # 'categories': {'ru': 'Выберите категорию товара:',
        #                'ua': "Оберіть категорію товару:"},
        # 'back_to_categories': {'ru': "<< Ко всем категориям",
        #                        'ua': "<< До всіх категорій"},
        # 'add_to_cart': {'ru': 'В корзину 🛒',
        #                 'ua': 'В корзину 🛒'},
        # 'more_info': {'ru': 'Подробнее 📝',
        #               'ua': 'Детальніше 📝'},
        'subcategory': {'ru': 'Выберите подкатегорию товара:',
                        'ua': 'Оберіть підкатегорію товару:'},
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

