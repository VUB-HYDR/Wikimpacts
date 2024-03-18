CREATE TABLE `Events` (
  `Event_ID` TEXT PRIMARY KEY NOT NULL COMMENT 'UID',
  `Event_Name` TEXT NOT NULL,
  `Source` TEXT NOT NULL COMMENT 'URL',
  `execution_time` REAL NOT NULL,
  `Main_Event` TEXT NOT NULL COMMENT 'Categorical',
  `Perils` OBJECT COMMENT 'Array',
  `Location` OBJECT COMMENT 'Array',
  `Single_Date_Day` INTEGER,
  `Single_Date_Month` INTEGER,
  `Single_Date_Year` INTEGER,
  `Start_Date_Day` INTEGER,
  `Start_Date_Month` INTEGER,
  `Start_Date_Year` INTEGER,
  `End_Date_Day` INTEGER,
  `End_Date_Month` INTEGER,
  `End_Date_Year` INTEGER,
  `Total_Deaths` INTEGER,
  `Total_Injuries` INTEGER,
  `Total_Displaced` INTEGER,
  `Total_Homeless` INTEGER,
  `Total_Insured_Damage` REAL,
  `Total_Insured_Damage_Units` TEXT COMMENT 'currency',
  `Total_Insured_Damage_Inflation_Adjusted` INTEGER COMMENT 'Boolean',
  `Total_Insured_Damage_Inflation_Adjusted_Year` INTEGER,
  `Total_Damage` REAL,
  `Total_Damage_Units` TEXT COMMENT 'currency',
  `Total_Damage_Inflation_Adjusted` INTEGER COMMENT 'Boolean',
  `Total_Damage_Inflation_Adjusted_Year` INTEGER,
  `Total_Buildings_Damaged` INTEGER
);

CREATE TABLE `Specific_Instance_Per_Country_Death` (
  `Event_ID` TEXT NOT NULL COMMENT 'UID',
  `Country` TEXT NOT NULL COMMENT 'Country Code',
  `Location_Death` TEXT,
  `Location_GCS` OBJECT COMMENT 'GCS',
  `Time_Death_Day` INTEGER,
  `Time_Death_Month` INTEGER,
  `Time_Death_Year` INTEGER,
  `Num_Death` INTEGER
);

CREATE TABLE `Specific_Instance_Per_Country_Injuries` (
  `Event_ID` TEXT NOT NULL COMMENT 'UID',
  `Country` TEXT NOT NULL COMMENT 'Country Code',
  `Location_Injuries` TEXT,
  `Location_GCS` OBJECT COMMENT 'GCS',
  `Time_Injuries_Day` INTEGER,
  `Time_Injuries_Month` INTEGER,
  `Time_Injuries_Year` INTEGER,
  `Num_Injuries` INTEGER
);

CREATE TABLE `Specific_Instance_Per_Country_Displacement` (
  `Event_ID` TEXT NOT NULL COMMENT 'UID',
  `Country` TEXT NOT NULL COMMENT 'Country Code',
  `Location_Displace` TEXT,
  `Location_GCS` OBJECT COMMENT 'GCS',
  `Time_Displaced_Day` INTEGER,
  `Time_Displaced_Month` INTEGER,
  `Time_Displaced_Year` INTEGER,
  `Num_Displaced` INTEGER
);

CREATE TABLE `Specific_Instance_Per_Country_Homelessness` (
  `Event_ID` TEXT NOT NULL COMMENT 'UID',
  `Country` TEXT NOT NULL COMMENT 'Country Code',
  `Location_Homeless` TEXT,
  `Location_GCS` OBJECT COMMENT 'GCS',
  `Time_Homeless_Day` INTEGER,
  `Time_Homeless_Month` INTEGER,
  `Time_Homeless_Year` INTEGER,
  `Num_Homeless` INTEGER
);

CREATE TABLE `Specific_Instance_Per_Country_Insured_Damage` (
  `Event_ID` TEXT NOT NULL COMMENT 'UID',
  `Country` TEXT NOT NULL COMMENT 'Country Code',
  `Location_Insured_Damage` TEXT,
  `Location_GCS` OBJECT COMMENT 'GCS',
  `Insured_Damage` REAL,
  `Insured_Damage_Units` TEXT COMMENT 'currency',
  `Insured_Damage_Inflation_Adjusted` INTEGER COMMENT 'Boolean',
  `Insured_Damage_Inflation_Adjusted_Year` INTEGER
);

CREATE TABLE `Specific_Instance_Per_Country_Economic_Damage` (
  `Event_ID` TEXT NOT NULL COMMENT 'UID',
  `Country` TEXT NOT NULL COMMENT 'Country Code',
  `Location_Damage` TEXT,
  `Location_GCS` OBJECT COMMENT 'GCS',
  `Damage` REAL,
  `Damage_Units` TEXT COMMENT 'currency',
  `Damage_Inflation_Adjusted` INTEGER COMMENT 'Boolean',
  `Damage_Inflation_Adjusted_Year` INTEGER
);

CREATE TABLE `Specific_Instance_Per_Country_Building_Damage` (
  `Event_ID` TEXT NOT NULL COMMENT 'UID',
  `Country` TEXT NOT NULL COMMENT 'Country Code',
  `Location_Building` TEXT,
  `Location_GCS` OBJECT COMMENT 'GCS',
  `Time_Building_Day` INTEGER,
  `Time_Building_Month` INTEGER,
  `Time_Building_Year` INTEGER,
  `Buildings_Damaged` REAL
);

ALTER TABLE `Specific_Instance_Per_Country_Death` ADD FOREIGN KEY (`Event_ID`) REFERENCES `Events` (`Event_ID`);

ALTER TABLE `Specific_Instance_Per_Country_Injuries` ADD FOREIGN KEY (`Event_ID`) REFERENCES `Events` (`Event_ID`);

ALTER TABLE `Specific_Instance_Per_Country_Displacement` ADD FOREIGN KEY (`Event_ID`) REFERENCES `Events` (`Event_ID`);

ALTER TABLE `Specific_Instance_Per_Country_Homelessness` ADD FOREIGN KEY (`Event_ID`) REFERENCES `Events` (`Event_ID`);

ALTER TABLE `Specific_Instance_Per_Country_Insured_Damage` ADD FOREIGN KEY (`Event_ID`) REFERENCES `Events` (`Event_ID`);

ALTER TABLE `Specific_Instance_Per_Country_Economic_Damage` ADD FOREIGN KEY (`Event_ID`) REFERENCES `Events` (`Event_ID`);

ALTER TABLE `Specific_Instance_Per_Country_Building_Damage` ADD FOREIGN KEY (`Event_ID`) REFERENCES `Events` (`Event_ID`);
