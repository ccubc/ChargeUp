import pandas as pd
import geopandas as gpd
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from scipy.spatial import distance
from shapely.geometry import Point

import os
file_dir = os.path.dirname(os.path.abspath('__file__'))
os.chdir(file_dir)

# Read trip data from Toronto's Transportation Survey 2016
df = pd.read_excel('data/raw/tts2016_ward_Toronto.xlsx')
df_trip = df[df.variable.str.contains('Number of trips made to the area as auto driver during ')].copy()
df_trip['time_of_day'] = ['morning', 'afternoon']
df_trip = df_trip.drop('variable', axis = 1).transpose()
df_trip['ward'] = df_trip.index
df_trip.columns = ['morning trips', 'afternoon trips', 'ward']
df_trip.to_excel('data/processed/trip_to_wards.xlsx', index=False)

# draw map to visualize number of trips to each ward
shp_path = 'data/raw/Toronto_wards/icitw_wgs84.shp'
df_ward = gpd.read_file(shp_path)
df_ward['SCODE_NAME']=df_ward['SCODE_NAME'].astype(int)
df_ward['ward'] = 'Ward '+ df_ward['SCODE_NAME'].astype(str)
ward_trip_shp = df_ward.merge(df_trip, how='left')
ward_trip_shp.plot(figsize=(10,10), column = 'morning trips',cmap='OrRd')

# combine with census tract shapefiles
shp_path2 ='data/raw/Toronto_shp/Toronto_CMA_01_popn_age_sex_marital.shp'
df_TRT_shp = gpd.read_file(shp_path2)
ward_trip_shp.crs = {'init' :'epsg:4326'}
df_TRT_shp.crs == ward_trip_shp.crs
ward_trip_shp = ward_trip_shp.to_crs(df_TRT_shp.crs)
CT_trips = gpd.sjoin(df_TRT_shp, ward_trip_shp, how="inner", op="intersects")
# get the CTs' centroids
CT_trips['centroid'] = CT_trips['geometry'].centroid
CT_trips['long']=CT_trips.centroid.x
CT_trips['lat']=CT_trips.centroid.y

CT_trips_clean = CT_trips[['CTNAME','POP06', 'L_AREA', 'ward', 'long', 'lat', 'morning trips', 'afternoon trips']].copy()
CT_trips_clean.loc[CT_trips_clean['morning trips'].isnull(),'morning trips'] = 0
CT_trips_clean.loc[CT_trips_clean['afternoon trips'].isnull(),'afternoon trips'] = 0

# evenly distribute Census Tracts to different wards if they intersect with various wards
CT_trips_clean['CT_ward_count'] = CT_trips_clean.groupby(['CTNAME'])['CTNAME'].transform('size')
CT_trips_clean['CT_ward_weight'] = 1/CT_trips_clean['CT_ward_count']
CT_trips_clean['ward_count_weighted']=CT_trips_clean['CT_ward_weight'].groupby(CT_trips_clean['ward']).transform('sum')
CT_trips_clean['CT_avg_AM_trips'] = CT_trips_clean['morning trips']/CT_trips_clean['ward_count_weighted']*CT_trips_clean['CT_ward_weight']
CT_trips_clean['CT_AM_trips'] = CT_trips_clean['CT_avg_AM_trips'].groupby(CT_trips_clean['CTNAME']).transform('sum')
CT_trips_clean=CT_trips_clean.drop_duplicates(subset = ['CTNAME'])
# each row represents a census tract, the info of "# trips in the ward that this CT belongs to" is added
CT_trips_clean = CT_trips_clean[['CTNAME', 'POP06', 'L_AREA', 'ward', 'long', 'lat', 'CT_AM_trips']]

# merge with count of charging stations
shp_path = 'data/processed/shape_join_points.shp'
df_TRT_shp = gpd.read_file(shp_path)
df_TRT_shp = df_TRT_shp[['CTNAME','charging s']]
CT_trips_pts = pd.merge(df_TRT_shp, CT_trips_clean, on = 'CTNAME')
CT_trips_pts = CT_trips_pts.set_index('CTNAME')
CT_trips_pts.to_excel('data/cleaned/optimization_CT_AM_trips_chgstn.xlsx')



# Locations of parking lots
df_parking = pd.read_excel('data/raw/TRT_parking_lots_2.xlsx')
def df_to_gdf(df):
    """takes a dataframe with columns named 'longitude' and 'latitude' 
    to transform to a geodataframe with point features"""
    
    df['coordinates'] = df[['longitude', 'latitude']].values.tolist()
    df['coordinates'] = df['coordinates'].apply(Point)
    df = gpd.GeoDataFrame(df, geometry = 'coordinates')
    return df
gdf_parking = df_to_gdf(df_parking)

# spacial join with ward's shapefile
gdf_parking.crs = {'init' :'epsg:4326'}
gdf_parking.crs == df_ward.crs
parking_ward = gpd.sjoin(gdf_parking, df_ward, how="inner", op="within")
parking_ward_hr = parking_ward[parking_ward['Rating']>0][['latitude','longitude','Rating','Name','Url','ID','ward']].copy()
parking_ward_hr = parking_ward_hr.set_index('ID')
parking_ward_hr.to_excel('data/cleaned/optimization_parking_location.xlsx')

# cluster the parking lots (to break down the problem for faster optimization)
gdf_parking = gdf_parking.reset_index()
gdf_parking2 = gdf_parking[['latitude','longitude']]
gdf_parking2 = gdf_parking2[['latitude','longitude']]

# Scaling the data to normalize
model = KMeans(n_clusters=40).fit(gdf_parking2)
x = gdf_parking2.latitude
y = gdf_parking2.longitude

gdf_parking2['cluster'] = model.labels_
gdf_parking3 = pd.merge(gdf_parking, gdf_parking2).drop_duplicates(subset=['latitude','longitude'])
df_parking_cluster = gdf_parking3[['latitude','longitude','Rating','Name','Url','ID','ward','cluster']].copy()
df_parking_cluster.to_excel('data/cleaned/optimization_parking_location_cluster.xlsx')


# assign trip destination points to nearest parking lots' cluster
classifier = KNeighborsClassifier(n_neighbors=1)
classifier.fit(gdf_parking3[['longitude','latitude']], gdf_parking3['cluster'])
CT_trips_pts['parking_cluster'] = classifier.predict(CT_trips_pts[['long','lat']])
CT_trips_pts.to_excel('data/cleaned/optimization_CT_AM_trips_cluster.xlsx')

# create distance matrix of parking lots to destination points

cluster_list = [i for i in range(40)]
for cluster_id in cluster_list:
    df_chg = gdf_parking3.loc[gdf_parking3['cluster']==cluster_id]
    coords_pk = [(x,y) for x,y in zip(df_chg['longitude'],df_chg['latitude'])]
    df_demand = CT_trips_pts.loc[CT_trips_pts['parking_cluster']==cluster_id]
    coords_trip = [(x,y) for x,y in zip(df_demand['long'],df_demand['lat'])]

    distance_matrix = distance.cdist(coords_pk, coords_trip, 'euclidean')
    transfer_ratio = 85 # roughly transfer distance to km
    distance_matrix2 = transfer_ratio*distance_matrix
    df_distance = pd.DataFrame(distance_matrix2, index = df_chg.ID.tolist() ,columns = df_demand.index.tolist())
    # print (df_distance.shape)
    df_distance.to_excel('data/cleaned/distance_mtx_cluster'+str(cluster_id)+'.xlsx')


