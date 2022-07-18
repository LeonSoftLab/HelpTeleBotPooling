import shelve
from mssqlworker import mssqlworker
from config import shelve_name, CONNECTION_STRING
from telebot import types

def groups(db):
    """
    Данный метод считает проекты в базе данных и сохраняет в хранилище.
    """
    all_groups = db.select_all_groups()
    with shelve.open(shelve_name) as storage:
        storage['all_groups'] = all_groups

def users(db):
    """
    Данный метод считает пользователей в базе данных и сохраняет в хранилище.
    """
    all_users = db.select_all_users()
    with shelve.open(shelve_name) as storage:
        storage['all_users'] = all_users

def init_data_from_db():
    """
    Данный метод запускает все процедуры считывания данных из базы.
    """
    _db = mssqlworker(CONNECTION_STRING)
    groups(_db)
    users(_db)
    _db.close()

def get_groups():
    """
    Получает из хранилища группы
    """
    with shelve.open(shelve_name) as storage:
        all_groups = storage['all_groups']
    return all_groups

def get_users():
    """
    Получает из хранилища пользователей
    """
    with shelve.open(shelve_name) as storage:
        all_users = storage['all_users']
    return all_users

def set_user_status(chat_id, user_status):
    """
    Записываем юзера в список и запоминаем его текущий статус.
    :param chat_id: id чата юзера
    :param user_status: статус юзера
    """
    with shelve.open(shelve_name) as storage:
        storage[str(chat_id)+"_user_status"] = user_status

def set_user_id(chat_id, user_id):
    """
    Записываем юзера в список и запоминаем id из базы данных.
    :param chat_id: id чата юзера
    :param user_id: id юзера из базы
    """
    with shelve.open(shelve_name) as storage:
        storage[str(chat_id)+"_user_id"] = str(user_id)

def clear_user_data(chat_id):
    """
    Чистим данные юзера в хранилище.
    :param chat_id: id чата юзера
    """
    with shelve.open(shelve_name) as storage:
        del storage[str(chat_id)+"_user_id"]
        del storage[str(chat_id)+"_user_status"]

def auth_user(chat_id, tel_num):
    """
    авторизация пользователя
    В случае, если человека не нашли в базе, возвращаем None
    """
    users = get_users();
    result = False
    for user in users:
        if user[2] == tel_num:
            result = True
            set_user_status(chat_id, "Authorized")
            set_user_id(chat_id, user[0])
    return result;

def get_user_status(chat_id):
    """
    Получаем статус текущего юзера.
    В случае, если человек не авторизован, возвращаем None
    :param chat_id: id юзера
    :return: (str) Текущий статус
    """
    with shelve.open(shelve_name) as storage:
        try:
            result = storage[str(chat_id)+"_user_status"]
            return result
        # Если человек не авторизован, ничего не возвращаем
        except KeyError:
            return None

def get_user_name(chat_id):
    """
    Получаем имя текущего юзера.
    В случае, если человек не авторизован, возвращаем None
    :param chat_id: id юзера
    :return: (str) Имя из базы
    """
    result = None
    with shelve.open(shelve_name) as storage:
        users = get_users();
        id_ = storage[str(chat_id)+"_user_id"]
        for user in users:
            if user[0] == int(id_):
                result = user[1]
    return result

def generate_markup_groups():
    """
    Создаем кастомную клавиатуру для категорий вопросов
    :return: Объект кастомной клавиатуры
    """
    markup = types.InlineKeyboardMarkup(); #клавиатура

    groups = get_groups()
    for group in groups:
        item = types.InlineKeyboardButton(text=str(group[1]), callback_data=str(group[3]))
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
