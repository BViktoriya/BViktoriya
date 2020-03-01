import sqlite3


class MyDataBase:
    def __init__(self, database_name):
        self.conn = sqlite3.connect(database_name)
        cursor = self.conn.cursor()

        with open('create_schema.sql', 'rt') as f:
            query = f.read()
            cursor.executescript(query)

            self.conn.commit()
        cursor.close()

    def close(self):
        self.conn.close()

    def add_users(self, fio, viber_id, t_last_answer):
        query = '''
                INSERT INTO users (fio, viber_id, t_last_answer)
                VALUES (?, ?, ?)
                '''
        try:
            self.conn.execute(query, (fio, viber_id, t_last_answer))
            self.conn.commit()
        except:
            self.conn.rollback()

    def add_learning(self, user_id, word, t_last_correct_answer):
        query = '''
                INSERT INTO learning (user_id, word, t_last_correct_answer)
                VALUES (?, ?, ?)
                '''
        try:
            self.conn.execute(query, (user_id, word, t_last_correct_answer))
            self.conn.commit()
        except:
            self.conn.rollback()

    # def add_game(self, user_id):
    #     query = '''
    #             INSERT INTO learning (user_id, count_all, count_correct)
    #             VALUES (?, 0, 0)
    #             '''
    #     try:
    #         self.conn.execute(query, (user_id,))
    #         self.conn.commit()
    #     except:
    #         self.conn.rollback()

    def find_user(self, viber_id):
        query = '''
                SELECT user_id FROM users 
                WHERE viber_id = ?
                '''
        ret_value = self.conn.execute(query, (viber_id, )).fetchall()
        return ret_value

    def last_game(self, user_id):
        query = '''
                SELECT * FROM game 
                WHERE user_id = ? and game_id = (
                                                    SELECT MAX(game_id)
                                                    FROM game
                                                    WHERE user_id = ?
                                                )
                '''
        ret_value = self.conn.execute(query, (user_id, user_id)).fetchall()
        return ret_value

    def find_learning(self, user_id, word):
        query = '''
                SELECT * FROM learning 
                WHERE user_id = ? and word = ?
                '''
        ret_value = self.conn.execute(query, (user_id, word)).fetchall()
        return ret_value

    def update_learning(self, user_id, word):
        query = '''
                UPDATE learning 
                SET correct_answer = correct_answer + 1  
                WHERE user_id = ? and word = ?
                '''
        try:
            self.conn.execute(query, (user_id, word))
            self.conn.commit()
        except:
            self.conn.rollback()

    def count_corrcect_word(self, user_id):
        query = '''
                SELECT COUNT (*) FROM learning 
                WHERE user_id = ? and correct_answer > 10
                '''
        ret_value = self.conn.execute(query, (user_id, )).fetchone()
        return ret_value

    def last_visit(self, viber_id):
        query = '''
                SELECT t_last_answer
                FROM users 
                WHERE viber_id = ?
                '''
        ret_value = self.conn.execute(query, (viber_id, )).fetchone()
        return ret_value
