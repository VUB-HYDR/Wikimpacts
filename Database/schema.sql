CREATE TABLE Events (
    Event_ID TEXT PRIMARY KEY NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Event_Name TEXT NOT NULL,
    Source TEXT NOT NULL, /* COMMENT 'URL', */
    execution_time REAL NOT NULL,
    Main_Event TEXT NOT NULL, /* COMMENT 'Categorical', */
    Perils OBJECT, /* COMMENT 'Array', */
    Location OBJECT, /* COMMENT 'Array', */
    Single_Date DATE,
    /* Single_Date_Day INTEGER CHECK (Single_Date_Day <= 31), */
    /* Single_Date_Month INTEGER CHECK (Single_Date_Month <= 12), */
    /* Single_Date_Year INTEGER CHECK (length(Single_Date_Year) = 4), */
    Start_Date DATE,
    /* Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31), */
    /* Start_Date_Month INTEGER CHECK (Start_Date_Month <= 12), */
    /* Start_Date_Year INTEGER CHECK (length(Start_Date_Year) = 4), */
    End_Date DATE,
    /* End_Date_Day INTEGER CHECK (End_Date_Day <= 31), */
    /* End_Date_Month INTEGER CHECK (End_Date_Month <= 12), */
    /* End_Date_Year INTEGER CHECK (length(End_Date_Year) = 4), */
    Total_Deaths INTEGER,
    Total_Injuries INTEGER,
    Total_Displaced INTEGER,
    Total_Homeless INTEGER,
    Total_Insured_Damage REAL,
    Total_Insured_Damage_Units TEXT, /* COMMENT 'currency', */
    Total_Insured_Damage_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean', */
    Total_Insured_Damage_Inflation_Adjusted_Year INTEGER CHECK (
        length(Total_Insured_Damage_Inflation_Adjusted_Year) = 4
    ),
    Total_Damage REAL,
    Total_Damage_Units TEXT, /* COMMENT 'currency', */
    Total_Damage_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean', */
    Total_Damage_Inflation_Adjusted_Year INTEGER CHECK (length(Total_Damage_Inflation_Adjusted_Year) = 4),
    Total_Buildings_Damaged INTEGER,
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Country_Death (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Country TEXT NOT NULL, /* COMMENT 'Country Code', */
    Location_Death TEXT,
    Location_GCS OBJECT, /* COMMENT 'GCS', */
    Time_Death DATE,
    Time_Death_Day INTEGER CHECK (Time_Death_Day <= 31),
    Time_Death_Month INTEGER CHECK (Time_Death_Month <= 12),
    Time_Death_Year INTEGER CHECK (length(Time_Death_Year) = 4),
    Num_Death INTEGER,
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Country_Injuries (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Country TEXT NOT NULL, /* COMMENT 'Country Code', */
    Location_Injuries TEXT,
    Location_GCS OBJECT, /* COMMENT 'GCS', */
    Time_Injuries DATE,
    Time_Injuries_Day INTEGER CHECK (Time_Injuries_Day <= 31),
    Time_Injuries_Month INTEGER CHECK (Time_Injuries_Month <= 12),
    Time_Injuries_Year INTEGER CHECK (length(Time_Injuries_Year) = 4),
    Num_Injuries INTEGER,
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Country_Displacement (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Country TEXT NOT NULL, /* COMMENT 'Country Code', */
    Location_Displace TEXT,
    Location_GCS OBJECT, /* COMMENT 'GCS', */
    Time_Displaced DATE,
    Time_Displaced_Day INTEGER CHECK (Time_Displaced_Day <= 31),
    Time_Displaced_Month INTEGER CHECK (Time_Displaced_Month <= 12),
    Time_Displaced_Year INTEGER CHECK (length(Time_Displaced_Year) = 4),
    Num_Displaced INTEGER,
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Country_Homelessness (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Country TEXT NOT NULL, /* COMMENT 'Country Code', */
    Location_Homeless TEXT,
    Location_GCS OBJECT, /* COMMENT 'GCS', */
    Time_Homeless DATE,
    Time_Homeless_Day INTEGER CHECK (Time_Homeless_Day <= 31),
    Time_Homeless_Month INTEGER CHECK (Time_Homeless_Month <= 12),
    Time_Homeless_Year INTEGER CHECK (length(Time_Homeless_Year) = 4),
    Num_Homeless INTEGER,
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Country_Insured_Damage (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Country TEXT NOT NULL, /* COMMENT 'Country Code', */
    Location_Insured_Damage TEXT,
    Location_GCS OBJECT, /* COMMENT 'GCS', */
    Insured_Damage REAL,
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
    Damage_Units TEXT, /* COMMENT 'currency', */
    Damage_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean', */
    Damage_Inflation_Adjusted_Year INTEGER CHECK (length(Damage_Inflation_Adjusted_Year) = 4),
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Country_Building_Damage (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID', */
    Country TEXT NOT NULL, /* COMMENT 'Country Code', */
    Location_Building TEXT,
    Location_GCS OBJECT, /* COMMENT 'GCS', */
    Time_Building DATE,
    Time_Building_Day INTEGER CHECK (Time_Building_Day <= 31),
    Time_Building_Month INTEGER CHECK (Time_Building_Month <= 12),
    Time_Building_Year INTEGER CHECK (length(Time_Building_Year) = 4),
    Buildings_Damaged REAL,
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);