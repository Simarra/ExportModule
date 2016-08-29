rem cd /d C:\OSGeo4W64\share\gdal\






ogr2ogr -t_srs EPSG:2154 -f "ESRI Shapefile" S:\00_MODULE_EXPORT_BDCEN\exports\faunepoint.shp ^
PG:"host=localhost dbname=dbname user=postgres password=****" ^
-sql "select * from export.r_id_all where id_perm like 'sig_faune_poly%%' "


ogr2ogr -t_srs EPSG:2154 -f "ESRI Shapefile" S:\00_MODULE_EXPORT_BDCEN\exports\faunepoint.shp ^
PG:"host=localhost dbname=dbname user=postgres password=****" ^
-sql "select * from export.r_id_all where id_perm like 'sig_faune_point%%' "



ogr2ogr -t_srs EPSG:2154 -f "ESRI Shapefile" S:\00_MODULE_EXPORT_BDCEN\exports\fauneline.shp ^
PG:"host=localhost dbname=dbname user=postgres password=****" ^
-sql "select * from export.r_id_all where id_perm like 'sig_faune_line%%' "



ogr2ogr -t_srs EPSG:2154 -f "ESRI Shapefile" S:\00_MODULE_EXPORT_BDCEN\exports\sitesgeo.shp ^
PG:"host=localhost dbname=dbname user=postgres password=****" ^
-sql "select * from export.r_codes_des_sites where geom is not null"




ogr2ogr -t_srs EPSG:2154 -f "ESRI Shapefile" S:\00_MODULE_EXPORT_BDCEN\exports\secteursgeo.shp ^
PG:"host=localhost dbname=dbname user=postgres password=****" ^
-sql "select * from export.r_id_des_secteurs where geom is not null"
