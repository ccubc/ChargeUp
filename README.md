# ChargeUp 
 
 [See Presentation Slides](https://drive.google.com/open?id=1ntPTFZRM_EoCcSugZF-p2skCiyNdUgxcnH89xkh76u4)

Many potential electric vehicle (EV) buyers are frustrated by the fact that the current charging station network is still underdeveloped. The terminology "range anxiety" describes the situation where EV owners are worried about exhausting their EV battery in a trip. Currently, most EV owners have access to home charging, whereas home charging is almost impossible for those living in an apartment or a condo. Therefore, to push EV sales to the next stage, it is necessary to grow the charging network. The federal government is investing \$ 182.5 million in an initiative that includes a coast-to-coast network of chargers. A natural question to ask is: **where to optimally locate them so that total social cost is minimized**? 

**ChargeUp** is an optimization and visualization tool designed for city planners to choose the optimal location for future electric vehicle (EV) charging stations in the City of Toronto. It allows the user to explore the optimal deployment of charging stations under different scenarios when demand for EV charging varies. The product is deployed as a [web app](http://chargeuptoronto.ca). 

## Packages
Please run `pip install -r requirements.txt` on your virtual environment to install the required python packages to run. This project solves the **optimization** problem using Pulp, **visualizes** the final result using Folium, and deploys the **web app** using Flask. 

## Data Source
* Demand for charging: number of day trips to districts in Toronto (from Transportation Tomorrow Survey) multiplied by parameters that determine EV charging demand in general (from user input)
* Supply for charging: currently existing charging stations + potential future charging stations ( currently existing parking lots) (from Google Place API)

## Optimization Model  
* The decision: choosing a subset of parking lots to install chargers (level II EV charger). 
* Objective: Minimizing (the cost of installing chargers + electric car drivers' travel cost from the charging station to their travel destination)
* Constraints:  <br>
(1) Charging demand at each destination places should be satisfied.<br>
(2) Charging capacity does not exceed each station's limit.

### Model Formulation
![formulation](https://github.com/ccubc/Insight-Project/blob/master/screenshots/formulation.png)

* For assumptions and parameter settings in the model, please refer to my [Presentation slides](https://drive.google.com/open?id=1ntPTFZRM_EoCcSugZF-p2skCiyNdUgxcnH89xkh76u4). 

### Alternative Model
I have also implemented an alternative optimization model as below.
* The decision: choosing a subset of parking lots to install chargers (level II EV charger).
* Objective: Minimizing (electric car drivers' travel cost from the charging station to their travel destination + penalty for unsatisfied charging demand)
* Constraints: <br>
(1) Charging capacity does not exceed each station's limit. <br>
(2) Total cost of installing chargers does not exceed a certain budget amount. <br>
The optimization results are very sensitive to both the budget and the penalty, hence not comparable to the previous model.

## The Web App
This section briefly explains the [web app](http://chargeuptoronto.ca). User will land on the home page and be asked to input two parameters: Electric Vehicle Penetration Ratio (among all cars, what percentage is electric) and Home Charging Ratio (among all EV drivers, what percentage has access to home charging), which are the two most important parameters in determining demand for charging. 
#### Landing Page and User Input
![user-input](https://github.com/ccubc/Insight-Project/blob/master/screenshots/webapp_1.png)
After the user clicks the button "Find Optimal Locations", the web app will show a table of parking lots that are optimal locations to install chargers. 
#### Output table
![output-table](https://github.com/ccubc/Insight-Project/blob/master/screenshots/webapp_2.png)
The user could also explore the results on a map.
#### Explore results on a map
![explore-map1](https://github.com/ccubc/Insight-Project/blob/master/screenshots/webapp_3.png)
![explore-map2](https://github.com/ccubc/Insight-Project/blob/master/screenshots/webapp_4.png)



