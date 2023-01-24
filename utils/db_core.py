import sqlite3
from sqlite3.dbapi2 import connect
from typing import Union
from data.structures import ReportStructure


class DbCore:
    def __init__(self) -> None:
        from data.config import DB_NAME
        self._path_to_db = DB_NAME

    @property
    def connection(self) -> sqlite3:
        return sqlite3.connect(self._path_to_db)

    def execute(self, sql_query: str = "", parameters: Union[list, tuple] = (),
                fetchone: bool = False, fetchall: bool = False, commit: bool = False) -> list:

        if isinstance(parameters, list):
            parameters = tuple(parameters)

        connection = self.connection

        query_output = connection.cursor().execute(sql_query, parameters)


        if fetchone:
            return query_output.fetchone()
        elif fetchall:
            return query_output.fetchall()

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

        self.execute(query, commit=True)


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
        self.execute(query, commit=True)


    def create_groups_name_table(self) -> None:
        query = """
            CREATE TABLE `groups_name` (
                group_id    INTEGER      NOT NULL,
                group_name  VARCHAR(255) NOT NULL
            )
        """
        self.execute(query, commit=True)


    def insert_into_groups_name(self, parameters: tuple = ()) -> None:
        query = """
            INSERT INTO `groups_name` (group_id, group_name)
            VALUES (?,?)
        """
        self.execute(query, parameters, commit=True)


    def insert_into_reports(self, rd: ReportStructure) -> None:
        assert type(rd) == ReportStructure

        query = "INSERT INTO `reports` (group_id, group_name, user_id, username, name, message) "
        query += f"VALUES ({rd.chat_id}, \"{rd.chat_title}\", {rd.user_id}, \"{rd.user_name}\", \"{rd.user_firstname}\", \"{rd.message}\")"
        self.execute(query, commit=True)


