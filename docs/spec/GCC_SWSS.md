GCC Soil Water Security Simulator (SWSS)
Claude Code Master Specification
Version: 1.0
Author: GDM Environmental Consultants & Studies CO. L.L.C.
Lead Concept: Gary Morgan
Scientific Domain: Hydrogeology Vadose Zone Hydrology Irrigation Science Soil Physics Environmental Engineering
________________________________________
PROJECT VISION
The majority of soil amendment products are evaluated using water retention metrics.
Most claims focus on:
•	Increased water retention
•	Increased plant available water
•	Reduced irrigation frequency
•	Improved drought resistance
However:
Water retention is not equivalent to water savings.
The scientific challenge is that water security is governed by the movement of water through the entire soil-plant-atmosphere system rather than by storage alone.
The platform must therefore evaluate:
•	Storage
•	Fluxes
•	Water Balance
•	Water Security
simultaneously.
The platform’s primary scientific statement is:
Retention curves tell us how water is stored.
Water balances tell us whether water is saved.
Until the fluxes are measured, claims of water security remain hypotheses rather than demonstrated outcomes.
________________________________________
CORE OBJECTIVE
Build a scientifically defensible simulation platform capable of evaluating whether soil amendments produce measurable reductions in irrigation demand under GCC environmental conditions.
The platform must answer:
“What happens to the water?”
rather than:
“How much water can be retained?”
________________________________________
SCIENTIFIC PHILOSOPHY
The software shall never assume:
More Retention = More Water Savings
This assumption is prohibited.
The software must always test whether increased storage translates into:
•	Reduced irrigation demand
•	Reduced drainage
•	Reduced runoff
•	Reduced evapotranspiration losses
without reducing plant performance.
________________________________________
TARGET MARKET
Primary Users:
•	Municipalities
•	Landscape Consultants
•	Irrigation Engineers
•	Environmental Regulators
•	Golf Courses
•	Parks Departments
•	Developers
Secondary Users:
•	Agriculture
•	Universities
•	Amendment Manufacturers
•	Research Institutions
________________________________________
SCIENTIFIC FRAMEWORK
The application shall consist of six modelling layers.
________________________________________
LAYER 1
SOIL HYDRAULIC CHARACTERISATION
Purpose:
Convert basic soil information into hydraulic properties.
Inputs:
•	Sand %
•	Silt %
•	Clay %
•	Bulk Density
•	Organic Matter
•	Gravel Fraction
•	EC
•	SAR
•	Root Zone Depth
Outputs:
•	θr
•	θs
•	α
•	n
•	Ks
•	Available Water Capacity
Methods:
•	Rosetta-style Pedotransfer Functions
•	Published Literature
•	User Calibration
Confidence Rating:
Level 1–4
must accompany every prediction.
________________________________________
LAYER 2
GCC CLIMATE ENGINE
Inputs:
•	Location
•	Temperature
•	Relative Humidity
•	Wind Speed
•	Solar Radiation
Calculate:
Reference ET0
Methods:
FAO-56 Penman-Monteith
Outputs:
Daily ET0
Seasonal ET0
Annual ET0
________________________________________
LAYER 3
VEGETATION RESPONSE ENGINE
Supported Categories:
•	Turf
•	Trees
•	Shrubs
•	Native Species
•	Agricultural Crops
Inputs:
Crop Coefficients
Rooting Depth
Stress Thresholds
Outputs:
Potential ET
Actual ET
Root Water Uptake
Plant Water Stress
________________________________________
LAYER 4
AMENDMENT RESPONSE ENGINE
Purpose:
Represent physical changes caused by amendments.
Supported Amendments:
•	Biochar
•	Engineered Biochar
•	Compost
•	Biosolids
•	LNC
•	Soil Conditioners
•	Dust Suppression Biopolymers
•	Custom User Defined
Each amendment may alter:
θs
θr
α
n
Ks
Bulk Density
Available Water Capacity
Salinity Response
Never use fixed values.
Use:
Minimum
Most Likely
Maximum
ranges.
________________________________________
LAYER 5
WATER BALANCE ENGINE
Core Equation
ΔS = P + I - ET - D - R
Where:
ΔS = Change in Storage
P = Rainfall
I = Irrigation
ET = Evapotranspiration
D = Deep Drainage
R = Runoff
Daily simulation required.
Track:
Storage
Drainage
Runoff
ET
Irrigation
Root Uptake
for every day.
Storage is a state variable.
Fluxes are accounting variables.
________________________________________
LAYER 6
WATER SECURITY ENGINE
Purpose:
Translate hydraulic behaviour into management decisions.
Calculate:
Annual Water Use
Annual Irrigation Requirement
Drainage Losses
Water Productivity
Root Zone Reliability
Water Security Index
Outputs must always answer:
Where did the water go?
________________________________________
SCIENTIFIC RULES
Rule 1
A retention curve alone cannot demonstrate water savings.
Rule 2
Additional storage does not automatically reduce irrigation demand.
Rule 3
Water savings only exist if one or more of the following occur:
Reduced ET
Reduced Drainage
Reduced Runoff
Reduced Irrigation Requirement
without reducing plant performance.
Rule 4
All outputs must include uncertainty.
Rule 5
No deterministic claims are permitted.
________________________________________
GCC SPECIFIC CONSTRAINTS
Represent:
Extreme Evaporation
High Salinity
Sandy Soils
Low Organic Matter
High Irrigation Dependency
Urban Landscaping
Typical Conditions:
ET0 = 5–15 mm/day
Ks = High
Storage Capacity = Low
Drainage Potential = High
________________________________________
MONTE CARLO UNCERTAINTY ENGINE
Every simulation shall support:
Minimum Scenario
Most Likely Scenario
Maximum Scenario
Optional:
1000 Monte Carlo Simulations
Outputs:
P10
P50
P90
Confidence Bands
________________________________________
WATER SECURITY INDEX
Develop a composite score:
0–100
Components:
Storage Reliability
Irrigation Reduction
Drainage Reduction
Salinity Risk
Plant Performance
Example:
WSI = 0.25(Storage Reliability) + 0.25(Irrigation Reduction) + 0.20(Drainage Reduction) + 0.15(Salinity Resistance) + 0.15(Plant Performance)
Normalize to 100.
________________________________________
SCENARIO COMPARISON DASHBOARD
Allow side-by-side comparison:
Baseline
Biochar
Compost
LNC
Polymer
Biosolids
Custom
Outputs:
Water Stored
Plant Available Water
Annual Irrigation Demand
Drainage
ET
Water Savings
Payback Period
Water Security Index
________________________________________
ECONOMIC MODULE
Inputs:
Water Cost
Amendment Cost
Application Cost
Outputs:
Annual Savings
Payback Period
Cost per Cubic Meter Saved
Net Present Value
Return on Investment
________________________________________
SALINITY MODULE
Future Version
Represent:
Salt Accumulation
Leaching Requirement
Root Zone Salinity
Osmotic Stress
Impact on Water Use Efficiency
________________________________________
SCIENTIFIC REPORT GENERATOR
Generate PDF Reports.
Executive Summary
Scientific Assumptions
Water Balance Results
Water Security Results
Uncertainty Assessment
Recommendations
Limitations
________________________________________
USER INTERFACE PHILOSOPHY
The application must not resemble an irrigation timer.
The application must resemble:
A hydrogeological decision-support system.
The central dashboard shall always display:
Storage
Fluxes
Water Balance
Water Security
simultaneously.
________________________________________
ULTIMATE QUESTION
The application is not designed to answer:
“How much water can this soil hold?”
The application is designed to answer:
“How much irrigation water can actually be avoided under GCC conditions, and what happens to that water within the soil-plant-atmosphere system?”
If the software cannot answer where the water went, then the simulation is incomplete.
END OF SPECIFICATION
