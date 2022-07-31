import telebot;
import utils;
import client;
from mssqlworker import mssqlworker;
from telebot import types;
from config import CONNECTION_STRING, BOT_TOKEN, DIRCONNECTION_STRING, _REPOSITORY;

try:
    db = mssqlworker(CONNECTION_STRING)
    print("--- База данных SQL подключена успешно;")
except BaseException as err:
    print("!!! Возникла ошибка при инициализации базы данных SQL")
    print(f"!!! Exception: {err=}, {type(err)=}")

try:
    bot = telebot.TeleBot(BOT_TOKEN)
    print("--- Бот подключен успешно;")
except BaseException as err:
    print("!!! Возникла ошибка при создании бота: " + BOT_TOKEN)
    print(f"!!! Except: {err=}, {type(err)=}")

clients = client.Clients(bot)

def get_telephone(message):
    user = clients.get_client(message.chat.id)
    user.to_log("get_telephone")
    keyboard_hider = types.ReplyKeyboardRemove()
    if message.contact is not None:
        tel = message.contact.phone_number
        if user.auth(message.contact.phone_number):
            bot.send_message(message.chat.id, "Спасибо "+user.name+", Вы успешно авторизовались. \n"+
                "Ваша Роль: "+user.role, reply_markup=keyboard_hider)
            user.goto_("menu", message)
        else:
            bot.send_message(message.chat.id, "Ошибка! вашего номера нет в базе: "+message.contact.phone_number, reply_markup=keyboard_hider)
    else:
        user.send_to_home(message)

def document_send(message, file_name):
    with open(file_name, 'rb') as new_file:
        print(str(message.chat.id)+": document_send: "+file_name)
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
    user.to_log("Main:clear")
    user.clear()

@bot.message_handler(commands=["menu"])
def menu(message): # вернуться в главное меню
    user = clients.get_client(message.chat.id)
    user.to_log("Main:menu")
    user.goto_("menu", message)

@bot.message_handler(func=lambda message: True)
def any_answers(message): #Любые сообщения вне логики бота
    user = clients.get_client(message.chat.id)
    user.to_log("any_answers: "+user.status+": "+message.text)
    if user.status != "Unknown":
        #TODO: Отправить вопрос пользователя на поддержку
        bot.send_message(message.chat.id, "Спасибо за Ваш вопрос, сейчас я его отправлю профильному специалисту. Ожидайте ответа.");
    else:
        user.send_to_home(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            user = clients.get_client(call.message.chat.id)
            user.to_log("callback_inline: call.data: "+str(call.data))
            if user.status == "menu":
                keyboard_hider = types.ReplyKeyboardRemove()
                codename = call.data
                bot.delete_message(call.message.chat.id, call.message.message_id)
                if codename == "reports":
                    user.goto_("reports", call.message)
                elif codename == "groups":
                    user.goto_("groups", call.message)
            elif user.status == "reports":
                keyboard_hider = types.ReplyKeyboardRemove()
                if call.data != "<-back":
                    report = utils.get_report_bycodename(call.data)
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    bot.send_message(call.message.chat.id, "Отчёт:\n"+report[1]+"\nОписание отчёта:\n"+report[2], reply_markup=keyboard_hider)
                    bot.send_message(call.message.chat.id, "Подождите немного, я отправляю файл: "+report[4], reply_markup=keyboard_hider)
                    document_send(call.message,DIR_REPOSITORY+report[4])
                else:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    user.goto_("menu", call.message)
            elif user.status == "groups":
                keyboard_hider = types.ReplyKeyboardRemove()
                if call.data != "<-back":
                    group = utils.get_group_bycodename(call.data)
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    bot.send_message(call.message.chat.id, "Категория:\n"+group[1]+"\nОписание категории:\n"+group[2], reply_markup=keyboard_hider)
                    user.goto_("grouprows", call.message, group)
                else:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    user.goto_("menu", call.message)
            elif user.status == "grouprows":
                keyboard_hider = types.ReplyKeyboardRemove()
                if call.data != "<-back":
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    grouprow = utils.get_grouprow_bycodename(call.data)
                    bot.send_message(call.message.chat.id, "Подождите немного, я отправляю файл: "+grouprow[2], reply_markup=keyboard_hider)
                    document_send(call.message,DIR_REPOSITORY+grouprow[4])
                else:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    user.goto_("groups", call.message)
            else:
                keyboard_hider = types.ReplyKeyboardRemove()
                bot.send_message(call.message.chat.id, "Неизвестная кнопка: "+call.data, reply_markup=keyboard_hider)
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")

if __name__ == '__main__':

    bot.infinity_polling()
