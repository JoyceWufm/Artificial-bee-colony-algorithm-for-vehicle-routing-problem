# Artificial-bee-colony-algorithm-for-vehicle-routing-problem
Inspired by Szeto, W. Y., Wu, Y., &amp; Ho, S. C. (2011). An artificial bee colony algorithm for the capacitated vehicle routing problem. European Journal of Operational Research, 215(1), 126-135.

***This is the codes applying ABC algorithm in CVRP***

Environment: Python 3.7.3, IDE: Spyder  

Needed packages: os, re, math, time, numpy, pandas, random, matplotlib  

## Modules:
main.py - the framework of whole ABC algorithm  
functions.py - list of functions used in ABC algorithm  
instances.py - read CVRP instances and save results  
results.py - visualize the results of ABC algorithm  

## Notebooks:
results_vrpnc6.ipynb - results of instance vrpnc6 from ABC algorithm  
results_vrpnc14.ipynb - results of instance vrpnc14 from ABC algorithm  

## Folders:
Instances - where the all instances and their solutions stored  
Results - where the results from ABC algorithm will save  

## HOW TO USE IT
1. check the results of selected instances  
Run the results_**.ipynb or results.py  

2. run the ABC algorithm  
Run the main.py and set the inputs properly  

Note: if run on macOS, please replace '\\' in path with '/'  
