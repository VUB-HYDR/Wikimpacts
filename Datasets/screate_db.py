import sqlite3

connection = sqlite3.connect("Database/impact.db")
cursor = connection.cursor()


def generate_db(sql_path="Database/schema.sql"):
    with open(sql_path, "r") as f:
        generate_database_command = f.read()

    commands = generate_database_command.split(';')
    for i in commands:
        if i:
            print("Executing:")
            print(i)
            cursor.execute(i)
            print("Done")
            print()

generate_db()