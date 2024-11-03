CREATE TABLE Total_Summary (
    Event_ID TEXT PRIMARY KEY NOT NULL CHECK (length(Event_ID) == 7), /* COMMENT 'UID' */
    Event_Names OBJECT NOT NULL, /* COMMENT 'Array' */
    Sources OBJECT NOT NULL, /* COMMENT 'Array' */
    Main_Event TEXT NOT NULL CHECK (Main_Event IN ("Flood", "Extratropical Storm/Cyclone", "Tropical Storm/Cyclone", "Extreme Temperature", "Drought", "Wildfire", "Tornado",)); /* COMMENT 'Categorical' */
    Hazards OBJECT NOT NULL, /* COMMENT 'Array', categorical */

    Administrative_Areas_Norm OBJECT NOT NULL, /* COMMENT 'Array' of TEXT/NULL */
    Administrative_Areas_GID OBJECT, /* COMMENT 'Array' of TEXT/NULL, categorical */
    Administrative_Areas_Type OBJECT, /* COMMENT 'Array' of TEXT/NULL, categorical */
    Administrative_Areas_GeoJson OBJECT, /* COMMENT 'Array' of GeoJson Objects or NULLs */

    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31 OR Start_Date_Day == NULL),
    Start_Date_Month INTEGER CHECK (Start_Date_Month <= 12 OR Start_Date_Month == NULL),
    Start_Date_Year INTEGER NOT NULL CHECK (length(Start_Date_Year) == 4 OR Start_Date_Year == NULL),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31 OR End_Date_Day == NULL),
    End_Date_Month INTEGER CHECK (End_Date_Month <= 12 OR End_Date_Month == NULL),
    End_Date_Year INTEGER NOT NULL CHECK (length(End_Date_Year) == 4),

    /* Numerical: Deaths */
    Total_Deaths_Min REAL CHECK (Total_Deaths_Min > 0 OR Total_Deaths_Min == NULL),
    Total_Deaths_Max REAL CHECK (Total_Deaths_Max > 0 OR Total_Deaths_Max == NULL),
    Total_Deaths_Approx INTEGER CHECK (Total_Deaths_Approx == 1 OR Total_Deaths_Approx == 0  OR Total_Deaths_Approx == NULL), /* COMMENT 'Boolean' */

    /* Numerical: Injuries */
    Total_Injuries_Min  REAL CHECK (Total_Injuries_Min > 0 OR Total_Injuries_Min == NULL),
    Total_Injuries_Max REAL CHECK (Total_Injuries_Max > 0 OR Total_Injuries_Max == NULL),
    Total_Injuries_Approx INTEGER CHECK (Total_Injuries_Approx == 1 OR Total_Injuries_Approx == 0 OR Total_Injuries_Approx == NULL), /* COMMENT 'Boolean' */

    /* Numerical: Affected */
    Total_Affected_Min REAL CHECK (Total_Affected_Min > 0 OR Total_Affected_Min == NULL),
    Total_Affected_Max REAL CHECK (Total_Affected_Max > 0 OR Total_Affected_Max == NULL),
    Total_Affected_Approx INTEGER CHECK (Total_Affected_Approx == 1 OR Total_Affected_Approx == 0 OR Total_Affected_Approx == NULL), /* COMMENT 'Boolean' */

    /* Numerical: Displaced */
    Total_Displaced_Min REAL CHECK (Total_Displaced_Min > 0 OR Total_Displaced_Min == NULL),
    Total_Displaced_Max REAL CHECK (Total_Displaced_Max > 0 OR Total_Displaced_Max == NULL),
    Total_Displaced_Approx INTEGER CHECK (Total_Displaced_Approx == 1 OR Total_Displaced_Approx == 0 OR Total_Displaced_Approx == NULL), /* COMMENT 'Boolean' */

    /* Numerical: Homeless */
    Total_Homeless_Min REAL CHECK (Total_Homeless_Min > 0 OR Total_Homeless_Min == NULL),
    Total_Homeless_Max REAL CHECK (Total_Homeless_Max > 0 OR Total_Homeless_Max == NULL),
    Total_Homeless_Approx INTEGER CHECK (Total_Homeless_Approx == 1 OR Total_Homeless_Approx == 0 OR Total_Homeless_Approx == NULL), /* COMMENT 'Boolean' */

    /* Numerical: Buildings_Damaged */
    Total_Buildings_Damaged_Min REAL CHECK (Total_Buildings_Damaged_Min > 0 OR Total_Buildings_Damaged_Min == NULL),
    Total_Buildings_Damaged_Max REAL CHECK (Total_Buildings_Damaged_Max > 0 OR Total_Buildings_Damaged_Max == NULL),
    Total_Buildings_Damaged_Approx INTEGER CHECK (Total_Buildings_Damaged_Approx == 1 OR Total_Buildings_Damaged_Approx == 0 OR Total_Buildings_Damaged_Approx == NULL), /* COMMENT 'Boolean' */

    /* Monetary: Insured_Damage */
    Total_Insured_Damage_Min REAL CHECK (Total_Insured_Damage_Min > 0 OR Total_Insured_Damage_Min == NULL),
    Total_Insured_Damage_Max REAL CHECK (Total_Insured_Damage_Max > 0 OR Total_Insured_Damage_Max == NULL),
    Total_Insured_Damage_Approx INTEGER CHECK (Total_Insured_Damage_Approx == 1 OR Total_Insured_Damage_Approx == 0 OR Total_Insured_Damage_Approx == NULL), /* COMMENT 'Boolean' */
    Total_Insured_Damage_Unit TEXT CHECK (Total_Insured_Damage_Unit in ("AFN", "EUR", "ALL", "DZD", "USD", "AOA", "XCD", "ARS", "AMD", "AWG", "AUD", "AZN", "BSD", "BHD", "BDT", "BBD", "BYN", "BZD", "XOF", "BMD", "INR", "BTN", "BOB", "BOV", "BAM", "BWP", "NOK", "BRL", "BND", "BGN", "BIF", "CVE", "KHR", "XAF", "CAD", "KYD", "CLP", "CLF", "CNY", "COP", "COU", "KMF", "CDF", "NZD", "CRC", "HRK", "CUP", "CUC", "ANG", "CZK", "DKK", "DJF", "DOP", "EGP", "SVC", "ERN", "SZL", "ETB", "FKP", "FJD", "XPF", "GMD", "GEL", "GHS", "GIP", "GTQ", "GBP", "GNF", "GYD", "HTG", "HNL", "HKD", "HUF", "ISK", "IDR", "XDR", "IRR", "IQD", "ILS", "JMD", "JPY", "JOD", "KZT", "KES", "KPW", "KRW", "KWD", "KGS", "LAK", "LBP", "LSL", "ZAR", "LRD", "LYD", "CHF", "MOP", "MKD", "MGA", "MWK", "MYR", "MVR", "MRU", "MUR", "XUA", "MXN", "MXV", "MDL", "MNT", "MAD", "MZN", "MMK", "NAD", "NPR", "NIO", "NGN", "OMR", "PKR", "PAB", "PGK", "PYG", "PEN", "PHP", "PLN", "QAR", "RON", "RUB", "RWF", "SHP", "WST", "STN", "SAR", "RSD", "SCR", "SLL", "SLE", "SGD", "XSU", "SBD", "SOS", "SSP", "LKR", "SDG", "SRD", "SEK", "CHE", "CHW", "SYP", "TWD", "TJS", "TZS", "THB", "TOP", "TTD", "TND", "TRY", "TMT", "UGX", "UAH", "AED", "USN", "UYU", "UYI", "UYW", "UZS", "VUV", "VES", "VED", "VND", "YER", "ZMW", "ZWL", "XBA", "XBB", "XBC", "XBD", "XTS", "XXX", "XAU", "XPD", "XPT", "XAG")), /* COMMENT 'currency' */
    Total_Insured_Damage_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Total_Insured_Damage_Inflation_Adjusted_Year INTEGER CHECK (
        length(Total_Insured_Damage_Inflation_Adjusted_Year) == 4
        OR Total_Insured_Damage_Inflation_Adjusted_Year == NULL
    ),

    /* Monetary: Damage */
    Total_Damage_Min REAL CHECK (Total_Damage_Min > 0 OR Total_Damage_Min == NULL),
    Total_Damage_Max REAL CHECK (Total_Damage_Max > 0 OR Total_Damage_Max == NULL),
    Total_Damage_Approx INTEGER CHECK (Total_Damage_Approx == 1 OR Total_Damage_Approx == 0 OR Total_Damage_Approx == NULL), /* COMMENT 'Boolean' */
    Total_Damage_Unit TEXT CHECK (Total_Insured_Damage_Unit in ("AFN", "EUR", "ALL", "DZD", "USD", "AOA", "XCD", "ARS", "AMD", "AWG", "AUD", "AZN", "BSD", "BHD", "BDT", "BBD", "BYN", "BZD", "XOF", "BMD", "INR", "BTN", "BOB", "BOV", "BAM", "BWP", "NOK", "BRL", "BND", "BGN", "BIF", "CVE", "KHR", "XAF", "CAD", "KYD", "CLP", "CLF", "CNY", "COP", "COU", "KMF", "CDF", "NZD", "CRC", "HRK", "CUP", "CUC", "ANG", "CZK", "DKK", "DJF", "DOP", "EGP", "SVC", "ERN", "SZL", "ETB", "FKP", "FJD", "XPF", "GMD", "GEL", "GHS", "GIP", "GTQ", "GBP", "GNF", "GYD", "HTG", "HNL", "HKD", "HUF", "ISK", "IDR", "XDR", "IRR", "IQD", "ILS", "JMD", "JPY", "JOD", "KZT", "KES", "KPW", "KRW", "KWD", "KGS", "LAK", "LBP", "LSL", "ZAR", "LRD", "LYD", "CHF", "MOP", "MKD", "MGA", "MWK", "MYR", "MVR", "MRU", "MUR", "XUA", "MXN", "MXV", "MDL", "MNT", "MAD", "MZN", "MMK", "NAD", "NPR", "NIO", "NGN", "OMR", "PKR", "PAB", "PGK", "PYG", "PEN", "PHP", "PLN", "QAR", "RON", "RUB", "RWF", "SHP", "WST", "STN", "SAR", "RSD", "SCR", "SLL", "SLE", "SGD", "XSU", "SBD", "SOS", "SSP", "LKR", "SDG", "SRD", "SEK", "CHE", "CHW", "SYP", "TWD", "TJS", "TZS", "THB", "TOP", "TTD", "TND", "TRY", "TMT", "UGX", "UAH", "AED", "USN", "UYU", "UYI", "UYW", "UZS", "VUV", "VES", "VED", "VND", "YER", "ZMW", "ZWL", "XBA", "XBB", "XBC", "XBD", "XTS", "XXX", "XAU", "XPD", "XPT", "XAG")), /* COMMENT 'currency' */
    Total_Damage_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Total_Damage_Inflation_Adjusted_Year INTEGER CHECK (
        length(Total_Damage_Inflation_Adjusted_Year) == 4
        OR Total_Damage_Inflation_Adjusted_Year == NULL
    ),

    FOREIGN KEY(Event_ID) REFERENCES Total_Summary_Events(Event_ID)
);
