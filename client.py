import utils;
from telebot import types;

class Client:
    """Класс содержащий информацию по юзеру"""
    def __init__(self, chat_id, bot, db):
        self.chat_id = chat_id
        self.bot = bot
        self.db = db
        self.status = "Unknown"
        self.role = "User"
        self.name = ""
        self.id = -1
        self.last_context =""
        self.list_messages = []

    def clear(self):
        """Чистим данные юзера."""
        self.to_log("clear")
        self.status = "Unknown"
        self.role = "User"
        self.name = ""
        self.id = -1
        self.last_context =""
        #TODO: пройтись по списку self.list_messages и поудалять сообщения
        #bot.delete_message(message.chat.id, message.message_id)
        
        keyboard_hider = types.ReplyKeyboardRemove()
        self.bot.send_message(self.chat_id, "Данные очищены", reply_markup=keyboard_hider)

    def to_log(self, msg):
        """Запись в лог событий"""
        print(utils.get_time()+str(self.chat_id)+": "+msg+": ")
        event = msg.split(":")[0]
        description = ":".join(msg.split(":")[1:])
        self.db.add_logevent(self.id, self.chat_id, event, self.status, description)

    def to_task(self, message_text):
        """Запись в лог событий"""
        self.to_log("to_task")
        self.db.add_task(self.id, self.last_context, message_text)

    def auth(self, tel_num):
        """
        авторизация пользователя
        В случае, если человека не нашли в базе, возвращаем False
        """
        user = self.db.get_user(tel_num);
        result = user is not None
        if result:
            self.id = user[0]
            self.name = user[1]
            self.role = user[3]
            self.status = "Authorized"
            self.to_log("auth: ---Авторизация успешна! Найден пользователь под именем: "+user[1])
        else:
            self.to_log("auth: !!! Авторизация не удалась! Номер телефона не найден в базе: "+tel_num)
        return result

    def goto_(self, type_mark, message, detail=None):
        self.to_log(type_mark)
        #if not any(word in self.status for word in ["Unknown", "dialog"]):
        if self.status != "Unknown":
            if type_mark != "dialog":
                markup = utils.generate_markup(type_mark, self.db, detail)
                if type_mark == "menu":
                    question = "Выберите пункт меню:"
                elif type_mark == "groups":
                    question = "Выберите проект:"
                elif type_mark == "reports":
                    question = "Выберите отчёт:"
                elif type_mark == "grouprows":
                    question = "Выберите какой файл нужно отправить, если Вы не нашли нужного файла, напишите запрос в поддержку."
                self.status = type_mark
                self.bot.send_message(self.chat_id, text=question, reply_markup=markup)
            else:
                self.status = type_mark
                keyboard_hider = types.ReplyKeyboardRemove()
                self.bot.send_message(self.chat_id, "Пожалуйста, задайте мне свой вопрос.", reply_markup=keyboard_hider)
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
        print(utils.get_time()+str(self.chat_id)+": send_to_home: Незарегистрированный пользователь отправил данные: "+message.text)
        self.bot.send_message(self.chat_id, 'Вы не указали свой контакт! Пройдите авторизацию : /start', reply_markup=keyboard_hider)

class Clients:
    """Класс для работы с подключёнными клиентами"""
    def __init__(self, bot, db):
        self.client_list = []
        self.bot = bot
        self.db = db

    def get_client(self, chat_id):
        result = None
        for client in self.client_list:
            if client.chat_id == chat_id:
                result = client
        if result is None:
            result = Client(chat_id, self.bot, self.db)
            self.client_list.append(result)
        return result

    def del_client(self, chat_id):
        result = False
        for client in self.client_list:
            if client.chat_id == chat_id:
                result = True
                self.client_list.remove(client)
        return result