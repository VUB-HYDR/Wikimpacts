import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("/home/nl/Wikimpacts/Annotation_V2/impactDB_gold_V2.db")
cursor = conn.cursor()

# Create tables
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Basic (
  Event_ID TEXT PRIMARY KEY,
  Main_Event TEXT,
  Hazards TEXT,
  Event_Names TEXT,
  Sources TEXT,
  Start_Date_Year INTEGER,
  Start_Date_Month INTEGER,
  Start_Date_Day INTEGER,
  End_Date_Year INTEGER,
  End_Date_Month INTEGER,
  End_Date_Day INTEGER
);
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Affected_Countries (
  Country TEXT,
  Event_ID TEXT,
  PRIMARY KEY (Event_ID, Country),
  FOREIGN KEY (Event_ID) REFERENCES Basic(Event_ID)
);
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Total_Deaths (
  Event_ID TEXT PRIMARY KEY,
  Total_Deaths_Raw TEXT,
  Total_Deaths_Min INTEGER,
  Total_Deaths_Max INTEGER,
  Total_Deaths_Approx BOOLEAN,
  FOREIGN KEY (Event_ID) REFERENCES Basic(Event_ID)
);
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Total_Injuries (
  Event_ID TEXT PRIMARY KEY,
  Total_Injuries_Raw TEXT,
  Total_Injuries_Min INTEGER,
  Total_Injuries_Max INTEGER,
  Total_Injuries_Approx BOOLEAN,
  FOREIGN KEY (Event_ID) REFERENCES Basic(Event_ID)
);
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Total_Affected (
  Event_ID TEXT PRIMARY KEY,
  Total_Affected_Raw TEXT,
  Total_Affected_Min INTEGER,
  Total_Affected_Max INTEGER,
  Total_Affected_Approx BOOLEAN,
  FOREIGN KEY (Event_ID) REFERENCES Basic(Event_ID)
);
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Total_Homeless (
  Event_ID TEXT PRIMARY KEY,
  Total_Homeless_Raw TEXT,
  Total_Homeless_Min INTEGER,
  Total_Homeless_Max INTEGER,
  Total_Homeless_Approx BOOLEAN,
  FOREIGN KEY (Event_ID) REFERENCES Basic(Event_ID)
);
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Total_Displaced (
  Event_ID TEXT PRIMARY KEY,
  Total_Displaced_Raw TEXT,
  Total_Displaced_Min INTEGER,
  Total_Displaced_Max INTEGER,
  Total_Displaced_Approx BOOLEAN,
  FOREIGN KEY (Event_ID) REFERENCES Basic(Event_ID)
);
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Total_Buildings_Damaged (
  Event_ID TEXT PRIMARY KEY,
  Total_Buildings_Damaged_Raw TEXT,
  Total_Buildings_Damaged_Min INTEGER,
  Total_Buildings_Damaged_Max INTEGER,
  Total_Buildings_Damaged_Approx BOOLEAN,
  FOREIGN KEY (Event_ID) REFERENCES Basic(Event_ID)
);
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Total_Damage (
  Event_ID TEXT,
  Total_Damage_Raw TEXT,
  Total_Damage_Min INTEGER,
  Total_Damage_Max INTEGER,
  Total_Damage_Approx BOOLEAN,
  Total_Damage_Unit TEXT,
  Total_Damage_Inflation_Adjusted BOOLEAN,
  Total_Damage_Inflation_Adjusted_Year INTEGER,
  PRIMARY KEY (Total_Damage_Unit, Total_Damage_Inflation_Adjusted, Total_Damage_Inflation_Adjusted_Year, Event_ID),
  FOREIGN KEY (Event_ID) REFERENCES Basic(Event_ID)
);
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Total_Insured_Damage (
  Event_ID TEXT,
  Total_Insured_Damage_Raw TEXT,
  Total_Insured_Damage_Min INTEGER,
  Total_Insured_Damage_Max INTEGER,
  Total_Insured_Damage_Approx BOOLEAN,
  Total_Insured_Damage_Unit TEXT,
  Total_Insured_Damage_Inflation_Adjusted BOOLEAN,
  Total_Insured_Damage_Inflation_Adjusted_Year INTEGER,
  PRIMARY KEY (Event_ID, Total_Insured_Damage_Unit, Total_Insured_Damage_Inflation_Adjusted, Total_Insured_Damage_Inflation_Adjusted_Year),
  FOREIGN KEY (Event_ID) REFERENCES Basic(Event_ID)
);
"""
)

# Create tables for Instance_Per_Administrative_Areas
tables = [
    "Instance_Per_Administrative_Areas_Deaths",
    "Instance_Per_Administrative_Areas_Injuries",
    "Instance_Per_Administrative_Areas_Homeless",
    "Instance_Per_Administrative_Areas_Displaced",
    "Instance_Per_Administrative_Areas_Affected",
    "Instance_Per_Administrative_Areas_Buildings_Damaged",
    "Instance_Per_Administrative_Areas_Damage",
    "Instance_Per_Administrative_Areas_Insured_Damage",
]

for table in tables:
    cursor.execute(
        f"""
    CREATE TABLE IF NOT EXISTS {table} (
      Event_ID TEXT,
      Country TEXT NOT NULL,
      Country_GID TEXT,
      Administrative_Areas TEXT,
      Administrative_Areas_GID TEXT,
      Hazards TEXT,
      Start_Date_Year INTEGER,
      Start_Date_Month INTEGER,
      Start_Date_Day INTEGER,
      End_Date_Year INTEGER,
      End_Date_Month INTEGER,
      End_Date_Day INTEGER,
      Num_Raw TEXT,
      Num_Min INTEGER,
      Num_Max INTEGER,
      Num_Approx BOOLEAN,
      PRIMARY KEY (Event_ID),
      UNIQUE (Event_ID, Country, Administrative_Areas),
      FOREIGN KEY (Event_ID) REFERENCES Affected_Countries(Event_ID)
    );
    """
    )

# Commit changes and close the connection
conn.commit()
conn.close()
