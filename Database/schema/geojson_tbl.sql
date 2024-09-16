
CREATE TABLE GeoJson_Obj (
    nid TEXT PRIMARY KEY NOT NULL, /* COMMENT 'NID' */
    geojson_obj OBJECT NOT NULL /* GeoJson Object */
);

    /* TODO: fix foreign key relations one-to-many with Administrative_Areas_GeoJson */
    /* FOREIGN KEY(nid) */
