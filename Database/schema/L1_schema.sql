CREATE TABLE Total_Summary_Events (
    Event_ID TEXT PRIMARY KEY NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Event_Names OBJECT NOT NULL, /* COMMENT 'Array' */
    Sources OBJECT NOT NULL, /* COMMENT 'Array' */
    Main_Event TEXT NOT NULL, /* COMMENT 'Categorical' */
    Hazards OBJECT NOT NULL, /* COMMENT 'Array', categorical */

    Administrative_Areas_Norm OBJECT NOT NULL, /* COMMENT 'Array' of TEXT/NULL */
    Administrative_Areas_GID OBJECT, /* COMMENT 'Array' of TEXT/NULL, categorical */
    Administrative_Areas_Type OBJECT, /* COMMENT 'Array' of TEXT/NULL, categorical */
    Administrative_Areas_GeoJson OBJECT, /* COMMENT 'Array' of GeoJson Objects or NULLs */

    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31),
    Start_Date_Month INTEGER CHECK (Start_Date_Month <= 12),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) = 4),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31),
    End_Date_Month INTEGER CHECK (End_Date_Month <= 12),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) = 4),

    /* Numerical: Deaths */
    Total_Deaths_Min REAL CHECK (Total_Deaths_Min > 0),
    Total_Deaths_Max REAL CHECK (Total_Deaths_Max > 0),
    Total_Deaths_Approx INTEGER CHECK (Total_Deaths_Approx == 1 OR Total_Deaths_Approx ==  0), /* COMMENT 'Boolean' */

    /* Numerical: Injuries */
    Total_Injuries_Min  REAL CHECK (Total_Injuries_Min > 0),
    Total_Injuries_Max REAL CHECK (Total_Injuries_Max > 0),
    Total_Injuries_Approx INTEGER CHECK (Total_Injuries_Approx == 1 OR Total_Injuries_Approx ==  0), /* COMMENT 'Boolean' */

    /* Numerical: Displacement */
    Total_Displacement_Min REAL CHECK (Total_Displacement_Min > 0),
    Total_Displacement_Max REAL CHECK (Total_Displacement_Max > 0),
    Total_Displacement_Approx INTEGER CHECK (Total_Displacement_Approx == 1 OR Total_Displacement_Approx ==  0), /* COMMENT 'Boolean' */

    /* Numerical: Homeless */
    Total_Homeless_Min REAL CHECK (Total_Homeless_Min > 0),
    Total_Homeless_Max REAL CHECK (Total_Homeless_Max > 0),
    Total_Homeless_Approx INTEGER CHECK (Total_Homeless_Approx == 1 OR Total_Homeless_Approx ==  0), /* COMMENT 'Boolean' */

    /* Numerical: Buildings_Damaged */
    Total_Buildings_Damaged_Min REAL CHECK (Total_Buildings_Damaged_Min > 0),
    Total_Buildings_Damaged_Max REAL CHECK (Total_Buildings_Damaged_Max > 0),
    Total_Buildings_Damaged_Approx INTEGER CHECK (Total_Buildings_Damaged_Approx == 1 OR Total_Buildings_Damaged_Approx ==  0), /* COMMENT 'Boolean' */

    /* Monetary: Insured_Damage */
    Total_Insured_Damage_Min REAL CHECK (Total_Insured_Damage_Min > 0),
    Total_Insured_Damage_Max REAL CHECK (Total_Insured_Damage_Max > 0),
    Total_Insured_Damage_Approx INTEGER CHECK (Total_Insured_Damage_Approx == 1 OR Total_Insured_Damage_Approx ==  0), /* COMMENT 'Boolean' */
    Total_Insured_Damage_Units TEXT, /* COMMENT 'currency' */
    Total_Insured_Damage_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Total_Insured_Damage_Inflation_Adjusted_Year INTEGER CHECK (
        length(Total_Insured_Damage_Inflation_Adjusted_Year) = 4
    ),

    /* Monetary: Damage */
    Total_Damage_Min REAL CHECK (Total_Damage_Min > 0),
    Total_Damage_Max REAL CHECK (Total_Damage_Max > 0),
    Total_Damage_Approx INTEGER CHECK (Total_Damage_Approx == 1 OR Total_Damage_Approx ==  0), /* COMMENT 'Boolean' */
    Total_Damage_Units TEXT, /* COMMENT 'currency' */
    Total_Damage_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Total_Damage_Inflation_Adjusted_Year INTEGER CHECK (
        length(Total_Damage_Inflation_Adjusted_Year) = 4
    ),

    FOREIGN KEY(Event_ID) REFERENCES Total_Summary_Events(Event_ID)
);
