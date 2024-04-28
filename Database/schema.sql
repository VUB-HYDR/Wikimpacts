CREATE TABLE Events (
    Event_ID TEXT PRIMARY KEY NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Event_Name TEXT NOT NULL,
    Source TEXT NOT NULL, /* COMMENT 'URL', */
    execution_time REAL NOT NULL,
    Main_Event TEXT NOT NULL, /* COMMENT 'Categorical', */
    Perils OBJECT, /* COMMENT 'Array', */
    Location OBJECT, /* COMMENT 'Array', */
    Country OBJECT, /* COMMENT 'Array', */
    /*  Single_Date DATE, */
    /* Single_Date_Day INTEGER CHECK (Single_Date_Day <= 31), */
    /* Single_Date_Month INTEGER CHECK (Single_Date_Month <= 12), */
    /* Single_Date_Year INTEGER CHECK (length(Single_Date_Year) = 4), */
    Start_Date DATE,
    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER CHECK (length(Start_Date_Year) = 4),
    End_Date DATE,
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER CHECK (length(End_Date_Year) = 4),
    Total_Deaths TEXT,
    Total_Deaths_Min REAL
    Total_Deaths_Max REAL
    Total_Deaths_Approx INTEGER, /* COMMENT 'Boolean', */
    Total_Injuries INTEGER,
    Total_Injuries_Min REAL
    Total_Injuries_Max REAL
    Total_Injuries_Approx INTEGER, /* COMMENT 'Boolean', */
    Total_Displacement INTEGER,
    Total_Displacement_Min REAL
    Total_Displacement_Max REAL
    Total_Displacement_Approx INTEGER, /* COMMENT 'Boolean', */
    Total_Homelessness INTEGER,
    Total_Homelessness_Min REAL
    Total_Homelessness_Max REAL
    Total_Homelessness_Approx INTEGER, /* COMMENT 'Boolean', */
    Total_Insured_Damage REAL,
    Total_Insured_Damage_Min REAL
    Total_Insured_Damage_Max REAL
    Total_Insured_Damage_Approx INTEGER, /* COMMENT 'Boolean', */
    Total_Insured_Damage_Units TEXT, /* COMMENT 'currency', */
    Total_Insured_Damage_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean', */
    Total_Insured_Damage_Inflation_Adjusted_Year INTEGER CHECK (
        length(Total_Insured_Damage_Inflation_Adjusted_Year) = 4
    ),
    Total_Damage REAL,
    Total_Damage_Min REAL
    Total_Damage_Max REAL
    Total_Damage_Approx INTEGER, /* COMMENT 'Boolean', */

    Total_Damage_Units TEXT, /* COMMENT 'currency', */
    Total_Damage_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean', */
    Total_Damage_Inflation_Adjusted_Year INTEGER CHECK (length(Total_Damage_Inflation_Adjusted_Year) = 4),
    Total_Buildings_Damage INTEGER,
    Total_Buildings_Damage_Min REAL
    Total_Buildings_Damage_Max REAL
    Total_Buildings_Damage_Approx INTEGER, /* COMMENT 'Boolean', */

    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Country_Death (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Country TEXT NOT NULL, /* COMMENT 'Country Code', */
    Location_Death TEXT,
    Location_GCS OBJECT, /* COMMENT 'GCS', */
    Start_Date_Death DATE,
    Start_Date_Death_Day INTEGER CHECK (Start_Date_Death_Day <= 31),
    Start_Date_Death_Month INTEGER CHECK (Start_Date_Death_Month <= 12),
    Start_Date_Death_Year INTEGER CHECK (length(Start_Date_Death_Year) = 4),
    End_Date_Death DATE,
    End_Date_Death_Day INTEGER CHECK (End_Date_Death_Day <= 31),
    End_Date_Death_Month INTEGER CHECK (End_Date_Death_Month <= 12),
    End_Date_Death_Year INTEGER CHECK (length(End_Date_Death_Year) = 4),
    Num_Death INTEGER,
    Num_Death_Min REAL
    Num_Death_Max REAL
    Num_Death_Approx INTEGER, /* COMMENT 'Boolean', */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Country_Injuries (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Country TEXT NOT NULL, /* COMMENT 'Country Code', */
    Location_Injuries TEXT,
    Location_GCS OBJECT, /* COMMENT 'GCS', */
    Start_Date_Injuries DATE,
    Start_Date_Injuries_Day INTEGER CHECK (Start_Date_Injuries_Day <= 31),
    Start_Date_Injuries_Month INTEGER CHECK (Start_Date_Injuries_Month <= 12),
    Start_Date_Injuries_Year INTEGER CHECK (length(Start_Date_Injuries_Year) = 4),
    End_Date_Injuries DATE,
    End_Date_Injuries_Day INTEGER CHECK (End_Date_Injuries_Day <= 31),
    End_Date_Injuries_Month INTEGER CHECK (End_Date_Injuries_Month <= 12),
    End_Date_Injuries_Year INTEGER CHECK (length(End_Date_Injuries_Year) = 4),
    Num_Injuries INTEGER,
    Num_Injuries_Min REAL
    Num_Injuries_Max REAL
    Num_Injuries_Approx INTEGER, /* COMMENT 'Boolean', */

    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Country_Displacement (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Country TEXT NOT NULL, /* COMMENT 'Country Code', */
    Location_Displacement TEXT,
    Location_GCS OBJECT, /* COMMENT 'GCS', */
    Start_Date_Displacement DATE,
    Start_Date_Displacement_Day INTEGER CHECK (Start_Date_Displacement_Day <= 31),
    Start_Date_Displacement_Month INTEGER CHECK (Start_Date_Displacement_Month <= 12),
    Start_Date_Displacement_Year INTEGER CHECK (length(Start_Date_Displacement_Year) = 4),
    End_Date_Displacement DATE,
    End_Date_Displacement_Day INTEGER CHECK (End_Date_Displacement_Day <= 31),
    End_Date_Displacement_Month INTEGER CHECK (End_Date_Displacement_Month <= 12),
    End_Date_Displacement_Year INTEGER CHECK (length(End_Date_Displacement_Year) = 4),
    Num_Displaced INTEGER,
    Num_Displaced_Min REAL
    Num_Displaced_Max REAL
    Num_Displaced_Approx INTEGER, /* COMMENT 'Boolean', */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Country_Homelessness (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Country TEXT NOT NULL, /* COMMENT 'Country Code', */
    Location_Homelessness TEXT,
    Location_GCS OBJECT, /* COMMENT 'GCS', */
    Start_Date_Homelessness DATE,
    Start_Date_Homelessness_Day INTEGER CHECK (Start_Date_Homelessness_Day <= 31),
    Start_Date_Homelessness_Month INTEGER CHECK (Start_Date_Homelessness_Month <= 12),
    Start_Date_Homelessness_Year INTEGER CHECK (length(Start_Date_Homelessness_Year) = 4),
    End_Date_Homelessness DATE,
    End_Date_Homelessness_Day INTEGER CHECK (End_Date_Homelessness_Day <= 31),
    End_Date_Homelessness_Month INTEGER CHECK (End_Date_Homelessness_Month <= 12),
    End_Date_Homelessness_Year INTEGER CHECK (length(End_Date_Homelessness_Year) = 4),
    Num_Homeless INTEGER,
    Num_Homeless_Min REAL
    Num_Homeless_Max REAL
    Num_Homeless_Approx INTEGER, /* COMMENT 'Boolean', */

    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Country_Insured_Damage (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Country TEXT NOT NULL, /* COMMENT 'Country Code', */
    Location_Insured_Damage TEXT,
    Location_GCS OBJECT, /* COMMENT 'GCS', */
    Insured_Damage REAL,
    Insured_Damage_Min REAL
    Insured_Damage_Max REAL
    Insured_Damage_Approx INTEGER, /* COMMENT 'Boolean', */
    Insured_Damage_Units TEXT, /* COMMENT 'currency', */
    Insured_Damage_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean', */
    Insured_Damage_Inflation_Adjusted_Year INTEGER CHECK (
        length(Insured_Damage_Inflation_Adjusted_Year) = 4
    ),
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Country_Economic_Damage (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Country TEXT NOT NULL, /* COMMENT 'Country Code', */
    Location_Damage TEXT,
    Location_GCS OBJECT, /* COMMENT 'GCS', */
    Damage REAL,
    Damage_Min REAL
    Damage_Max REAL
    Damage_Approx INTEGER, /* COMMENT 'Boolean', */
    Damage_Units TEXT, /* COMMENT 'currency', */
    Damage_Inflation_Adjusted INTEGER,/* COMMENT 'Boolean', */Damage_Inflation_Adjusted_Year INTEGER CHECK (length(Damage_Inflation_Adjusted_Year) = 4),FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Country_Building_Damage (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Country TEXT NOT NULL, /* COMMENT 'Country Code', */
    Location_Building TEXT,
    Location_GCS OBJECT, /* COMMENT 'GCS', */
    Start_Date_Building DATE,
    Start_Date_Building_Day INTEGER CHECK (Start_Date_Building_Day <= 31),
    Start_Date_Building_Month INTEGER CHECK (Start_Date_Building_Month <= 12),
    Start_Date_Building_Year INTEGER CHECK (length(Start_Date_Building_Year) = 4),
    End_Date_Building DATE,
    End_Date_Building_Day INTEGER CHECK (End_Date_Building_Day <= 31),
    End_Date_Building_Month INTEGER CHECK (End_Date_Building_Month <= 12),
    End_Date_Building_Year INTEGER CHECK (length(End_Date_Building_Year) = 4),
    Buildings_Damaged REAL,
    Buildings_Damaged_Min REAL
    Buildings_Damaged_Max REAL
    Buildings_Damaged_Approx INTEGER, /* COMMENT 'Boolean', */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);