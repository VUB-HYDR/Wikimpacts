CREATE TABLE Specific_Instance_Per_Country_type_numerical (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */

    Administrative_Area_Norm TEXT NOT NULL,
    Administrative_Area_GID TEXT, /* categorical */
    Administrative_Area_Type TEXT, /* categorical */
    Administrative_Area_GeoJson OBJECT, /* COMMENT GeoJSON object */

    Locations_Norm OBJECT NOT NULL, /* COMMENT 'Array' of TEXT/NULL */
    Locations_GID OBJECT, /* COMMENT 'Array' of TEXT/NULL, categorical */
    Locations_Type OBJECT, /* COMMENT 'Array' of TEXT/NULL, categorical */
    Locations_GeoJson OBJECT, /* COMMENT 'Array' of GeoJson Objects or NULLs */

    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER CHECK (length(End_Date_Year) = 4),

    Num_Min REAL CHECK (Num_Min > 0),
    Num_Max REAL CHECK (Num_Max > 0),
    Num_Approx INTEGER CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Total_Summary_Events(Event_ID)
);


CREATE TABLE Specific_Instance_Per_Country_type_monetary (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */

    Administrative_Area_Norm TEXT NOT NULL,
    Administrative_Area_GID TEXT, /* categorical */
    Administrative_Area_Type TEXT, /* categorical */
    Administrative_Area_GeoJson OBJECT, /* COMMENT GeoJSON object */

    Locations_Norm OBJECT NOT NULL, /* COMMENT 'Array' of TEXT/NULL */
    Locations_GID OBJECT, /* COMMENT 'Array' of TEXT/NULL, categorical */
    Locations_Type OBJECT, /* COMMENT 'Array' of TEXT/NULL, categorical */
    Locations_GeoJson OBJECT, /* COMMENT 'Array' of GeoJson Objects or NULLs */

    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER NOT NULL CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) = 4),

    Num_Min REAL NOT NULL CHECK (Num_Min > 0),
    Num_Max REAL NOT NULL CHECK (Num_Max > 0),
    Num_Approx INTEGER NOT NULL CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
    Num_Units TEXT NOT NULL, /* COMMENT 'currency' */
    Num_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Num_Inflation_Adjusted_Year INTEGER CHECK (
        length(Num_Inflation_Adjusted_Year) = 4
    ),

    FOREIGN KEY(Event_ID) REFERENCES Total_Summary_Events(Event_ID)
);
