#Prepara il file dataset_milano.csv
import geopandas as gpd
import pandas as pd
from shapely.wkt import loads

trips = pd.read_csv('.../202209-202311_trips-001-001/202307_trips.csv')

trips_filtered = trips.sample(frac =.10)


trips_filtered['geom_wkt_estimated_route'] = trips_filtered['geom_wkt_estimated_route'].apply(loads)
nil_milano = pd.read_csv('.../quartieri_2030.csv', usecols=['WKT','NIL'])
nil_milano['WKT'] = nil_milano['WKT'].apply(loads)
nil_milano= gpd.GeoDataFrame(nil_milano, geometry="WKT", crs='epsg:4326')

trips_filtered['geom_wkt_raw_start_point'] = trips_filtered['geom_wkt_raw_start_point'].apply(loads)
trips_filtered['geom_wkt_raw_end_point'] = trips_filtered['geom_wkt_raw_end_point'].apply(loads)
trips_filtered = gpd.GeoDataFrame(trips_filtered, geometry='geom_wkt_raw_start_point', crs='epsg:4326')

joined_data = gpd.sjoin(trips_filtered, nil_milano, predicate="intersects", how="left")
joined_data = joined_data.drop(columns= ['index_right'])
joined_data = joined_data.rename(columns = {'NIL': 'Partenza'})

joined_data = gpd.GeoDataFrame(joined_data, geometry='geom_wkt_raw_end_point',crs='epsg:4326')
joined_data2 = gpd.sjoin(joined_data, nil_milano, predicate="intersects", how = 'left')
joined_data2 = joined_data2.drop(columns= ['index_right'])
joined_data2 = joined_data2.rename(columns = {'NIL': 'Arrivo'})

joined_data2 = joined_data2[joined_data2['Partenza'] != joined_data2['Arrivo']]

joined_data2['lon_part'] = joined_data2.geom_wkt_raw_start_point.x
joined_data2['lat_part'] = joined_data2.geom_wkt_raw_start_point.y

joined_data2['lon_dest'] = joined_data2.geom_wkt_raw_end_point.x
joined_data2['lat_dest'] = joined_data2.geom_wkt_raw_end_point.y


joined_data2= joined_data2.drop(columns=['geom_wkt_raw_start_point','geom_wkt_raw_end_point','geom_wkt_estimated_route'])

pd.DataFrame.to_csv(joined_data2, 'dataset_milano.csv')
