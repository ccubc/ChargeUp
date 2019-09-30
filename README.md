# Choosing the Optimal Location for Future Electric Vehicle Charging Stations in the City of Toronto

This project aims to explore the question "Where should we allocate the next electric vehicle charger charging stations". 

Many potential electric vehicle (EV) buyers are frustrated by the fact that the current charging station network is still underdeveloped. The terminology "range anxiety" describes the situation where EV owners are worried about exhausting their EV battery in a trip. Currently, most EV owners have access to home charging, whereas home charging is almost impossible for those living in an apartment or a condo. Therefore, to push EV sales to the next stage, it is necessary to grow the charging network. The federal government is investing \$ 182.5 million in an initiative that includes a coast-to-coast network of chargers. A natural question to ask is: where to optimally locate them so that total social cost is minimized? 

## Optimization Model
* The decision: choose a subset of parking lots to install chargers
* Objective: Minimize the cost of installing chargers + electric car drivers' travel cost to and from the charging station to their travel destination
* Constraints:  <br>
(1) Charging demand at each destination places should be satisfied.
(2) Charging capacity does not surpass each station's limit
* Formulation: 
$$\min \sum^m_{j=1}f_j y_j + \sum^n_i \sum^m_j c_{ij}x_{ij}$$
$$ s.t.\ \sum^m_{j=1}x_{ij} = d_i,\ \ \ \ i = 1,...,n$$
$$ \ \ \ \ \ \sum^n_{i=1}x_{ij} \leqslant M_j y_j, \ \ \ \ j = 1,...,m$$
$$ \ \ \ \ \ x_{ij}\leqslant d_i y_j, \ \ \ \ i = 1,...,n$$
$$ \ \ \ x_{ij}\geqslant 0 $$
$$ \ \ \ y_j \in \{0,\ 1\}$$
where $f_j$ = fixed cost of charging station at location $j$,  
$y_j \in \{0,1\}$ indicates whether to build a charging station at location $j$,  
$c_{ij}$ is the travel cost for person at desired destination location $i$ to charging station at location $j$,  
$x_{ij}$ is the demand of charging by person at location $i$ that will be covered by charging station at location $j$,  
$d_i$ is demand of charging at destination location $i$.
