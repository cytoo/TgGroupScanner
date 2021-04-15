from sqlite3 import *
from typing import Union


class DB:
    def __init__(self):
        self.db = connect("app.db")
        self.cr = self.db.cursor()
        self.cr.execute("create table if not exists `users`(user_id INTEGER, username TEXT, chat TEXT)")

    async def get_user(
            self, user_id=None, username=None
    ) -> list:
        self.cr.execute("select * from `users` where user_id = ?", (user_id,)) if user_id else self.cr.execute(
            "select * from `users` where username = ?", (username,))
        data = self.cr.fetchall()
        return data

    async def insert_user(
            self, user_id: Union[str, int], username: str, chat: Union[str, int]
    ):
        self.cr.execute("select * from `users` where user_id = ? and chat = ?", (user_id, chat))
        results = self.cr.fetchall()
        if results:
            return
        self.cr.execute(
            "insert into `users`(user_id, username, chat) values(?, ?, ?)",
            (user_id, username, chat)
        )
        self.db.commit()
