rem cd /d C:\OSGeo4W64\share\gdal\


ogr2ogr -overwrite -t_srs EPSG:2154  -geomfield geom -f "ESRI Shapefile" S:\00_MODULE_EXPORT_BDCEN\exports\st_sig_poly.shp ^
PG:"host=localhost dbname=dbname user=postgres password=*****" ^
-sql "select * from export.e_st_sig_poly"


ogr2ogr -overwrite -t_srs EPSG:2154  -geomfield geom -f "ESRI Shapefile" S:\00_MODULE_EXPORT_BDCEN\exports\st_sig_point.shp ^
PG:"host=localhost dbname=dbname user=postgres password=*****" ^
-sql "select * from export.e_st_sig_point"


ogr2ogr -overwrite -t_srs EPSG:2154  -geomfield geom -f "ESRI Shapefile" S:\00_MODULE_EXPORT_BDCEN\exports\st_sig_lignes.shp ^
PG:"host=localhost dbname=dbname user=postgres password=*****" ^
-sql "select * from export.e_st_sig_lignes"
