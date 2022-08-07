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
            recset = self.cursor.execute("SELECT * FROM [dbo].[groups] with(nolock) WHERE [codename]=?", (str(codename))).fetchone()
        else:
            recset = self.cursor.execute('SELECT * FROM [dbo].[groups] with(nolock)').fetchall()
        return recset

    def get_grouprows(self, idgroup, codename=None):
        """ Получаем все строки по группе """
        if codename is not None:
            recset = self.cursor.execute("SELECT * FROM [dbo].[grouprows] with(nolock) WHERE [idgroup]=? and [commandtext]=?", (int(idgroup),str(codename))).fetchone()
        else:
            recset = self.cursor.execute('SELECT * FROM [dbo].[grouprows] with(nolock) WHERE [idgroup]=?', (int(idgroup))).fetchall()
        return recset

    def get_grouprows_by_split_codename(self, codename):
        """ Получаем все строки по кодовому имени группы и строки """
        splitted_codename = codename.split("_")
        recset = self.cursor.execute("SELECT distinct gr.* "+
        "  FROM [dbo].[groups] g with(nolock) "+
        "    inner join [dbo].[grouprows] gr with(nolock) on gr.idgroup = g.id "+
        "  WHERE g.codename = ? and gr.[commandtext] = ?", (splitted_codename[0],splitted_codename[1])).fetchone()
        return recset

    def get_reports(self, user_id=-1, codename=None):
        """ Получает из базы доступные отчёты """
        #TODO: учитывать доступ пользователя
        if codename is not None:
            recset = self.cursor.execute("SELECT * FROM [dbo].[reports] with(nolock) WHERE [codename]=?", (str(codename))).fetchone()
        else:
            recset = self.cursor.execute('SELECT * FROM [dbo].[reports] with(nolock)').fetchall()
        return recset

    def get_user(self, tel):
        """ Получаем из базы сотрудников """
        recset = self.cursor.execute("SELECT * FROM [dbo].[users] with(nolock) WHERE [tel]=? or '+'+[tel]=?", (tel,tel)).fetchone()
        return recset

    def add_logevent(self, iduser, chat_id, event, status, description):
        """ Делаем запись в лог событий """
        self.cursor.execute("INSERT INTO [dbo].[logevents] "+
        "           ([iduser] "+
        "           ,[chat_id] "+
        "           ,[datetimestamp] "+
        "           ,[event] "+
        "           ,[status] "+
        "           ,[description]) "+
        "     VALUES "+
        "           (? "+
        "           ,? "
        "           ,getdate() "+
        "           ,? "+
        "           ,? "+
        "           ,?) ", (iduser,chat_id,event,status,description))
        self.connection.commit()

    def add_task(self, iduser, last_context, message_text):
        """ Делаем запись в задачи пользователя """
        self.cursor.execute("INSERT INTO [dbo].[dh_tasks] "+
        "           ([iduser] "+
        "           ,[last_context] "+
        "           ,[message_text]) "+
        "     VALUES "+
        "           (? "+
        "           ,? "+
        "           ,? )", (iduser, last_context, message_text))
        self.connection.commit()

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()

if __name__ == '__main__':
    db = mssqlworker(config.CONNECTION_STRING)
    user = db.get_user("380503857563");
    result = user is not None
    if result:
        print("Yep"+user[1])
    db.close