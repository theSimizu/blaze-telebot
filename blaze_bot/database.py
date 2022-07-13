import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

host = os.getenv('host')
dbname = os.getenv('dbname')
user = os.getenv('user')
password = os.getenv('password')
port = os.getenv('port')



conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
cursor = conn.cursor()

class Users:
    def __init__(self) -> None:
        pass

    @staticmethod
    def filter_by(by, value):
        try:
            cursor.execute(f"SELECT * FROM users WHERE {by} = '{value}';")
            return Query(cursor.fetchall())
        except Exception as ex:
            print(ex)

    @staticmethod
    def create_user(name, telegram, email=''):
        try:
            cursor.execute\
                (f'''
                    INSERT INTO users (name, telegram, email) VALUES ('{name}', '{telegram}', '{email}');
                ''')
            conn.commit()
            return Users.filter_by('telegram', telegram)
        except Exception as ex:
            print(ex)

    @staticmethod
    def get_users_from_strategy(data):
        try:
            strategy = ''.join(data).replace('red', 'V')\
                                    .replace('black', 'P')\
                                    .replace('white', 'B')
            cursor.execute\
                (f'''
                    SELECT * FROM strategies WHERE '{strategy}' LIKE concat('%', sequence)
                
                ''')
            return cursor.fetchall()
            
        except:
            pass

class Query:
        def __init__(self, query) -> None:
            self._id, self.name, self.telegram, self.email = query[0]

        def create_strategy(self, name, sequence, choice):
            cursor.execute\
                (f'''
                    INSERT INTO strategies (name, sequence, choice, creation_date, user_id) 
                    VALUES ('{name}', '{sequence}', '{choice}', '{datetime.utcnow()}', {self._id});
                ''')
            
            conn.commit()

        def add_email(self, email):
                cursor.execute\
                    (f'''
                        UPDATE users
                        SET email='{email}'
                        WHERE telegram='{self.telegram}';
                    ''')
                conn.commit()
        
        def get_strategies(self):
            cursor.execute\
                (f'''
                    SELECT name, sequence, choice FROM strategies WHERE user_id='{self._id}';
                ''')
            return cursor.fetchall()
        
        def delete_strategies(self, message):
            cursor.execute\
                (f'''
                    DELETE FROM strategies WHERE user_id='{self._id}' AND name='{message.text}';
                ''')
            conn.commit()




