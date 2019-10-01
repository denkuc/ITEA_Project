from random import randint, uniform

from mongoengine import connect

import requests as r
from bs4 import BeautifulSoup
from sqlalchemy.sql.functions import random

from models.product import Category, Product
from config import SHOP_URL

connect("bot_shop")


def get_soup(url):
    return BeautifulSoup(r.get(url).content)


def get_soup_for_obj(obj):
    url = f'{SHOP_URL}{obj.href}'
    return get_soup(url)


def create_categories():
    soup = get_soup(SHOP_URL)
    menu_tag = soup.find('div', {'class': 'menu'})
    category_tags = menu_tag.find_all('a')
    for category_tag in category_tags:
        category_name = category_tag.text
        category_obj = Category.objects(title=category_name).first()
        if not category_obj:
            category_obj = Category()
            category_obj.href = category_tag.get('href')
            category_obj.title = category_tag.text
            category_obj.main = True
            create_and_setup_categories(category_obj)
            category_obj.save()


def create_and_setup_categories(category_obj):
    category_soup = get_soup_for_obj(category_obj)
    try:
        category_obj.description = category_soup.\
            find('div', {'class': 'categoryDesc'}).\
            find('p').text
    except:
        category_obj.description = ''
    category_obj.save()
    try:
        sub_category_tags = category_soup.\
            find('table', {'class': 'categoryList'}). \
            find_all('td', {'class': 'categoryListItem'})
        for sub_category_tag in sub_category_tags[:5]:
            category_obj.sub_categories.append(get_sub_category(sub_category_tag))
        category_obj.save()
    except:
        product_tags = category_soup.find_all('td', {'class': 'prodWrap'})
        for product_tag in product_tags[:5]:
            product_obj = Product()
            product_obj.category = category_obj
            product_obj.href = product_tag.find('a').get('href')
            product_obj.image_url = product_tag.\
                find('td', {'class': 'imageWrap'}).find('img').get('src')
            product_obj.title = product_tag.\
                find('div', {'class': 'productsname'}).find('a').text
            product_obj.save()


def get_sub_category(sub_category_tag):
    category_obj = Category()
    category_obj.href = sub_category_tag.find('h2').find('a').get('href')
    category_obj.title = sub_category_tag.find('h2').find('a').text
    create_and_setup_categories(category_obj)
    category_obj.save()

    return category_obj


def setup_product_info():
    for product_obj in Product.objects().all():
        product_soup = get_soup_for_obj(product_obj)
        product_obj.views = 0
        try:
            try:
                product_price = product_soup. \
                    find('span', {'class': 'price sale'}). \
                    find('b', {'class': 'int'}).text. \
                    replace('\xa0', '')
                product_obj.is_discount = True
                product_obj.discount = product_soup. \
                    find('td', {'class': 'salePercent'}).find('b').text
            except:
                product_price = product_soup. \
                    find('span', {'class': 'price'}). \
                    find('b', {'class': 'int'}).text. \
                    replace('\xa0', '')
                product_obj.is_discount = False
            product_obj.price = int(product_price)
            product_obj.availability = True
            product_obj.quantity = randint(1, 10)
        except:
            product_obj.availability = False
            product_obj.quantity = 0
        product_obj.weight = uniform(0, 100)
        product_obj.height = uniform(0, 100)
        product_obj.width = uniform(0, 100)
        product_obj.save()


if __name__ == '__main__':
    # create_categories()
    setup_product_info()
