import os
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from scipy.spatial import distance
from pulp import *
import folium
from folium.plugins import MarkerCluster
file_dir = os.path.dirname(os.path.abspath('__file__'))
os.chdir(file_dir)

# load cleaned datasets
df_demand = pd.read_excel('data/cleaned/optimization_CT_AM_trips_cluster.xlsx')
df_parking= pd.read_excel('data/cleaned/optimization_parking_location_cluster.xlsx')

# To speed up the optimization process, optimize over 40 clusters of parking lots, then combine the results
cluster_list = [i for i in range(40)]


def gen_sets(cluster_id, df_demand, df_parking):
    """Generate sets to use in the optimization problem
    
    Args
    -----------
    cluster_id: id of the cluster to optimize over
    df_demand: dataframe of demand for charging
    df_parking: dataframe of parking lots (candidates for charging stations)
    
    Returns
    -----------
    lists of demand location and potential charging station location
    
    """
    # set of charging demand locations (destinations)
    df_demand_cls = df_demand.loc[df_demand['parking_cluster'] == cluster_id]
    demand_lc = df_demand_cls.index.tolist()
    # set of candidates for charging station locations (currently existing parking lots)
    df_parking_cls = df_parking.loc[df_parking['cluster'] == cluster_id]
    chg_lc = df_parking_cls.index.tolist()
    return demand_lc, chg_lc

def gen_parameters(cluster_id, df_demand, df_parking):
    """Generate parameters to use in the optimization problem, 
    including capacity of charging station, cost to install charging stations, 
    and travel costs to and from the charging stations (present value)
    
    Args
    -----------
    cluster_id: id of the cluster to optimize over
    df_demand: dataframe of demand for charging
    df_parking: dataframe of parking lots (candidates for charging stations)

    Returns
    -----------
    dictionaries of fixed cost to build charging stations, capacity of charging stations,
    travel cost matrix of demand points to charging stations
    """
    # fixed cost to install a charging station with 5 level II chargers
    df_parking_cls = df_parking.loc[df_parking['cluster'] == cluster_id].copy()
    df_parking_cls['fixed_cost'] = 11000
    fixed_cost = df_parking_cls['fixed_cost'].to_dict()
    
    # capacity: 5 chargers, with each charger charging 4 cars at most per day
    df_parking_cls['chg_capacity'] = 20
    capacity = df_parking_cls['chg_capacity'].to_dict()
    
    # distance matrix of charging station location candidates and charging demand location
    
    coords_pk = [(x,y) for x,y in zip(df_parking_cls['longitude'],df_parking_cls['latitude'])]
    df_demand_cls = df_demand.loc[df_demand['parking_cluster']==cluster_id]
    coords_trip = [(x,y) for x,y in zip(df_demand_cls['long'],df_demand_cls['lat'])]

    distance_matrix = distance.cdist(coords_pk, coords_trip, 'euclidean')
    transfer_ratio = 85
    distance_matrix2 = transfer_ratio*distance_matrix
    df_distance = pd.DataFrame(distance_matrix2, index = df_parking_cls.index.tolist() ,columns = df_demand_cls.index.tolist())
    df_travel_cost = df_distance * 1457
    dic_cost_matrix = df_travel_cost.to_dict('index')
    return fixed_cost, capacity, dic_cost_matrix

def gen_demand(df, demand_ratio, column = 'CT_AM_trips'):
    """generate the (unsatisfied) demand for charging (during day time) for each census tract, 
    which equals to total demand for charging minus charging capacity of currently existing charging stations
    
    Args
    -----------
    df: dataframe that tells number of car trips to each demand location
    demand_ratio: a ratio that equals number of electric cars needs charging divided by number of car trips
    
    Returns
    -----------
    df1: dataframe that shows given today's charging capacity, how many electric cars need charging at each location
    """
    df1 = df.copy()
    df1['demand_chg'] = df1[column]*demand_ratio
    df1['extra_demand_chg'] = df1['demand_chg'] - df1['charging s']*20
    # replace the negative charging demand to 0
    num = df1._get_numeric_data()
    num[num < 0] = 0 
    df1 = df1.round({'extra_demand_chg':0})
    return df1

# create a list that iterates all possible combinations of EVPR and homg_chg_ratio and return resulted EVPR*pr_ch
# need to carefully define long_commute ratio
# allow home charging ratio to range between 0.5 and 0.9
# allow EVPR to range between 0.01 to 0.2
# maximum of demand ratio would be: 0.2*(0.1*1+0.9*0.5/5) = 0.038
# minimum of demand ratio would be: 0.01*(0.1*1+0.9*0.1/5) = 0.00118
list_demand_ratio = np.linspace(0.00118, 0.038, num=30).tolist()
# will iterate through the 30 numbers to plot the map with optimal locations of stations

def optimize_cls(cluster_id, df_demand, df_parking, demand_ratio):
    """
    Optimize over a cluster of parking lots to find optimal charging station locations
    
    Args
    -----------
    cluster_id: id of the cluster to optimize over
    df_demand: dataframe of demand for charging
    df_parking: dataframe of parking lots (candidates for charging stations)
    demand_ratio: a ratio that equals number of electric cars needs charging divided by number of car trips

    Returns
    -----------
    opt_location: a list of optimal locations
    df_status: the status of the optimization (Optimal/Infeasible)
    """
    demand_lc, chg_lc = gen_sets(cluster_id, df_demand, df_parking)
    fixed_cost, capacity, dic_cost_matrix = gen_parameters(cluster_id, df_demand, df_parking)
    df_demand_cls = df_demand.loc[df_demand['parking_cluster'] == cluster_id]
    df_demand = gen_demand(df_demand_cls, demand_ratio)
    demand = df_demand['demand_chg'].to_dict()
    # set up the optimization problem
    prob = LpProblem('FacilityLocation', LpMinimize)
    serv_vars = LpVariable.dicts("Service",
                                 [(i,j) for i in demand_lc
                                        for j in chg_lc],
                                  0)
    use_vars = LpVariable.dicts("UseLocation", chg_lc, 0, 1, LpBinary)
    prob += lpSum(fixed_cost[j]*use_vars[j] for j in chg_lc) + lpSum(dic_cost_matrix[j][i]*serv_vars[(i,j)] for j in chg_lc for i in demand_lc)
    for i in demand_lc:
        prob += lpSum(serv_vars[(i,j)] for j in chg_lc) == demand[i] # constraint 1
    for j in chg_lc:
        prob += lpSum(serv_vars[(i,j)] for i in demand_lc) <= capacity[j]*use_vars[j]
    for i in demand_lc:
        for j in chg_lc:
            prob += serv_vars[(i,j)] <= demand[i]*use_vars[j]
    print(cluster_id)
    prob.solve()
    print("Status: ", LpStatus[prob.status])
    TOL = .00001
    opt_location = []
    for i in chg_lc:
        if use_vars[i].varValue > TOL:
            opt_location.append(i)
            print("Eslablish charging station at site", i)
    df_status = pd.DataFrame({"cluster": [cluster_id], "status": [LpStatus[prob.status]], "N_chg": [len(opt_location)]})
    return opt_location, df_status

def df_to_gdf(df):
    """takes a dataframe with columns named 'longitude' and 'latitude' 
    to transform to a geodataframe with point features    
    """
    
    df['coordinates'] = df[['longitude', 'latitude']].values.tolist()
    df['coordinates'] = df['coordinates'].apply(Point)
    df = gpd.GeoDataFrame(df, geometry = 'coordinates')
    return df

# load current charging stations to be shown on map
df_chg_stn = pd.read_excel('data/raw/TRT_charging.xlsx')
gdf_chg_stn = df_to_gdf(df_chg_stn)

def main_map_generater(demand_ratio, df_demand, df_parking, cluster_list):
    """
    Because the optimization process takes about 3 - 5 minutes per iteration, 
    I prepare the results of optimization beforehead for the webapp.
    
    Args
    ------------
    cluster_list: list of the cluster ids to optimize over
    df_demand: dataframe of demand for charging
    df_parking: dataframe of parking lots (candidates for charging stations)
    demand_ratio: a ratio that equals number of electric cars needs charging divided by number of car trips
    
    Returns
    ------------
    df_output_status: dataframe of optimization output status (optimal/infeasible)
    gdf_optimal_parking: geodataframe of optimal locations for charging stations
    
    """
    opt_chg_location = []
    df_output_status = pd.DataFrame(columns = ['cluster', 'status', 'N_chg'])
    for cluster_id in cluster_list:
        opt_location, df_status = optimize_cls(cluster_id, df_demand, df_parking, demand_ratio)
        opt_chg_location += opt_location
        df_output_status =df_output_status.append(df_status)
    df_output_status.to_excel('data/processed/chg_stn_status_cluster_demand_ratio'+str(demand_ratio)[2:]+'.xlsx')
    df_opt_chg_lc = df_parking.ix[opt_chg_location]
    df_opt_chg_lc.to_excel('data/processed/chg_stn_location_cluster_demand_ratio'+str(demand_ratio)[2:]+'.xlsx')
    gdf_optimal_parking = df_to_gdf(df_opt_chg_lc)
    gdf_optimal_parking.plot()
    plt.savefig('graphs/location_cluster_demand_ratio_'+str(demand_ratio)[2:]+'.jpg')
    # draw map using folium
    # add base layer --- map of Toronto
    lat, lng = 43.653908, -79.384293  # Toronto City Hall
    map_TRT = folium.Map(location=[lat, lng], zoom_start = 14) 
    # add layer --- existing charging stations
    chg_layer = folium.FeatureGroup(name = 'Existing Charging Stations')
    marker_cluster = MarkerCluster()
    for idx, row in gdf_chg_stn.iterrows():
        folium.Marker([float(row['coordinates'].y), 
                       float(row['coordinates'].x)], 
                     popup = row['Name']).add_to(marker_cluster)
    chg_layer.add_child(marker_cluster)
    map_TRT.add_child(chg_layer)
    # add layer --- suggested extra charging stations
    opt_chg_layer = folium.FeatureGroup(name = 'Suggested Charging Station Locations')
    marker_cluster = MarkerCluster()
    for idx, row in gdf_optimal_parking.iterrows():
        folium.Marker([float(row['coordinates'].y), 
                       float(row['coordinates'].x)], 
                    icon = folium.Icon(color = 'green', icon = 'circle'),
                     popup = row['Name']).add_to(marker_cluster)
    opt_chg_layer.add_child(marker_cluster)
    map_TRT.add_child(opt_chg_layer)
    map_TRT.add_child(folium.LayerControl())
    map_TRT.save('graphs/folium/TRT_map_demand_ratio_'+str(demand_ratio)[2:]+'.html')
    return df_output_status, gdf_optimal_parking

# iterate through possible demand ratios, optimize and draw maps
counter = 0
for demand_ratio in list_demand_ratio:    
    print('demand ratio = ', demand_ratio)
    main_map_generater(demand_ratio, df_demand, df_parking, cluster_list) 
    print('progress: ', counter)
    counter += 1

