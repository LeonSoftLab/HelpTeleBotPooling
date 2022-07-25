import telebot;
import utils;
import client;
from telebot import types;
from config import BOT_TOKEN, DIR_REPOSITORY;

clients = client.Clients()

try:
    bot = telebot.TeleBot(BOT_TOKEN)
    print("--- Бот подключен успешно;")
except BaseException as err:
    print("!!! Возникла ошибка при создании бота: " + BOT_TOKEN)
    print(f"!!! Except: {err=}, {type(err)=}")


def get_menu(message):
    user = clients.get_client(message.chat.id)
    user.to_log("get_menu")
    if user.status != "Unknown":
        markup = utils.generate_markup_menu()
        question = "Выберите пункт меню:"
        bot.send_message(message.chat.id, text=question, reply_markup=markup);
    else:
        send_user_to_home(message)

def get_groups(message):
    user = clients.get_client(message.chat.id)
    user.to_log("get_groups")
    if user.status != "Unknown":
        markup = utils.generate_markup_groups()
        question = "К какой категории относится Ваш вопрос?"
        bot.send_message(message.chat.id, text=question, reply_markup=markup);
    else:
        send_user_to_home(message)

def get_reports(message):
    user = clients.get_client(message.chat.id)
    user.to_log("get_groups")
    if user.status != "Unknown":
        markup = utils.generate_markup_reports()
        question = "Выберите отчёт:"
        bot.send_message(message.chat.id, text=question, reply_markup=markup);
    else:
        send_user_to_home(message)

def get_grouprows(message,group):
    user = clients.get_client(message.chat.id)
    user.to_log("get_grouprows")
    if user.status != "Unknown":
        markup = utils.generate_markup_grouprows(group)
        question = "Выберите пункт и я отправлю Вам файл:"
        bot.send_message(message.chat.id, text=question, reply_markup=markup);
    else:
        send_user_to_home(message)

def send_user_to_home(message):
    keyboard_hider = types.ReplyKeyboardRemove()
    print(str(message.chat.id)+": Незарегистрированный пользователь отправил данные: "+message.text)
    bot.send_message(message.chat.id, 'Вы не указали свой контакт! Пройдите авторизацию : /start', reply_markup=keyboard_hider);

def get_telephone(message):
    user = clients.get_client(message.chat.id)
    user.to_log("get_telephone")
    keyboard_hider = types.ReplyKeyboardRemove()
    if user.status != "Unknown":
        if message.contact is not None:
            tel = message.contact.phone_number
            if user.auth(message.contact.phone_number):
                bot.send_message(message.chat.id, "Спасибо "+user.name+", Вы успешно авторизовались. \n"+
                    "Ваша Роль: "+user.role, reply_markup=keyboard_hider)
                user.status = "InMenu"
                get_menu(message)
            else:
                bot.send_message(message.chat.id, "Ошибка! вашего номера нет в базе: "+message.contact.phone_number, reply_markup=keyboard_hider)
        else:
            send_user_to_home(message)
    else:
        send_user_to_home(message)

def document_send(message, file_name):
    with open(file_name, 'rb') as new_file:
        print(str(call.message.chat.id)+": document_send: "+file_name)
        bot.send_document(message.chat.id, new_file)

@bot.message_handler(commands=["start"])
def start(message): # Название функции не играет никакой роли
    user = clients.get_client(message.chat.id)
    user.to_log("start")
    markup = utils.generate_markup_tel(True,False)
    bot.send_message(message.chat.id, "Чтобы авторизоваться, отправьте мне свой номер телефона пожалуйста", reply_markup=markup)
    bot.register_next_step_handler(message, get_telephone)

@bot.message_handler(commands=["clear"])
def clear(message): # чистка состояния и чата
    user = clients.get_client(message.chat.id)
    user.to_log("clear")
    user.clear()
    bot.delete_message(message.chat.id, message.message_id)
    keyboard_hider = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Данные очищены", reply_markup=keyboard_hider)

@bot.message_handler(func=lambda message: True)
def any_answers(message): #Любые сообщения вне логики бота
    user = clients.get_client(message.chat.id)
    user.to_log("any_answers: "+message.text)
    if user.status != "Unknown":
        #TODO: Отправить вопрос пользователя на поддержку
        bot.send_message(message.chat.id, "Спасибо за Ваш вопрос, сейчас я его отправлю профильному специалисту. Ожидайте ответа.");
    else:
        send_user_to_home(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            user = clients.get_client(message.chat.id)
            user.to_log("callback_inline: call.data: "+str(call.data))
            if user.status == "InMenu":
                keyboard_hider = types.ReplyKeyboardRemove()
                codename = call.data
                bot.delete_message(call.message.chat.id, call.message.message_id)
                if codename == "reports":
                    user.status = "InReports"
                    get_reports(call.message)
                elif codename == "groups":
                    user.status = "InGroups"
                    get_groups(call.message)
            elif user.status == "InReports":
                keyboard_hider = types.ReplyKeyboardRemove()
                if call.data != "<-back":
                    report = utils.get_report_bycodename(call.data)
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    bot.send_message(call.message.chat.id, "Отчёт:\n"+report[1]+"\nОписание отчёта:\n"+report[2], reply_markup=keyboard_hider)
                    bot.send_message(call.message.chat.id, "Подождите немного, я отправляю файл: "+report[4], reply_markup=keyboard_hider)
                    document_send(call.message,DIR_REPOSITORY+report[4])
                else:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    user.status = "InMenu"
                    get_menu(call.message)
            elif user.status == "InGroups":
                keyboard_hider = types.ReplyKeyboardRemove()
                if call.data != "<-back":
                    group = utils.get_group_bycodename(call.data)
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    bot.send_message(call.message.chat.id, "Категория:\n"+group[1]+"\nОписание категории:\n"+group[2], reply_markup=keyboard_hider)
                    user.status = "InGroupRows"
                    get_grouprows(call.message,group)
                else:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    user.status = "InMenu"
                    get_menu(call.message)
            elif user.status == "InGroupRows":
                keyboard_hider = types.ReplyKeyboardRemove()
                if call.data != "<-back":
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    grouprow = utils.get_grouprow_bycodename(call.data)
                    bot.send_message(call.message.chat.id, "Подождите немного, я отправляю файл: "+grouprow[2], reply_markup=keyboard_hider)
                    document_send(call.message,DIR_REPOSITORY+grouprow[4])
                else:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    user.status = "InGroups"
                    get_groups(call.message)
            else:
                keyboard_hider = types.ReplyKeyboardRemove()
                bot.send_message(call.message.chat.id, "Неизвестная кнопка: "+call.data, reply_markup=keyboard_hider)
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")

if __name__ == '__main__':

    try:
        utils.init_data_from_db();
        print("--- База данных SQL подключена успешно;")
    except BaseException as err:
        print("!!! Возникла ошибка при инициализации базы данных SQL")
        print(f"!!! Exception: {err=}, {type(err)=}")

    bot.infinity_polling()
