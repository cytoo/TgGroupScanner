import mysql.connector
from typing import Union


class DB:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="",
            user="",
            passwd="",
            database=""
        )
        self.cr = self.db.cursor()
        self.cr.execute("create table if not exists `users`(user_id INTEGER, username TEXT, chat TEXT)")

    def __del__(self):
        self.db.close()

    async def get_user(
            self, user_id=None, username=None
    ) -> list:

        self.cr.execute("select * from `users` where user_id = %s", (user_id,)) if user_id else self.cr.execute(
            "select * from `users` where username = %s", (username,))
        data = self.cr.fetchall()
        return data

    async def insert_user(
            self, user_id: Union[str, int], username: str, chat: Union[str, int]
    ):
        self.cr.execute("select * from `users` where user_id = %s and chat = %s", (user_id, chat))
        results = self.cr.fetchall()
        if results:
            return
        self.cr.execute(
            "insert into `users`(user_id, username, chat) values(%s, %s, %s)",
            (user_id, username, chat)
        )
        self.db.commit()
