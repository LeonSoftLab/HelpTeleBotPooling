import utils;
from telebot import types;

class Client:
    """Класс содержащий информацию по юзеру"""
    def __init__(self, chat_id, bot):
        self.chat_id = chat_id
        self.bot = bot
        self.status = "Unknown"
        self.role = "User"
        self.name = ""

    def clear(self):
        """Чистим данные юзера."""
        self.to_log("clear")
        self.status = "Unknown"
        self.role = "User"
        self.name = ""
        keyboard_hider = types.ReplyKeyboardRemove()
        self.bot.send_message(self.chat_id, "Данные очищены", reply_markup=keyboard_hider)

    def to_log(self, msg):
        """Запись в лог событий"""
        print(str(self.chat_id)+": "+msg+": ")

    def auth(self, tel_num):
        """
        авторизация пользователя
        В случае, если человека не нашли в базе, возвращаем False
        """
        users = utils.get_users();
        result = False
        for user in users:
            if user[2] == tel_num or "+"+str(user[2]) == tel_num:
                result = True
                self.name = user[1]
                self.role = user[3]
                self.status = "Authorized"
                self.to_log("---Авторизация успешна! Найден пользователь под именем: "+user[1])
        if result == False:
            self.to_log("!!! Авторизация не удалась! Номер телефона не найден в базе: "+tel_num)
        return result

    def goto_(self, type_mark, message, detail=None):
        self.to_log(type_mark)
        if self.status != "Unknown":
            markup = utils.generate_markup(type_mark, detail)
            if type_mark == "menu":
                question = "Выберите пункт меню:"
            elif type_mark == "groups":
                question = "К какой категории относится Ваш вопрос?"
            elif type_mark == "reports":
                question = "Выберите отчёт:"
            elif type_mark == "grouprows":
                question = "Выберите пункт и я отправлю Вам файл:"
            self.status = type_mark
            self.bot.send_message(self.chat_id, text=question, reply_markup=markup)
        else:
            self.send_to_home(message)

    def goto_telephone(message):
        self.to_log("telephone")
        keyboard_hider = types.ReplyKeyboardRemove()
        if message.contact is not None:
            if self.auth(message.contact.phone_number):
                self.bot.send_message(self.chat_id, "Спасибо "+user.name+", Вы успешно авторизовались. \n"+
                    "Ваша Роль: "+user.role, reply_markup=keyboard_hider)
                self.goto_("menu", message)
            else:
                self.bot.send_message(self.chat_id, "Ошибка! вашего номера нет в базе: "+message.contact.phone_number, reply_markup=keyboard_hider)
        else:
            self.send_to_home(message)

    def send_to_home(self, message):
        keyboard_hider = types.ReplyKeyboardRemove()
        print(str(self.chat_id)+": Незарегистрированный пользователь отправил данные: "+message.text)
        self.bot.send_message(self.chat_id, 'Вы не указали свой контакт! Пройдите авторизацию : /start', reply_markup=keyboard_hider)

class Clients:
    """Класс для работы с подключёнными клиентами"""
    def __init__(self, bot):
        self.client_list = []
        self.bot = bot

    def get_client(self, chat_id):
        result = None
        for client in self.client_list:
            if client.chat_id == chat_id:
                result = client
        if result is None:
            result = Client(chat_id, self.bot)
            self.client_list.append(result)
        return result

    def del_client(self, chat_id):
        result = False
        for client in self.client_list:
            if client.chat_id == chat_id:
                result = True
                self.client_list.remove(client)
        return result