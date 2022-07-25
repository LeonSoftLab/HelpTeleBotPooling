import utils;

class Client:
    """Класс содержащий информацию по юзеру"""
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.status = "Unknown"
        self.role = "User"
        self.name = ""

    def clear(self):
        """Чистим данные юзера."""
        with self:
            status = "Unknown"
            role = "User"
            name = ""

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

class Clients:
    """Класс для работы с подключёнными клиентами"""
    def __init__(self):
        self.client_list = []

    def get_client(self, chat_id):
        result = None
        for client in self.client_list:
            if client.chat_id == chat_id:
                result = client
        if result is None:
            result = Client(chat_id)
            self.client_list.append(result)
        return result

    def del_client(self, chat_id):
        result = False
        for client in self.client_list:
            if client.chat_id == chat_id:
                result = True
                self.client_list.remove(client)
        return result