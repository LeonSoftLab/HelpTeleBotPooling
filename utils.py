from telebot import types;
from datetime import datetime;

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
