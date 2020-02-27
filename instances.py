"""
Instances

Environment: Python 3.7.3, IDE: Spyder, CPU: 3.00GHz
"""

import numpy
import math

'''***********************Inputs verification**********************************
Aims:
    verify the entered inputs of experiment
Inputs:
    1.  sets - instances sets, 1 or 2
    2.  instances - instance number, 1-14 for set 1, 1-20 for set 2
    3.  algorithm - algorithm number, 1 origin 2 semi-enhanced and 3 enhanced
    4.  operators - combination of any operators out of 7 preselected operators    
Outputs:
    give notifications if any parameters is invalid
****************************************************************************'''
def verifyPara(sets, instances, algorithm, operators):
    if sets not in [1, 2]:
        print('Please re-enter the set number')
    elif sets == 1:
        if instances > 14 or instances < 1:
            print('Please re-enter the instance number')
    elif sets == 2:
        if instances > 20 or instances < 1:
            print('Please re-enter the instance number')
    
    for i in range(len(algorithm)): 
        if algorithm[i] not in [1, 2, 3]:
            print('Please re-enter the algorithm number')
        
    if min(operators) < 1 or max(operators) > 7:
        print('Please re-enter the operator number')  

'''*****************Instances data pre-processing******************************   
Aims:
    Read instance file and calculate distance between each pair of vertices
Inputs:
    1.  sets (int) - number of instance set, acceptable values: 1, 2. set 1 is 
        14 classical instances and set 2 is 20 large scale instances
    2.  instances (int) - instance number, for set 1, acceptable values: 1-14, 
        and for set 2, acceptable values: 1-20
Returns:
    1.  BestKnown (int) - the objective value of best known solution
    2.  Dimension (int) - the total number of customers and depot
    3.  Capacity (int) - the capacity constraint
    4.  Duration (int) - the duration constraint
    5.  ServiceTime (int) - the service time for each customer
    6.  Vehicles (int) - the total number of vehicles
    7.  Coordinates (list) - all the coordinates of customers, 
        [[x1, y1], [x2, y2], ..., [xi, yi]]
    8.  Distance (list) - distances between each pair of customers and depot,
        [[d1, d2, ..., di], [d1, d2, ..., di], ..., [d1, d2, ..., di]]
    9.  Demand (list) - demand of each customer, [1, 2, ..., i]
    10. File (string) - name of instance file
****************************************************************************'''
def dealData(sets, instances):

    # pointers for the beginnings of each section of content
    coordinate_begin = -1 # customers coordinate section
    demand_begin = -1 # customers demand section
    origin_begin = -1 # depot coordinate section

    # for those instances without capacity and duration constraints, set its constraints as 9999
    Duration = 9999
    Capacity = 9999
    # for those instances without considering service time, set its service time as 0
    ServiceTime = 0 

    'find out the file name of studied instance' 
    if sets == 1:        
        instances = 'CMT' + str(instances) + '.vrp'
    elif sets == 2:
        instances = 'Golden_' + str(instances) + '.vrp'
        
    'read the information of instance'
    with open('Instances\\'+ instances) as lines:
        for line in lines:
            # BestKnown - the best known solution
            if ('COMMENT' in line):
                a = line.replace("\n", "")
                b = a.split(': ')
                BestKnown = float(b[1])
            # Dimension - sum of customers and depot
            if ('DIMENSION' in line):
                a = line.replace("\n", "")
                b = a.split(': ')
                Dimension = int(b[1])
            # Capacity - the maximum demands that a vehicle can take
            if ('CAPACITY' in line):
                a = line.replace("\n", "")
                b = a.split(': ')
                Capacity = int(b[1])
            # Duration - the maximum sum of travel distance and service time that a vehicle can take
            if ('DISTANCE' in line):
                a = line.replace("\n", "")
                b = a.split(': ')
                Duration = int(float(b[1]))
            # ServiceTime - service time of each customer
            if ('SERVICE_TIME' in line):
                a = line.replace("\n", "")
                b = a.split(': ')
                ServiceTime = int(float(b[1]))
            # Vehicles - the number of vehicles serving all customers
            if ('VEHICLES' in line):
                a = line.replace("\n", "")
                b = a.split(': ')
                Vehicles = int(b[1])
            # x,y coordinates of vertices
            if ('NODE_COORD_SECTION' in line):
                Coordinates = numpy.zeros((Dimension, 2))
                coordinate_begin = 1
                continue
            if coordinate_begin > 0 and coordinate_begin < Dimension:
                a = line.replace("\n", "")
                b = a.split(' ')
                Coordinates[coordinate_begin][0] = float(b[1])
                Coordinates[coordinate_begin][1] = float(b[2])
                coordinate_begin = coordinate_begin + 1
            # x,y coordinates of depot
            if ('DEPOT_SECTION' in line):
                origin_begin = 1
                demand_begin = -1
                continue
            if origin_begin == 1:
                a = line.replace("\n", "")
                b = a.split(' ')
                Coordinates[0][0] = float(b[0])
                Coordinates[0][1] = float(b[1])
                origin_begin = origin_begin + 1
            # Demand - the demand of customers
            if ('DEMAND_SECTION' in line):
                coordinate_begin = -1
                demand_begin = 1
                Demand = [0]
                continue
            if demand_begin > 0 and demand_begin < Dimension:
                a = line.replace("\n", "")
                b = a.split(' ')
                Demand.append(float(b[1]))
                demand_begin = demand_begin + 1
    
    'Calculate distance between each pair of vertices, including customers and depot'
    Distance=[]
    for i in range(Dimension):
        x=[]
        for j in range(Dimension):
            p3=Coordinates[i]-Coordinates[j]
            x.append(math.hypot(p3[0],p3[1]))
        Distance.append(x)

    return BestKnown, Dimension, Capacity, Duration, ServiceTime, Vehicles, Coordinates, Distance, Demand, instances

'''**************************Solution load*************************************
Aims:
    load the best known solution for result comparation
Input:
    1.  sets (int) - number of instance set, acceptable values: 1, 2. set 1 is 
        14 classical instances and set 2 is 20 large scale instances
    2.  instances (int) - instance number, for set 1, acceptable values: 1-14, 
        and for set 2, acceptable values: 1-20
Returns:
    solroutes (list) - the vehicle trace of best known solution, 
    [[0, 1, 0], [0, 2, 0], ..., [0, i, 0]]
****************************************************************************'''
def loadSolution(sets, instances):

    if sets == 1:        
        solution = 'CMT' + str(instances) + '.sol'
    elif sets == 2:
        solution = 'Golden_' + str(instances) + '.sol'

    linenumber = 0
    Vehicles = 0
    with open('Instances\\' + solution) as lines:
        for line in lines:
            linenumber += 1
            if linenumber == 2:
                a = line.replace("\n", "").replace("  ", " ")
                Vehicles = int(a)
                solroutes = [[0] for i in range(Vehicles)]
            if linenumber > 4:
                a = line.replace("\n", "").replace("  ", " ")
                b = a.split(' ')
                solroutes[linenumber - 5] = list(map(int, b[7:len(b)]))
                
    return solroutes

'''**************************Results savers************************************
Aims:
    save all the results for visualization
Input:
    1.  name (string) - folder path for saving results
    2.  itt (int) - the number of current run
    3.  algorithm (int) - current algorithm
    5.  infeasibest (list) - the best calculated fitness in each iteration
    6.  infeasisol (list) - a solution with the best calculated fitness
    7.  feasibest (list) - the best objective value in each iteration
    8.  feasisol (list) - a solution with the best objective value
Outputs:
    files saving the coverging process of objective value and the best solution
****************************************************************************'''
def saveResult(name, itt, algorithm, infeasibest, infeasisol, feasibest, feasisol):
    numpy.save(str(name) + '\\feasible_fitness-algorithm' + str(algorithm) + '-run' + str(itt+1) + '.npy', numpy.array(feasibest))
    numpy.save(str(name) + '\\feasible_solution-algorithm' + str(algorithm) + '-run' + str(itt+1) + '.npy', numpy.array(feasisol))

'''***********************Running time calculation*****************************
Aims:
    achieve the average running time of each run
Input:
    1.  timers (list) - a set of system time records when each run started
    2.  algorithm (int) - current algorithm
    3.  name (string) - folder path for saving results
    4.  iterations (int) - total number of iterations
    5.  size (int) - solution size, equals the size of employed bees
Outputs:
    1.  print the average time of each run
    2.  save the time records when each run ends
****************************************************************************'''
def Timer(timers, algorithm, name, iterations, size):
    if len(timers) == 1:
        print('cannot calculate with only one run')
    else:
        count = len(timers) - 1
        print('average running time in minutes for algorithm %s: %f' % (algorithm, (timers[len(timers)-1]-timers[0])/count/60))    
    numpy.savetxt(str(name) + '\\timers-algorithm' + str(algorithm) + '-size' + str(size) + '-iterations' + str(iterations) + '.csv', numpy.array(timers))
