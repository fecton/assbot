import sqlite3
from typing import Union


class DbCore:
    def __init__(self) -> None:
        from data.config import DB_NAME
        self._path_to_db = DB_NAME

    @property
    def connection(self) -> sqlite3:
        return sqlite3.connect(self._path_to_db)

    def execute(self, sql_queries: str, parameters: Union[list, tuple] = (),
                fetchone=False, fetchall=False, commit=False, via_percent=False) -> list:

        if isinstance(parameters, list):
            parameters = tuple(parameters)

        connection = self.connection
        cursor = connection.cursor()

        if fetchone:
            return cursor.execute(sql_queries, parameters).fetchone()
        elif fetchall:
            return cursor.execute(sql_queries, parameters).fetchall()
        else:
            cursor.execute(sql_queries, parameters)

        if commit:
            connection.commit()

        connection.close()

    def create_group_table(self, group_id: int) -> None:
        query = """
            CREATE TABLE `%d`(
            user_id       INTEGER     PRIMARY KEY NOT NULL,
            username      VARCHAR(35)             NOT NULL,
            name          VARCHAR(255)            NOT NULL,
            length        INTEGER                 NOT NULL,
            endtime       INTEGER                 NOT NULL,
            spamcount     INTEGER                 NOT NULL,
            blacklisted   BOOLEAN                 NOT NULL,
            luck_timeleft INTEGER                 NOT NULL
        )""" % group_id

        connection = self.connection
        cursor = connection.cursor()

        cursor.execute(query)
        connection.commit()

        connection.close()

    def create_reports_table(self) -> None:
        query = """
            CREATE TABLE `reports` (
                group_id    INTEGER        NOT NULL,
                group_name  VARCHAR(255)   NOT NULL,
                user_id     INTEGER        NOT NULL,
                username    VARCHAR(35)    NOT NULL,
                name        VARCHAR(255)   NOT NULL,
                message     TEXT           NOT NULL
            )
        """

        connection = self.connection
        cursor = connection.cursor()

        cursor.execute(query)
        connection.commit()
        connection.close()

    def create_groups_name_table(self) -> None:
        query = """
            CREATE TABLE `groups_name` (
                group_id    INTEGER      NOT NULL,
                group_name  VARCHAR(255) NOT NULL
            )
        """

        connection = self.connection
        cursor = connection.cursor()

        cursor.execute(query)
        connection.commit()
        connection.close()

    def insert_into_groups_name(self, parameters: tuple = ()) -> None:
        query = """
            INSERT INTO `groups_name` (group_id, group_name)
            VALUES (?,?)
        """

        connection = self.connection
        cursor = connection.cursor()

        cursor.execute(query, parameters)

        connection.commit()
        connection.close()

    def insert_into_reports(self, parameters: tuple = ()) -> None:
        query = """
            INSERT INTO `reports` (group_id, group_name, user_id, username, name, message)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        connection = self.connection

        cursor = connection.cursor()
        cursor.execute(query, parameters)
        connection.commit()
        connection.close()
