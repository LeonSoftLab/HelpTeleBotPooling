import telebot;
import config;
import utils;
from telebot import types;

try:
    bot = telebot.TeleBot(config.BOT_TOKEN)
    print("--- Бот подключен успешно;")
except BaseException as err:
    print("!!! Возникла ошибка при создании бота: " + config.BOT_TOKEN)
    print(f"!!! Except: {err=}, {type(err)=}")

def get_groups(message):
    userstatus = utils.get_user_status(message.chat.id)
    print(str(message.chat.id)+": get_groups: "+str(userstatus))
    if userstatus != "Unknown" and userstatus is not None:
        markup = utils.generate_markup_groups()
        question = "К какой категории относится Ваш вопрос?"
        bot.send_message(message.chat.id, text=question, reply_markup=markup);
    else:
        send_user_to_home(message)

def get_grouprows(message,group):
    userstatus = utils.get_user_status(message.chat.id)
    print(str(message.chat.id)+": get_grouprows: "+str(userstatus))
    if userstatus != "Unknown" and userstatus is not None:
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
    userstatus = utils.get_user_status(message.chat.id)
    print(str(message.chat.id)+": get_telephone: "+str(userstatus))
    keyboard_hider = types.ReplyKeyboardRemove()
    if userstatus == "Unknown" or userstatus is None:
        if message.contact is not None:
            tel = message.contact.phone_number
            if utils.auth_user(message.chat.id,tel):
                name = utils.get_user_name(message.chat.id)
                print(str(message.chat.id)+": ---Авторизация успешна! Найден пользователь под именем: "+name)
                bot.send_message(message.chat.id, "Спасибо "+name+", Вы успешно авторизовались. \n"+
                    "Ваша Роль: "+str(utils.get_user_role(message.chat.id)), reply_markup=keyboard_hider)
                utils.set_user_status(message.chat.id, "InGroups")
                get_groups(message)
            else:
                print(str(message.chat.id)+": !!! Авторизация не удалась! Номер телефона не найден в базе: "+tel)
                bot.send_message(message.chat.id, "Ошибка! вашего номера нет в базе: "+tel, reply_markup=keyboard_hider)
        else:
            send_user_to_home(message)
    else:
        send_user_to_home(message)

def document_send(message, file_name):
    with open(file_name, 'rb') as new_file:
        bot.send_document(message.chat.id, new_file)

@bot.message_handler(commands=["start"])
def start(message): # Название функции не играет никакой роли
    utils.set_user_status(message.chat.id, "Unknown")
    userstatus = utils.get_user_status(message.chat.id)
    print(str(message.chat.id)+": start: "+str(userstatus))
    markup = utils.generate_markup_tel(True,False)
    bot.send_message(message.chat.id, "Чтобы авторизоваться, отправьте мне свой номер телефона пожалуйста", reply_markup=markup)
    bot.register_next_step_handler(message, get_telephone)

@bot.message_handler(commands=["clear"])
def clear(message): # чистка состояния и чата
    utils.clear_user_data(message.chat.id)
    bot.delete_message(message.chat.id, message.message_id)
    utils.set_user_status(message.chat.id, "Unknown")
    userstatus = utils.get_user_status(message.chat.id)
    keyboard_hider = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Данные очищены", reply_markup=keyboard_hider)
    print(str(message.chat.id)+": clear: "+str(userstatus))

@bot.message_handler(func=lambda message: True)
def any_answers(message): #Любые сообщения вне логики бота
    userstatus = utils.get_user_status(message.chat.id)
    print(str(message.chat.id)+": any_answers: "+str(userstatus)+": message: "+message.text)
    if userstatus != "Unknown" and userstatus is not None:
        bot.send_message(message.chat.id, "Я не понимаю этого");
    else:
        send_user_to_home(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            userstatus = utils.get_user_status(call.message.chat.id)
            print(str(call.message.chat.id)+": callback_inline: "+str(userstatus)+": call.data: "+str(call.data))
            if userstatus == "InGroups":
                keyboard_hider = types.ReplyKeyboardRemove()
                group = utils.get_group_bycodename(call.data)
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, "Категория:\n"+group[1]+"\nОписание категории:\n"+group[2], reply_markup=keyboard_hider)
                utils.set_user_status(call.message.chat.id, "InGroupRows")
                get_grouprows(call.message,group)
                #TODO: Подумать над уровнями (в callbackdata) Реализация подменю
            elif userstatus == "InGroupRows":
                keyboard_hider = types.ReplyKeyboardRemove()
                if call.data != "<-back":
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    grouprow = utils.get_grouprow_bycodename(call.data)
                    bot.send_message(call.message.chat.id, "Подождите немного, я отправляю файл: "+grouprow[2], reply_markup=keyboard_hider)
                    print(config.DIR_REPOSITORY+grouprow[4])
                    document_send(call.message,config.DIR_REPOSITORY+grouprow[4])
                else:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    utils.set_user_status(call.message.chat.id, "InGroups")
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
        print("!!! Возникла ошибка при подключении к базе данных SQL, строка подключения: " + config.CONNECTION_STRING)
        print(f"!!! Exception: {err=}, {type(err)=}")
    bot.infinity_polling()
