import sqlite3


class UsersBD:
    def __init__(self):
        self.con = sqlite3.connect("bd\\users.db", check_same_thread=False)
        self.cur = self.con.cursor()
    
    def add_user(self, nickname, clas, chat_id=''):  # chat_id might be not defined for the tests
        if self.check_user_in_bd(nickname):
            self.cur.execute(f'''UPDATE users_table SET clas = '{clas}', chat_id={chat_id}
                        WHERE nickname = "{nickname}"''')
        else:
            self.cur.execute(f"""INSERT INTO users_table(nickname, clas, sendmessages, chat_id)
                                VALUES('{nickname}','{clas}', 1, {chat_id})""")
        self.con.commit()

    def get_clas(self, nickname):
        result = self.cur.execute(f"""SELECT Clas FROM users_table
                    WHERE nickname = '{nickname}'""").fetchone()
        return result[0]
    
    def get_clas_if_notifications_on(self, nickname):
        # if notifications on - return clas. else return false
        result = self.cur.execute(f"""SELECT Clas, SendMessages FROM users_table
                    WHERE nickname = '{nickname}'""").fetchone()
        if result[1]:
            return result[0]
        else:
            return False
    
    def turn_notifications_off_on(self, nickname):
        result = self.cur.execute(f"""SELECT SendMessages FROM users_table
                    WHERE nickname = '{nickname}'""").fetchone()[0]
        result = not(result)

        self.cur.execute(f'''UPDATE users_table SET SendMessages = {result}
                        WHERE nickname = "{nickname}"''')
        self.con.commit()
        if result:
            return 'Уведомления были включены'
        return 'Уведомления были выключены'
    
    def check_user_in_bd(self, nickname):
        result = self.cur.execute(f"""SELECT Clas FROM users_table
                    WHERE nickname = '{nickname}'""").fetchall()
        if len(result) == 0:
            return False
        return True
    
    def get_list_of_all_users(self):
        result = self.cur.execute(f"""SELECT nickname, chat_id FROM users_table
                    WHERE SendMessages = 'true'""").fetchall()
        return result
        
    def add_test_data(self):
        self.add_user('@guy', '9a')
        self.add_user('@guy1', '10a')
        self.add_user('@guy2', '11a')
        self.add_user('@guy3', '11в')

    def clear_db(self):
        self.con.execute("""drop table users_table""")
        self.con.execute("""create table users_table (
                                nickname char(255),
                                clas char(255),
                                sendmessages bool
                                )""")

    def __del__(self):
        self.con.close()


def tests():
    # better be run in main.py
    users = UsersBD()

    users.add_test_data()
    users.add_user('@random_guy', '11d')
    print(users.get_clas('@random_guy'))  # 11d
    users.add_user('@random_guy', '14d') # class is changed
    print(users.get_clas('@random_guy'))  # 14d

    print(users.get_clas_if_notifications_on('@random_guy'))  # 14d
    users.turn_notifications_off_on('@random_guy')
    print(users.get_clas_if_notifications_on('@random_guy'))  # false
    users.clear_db()

