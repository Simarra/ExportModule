--cd C:\OSGeo4W64\share\gdal
## referencement du fichier de projection : gcs.csv


-- DOIT TAPER DANS DES VUES

ogr2ogr -t_srs EPSG:2154 -f "ESRI Shapefile" C:\Users\stagesig\Desktop\cobaye0\maTable.shp ^
PG:"host=192.168.1.2 dbname=bdcenpicardie_dev user=postgres password=burotec" ^
-sql "select * from export.r_faune where id_perm like 'sig_faune_poly%'"^


pause


ogr2ogr -t_srs EPSG:2154 -f "ESRI Shapefile" C:\Users\stagesig\Desktop\cobaye0\maTable.shp ^
PG:"host=192.168.1.2 dbname=bdcenpicardie_dev user=postgres password=burotec" ^
-sql "select * from export.r_faune where id_perm like 'sig_faune_poly%'"^