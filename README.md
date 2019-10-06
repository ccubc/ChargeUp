# ChargeUp 

Many potential electric vehicle (EV) buyers are frustrated by the fact that the current charging station network is still underdeveloped. The terminology "range anxiety" describes the situation where EV owners are worried about exhausting their EV battery in a trip. Currently, most EV owners have access to home charging, whereas home charging is almost impossible for those living in an apartment or a condo. Therefore, to push EV sales to the next stage, it is necessary to grow the charging network. The federal government is investing \$ 182.5 million in an initiative that includes a coast-to-coast network of chargers. A natural question to ask is: **where to optimally locate them so that total social cost is minimized**? 

**ChargeUp** is an optimization and visualization tool designed for city planners to choose the optimal location for future electric vehicle (EV) charging stations in the City of Toronto. It allows the user to explore the optimal deployment of charging stations under different scenarios when demand for EV charging varies. The product is deployed as a [web app](http://chargeuptoronto.ca). Presentation slides about ChargeUp can be found [here](https://drive.google.com/open?id=1ntPTFZRM_EoCcSugZF-p2skCiyNdUgxcnH89xkh76u4).

## Packages
Please run `<pip install -r requirements.txt>` on your virtual environment to install the required python packages to run. This project solves the **optimization** problem using Pulp, **visualizes** the final result using Folium, and deploys the **web app** using Flask. 

## Optimization Model
* The decision: choosing a subset of parking lots to install chargers.
* Objective: Minimizing (the cost of installing chargers + electric car drivers' travel cost from the charging station to their travel destination)
* Constraints:  <br>
(1) Charging demand at each destination places should be satisfied.<br>
(2) Charging capacity does not surpass each station's limit
* Formulation: 


