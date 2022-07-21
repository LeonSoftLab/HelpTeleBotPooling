import pyodbc;

class mssqlworker:

    def __init__(self, constr):
        self.connection = pyodbc.connect(constr, autocommit=True)
        self.cursor = self.connection.cursor()

    def select_all_groups(self):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM [dbo].[groups] with(nolock)').fetchall()

    def select_all_grouprows(self):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM [dbo].[grouprows] with(nolock)').fetchall()

    def select_all_users(self):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM [dbo].[users] with(nolock)').fetchall()

#    def select_user(self, tel):
#        """ Получаем одну строку пользователя по номеру телефона """
#        with self.connection:
#            return self.cursor.execute('SELECT [id] ,[name] ,[tel] FROM [dbo].[users] with(nolock) where [tel] = ?', (tel,)).fetchall()[0]

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()
