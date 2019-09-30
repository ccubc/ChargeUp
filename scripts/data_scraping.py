from googleplaces import GooglePlaces
import pandas as pd
import numpy as np
import os
file_dir = os.path.dirname(os.path.abspath('__file__'))
os.chdir(file_dir)
# read my Google API
API_path = os.path.join(file_dir, "..")
my_API_key = open(API_path+'/'+"GoogleAPIKey.txt", "r").read()

google_places = GooglePlaces(my_API_key)
def googleplaces_query_to_dataframe (lng, lat, keyword, radius, *place_type):
    """Transform query results from Google API to pandas dataframe
    
    Args
    ------------
    lng: longitude of the searching point
    lat: latitude of the searching point
    keyword: keyword to search for, e.g., parking lot, charging station, etc.
    radius: radius of the search range
    place_type: type of the place
    
    Returns
    ------------
    dataframe of searching result
    """
    places_data_list = []
    query_result = google_places.nearby_search(
    lat_lng={'lat': lat, 'lng': lng}, keyword=keyword,
    radius=radius)    
#    query_result = google_places.nearby_search(
#    lat_lng={'lat': lat, 'lng': lng}, keyword=keyword,
#    radius=radius, rankby = 'distance')
    for place in query_result.places: 
        place.get_details()
        places_data_list.append([place.place_id, place.name, float(place.geo_location['lat']),float(place.geo_location['lng']), place.rating, place.url])
    #default query only returns the first 20
    while query_result.has_next_page_token :
        query_result= google_places.nearby_search(pagetoken=query_result.next_page_token)
        for place in query_result.places:
            place.get_details()
            places_data_list.append([place.place_id, place.name, float(place.geo_location['lat']),float(place.geo_location['lng']), place.rating, place.url])
    df = pd.DataFrame(places_data_list, columns = ['ID','Name', 'latitude', 'longitude', 'Rating', 'Url'])
    return df
# Google place ranks by prominanse and shows up to 60 results
# If only search nearby one coordinate, can not get all data
# therefore will search over a grid of coordinates with reasonable distance away from each other and then delete the repeated ones

# create coordinates grid to search for
lat_list = np.arange(43.582157, 43.792441, 0.025)
lng_list = np.arange(-79.639066, -79.118471,0.05)
xx,yy = np.meshgrid(lat_list,lng_list) 
coords = np.array([xx, yy]).reshape(2,-1).T
coords = pd.DataFrame(coords, columns = ['Lat', 'Lon'])

def poi_scrape(centroids_df, keyword, output_file_name, *place_type):
    """ Scraping points of interests given a dataframe that contains geo-coordinates of centroids 
    
    Args
    ---------
    centroids_df: a dataframe of points to search for, must contain columns 'Lat' and 'Lon' 
    keyword: searching keyword
    output_file_name: file name of the search output
    place_type: type of the searched place
    
    Returns
    ---------
    a dataframe of searching result
    
    
    """
    df = pd.DataFrame()
    row_index = 0
    radius = 3000
    for index, row in centroids_df.iterrows():
        lat, lng= row['Lat'], row['Lon']   
        current_length = len(df)
        df = df.append(googleplaces_query_to_dataframe (lng, lat, keyword, radius, *place_type ))
        print('scraped row ', row_index, ' and found', len(df)-current_length, 'results')
        row_index += 1
    print('# results before dup drop', len(df))
    df_drop_dup = df.drop_duplicates('ID')
    print('# results after dup drop', len(df_drop_dup))
    df_drop_dup.to_excel('/data/raw/'+output_file_name)
    return df_drop_dup

# scrape charging stations in Toronto
df_charging = poi_scrape(coords, 'charging station','TRT_charging.xlsx')
# scrape parking lots in Toronto
df_parking = poi_scrape(coords, 'parking', 'TRT_parking_type_parking.xlsx', 'parking')
# drop the "parks" observations
df_parking2 = df_parking[df_parking.Name.str.endswith('Park') == False]
df_parking2.to_excel('/data/raw/TRT_parking_lots_2.xlsx')

df_foodcourt = poi_scrape(coords, 'food court', 'TRT_foodcourt.xlsx')
df_shopping = poi_scrape(coords, 'shopping center', 'TRT_shopping.xlsx')
df_restaurant = poi_scrape(coords, 'restaurant', 'TRT_restaurant.xlsx')
df_grocery = poi_scrape(coords, 'grocery store', 'TRT_grocery.xlsx')
df_gas = poi_scrape(coords, 'gas station', 'TRT_gas.xlsx')
df_university = poi_scrape(coords, 'university', 'TRT_university.xlsx')
