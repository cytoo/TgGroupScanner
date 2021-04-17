from sqlite3 import *
from typing import Union


class DB:
    def __init__(self):
        self.db = connect("app.db")
        self.cr = self.db.cursor()
        self.cr.execute("create table if not exists `users`(user_id INTEGER, username TEXT, chat_name TEXT, "
                        "chat_username TEXT, chat_id INTEGER)")

    def __del__(self):
        self.db.close()

    async def get_user(
            self, user_id=None, username=None
    ) -> list:

        self.cr.execute("select * from `users` where user_id = ?", (user_id,)) if user_id else self.cr.execute(
            "select * from `users` where username = ?", (username,))
        data = self.cr.fetchall()
        return data

    async def get_all(
            self
    ) -> list:
        self.cr.execute("select * from users")
        res = self.cr.fetchall()
        return res

    async def insert_user(
            self,
            user_id: Union[str, int],
            username: str,
            chat_id: Union[str, int],
            chat_name: str,
            chat_username: str
    ):
        self.cr.execute("select * from `users` where user_id = ? and chat_id = ?", (user_id, chat_id))
        results = self.cr.fetchall()
        if results:
            return
        self.cr.execute(
            "insert into `users`(user_id, username, chat_id, chat_name, chat_username) values(?, ?, ?, ?, ?)",
            (user_id, username, chat_id, chat_name, chat_username)
        )
        self.db.commit()
