import telebot;
import config;
import utils;
from telebot import types;

try:
    bot = telebot.TeleBot(config.BOT_TOKEN)
    print("Бот подключен успешно;")
except BaseException as err:
    print("!!! Возникла ошибка при создании бота: " + config.BOT_TOKEN)
    print(f"Except: {err=}, {type(err)=}")

def get_groups(message):
    userstatus = utils.get_user_status(message.chat.id)
    print("get_groups_UserStatus: "+str(userstatus))
    if userstatus != "Unknown" and userstatus is not None:
        markup = utils.generate_markup_groups()
        question = "Выберите категорию вашего вопроса:"
        bot.send_message(message.from_user.id, text=question, reply_markup=markup);
    else:
        send_user_to_home(message)

def get_telephone(message):
    userstatus = utils.get_user_status(message.chat.id)
    print("get_telephone_UserStatus: "+str(userstatus))
    keyboard_hider = types.ReplyKeyboardRemove()
    if userstatus == "Unknown" or userstatus is None:
        if message.contact is not None:
            tel = message.contact.phone_number
            if utils.auth_user(message.chat.id,tel):
                name = utils.get_user_name(message.chat.id)
                print("Авторизация успешна! Найден пользователь под именем: "+name)
                bot.send_message(message.chat.id, "Поздравляю "+name+"! Вы успешно авторизовались", reply_markup=keyboard_hider)
                utils.set_user_status(message.chat.id, "InGroups")
                get_groups(message)
            else:
                print("!!! Авторизация не удалась! Номер телефона не найден в базе: "+tel)
                bot.send_message(message.chat.id, "Ошибка! вашего номера нет в базе: "+tel, reply_markup=keyboard_hider)
        else:
            send_user_to_home(message)
    else:
        send_user_to_home(message)

def send_user_to_home(message):
    keyboard_hider = types.ReplyKeyboardRemove()
    print("Незарегистрированный пользователь отправил данные: "+message.text)
    bot.send_message(message.chat.id, 'Вы не указали свой контакт! Пройдите авторизацию : /start', reply_markup=keyboard_hider);

@bot.message_handler(commands=["start"])
def start(message): # Название функции не играет никакой роли
    utils.set_user_status(message.chat.id, "Unknown")
    userstatus = utils.get_user_status(message.chat.id)
    print("start_UserStatus: "+str(userstatus))
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
    print("clear_UserStatus: "+str(userstatus))

@bot.message_handler(func=lambda message: True)
def any_answers(message): #Любые сообщения вне логики бота
    userstatus = utils.get_user_status(message.chat.id)
    print("any_answers_UserStatus: "+str(userstatus))
    if userstatus != "Unknown" and userstatus is not None:
        bot.send_message(message.chat.id, "Я не понимаю этого");
    else:
        send_user_to_home(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            userstatus = utils.get_user_status(call.message.chat.id)
            print("callback_inline_UserStatus: "+str(userstatus))
            if userstatus == "InGroups":
                keyboard_hider = types.ReplyKeyboardRemove()
                groups = utils.get_groups()
                for group in groups:
                    if call.data == str(group[3]):
                        #bot.delete_message(call.message.chat.id, call.message.message_id)
                        bot.send_message(call.message.chat.id, group[2], reply_markup=keyboard_hider)
                        #utils.set_user_status(call.message.chat.id, "InGroupDetails")
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")

if __name__ == '__main__':
    try:
        utils.init_data_from_db();
        print("База данных SQL подключена успешно;")
    except BaseException as err:
        print("!!! Возникла ошибка при подключении к базе данных SQL, строка подключения: " + config.CONNECTION_STRING)
        print(f"Exception: {err=}, {type(err)=}")

    bot.infinity_polling()
