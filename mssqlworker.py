import pyodbc;
import config;

class mssqlworker:

    def __init__(self, constr):
        self.connection = pyodbc.connect(constr, autocommit=True)
        self.cursor = self.connection.cursor()

    def get_groups(self, codename=None):
        """
        Получает из базы группы вопросов(проекты)
        """
        if codename is not None:
            recset = self.cursor.execute("SELECT * FROM [dbo].[groups] with(nolock) WHERE [codename]=?", (codename)).fetchall()
        else:
            recset = self.cursor.execute('SELECT * FROM [dbo].[groups] with(nolock)').fetchall()
        return recset

    def get_grouprows(self, idgroup, codename=None):
        """ Получаем все строки по группе """
        if codename is not None:
            recset = self.cursor.execute("SELECT * FROM [dbo].[grouprows] with(nolock) WHERE [idgroup]=? and [commandtext]=?", (idgroup,codename)).fetchall()
        else:
            recset = self.cursor.execute('SELECT * FROM [dbo].[grouprows] with(nolock) WHERE [idgroup]=?', (idgroup)).fetchall()
        return recset

    def get_grouprows_by_split_codename(self, codename):
        """ Получаем все строки по кодовому имени группы и строки """
        splitted_codename = codename.split("_")
        recset = self.cursor.execute("SELECT distinct gr.* "+
        "  FROM [dbo].[groups] g with(nolock) "+
        "    inner join [dbo].[grouprows] gr with(nolock) on gr.idgroup = g.id "+
        "  WHERE g.codename = ? and gr.[commandtext] = ?", (splitted_codename[0],splitted_codename[1])).fetchall()
        return recset

    def get_reports(self, user_id=-1, codename=None):
        """ Получает из базы доступные отчёты """
        #TODO: учитывать доступ пользователя
        if codename is not None:
            recset = self.cursor.execute("SELECT * FROM [dbo].[reports] with(nolock) WHERE [codename]=?", (codename)).fetchall()
        else:
            recset = self.cursor.execute('SELECT * FROM [dbo].[reports] with(nolock)').fetchall()
        return recset

    def get_user(self, tel):
        """ Получаем из базы сотрудников """
        recset = self.cursor.execute("SELECT * FROM [dbo].[users] with(nolock) WHERE [tel]=? or '+'+[tel]=?", (tel,tel)).fetchall()
        return recset

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()

db = mssqlworker(config.CONNECTION_STRING)
users = db.get_user("380503857563");
result = False
if len(users)>0:
    result = True
    print(users[0][0])
    print("---Авторизация успешна! Найден пользователь под именем: "+users[0][1])
if result == False:
    print("!!! Авторизация не удалась! Номер телефона не найден в базе: ")
db.close