INSERT_into_groups_name = """
    INSERT INTO `groups_name` (group_id, group_name)
    VALUES (?,?)
"""

INSERT_into_reports = """
    INSERT INTO `reports` (group_id, group_name, user_id, username, name, message)
    VALUES (?, ?, ?, ?, ?, ?)
"""