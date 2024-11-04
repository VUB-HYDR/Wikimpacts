CREATE TABLE Instance_Per_Administrative_Areas_type_numerical (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) == 7), /* COMMENT 'UID' */
    Administrative_Areas_Norm OBJECT NOT NULL, /* COMMENT 'Array' of TEXT/NULL */
    Administrative_Areas_GID OBJECT, /* COMMENT 'Array' */
    Administrative_Areas_Type OBJECT, /* COMMENT 'Array' of TEXT/NULL */
    Administrative_Areas_GeoJson OBJECT, /* COMMENT 'Array' of GeoJson Objects or NULLs */

    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31 OR Start_Date_Day == NULL),
    Start_Date_Month INTEGER CHECK (Start_Date_Month <= 12 OR Start_Date_Month == NULL),
    Start_Date_Year INTEGER CHECK (length(Start_Date_Year) == 4 OR Start_Date_Year == NULL),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31 OR End_Date_Day == NULL),
    End_Date_Month INTEGER CHECK (End_Date_Month <= 12 OR End_Date_Month == NULL),
    End_Date_Year INTEGER CHECK (length(End_Date_Year) == 4 OR End_Date_Year == NULL),

    Num_Min REAL NOT NULL CHECK (Num_Min >= 0),
    Num_Max REAL NOT NULL CHECK (Num_Max >= 0),
    Num_Approx INTEGER NOT NULL CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
    FOREIGN KEY(Event_ID) REFERENCES Total_Summary_Events(Event_ID)
);

CREATE TABLE Instance_Per_Administrative_Areas_type_monetary (
    Event_ID TEXT NOT NULL CHECK (length(Event_ID) == 7), /* COMMENT 'UID' */

    Administrative_Areas_Norm OBJECT NOT NULL, /* COMMENT 'Array' of TEXT/NULL */
    Administrative_Areas_GID OBJECT, /* COMMENT 'Array' */
    Administrative_Areas_Type OBJECT, /* COMMENT 'Array' of TEXT/NULL */
    Administrative_Areas_GeoJson OBJECT, /* COMMENT 'Array' of GeoJson Objects or NULLs */

    Start_Date_Day INTEGER CHECK (Start_Date_Day <= 31 OR Start_Date_Day == NULL),
    Start_Date_Month INTEGER CHECK (Start_Date_Month <= 12 OR Start_Date_Month == NULL),
    Start_Date_Year INTEGER CHECK (length(Start_Date_Year) == 4 OR Start_Date_Year == NULL),
    End_Date_Day INTEGER CHECK (End_Date_Day <= 31 OR End_Date_Day == NULL),
    End_Date_Month INTEGER CHECK (End_Date_Month <= 12 OR End_Date_Month == NULL),
    End_Date_Year INTEGER CHECK (length(End_Date_Year) == 4 OR End_Date_Year == NULL),

    Num_Min REAL NOT NULL CHECK (Num_Min >= 0),
    Num_Max REAL NOT NULL CHECK (Num_Max >= 0),
    Num_Approx INTEGER NOT NULL CHECK (Num_Approx == 1 OR Num_Approx ==  0), /* COMMENT 'Boolean' */
    Num_Unit TEXT NOT NULL CHECK (Num_Unit in ('AFN', 'EUR', 'ALL', 'DZD', 'USD', 'AOA', 'XCD', 'ARS', 'AMD', 'AWG', 'AUD', 'AZN', 'BSD', 'BHD', 'BDT', 'BBD', 'BYN', 'BZD', 'XOF', 'BMD', 'INR', 'BTN', 'BOB', 'BOV', 'BAM', 'BWP', 'NOK', 'BRL', 'BND', 'BGN', 'BIF', 'CVE', 'KHR', 'XAF', 'CAD', 'KYD', 'CLP', 'CLF', 'CNY', 'COP', 'COU', 'KMF', 'CDF', 'NZD', 'CRC', 'HRK', 'CUP', 'CUC', 'ANG', 'CZK', 'DKK', 'DJF', 'DOP', 'EGP', 'SVC', 'ERN', 'SZL', 'ETB', 'FKP', 'FJD', 'XPF', 'GMD', 'GEL', 'GHS', 'GIP', 'GTQ', 'GBP', 'GNF', 'GYD', 'HTG', 'HNL', 'HKD', 'HUF', 'ISK', 'IDR', 'XDR', 'IRR', 'IQD', 'ILS', 'JMD', 'JPY', 'JOD', 'KZT', 'KES', 'KPW', 'KRW', 'KWD', 'KGS', 'LAK', 'LBP', 'LSL', 'ZAR', 'LRD', 'LYD', 'CHF', 'MOP', 'MKD', 'MGA', 'MWK', 'MYR', 'MVR', 'MRU', 'MUR', 'XUA', 'MXN', 'MXV', 'MDL', 'MNT', 'MAD', 'MZN', 'MMK', 'NAD', 'NPR', 'NIO', 'NGN', 'OMR', 'PKR', 'PAB', 'PGK', 'PYG', 'PEN', 'PHP', 'PLN', 'QAR', 'RON', 'RUB', 'RWF', 'SHP', 'WST', 'STN', 'SAR', 'RSD', 'SCR', 'SLL', 'SLE', 'SGD', 'XSU', 'SBD', 'SOS', 'SSP', 'LKR', 'SDG', 'SRD', 'SEK', 'CHE', 'CHW', 'SYP', 'TWD', 'TJS', 'TZS', 'THB', 'TOP', 'TTD', 'TND', 'TRY', 'TMT', 'UGX', 'UAH', 'AED', 'USN', 'UYU', 'UYI', 'UYW', 'UZS', 'VUV', 'VES', 'VED', 'VND', 'YER', 'ZMW', 'ZWL', 'XBA', 'XBB', 'XBC', 'XBD', 'XTS', 'XXX', 'XAU', 'XPD', 'XPT', 'XAG')), /* COMMENT 'currency' */
    Num_Inflation_Adjusted INTEGER, /* COMMENT 'Boolean' */
    Num_Inflation_Adjusted_Year INTEGER CHECK (
        length(Num_Inflation_Adjusted_Year) == 4
        OR Num_Inflation_Adjusted_Year == NULL
    ),

    FOREIGN KEY(Event_ID) REFERENCES Total_Summary_Events(Event_ID)
);
