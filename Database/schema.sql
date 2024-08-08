CREATE TABLE Events (
    Event_ID TEXT PRIMARY KEY NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Event_Name TEXT NOT NULL,
    Source TEXT NOT NULL, /* COMMENT 'URL' */
    execution_time REAL NOT NULL,
    Main_Event TEXT NOT NULL, /* COMMENT 'Categorical' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Location_GID OBJECT, /* COMMENT 'Array' */
    Location_Norm OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Type OBJECT, /* COMMENT 'Array' of TEXT */
    Location_GeoJson OBJECT, /* COMMENT 'Array' of TEXT */
    Administrative_Area OBJECT NOT NULL, /* COMMENT 'Array' */
    Administrative_Area_GID OBJECT, /* COMMENT 'Array' */
    Administrative_Area_Norm OBJECT, /* COMMENT 'Array' of TEXT */
    Administrative_Area_Type OBJECT, /* COMMENT 'Array' of TEXT */
    Administrative_Area_GeoJson TEXT,
    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER CHECK (length(End_Date_Year) = 4),
    Total_Deaths TEXT,
    Total_Deaths_Min REAL,
    Total_Deaths_Max REAL,
    Total_Deaths_Approx INTEGER, /* COMMENT 'Boolean' */
    Total_Injuries INTEGER,
    Total_Injuries_Min REAL,
    Total_Injuries_Max REAL,
    Total_Injuries_Approx INTEGER, /* COMMENT 'Boolean' */
    Total_Displacement INTEGER,
    Total_Displacement_Min REAL,
    Total_Displacement_Max REAL,
    Total_Displacement_Approx INTEGER, /* COMMENT 'Boolean' */
    Total_Homeless INTEGER,
    Total_Homeless_Min REAL,
    Total_Homeless_Max REAL,
    Total_Homeless_Approx INTEGER, /* COMMENT 'Boolean' */
    Total_Insured_Damage REAL,
    Total_Insured_Damage_Min REAL,
    Total_Insured_Damage_Max REAL,
    Total_Insured_Damage_Approx INTEGER, /* COMMENT 'Boolean' */
    Total_Insured_Damage_Units TEXT, /* COMMENT 'currency' */
    Total_Insured_Damage_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Total_Insured_Damage_Inflation_Adjusted_Year INTEGER CHECK (
        length(Total_Insured_Damage_Inflation_Adjusted_Year) = 4
    ),
    Total_Damage REAL,
    Total_Damage_Min REAL,
    Total_Damage_Max REAL,
    Total_Damage_Approx INTEGER, /* COMMENT 'Boolean' */
    Total_Damage_Units TEXT, /* COMMENT 'currency' */
    Total_Damage_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Total_Damage_Inflation_Adjusted_Year INTEGER CHECK (length(Total_Damage_Inflation_Adjusted_Year) = 4),
    Total_Buildings_Damaged INTEGER,
    Total_Buildings_Damaged_Min REAL,
    Total_Buildings_Damaged_Max REAL,
    Total_Buildings_Damaged_Approx INTEGER, /* COMMENT 'Boolean' */

    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Administrative_Area_Deaths (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Administrative_Area TEXT NOT NULL,
    Administrative_Area_GID TEXT,
    Administrative_Area_Norm TEXT,
    Administrative_Area_Type TEXT,
    Administrative_Area_GeoJson TEXT, /* COMMENT GeoJSON object */
    Location_GID OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Norm OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Type OBJECT, /* COMMENT 'Array' of TEXT */
    Location_GeoJson OBJECT, /* COMMENT 'Array' of TEXT */
    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER NOT NULL CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER NOT NULL CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) = 4),
    Num_Min REAL,
    Num_Max REAL,
    Num_Approx INTEGER, /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);


CREATE TABLE Deaths_Per_Administrative_Area (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Administrative_Area TEXT NOT NULL,
    Administrative_Area_GID TEXT,
    Administrative_Area_Norm TEXT,
    Administrative_Area_Type TEXT,
    Administrative_Area_GeoJson TEXT, /* COMMENT GeoJSON object */
    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER NOT NULL CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER NOT NULL CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) = 4),
    Num_Min REAL,
    Num_Max REAL,
    Num_Approx INTEGER, /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Administrative_Area_Injuries (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Administrative_Area TEXT NOT NULL,
    Administrative_Area_GID TEXT,
    Administrative_Area_Norm TEXT,
    Administrative_Area_Type TEXT,
    Administrative_Area_GeoJson TEXT, /* COMMENT GeoJSON object */
    Location_GID OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Norm OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Type OBJECT, /* COMMENT 'Array' of TEXT */
    Location_GeoJson OBJECT, /* COMMENT 'Array' of TEXT */
    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER NOT NULL CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER NOT NULL CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) = 4),
    Num_Min REAL,
    Num_Max REAL,
    Num_Approx INTEGER, /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Injuries_Per_Administrative_Area (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Administrative_Area TEXT NOT NULL,
    Administrative_Area_GID TEXT,
    Administrative_Area_Norm TEXT,
    Administrative_Area_Type TEXT,
    Administrative_Area_GeoJson TEXT, /* COMMENT GeoJSON object */
    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER NOT NULL CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER NOT NULL CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) = 4),
    Num_Min REAL,
    Num_Max REAL,
    Num_Approx INTEGER, /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Administrative_Area_Displacement (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Administrative_Area TEXT NOT NULL,
    Administrative_Area_GID TEXT,
    Administrative_Area_Norm TEXT,
    Administrative_Area_Type TEXT,
    Administrative_Area_GeoJson TEXT, /* COMMENT GeoJSON object */
    Location_GID OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Norm OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Type OBJECT, /* COMMENT 'Array' of TEXT */
    Location_GeoJson OBJECT, /* COMMENT 'Array' of TEXT */
    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER NOT NULL CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER NOT NULL CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) = 4),
    Num_Min REAL,
    Num_Max REAL,
    Num_Approx INTEGER, /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);


CREATE TABLE Injuries_Per_Displacement (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Administrative_Area TEXT NOT NULL,
    Administrative_Area_GID TEXT,
    Administrative_Area_Norm TEXT,
    Administrative_Area_Type TEXT,
    Administrative_Area_GeoJson TEXT, /* COMMENT GeoJSON object */
    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER NOT NULL CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER NOT NULL CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) = 4),
    Num_Min REAL,
    Num_Max REAL,
    Num_Approx INTEGER, /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);


CREATE TABLE Specific_Instance_Per_Administrative_Area_Homeless (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Administrative_Area TEXT NOT NULL,
    Administrative_Area_GID TEXT,
    Administrative_Area_Norm TEXT,
    Administrative_Area_Type TEXT,
    Administrative_Area_GeoJson TEXT, /* COMMENT GeoJSON object */
    Location_GID OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Norm OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Type OBJECT, /* COMMENT 'Array' of TEXT */
    Location_GeoJson OBJECT, /* COMMENT 'Array' of TEXT */
    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER NOT NULL CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER NOT NULL CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) = 4),
    Num_Min REAL,
    Num_Max REAL,
    Num_Approx INTEGER, /* COMMENT 'Boolean' */

    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Injuries_Per_Homeless (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Administrative_Area TEXT NOT NULL,
    Administrative_Area_GID TEXT,
    Administrative_Area_Norm TEXT,
    Administrative_Area_Type TEXT,
    Administrative_Area_GeoJson TEXT, /* COMMENT GeoJSON object */
    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER NOT NULL CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER NOT NULL CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) = 4),
    Num_Min REAL,
    Num_Max REAL,
    Num_Approx INTEGER, /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Administrative_Area_Insured_Damage (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Administrative_Area TEXT NOT NULL,
    Administrative_Area_GID TEXT,
    Administrative_Area_Norm TEXT,
    Administrative_Area_Type TEXT,
    Administrative_Area_GeoJson TEXT, /* COMMENT GeoJSON object */

    Location_GID OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Norm OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Type OBJECT, /* COMMENT 'Array' of TEXT */
    Location_GeoJson OBJECT, /* COMMENT 'Array' of TEXT */
    Num_Min REAL,
    Num_Max REAL,
    Num_Approx INTEGER, /* COMMENT 'Boolean' */
    Units TEXT, /* COMMENT 'currency' */
    Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Inflation_Adjusted_Year INTEGER CHECK (
        length(Inflation_Adjusted_Year) = 4
    ),
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Injuries_Per_Insured_Damage (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Administrative_Area TEXT NOT NULL,
    Administrative_Area_GID TEXT,
    Administrative_Area_Norm TEXT,
    Administrative_Area_Type TEXT,
    Administrative_Area_GeoJson TEXT, /* COMMENT GeoJSON object */
    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER NOT NULL CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER NOT NULL CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) = 4),
    Num_Min REAL,
    Num_Max REAL,
    Num_Approx INTEGER, /* COMMENT 'Boolean' */
    Units TEXT, /* COMMENT 'currency' */
    Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Inflation_Adjusted_Year INTEGER CHECK (length(Inflation_Adjusted_Year) = 4),
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Administrative_Area_Damage (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Administrative_Area TEXT NOT NULL,
    Administrative_Area_GID TEXT,
    Administrative_Area_Norm TEXT,
    Administrative_Area_Type TEXT,
    Administrative_Area_GeoJson TEXT, /* COMMENT GeoJSON object */
    Location_Damage TEXT,
    Location_GID OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Norm OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Type OBJECT, /* COMMENT 'Array' of TEXT */
    Location_GeoJson OBJECT, /* COMMENT 'Array' of TEXT */
    Num_Min REAL,
    Num_Max REAL,
    Num_Approx INTEGER, /* COMMENT 'Boolean' */
    Units TEXT, /* COMMENT 'currency' */
    Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Inflation_Adjusted_Year INTEGER CHECK (length(Inflation_Adjusted_Year) = 4),
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Injuries_Per_Damage (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Administrative_Area TEXT NOT NULL,
    Administrative_Area_GID TEXT,
    Administrative_Area_Norm TEXT,
    Administrative_Area_Type TEXT,
    Administrative_Area_GeoJson TEXT, /* COMMENT GeoJSON object */
    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER NOT NULL CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER NOT NULL CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) = 4),
    Num_Min REAL,
    Num_Max REAL,
    Num_Approx INTEGER, /* COMMENT 'Boolean' */
    Units TEXT, /* COMMENT 'currency' */
    Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Inflation_Adjusted_Year INTEGER CHECK (
        length(Inflation_Adjusted_Year) = 4
    ),
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Administrative_Area_Building_Damaged (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Administrative_Area TEXT NOT NULL,
    Administrative_Area_GID TEXT,
    Administrative_Area_Norm TEXT,
    Administrative_Area_Type TEXT,
    Administrative_Area_GeoJson TEXT, /* COMMENT GeoJSON object */
    Location_GID OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Norm OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Type OBJECT, /* COMMENT 'Array' of TEXT */
    Location_GeoJson OBJECT, /* COMMENT 'Array' of TEXT */
    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER NOT NULL CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER NOT NULL CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) = 4),
    Num_Min REAL,
    Num_Max REAL,
    Num_Approx INTEGER, /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Injuries_Per_Building_Damaged (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Hazard OBJECT, /* COMMENT 'Array' */
    Administrative_Area TEXT NOT NULL,
    Administrative_Area_GID TEXT,
    Administrative_Area_Norm TEXT,
    Administrative_Area_Type TEXT,
    Administrative_Area_GeoJson TEXT, /* COMMENT GeoJSON object */
    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER NOT NULL CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER NOT NULL CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) = 4),
    Num_Min REAL,
    Num_Max REAL,
    Num_Approx INTEGER, /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);
