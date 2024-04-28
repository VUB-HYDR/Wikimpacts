import sqlite3


def generate_db(sql_path="Database/schema.sql"):
    with open(sql_path, "r") as f:
        generate_database_command = f.read()

    commands = generate_database_command.split(";")
    for i in commands:
        if i:
            print("Executing:")
            print(i)
            cursor.execute(i)
            print("Done\n")


if __name__ == "__main__":
    connection = sqlite3.connect("Database/output/impact.db")
    cursor = connection.cursor()
    generate_db()
    connection.close()
