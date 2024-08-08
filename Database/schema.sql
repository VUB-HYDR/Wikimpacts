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
    Total_Deaths_Min REAL CHECK (Total_Deaths_Min > 0),
    Total_Deaths_Max REAL CHECK (Total_Deaths_Max > 0),,
    Total_Deaths_Approx INTEGER CHECK (Total_Deaths_Approx == 1 OR Total_Deaths_Approx ==  0), /* COMMENT 'Boolean' */
    Total_Injuries_Min  REAL CHECK (Total_Injuries_Min > 0),
    Total_Injuries_Max REAL CHECK (Total_Injuries_Max > 0),
    Total_Injuries_Approx INTEGER CHECK (Total_Injuries_Approx == 1 OR Total_Injuries_Approx ==  0), /* COMMENT 'Boolean' */
    Total_Displacement_Min REAL CHECK (Total_Displacement_Min > 0),
    Total_Displacement_Max REAL CHECK (Total_Displacement_Max > 0),
    Total_Displacement_Approx INTEGER CHECK (Total_Displacement_Approx == 1 OR Total_Displacement_Approx ==  0), /* COMMENT 'Boolean' */
    Total_Homeless_Min REAL CHECK (Total_Homeless_Min > 0),
    Total_Homeless_Max REAL CHECK (Total_Homeless_Max > 0),
    Total_Homeless_Approx INTEGER CHECK (Total_Homeless_Approx == 1 OR Total_Homeless_Approx ==  0), /* COMMENT 'Boolean' */
    Total_Insured_Damage_Min REAL CHECK (Total_Insured_Damage_Min > 0),
    Total_Insured_Damage_Max REAL CHECK (Total_Insured_Damage_Max > 0),
    Total_Insured_Damage_Approx INTEGER CHECK (Total_Insured_Damage_Approx == 1 OR Total_Insured_Damage_Approx ==  0), /* COMMENT 'Boolean' */
    Total_Insured_Damage_Units TEXT, /* COMMENT 'currency' */
    Total_Insured_Damage_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Total_Insured_Damage_Inflation_Adjusted_Year INTEGER CHECK (
        length(Total_Insured_Damage_Inflation_Adjusted_Year) = 4
    ),
    Total_Damage_Min REAL CHECK (Total_Damage_Min > 0),
    Total_Damage_Max REAL CHECK (Total_Damage_Max > 0),
    Total_Damage_Approx INTEGER CHECK (Total_Damage_Approx == 1 OR Total_Damage_Approx ==  0), /* COMMENT 'Boolean' */
    Total_Damage_Units TEXT, /* COMMENT 'currency' */
    Total_Damage_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Total_Damage_Inflation_Adjusted_Year INTEGER CHECK (length(Total_Damage_Inflation_Adjusted_Year) = 4),
    Total_Buildings_Damaged_Min REAL CHECK (Total_Buildings_Damaged_Min > 0),
    Total_Buildings_Damaged_Max REAL CHECK (Total_Buildings_Damaged_Max > 0),
    Total_Buildings_Damaged_Approx INTEGER CHECK (Total_Buildings_Damaged_Approx == 1 OR Total_Buildings_Damaged_Approx ==  0), /* COMMENT 'Boolean' */

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
    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);


CREATE TABLE Impact_Per_Administrative_Area_Deaths (
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
    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
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
    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Impact_Per_Administrative_Area_Injuries (
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
    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
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
    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);


CREATE TABLE Impact_Per_Administrative_Area_Displacement (
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
    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
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
    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */

    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Impact_Per_Administrative_Area_Homeless (
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
    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
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
    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
    Units TEXT, /* COMMENT 'currency' */
    Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Inflation_Adjusted_Year INTEGER CHECK (
        length(Inflation_Adjusted_Year) = 4
    ),
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Impact_Per_Administrative_Area_Insured_Damage (
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
    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
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
    Location_GID OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Norm OBJECT, /* COMMENT 'Array' of TEXT */
    Location_Type OBJECT, /* COMMENT 'Array' of TEXT */
    Location_GeoJson OBJECT, /* COMMENT 'Array' of TEXT */
    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
    Units TEXT, /* COMMENT 'currency' */
    Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Inflation_Adjusted_Year INTEGER CHECK (length(Inflation_Adjusted_Year) = 4),
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Impact_Per_Administrative_Area_Damage (
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
    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
    Units TEXT, /* COMMENT 'currency' */
    Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Inflation_Adjusted_Year INTEGER CHECK (
        length(Inflation_Adjusted_Year) = 4
    ),
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Specific_Instance_Per_Administrative_Area_Buildings_Damaged (
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
    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);

CREATE TABLE Impact_Per_Administrative_Area_Buildings_Damaged (
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
    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Events(Event_ID)
);
