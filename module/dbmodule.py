import pymysql


class Database:
    def __init__(self):
        # password, db -> 언제 입력하는지 확인
        self.db = pymysql.connect(host='localhost',
                                  user='root',
                                  password='1q2w3e',
                                  db='medilearn_db',
                                  charset='utf8')
        # pymysql.cursors.DictCursor -> 무슨 기능을 하는지 확인
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)

    def execute(self, query, args={}):
        self.cursor.execute(query, args)

    def executeOne(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchone()
        return row

    def executeAll(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchall()
        return row

    def commit(self):
        self.db.commit()
