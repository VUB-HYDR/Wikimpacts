import sqlite3

from Database.scr.normalize_utils import Logging

logger = Logging.get_logger("create_db")


def generate_db(
    l1_schema: str = "Database/schema/L1_schema.sql",
    l2_schema: str = None,
    l3_schema: str = None,
    type_numerical_cat: list[str] = ["Injuries", "Deaths", "Displaced", "Homeless", "Buildings_Damaged", "Affected"],
    type_monetary_cat: list[str] = ["Insured_Damage", "Damage"],
):
    commands = []
    if l1_schema:
        with open(l1_schema, "r") as f:
            generate_database_command = f.read()

        l1_commands = generate_database_command.split(";")
        l1_commands = [i for i in l1_commands if i.strip()]

        commands.extend(l1_commands)
        del generate_database_command

    for schema_path in (l2_schema, l3_schema):
        if schema_path:
            numerical_tables, numerical_tables = [], []

            with open(schema_path, "r") as f:
                generate_database_command = f.read()

            template_commands = generate_database_command.split(";")
            template_commands = [i for i in template_commands if i.strip()]

            for com in template_commands:
                if "_type_numerical" in com:
                    numerical_tables = [com.replace("_type_numerical", f"_{cat}") for cat in type_numerical_cat]
                    commands.extend(numerical_tables)
                if "_type_monetary" in com:
                    monetary_tables = [com.replace("_type_monetary", f"_{cat}") for cat in type_monetary_cat]
                    commands.extend(monetary_tables)
            del generate_database_command

    for i in commands:
        if i:
            logger.info(f"Executing DB command:\n{i}")
            try:
                cursor.execute(i)
            except sqlite3.Error as err:
                logger.error(f"Could not create table. {type(err).__name__}: {err}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-db",
        "--database",
        dest="database",
        default="impact.v1.db",
        help="Path to sqlite database",
        required=True,
        type=str,
    )

    args = parser.parse_args()
    parser = argparse.ArgumentParser()
    connection = sqlite3.connect(args.database, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = connection.cursor()
    generate_db(
        l1_schema="Database/schema/L1_schema.sql",
        l2_schema="Database/schema/L2_schema_template.sql",
        l3_schema="Database/schema/L3_schema_template.sql",
    )
    connection.close()
