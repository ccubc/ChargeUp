# ChargeUp: Choosing the Optimal Location for Future Electric Vehicle Charging Stations in the City of Toronto


Many potential electric vehicle (EV) buyers are frustrated by the fact that the current charging station network is still underdeveloped. The terminology "range anxiety" describes the situation where EV owners are worried about exhausting their EV battery in a trip. Currently, most EV owners have access to home charging, whereas home charging is almost impossible for those living in an apartment or a condo. Therefore, to push EV sales to the next stage, it is necessary to grow the charging network. The federal government is investing \$ 182.5 million in an initiative that includes a coast-to-coast network of chargers. A natural question to ask is: **where to optimally locate them so that total social cost is minimized**? 

This project solves this **optimization** problem using Pulp, **visualizes** the final result using Folium, and deploys the product -- a **web app** using Flask. 

## Optimization Model
* The decision: choose a subset of parking lots to install chargers
* Objective: Minimize the cost of installing chargers + electric car drivers' travel cost from the charging station to their travel destination
* Constraints:  <br>
(1) Charging demand at each destination places should be satisfied.<br>
(2) Charging capacity does not surpass each station's limit
* Formulation: 

