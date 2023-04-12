import re
from telebot import types
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from config import DIALOG_DB

alphabet = ' 1234567890-йцукенгшщзхъфывапролджэячсмитьбюёqwertyuiopasdfghjklzxcvbnm?%.,()!:;'

def clean_str(r):
    r = r.lower()
    r = [c for c in r if c in alphabet]
    return ''.join(r)

def get_time():
    return str(datetime.now())+': '

def generate_markup(type_mark, db, detail=None):
    """
    Создаем кастомную клавиатуру согласно типа
    :return: Объект кастомной клавиатуры
    """
    markup = types.InlineKeyboardMarkup(); #клавиатура

    if type_mark == "groups":
        groups = db.get_groups()
        for group in groups:
            item = types.InlineKeyboardButton(text=str(group[1]), callback_data=str(group[3]))
            markup.add(item)
        item = types.InlineKeyboardButton(text="<-Назад", callback_data="<-back")
        markup.add(item)

    if type_mark == "reports":
        reports = db.get_reports()
        for report in reports:
            item = types.InlineKeyboardButton(text=str(report[1]), callback_data=str(report[3]))
            markup.add(item)
        item = types.InlineKeyboardButton(text="<-Назад", callback_data="<-back")
        markup.add(item)

    if type_mark == "menu":
        item = types.InlineKeyboardButton(text="Получить отчёт", callback_data="reports")
        markup.add(item)
        item = types.InlineKeyboardButton(text="Получить инструкцию", callback_data="groups")
        markup.add(item)
        item = types.InlineKeyboardButton(text="Задать вопрос (тест)", callback_data="dialog")
        markup.add(item)

    if type_mark == "grouprows":
        grouprows = db.get_grouprows(detail[0])
        for grouprow in grouprows:
            item = types.InlineKeyboardButton(text=str(grouprow[2]), callback_data=str(detail[3]+"_"+grouprow[3]))
            markup.add(item)
        item = types.InlineKeyboardButton(text="<-Назад", callback_data="<-back")
        markup.add(item)

    return markup

def generate_markup_tel(tel, geo):
    """
    Создаем кастомную клавиатуру для отправки данных с телефона
    :param tel: Параметр определяет, нужно ли включать кнопку отправки телефона
    :param geo: Параметр определяет, нужно ли включать кнопку отправки геолокации
    :return: Объект кастомной клавиатуры
    """
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)

    if tel:
        button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
        markup.add(button_phone);
    if geo:
        button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
        markup.add(button_geo);
    return markup


def update_dictagent():
    with open(DIALOG_DB, encoding='utf-8') as f:
        content = f.read()

    blocks = content.split('\n')
    dataset = []

    for block in blocks:
        replicas = block.split('\\')[:2]
        if len(replicas) == 2:
            pair = [clean_str(replicas[0]), clean_str(replicas[1])]
            if pair[0] and pair[1]:
                dataset.append(pair)

    X_text = []
    y = []

    for question, answer in dataset[:10000]:
        X_text.append(question)
        y += [answer]

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(X_text)

    clf = LogisticRegression()
    clf.fit(X, y)

    return vectorizer, clf


def add_answer(question, messagetext):
    a = f"{question}\{messagetext.lower()} \n"
    with open(DIALOG_DB, "a", encoding='utf-8') as f:
        f.write(a)
