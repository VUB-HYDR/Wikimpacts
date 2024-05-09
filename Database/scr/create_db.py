import sqlite3

from normalize_utils import NormalizeUtils

logger = NormalizeUtils.get_logger("create_db")


def generate_db(sql_path="Database/schema.sql"):
    with open(sql_path, "r") as f:
        generate_database_command = f.read()

    commands = generate_database_command.split(";")
    commands = [i for i in commands if i.strip()]
    for i in commands:
        if i:
            try:
                logger.debug(f"Executing DB command:\n{i}")
                cursor.execute(i)
            except sqlite3.Error as err:
                logger.error(f"Could not create table. {type(err).__name__}: {err}")


if __name__ == "__main__":
    connection = sqlite3.connect("impact.db")
    cursor = connection.cursor()
    generate_db()
    connection.close()
