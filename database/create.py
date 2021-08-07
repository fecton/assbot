CREATE_table_groups = """
    CREATE TABLE `%d`(
    user_id       INTEGER     PRIMARY KEY NOT NULL,
    username      VARCHAR(35)             NOT NULL,
    name          VARCHAR(255)            NOT NULL,
    length        INTEGER                 NOT NULL,
    endtime       INTEGER                 NOT NULL,
    spamcount     INTEGER                 NOT NULL,
    blacklisted   BOOLEAN                 NOT NULL,
    luck_timeleft INTEGER                 NOT NULL
)"""

CREATE_table_reports = """
    CREATE TABLE `reports` (
        group_id    INTEGER        NOT NULL,
        group_name  VARCHAR(255)   NOT NULL,
        user_id     INTEGER        NOT NULL,
        username    VARCHAR(35)    NOT NULL,
        name        VARCHAR(255)   NOT NULL,
        message     TEXT           NOT NULL
    )
"""

CREATE_table_groups_name = """
    CREATE TABLE `groups_name` (
        group_id    INTEGER      NOT NULL,
        group_name  VARCHAR(255) NOT NULL
    )
"""
