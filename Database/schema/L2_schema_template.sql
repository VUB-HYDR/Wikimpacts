CREATE TABLE Instance_Per_Administrative_Areas_type_numerical (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */
    Administrative_Areas_Norm OBJECT NOT NULL, /* COMMENT 'Array' of TEXT/NULL */
    Administrative_Areas_GID OBJECT, /* COMMENT 'Array' */
    Administrative_Areas_Type OBJECT, /* COMMENT 'Array' of TEXT/NULL */
    Administrative_Areas_GeoJson OBJECT, /* COMMENT 'Array' of GeoJson Objects or NULLs */

    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31 OR Start_Date_Day == NULL),
    Start_Date_Month INTEGER CHECK (Start_Date_Month <= 12 OR Start_Date_Month == NULL),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) == 4 OR Start_Date_Year == NULL),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31 OR End_Date_Day == NULL),
    End_Date_Month INTEGER CHECK (End_Date_Month <= 12 OR End_Date_Month == NULL),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) == 4),

    Num_Min REAL NOT NULL CHECK (Num_Min > 0),
    Num_Max REAL NOT NULL CHECK (Num_Max > 0),
    Num_Approx INTEGER NOT NULL CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Total_Summary_Events(Event_ID)
);

CREATE TABLE Instance_Per_Administrative_Areas_type_monetary (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) = 7), /* COMMENT 'UID' */

    Administrative_Areas_Norm OBJECT NOT NULL, /* COMMENT 'Array' of TEXT/NULL */
    Administrative_Areas_GID OBJECT, /* COMMENT 'Array' */
    Administrative_Areas_Type OBJECT, /* COMMENT 'Array' of TEXT/NULL */
    Administrative_Areas_GeoJson OBJECT, /* COMMENT 'Array' of GeoJson Objects or NULLs */

    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31 OR Start_Date_Day == NULL),
    Start_Date_Month INTEGER CHECK (Start_Date_Month <= 12 OR Start_Date_Month == NULL),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) == 4 OR Start_Date_Year == NULL),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31 OR End_Date_Day == NULL),
    End_Date_Month INTEGER CHECK (End_Date_Month <= 12 OR End_Date_Month == NULL),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) == 4 OR End_Date_Year == NULL),

    Num_Min REAL NOT NULL CHECK (Num_Min > 0),
    Num_Max REAL NOT NULL CHECK (Num_Max > 0),
    Num_Approx INTEGER NOT NULL CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
    Num_Unit TEXT NOT NULL, /* COMMENT 'currency' */
    Num_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Num_Inflation_Adjusted_Year INTEGER CHECK (
        length(Num_Inflation_Adjusted_Year) == 4
        OR Num_Inflation_Adjusted_Year == NULL
    ),

    FOREIGN KEY(Event_ID) REFERENCES Total_Summary_Events(Event_ID)
);
