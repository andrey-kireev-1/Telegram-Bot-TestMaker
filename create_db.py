import sqlite3
import config

conn = sqlite3.connect(config.DB_FILENAME)
cur = conn.cursor()
cur.execute('CREATE TABLE users_tests(hash TEXT, owner TEXT, test_name TEXT, test_description TEXT, question_text TEXT, question_answers TEXT, question_answers_rate TEXT, results TEXT)')