import shelve;
from mssqlworker import mssqlworker;
from config import SHELVE_NAME, CONNECTION_STRING;
from telebot import types;

def groups(db):
    """
    Данный метод считает проекты в базе данных и сохраняет в хранилище.
    """
    all_groups = db.select_all_groups()
    with shelve.open(SHELVE_NAME) as storage:
        storage['all_groups'] = all_groups

def grouprows(db):
    """
    Данный метод считает детализацию (пункты меню) для проектов в базе данных и сохраняет в хранилище.
    """
    all_grouprows = db.select_all_grouprows()
    with shelve.open(SHELVE_NAME) as storage:
        storage['all_grouprows'] = all_grouprows

def users(db):
    """
    Данный метод считает пользователей в базе данных и сохраняет в хранилище.
    """
    all_users = db.select_all_users()
    with shelve.open(SHELVE_NAME) as storage:
        storage['all_users'] = all_users

def reports(db):
    """
    Данный метод считает отчёты в базе данных и сохраняет в хранилище.
    """
    all_reports = db.select_all_reports()
    with shelve.open(SHELVE_NAME) as storage:
        storage['all_reports'] = all_reports

def init_data_from_db():
    """
    Данный метод запускает все процедуры считывания данных из базы.
    """
    _db = mssqlworker(CONNECTION_STRING)
    groups(_db)
    grouprows(_db)
    users(_db)
    reports(_db)
    _db.close()

def get_groups():
    """
    Получает из хранилища группы вопросов(проекты)
    """
    with shelve.open(SHELVE_NAME) as storage:
        all_groups = storage['all_groups']
    return all_groups

def get_reports():
    """
    Получает из хранилища доступные отчёты
    """
    #TODO: предусмотреть доступ к отчёту
    with shelve.open(SHELVE_NAME) as storage:
        all_reports = storage['all_reports']
    return all_reports

def get_group_bycodename(codename):
    """
    Получает из хранилища группу по заданному кодовому имени(вызов)
    """
    result = None
    with shelve.open(SHELVE_NAME) as storage:
        all_groups = storage['all_groups']
        for group in all_groups:
            if group[3] == codename:
                result = group
    return result

def get_report_bycodename(codename):
    """
    Получает из хранилища отчет по заданному кодовому имени(вызов)
    """
    result = None
    with shelve.open(SHELVE_NAME) as storage:
        all_reports = storage['all_reports']
        for report in all_reports:
            if report[3] == codename:
                result = report
    return result

def get_grouprows(group_id):
    """
    Получает из хранилища подпункты для проекта
    :param chat_id: id чата юзера
    """
    with shelve.open(SHELVE_NAME) as storage:
        all_grouprows = storage['all_grouprows']
        grouprows = list()
        for grouprow in all_grouprows:
            if grouprow[1] == group_id:
                grouprows.append(grouprow)
    return grouprows

def get_grouprow_bycodename(codename):
    """
    Получает из хранилища группу по заданному кодовому имени(вызов)
    """
    result = None
    with shelve.open(SHELVE_NAME) as storage:
        splitted_codename = codename.split("_")
        group = get_group_bycodename(splitted_codename[0])
        all_grouprows = get_grouprows(group[0])
        for grouprow in all_grouprows:
            if grouprow[3] == splitted_codename[1]:
                result = grouprow
    return result

def get_users():
    """
    Получает из хранилища пользователей
    """
    with shelve.open(SHELVE_NAME) as storage:
        all_users = storage['all_users']
    return all_users

def generate_markup(type_mark, detail=None):
    """
    Создаем кастомную клавиатуру согласно типа
    :return: Объект кастомной клавиатуры
    """
    markup = types.InlineKeyboardMarkup(); #клавиатура

    if type_mark == "groups":
        groups = get_groups()
        for group in groups:
            item = types.InlineKeyboardButton(text=str(group[1]), callback_data=str(group[3]))
            markup.add(item)
        item = types.InlineKeyboardButton(text="<-Назад", callback_data="<-back")
        markup.add(item)

    if type_mark == "reports":
        reports = get_reports()
        for report in reports:
            item = types.InlineKeyboardButton(text=str(report[1]), callback_data=str(report[3]))
            markup.add(item)
        item = types.InlineKeyboardButton(text="<-Назад", callback_data="<-back")
        markup.add(item)

    if type_mark == "menu":
        item = types.InlineKeyboardButton(text="Получить отчёты", callback_data="reports")
        markup.add(item)
        item = types.InlineKeyboardButton(text="Получить помощь", callback_data="groups")
        markup.add(item)

    if type_mark == "grouprows":
        grouprows = get_grouprows(detail[0])
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
