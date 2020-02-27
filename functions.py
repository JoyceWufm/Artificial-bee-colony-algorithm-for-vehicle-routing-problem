"""
Functions

Environment: Python 3.7.3, IDE: Spyder, CPU: 3.00GHz
"""
import numpy
import random
import matplotlib.pyplot as plt

from main import Capacity, Duration, ServiceTime, Vehicles, Coordinates, Distance, Demand, Size, Limit, delta     

'''*******************Initial solution generation******************************
Aims:
    generate initial solutions of CVRP
Inputs:
    size (int) - the size of employed bee, half of the colony size
Returns:
    solutions (list) - a set of solutions with size equaling input Size, 
    [[solution1], [solution2], ..., [solutioni]]
****************************************************************************'''
def initial(size):
    solutions = []
    x = []
    for j in range(size):       
        
        currentVehicleLoc = list(numpy.arange(Vehicles)*0) # current position of vehicle, format: list [0,0,0,0,0,0]             
        routes_list =[[0] for i in range(Vehicles)] # initial route list, format: [[0],[0],[0],[0],[0],[0]]            
        x, y = numpy.hsplit(numpy.array(Coordinates), 2) # split location into X, Y                 
        Array_Dis = numpy.array(Distance) # change into array format for convenience                                   
        remainLoc = list(numpy.arange(1, len(Coordinates)))# generate customer id from 1 to 50

        'select a customer randomly'
        for i in range(len(remainLoc)):
            random_item_from_list = random.choice(remainLoc) # randomly pick a customer from the list
            remainLoc.remove(random_item_from_list) # remove it
            'obtain the distance between all vehicles and the selected customer'
            compareList = [] # list for comparison
            for i in range(Vehicles): # loop for filling the list
                compareList.append(Array_Dis[currentVehicleLoc[i]][random_item_from_list])    
            'assign the customer to the nearest vehicle'
            # update the vehicle position with the customer location
            currentVehicleLoc[compareList.index(min(compareList))] = random_item_from_list 
            # append it subsequently in corresponding route number
            routes_list[compareList.index(min(compareList))].append(random_item_from_list)  
        
        for i in range(1, len(routes_list)):
            routes_list[0].extend(routes_list[i])
        solutions.append(routes_list[0][1:len(routes_list[0])])

    return solutions

'''*************************Solution calculation*******************************
Aims:
    calculate the travel distance, load, service time and generate traces of 
    each vehicle in the solution
Inputs: 
    x (list) - a solution, [1, 2, 0, 3, 4, 0, 5, 6]
Returns:
    1.  load (list) - load of each vehicle, [1, 2, ..., 3]
    2.  traveldis (list) - the travel distance of each vehicle, [1, 2, ..., 3]
    3.  stime (list) - the total service time of each vehicle, [1, 2, ..., 3]
    4.  trace (list) - the total service time of each vehicle, 
        [[0, 1, 0], [0, 2, 0], ..., [0, i, 0]]
****************************************************************************'''
def calSol(x):
    'generate the trace of each vehicle'
    x1 = x[:]
    trace = [[0] for i in range(Vehicles)]
    t = 0
    for i in range(len(x1)):
        if x1[i] != 0:
            trace[t].extend([x1[i]])
        else:
            trace[t].extend([0])
            t += 1
    trace[Vehicles-1].extend([0])
       
    traveldis = []
    load = []
    stime=[]
    for car in range(Vehicles):        
        'calculate the travel distance of each vehicle'
        x=0
        for k in range(len(trace[car])-1):
            x = x + Distance[trace[car][k]][trace[car][k + 1]]
        traveldis.append(x)
        'calculate the travel distance of each vehicle'
        x=0
        for k in trace[car]:
            x = x + Demand[k]
        load.append(x)        
        'calculate the service time of each vehicle'
        stime.append((len(trace[car])-2)*ServiceTime)
    
    return load, traveldis, stime, trace

'''*************************Cost function calculation**************************
Aims:
    calculate the cost fo solutions, including travel cost, the violation of 
    capacity and duration constraints
Inputs:
    1.  sol (list) - a set of solutions, [[solution1], [solution2], ..., [solutioni]]
    2.  alpha (float) - coefficient of the violation of capacity constraints 
    3.  beta (float) - coefficient of the violation of duration constraints
Returns:
    1.  Allfit (list) - the fitness of each solution
    2.  CapVio (list) - the violation of capacity constraint of each solution
    3.  CapVio (list) - the violation of duration constraint of each solution
****************************************************************************'''
def fun(sol, alpha, beta):
    Allfit = []
    CapVio = []
    DurVio = []

    for j in range(len(sol)):
        'calculate the travel distance, service time and load of each solution'
        Load, traveldis, stime, trace = calSol(sol[j])

        fit=0
        vio1=0
        vio2=0
        fit1=float(sum(traveldis))
        for jl in range(Vehicles):
            'the violation of capacity constraint'
            if Load[jl]-Capacity>0:
                vio1=vio1+(Load[jl]-Capacity)
            'the violation of duration constraint'
            if traveldis[jl]+stime[jl]-Duration>0:
                vio2=vio2+((traveldis[jl]+stime[jl])-Duration)
        'cost function, objective value plus penalty value'
        fit = fit1 + alpha*vio1 + beta*vio2
        
        Allfit.append(fit)
        CapVio.append(vio1)
        DurVio.append(vio2)
        
    return Allfit, CapVio, DurVio

'''**********************Roulette wheel selection******************************
Aims:
    select a current solution based on its fitness
Inputs:
    1.  solfit (list) - list of the fitness of current solutions
    2.  solutions (list) - set of current solutions
Returns:
    1.  choosesol (list) -  set of selected solutions from current solutions
    2.  sourceid (list) - list of index of selected solutions in current 
        solutions set, eg. sourceid[0] = 1 means the 2nd current solution was 
        selected by the 1st onlooker
****************************************************************************'''
def choose(solfit, solutions):
    fit=solfit[:]
    sol=solutions[:]
    
    for j in range(len(fit)):
        fit[j] = 1/fit[j]
        
    s = sum(fit)
    for j in range(len(fit)):
        fit[j] = fit[j] / s

    Fit = numpy.zeros(len(fit) + 1)
    for j in range(len(fit)):
        Fit[j + 1] = Fit[j] + fit[j]

    choosesol = []
    sourceid=[]
    for j in range(Size):
        n = random.random()
        for k in range(len(Fit) - 1):
            if n >= Fit[k] and n <= Fit[k + 1]:
                choosesol.append(sol[k])
                sourceid.append(k)
                break
    return choosesol,sourceid

'''**********************Neighborhood operators********************************
Aims:
    select one of the neighbor operators and apply to a current solution by 
    pick positions to divided solution into pieces and perform operators
Inputs:
    x (list) - a current solution used as source in neighborhood operations
Returns:
    x (list) -  a neighbor solution generated by selected neighborhood operator
****************************************************************************'''
def change(x, operators):
    'pick one of the neighborhood operator from the predetermined set'
    changerandom = random.choice(operators)
    
    'Random swaps'   
    if changerandom == 1:      
        judge=0 # pick two positions
        while judge==0:
            index1=random.randint(0, len(x)-1)
            index2=random.randint(0, len(x)-1)
            if x[index1]!=x[index2] and x[index1] != 0 and x[index2] != 0:            
                judge=1        
        x1=x[:] # swap the customers
        x1[index1], x1[index2] = x1[index2], x1[index1]
        x=x1        
    'Random swaps of sebsequences'
    if changerandom == 2: 
        # pick four positions
        a = [i for i in range(len(x))]
        index=numpy.sort(random.sample(a,4))        
        # swaps the subsequences
        x1=[]
        x1.extend(x[0:index[0]])
        x1.extend(x[index[2]:index[3]])
        x1.extend(x[index[1]:index[2]])
        x1.extend(x[index[0]:index[1]])
        x1.extend(x[index[3]:len(x)])
        x=x1        
    'Random insertions'
    if changerandom == 3:
        # pick two positions
        judge=0
        while judge==0:
            index1=random.randint(0, len(x)-1)
            index2=random.randint(0, len(x)-1)
            if x[index1]!=x[index2] and x[index1] != 0 and x[index2] != 0:            
                judge=1
        # insert the customer in the first position to the second position
        x1=x[:]
        a=random.randint(0,len(x)-1)
        del x1[a]
        b=random.randint(0,len(x)-1)
        x1.insert(b,x[a])
        x=x1   
    'Random insertions of subquences'
    if changerandom == 4:
        # pick three positions
        a = [i for i in range(len(x))]
        index=numpy.sort(random.sample(a,3))
        # reorder the subsequences
        x1=[]
        x1.extend(x[0:index[0]])
        x1.extend(x[index[1]:index[2]])
        x1.extend(x[index[0]:index[1]])
        x1.extend(x[index[2]:len(x)])
        x=x1
    'Reversing a subsequence'
    if changerandom == 5:
        #pick two positions
        index=random.randint(0,len(x)-2)
        length=random.randint(2,len(x)-index)
        # reverse the middle part of solutions
        x1=[]
        x1.extend(x[0:index])
        x2=x[index:index+length]
        x2.reverse()
        x1.extend(x2)
        x1.extend(x[index+length:len(x)])
        x=x1
    'Random swaps of reversed subsequences'
    if changerandom == 6:
        # pick four positions
        index=[1,2,3,4]
        a = [i for i in range(len(x))]
        while index[1] - index[0] < 2 or index[2] - index[1] < 2 or index[3] - index[2] < 2:
            index = numpy.sort(random.sample(a,4))
        # reorder the subsequences and reverse the swaped one with 50% chance
        x1=[]
        x1.extend(x[0:index[0]])
        x2 = x[index[2]:index[3]]
        # probability of reversed, 0 no reversed and 1 reversed
        if random.choice([0, 1]) == 0:
            x1.extend(x2)
        else:
            x2.reverse()
            x1.extend(x2)    
        x1.extend(x[index[1]:index[2]])    
        x2 = x[index[0]:index[1]]
        if random.choice([0, 1]) == 0:
            x1.extend(x2)
        else:
            x2.reverse()
            x1.extend(x2)    
        x1.extend(x[index[3]:len(x)])
        x=x1
    'Random insertions of reversed subsequences'
    if changerandom == 7:
        # pick three positions
        a = [i for i in range(len(x))]
        index=numpy.sort(random.sample(a,3))
        # reorder the subsequences and reverse the swaped one with 50% chance
        x1=[]
        x1.extend(x[0:index[0]])
        x2 = x[index[1]:index[2]]
        if random.choice([0, 1]) == 0:
            x1.extend(x2)
        else:
            x2.reverse()
            x1.extend(x2)    
        x1.extend(x[index[0]:index[1]])
        x1.extend(x[index[2]:len(x)])
        x=x1
    
    return x

'''**********************Neighbor solutions selection**************************
Aims:
    select the neighbor solution with best fitness
Inputs:
    1.  i (int) - the ith current solution
    2.  nsolutionfit (list) - fitness of neighbor solutions
    3.  sourceID (list) - index of current solutions, which were used as inputs
        in neighborhood operator
Returns:
    1.  minGi (float) - the fitness of best neighbor solution of all neighbor
        solutions from ith current solution
    2.  locGi (int) - the index of the best neighbor solution in the neighbor 
        solution list
****************************************************************************''' 
def generateGi(i, nsolutionfit, sourceID):
    fitGi=[]
    GiIndex = []
    for j in range(len(sourceID)):
        if sourceID[j] == i:
            GiIndex.append(j)
            fitGi.append(nsolutionfit[j])
    minGi = min(fitGi)
    locGi = GiIndex[fitGi.index(min(fitGi))]      
    return minGi, locGi

'''***********************Solution renewal*************************************
Aims:
    1.  compare the fitness of current solution with the new solution from 
        neighborhood operator
    2.  keep the solution with lower cost between these two as the final 
        solution and update its iteration limit and violations
    3.  replace solution exceeding limit with a initial solution or a new 
        solution from neighborhood operators and calculate its violations
Inputs:
    1.  solutionfit (list) - the fitness of all current solutions 
    2.  nsolutionfit (list) - the fitness of all new solutions
    3.  solutions (list) - a set of current solutions
    4.  newsolutions (list) - a set of new solutions
    5.  lcount (list) - counter of the number of iterations that the fitness 
        of solution is not improving
    6.  capvio (list) - the violation of capacity constraint for each current solution
    7.  durvio (list) - the violation of duration constraint for each current solution
    8.  ncapvio (list) - the violation of capacity constraint for each new solution
    9.  ndurvio (list) - the violation of duration constraint for each new solution
    10. i (int) - index of current solution
    11. minGi (float) - the fitness of best neighbor solution of all neighbor
        solutions from ith current solution
    12. locGi (int) - the index of the best neighbor solution in the neighbor 
        solution list
    13. alpha (float) - coefficient regarding capacity constraint
    14. beta (float) - coefficient regarding duration constraint   
Returns:
    1.  solutions (list) - a set of renewed solutions
    2.  solutionfit (list) - the fitness of all renewed solutions
    3.  capvio (list) - the violation of capacity constraint for renewed solutions 
    4.  durvio (list) - the violation of duration constraint for renewed solutions 
****************************************************************************'''

'''----------------------------------------------------------------------------
Exploitation process: when employed bee found a better neighbor solution
----------------------------------------------------------------------------'''
def renewal1(solutionfit, nsolutionfit, solutions, newsolutions, lcount, capvio, durvio, ncapvio, ndurvio):
    for j in range(Size):
        if nsolutionfit[j] < solutionfit[j]:
            solutionfit[j] = nsolutionfit[j]
            solutions[j] = newsolutions[j]
            lcount[j] = 0
            capvio[j] = ncapvio[j]
            durvio[j] = ndurvio[j]
        else:
            lcount[j]=lcount[j]+1
    return solutions, solutionfit, lcount, capvio, durvio

'''----------------------------------------------------------------------------
Exploration process: when onlookers found a better neighbor solution
----------------------------------------------------------------------------'''
'original and semi-enhanced: replace the corresponding current solution with the new solution'
def renewal2(i, minGi, locGi, solutionfit, solutions, nsolutionfit, newsolutions, lcount, capvio, durvio, ncapvio, ndurvio):
    if minGi < solutionfit[i]:
        solutionfit[i] = minGi
        solutions[i] = newsolutions[locGi]
        capvio[i] = ncapvio[locGi]
        durvio[i] = ndurvio[locGi] 
        lcount[i]=0
    else:
        lcount[i] += 1

    return solutions, solutionfit, lcount, capvio, durvio    

'enhanced: replace the current solution with maximum limit with the new solution'
def renewal3(i, minGi, locGi, solutionfit, solutions, nsolutionfit, newsolutions, lcount, capvio, durvio, ncapvio, ndurvio):
    # find current solutions with fitness worser than that of neighbor solution
    if minGi < solutionfit[i]:
        limitGi=[]
        Ggi_id=[]
        for j in range(Size):
            if solutionfit[j]> minGi:
                limitGi.append(lcount[j])
                Ggi_id.append(j)
        # find the one with maximum number of limit  
        index=Ggi_id[limitGi.index(max(limitGi))]
        solutionfit[index]=nsolutionfit[locGi]
        solutions[index]=newsolutions[locGi]
        capvio[index] = ncapvio[locGi]
        durvio[index] = ndurvio[locGi]        
        lcount[index]=0
    else:
        lcount[i] += 1
    
    return solutions, solutionfit, lcount, capvio, durvio

'''----------------------------------------------------------------------------
when no improving neighbor solutions of the current solution have been 
identified during limit successive iterations
----------------------------------------------------------------------------'''
'original: replace the current solution with an initial solution'       
def renewal4(lcount, solutions, solutionfit, capvio, durvio, alpha, beta):
    for j in range(Size):
        if lcount[j] > Limit: # reach Limit
            lcount[j]=0
            temp = initial(1)
            solutions[j] = temp[0]
            solutionfitj, capvioj, durvioj = fun([solutions[j]], alpha, beta)
            solutionfit[j] = solutionfitj[0]
            capvio[j] = capvioj[0]
            durvio[j] = durvioj[0]
    return solutions, solutionfit, capvio, durvio, lcount

'semi-enhanced and enhanced: replace the current solution with its neighbor solution'
def renewal5(lcount, solutions, solutionfit, capvio, durvio, alpha, beta, operators):
    for j in range(Size):
        if lcount[j]>Limit: # reach Limit
            solutions[j]=change(solutions[j], operators)
            solutionfitj, capvioj, durvioj = fun([solutions[j]], alpha, beta)                       
            solutionfit[j] = solutionfitj[0]
            capvio[j] = capvioj[0]
            durvio[j] = durvioj[0]
            lcount[j]=0
            
    return solutions, solutionfit, capvio, durvio, lcount
            
'''***********************Iteration update************************************
Aims:
    1.  find the best solution in each iteration
    2.  update the coefficients alpha and beta
Inputs:
    1.  sol (list) - a set of solutions, [[solution1], [solution2], ..., [solutioni]]
    2.  solfit (list) - the fitness of all solutions
    3.  alpha (float) - original coefficients, updated according to the number of 
        solutions with violations of capacity constraint
    4.  beta (float) - original coefficients, updated according to the number of 
        solutions with violations of duration constraint
    5.  infeasibest (list) - the best calculated fitness in each iteration
    6.  infeasisol (list) - a solution with the best calculated fitness
    7.  feasibest (list) - the best objective value in each iteration
    8.  feasisol (list) - a solution with the best objective value
    9.  capvio (list) - the violation of capacity constraint for each solution
    10. durvio (list) - the violation of duration constraint for each solution
Returns:
    1.  solfit (list) - the updated fitness of all solutions, recalculated
        with updated coefficients
    2.  alpha (float) - updated coefficients, updated according to the number of 
        solutions with violations of capacity constraint
    3.  beta (float) - updated coefficients, updated according to the number of 
        solutions with violations of capacity constraint
    4.  infeasibest (list) - the best fitness till current iteration
    5.  infeasisol (list) - a solution with the best fitness till current iteration
    6.  feasibest (list) - the best objective value in each iteration
    7.  feasisol (list) - a solution with the best objective value
****************************************************************************'''
def update(sol, solfit, alpha, beta, infeasibest, infeasisol, feasibest, feasisol, capvio, durvio):    
    'update gather fit, find the best feasible one'
    totalcount1 = 0 # count the number of solutions with the violation of capacity constraints
    totalcount2 = 0 # count the number of solutions with the violation of duration constraints
    fit = [] # record the fitness of feasible solutions
    dis = [] # record the travel cost of solutions

    for j in range(Size):
        count1 = 0 #indicator of violation of capacity, 0 means no violation and 1 means violated
        count2 = 0 #indicator of violation of duration, 0 means no violation and 1 means violated
        
        if capvio[j] > 0: # the violation of capacity constraints exists
            count1 = 1
        if durvio[j] > 0: # the violation of duration constraints exists
            count2 = 1
        
        'record the fitness and objective value'
        if count1 == 0 and count2 == 0: # when no violation of two constraints
            fit.append(solfit[j]) # fitness
            dis.append(solfit[j]) # objective value
        else: # when with violation of two constraints, calculate objective values
            dis.append(solfit[j] - alpha*capvio[j] - beta*durvio[j])
        
        'count the number of solutions with violations of constraints'
        totalcount1 = totalcount1 + count1
        totalcount2 = totalcount2 + count2
    
    'adjust alpha and beta'    
    # the number of solutions with violation of the capacity constraints is greater than employed bee size
    if totalcount1 > int(Size/2): 
        alpha = alpha*(1+delta)
    else:
        alpha = alpha/(1+delta)
    if totalcount2 > int(Size/2):
        beta = beta*(1+delta)
    else:
        beta = beta/(1+delta)
    
    'find out the best infeasible solution and its fitness till current iteration'
    if min(solfit) < min(infeasibest): 
        infeasibest.append(min(solfit))
        infeasisol = sol[solfit.index(min(solfit))]
    else:
        infeasibest.append(min(infeasibest))
    
    'find out the best feasible solution and its fitness till current iteration'
    if fit and min(fit) < min(feasibest): 
        feasibest.append(min(fit))
        feasisol = sol[solfit.index(min(fit))]
    else: # if cannot find the feasible solution
        feasibest.append(min(feasibest))
    
    'update the fitness of solutions with new alpha and beta'
    for j in range(Size):
        solfit[j] = dis[j] + alpha*capvio[j] + beta*durvio[j]
    
    return solfit, alpha, beta, infeasibest, infeasisol, feasibest, feasisol

'''***********************Result visualization*********************************
Aims:
    1.  show the coverging process of fitness in each run
    2.  plot the best solution in each run and compare with the best known solution
Inputs:
    1.  feasibest (list) - the best objective value in each iteration
    2.  infeasibest (list) - the best fitness till current iteration
    3.  feasisol (list) - a solution with the best objective value
    4.  Iterations (int) - the total number of iterations in each run
    5.  fname (string) - the path of folder where the results will be saved
    6.  algorithm (int) - 1 original 2 semi-enhanced and 3 enhanced
    7.  itt (int) - the number of current iteration
    8.  Solroutes (list) - the vehicle trace of best known solution, 
        [[0, 1, 0], [0, 2, 0], ..., [0, i, 0]]
Outputs:
    1.  the figure shows the coverging process of fitness and objective value
    2.  the figure compares the best solution from algorithm and the best known one
    3.  print the information of best solution found in each run, including
        its overall objective value, trace, travel distance and service time
        of each vehicle
****************************************************************************'''
def visualize(feasibest, infeasibest, feasisol, Iterations, fname, algorithm, itt, Solroutes):
    'plot the coverging process of fitness and objective value'
    plt.figure(1)
    name = ['Objective value', 'Fitness']        
    plt.plot(feasibest)
    plt.plot(infeasibest)
    plt.axis([0, Iterations, infeasibest[len(infeasibest)-1]-infeasibest[0]/10, infeasibest[0]*1.1])
    plt.xlabel('Iterations', fontproperties='SimHei')
    plt.ylabel('Value', fontproperties='SimHei')                
    plt.legend(name,loc=1)
    plt.grid(True)
    plt.savefig(str(fname) + '\\fitness-algorithm' + str(algorithm) + '-run' + str(itt+1) +'.jpg')
    plt.show()
    
    'plot the best solution and compare it with the best known solution'
    name = [] 
    for i in range(Vehicles):
        name.append('Route' + str(i+1)) # generate the name for legend
    
    if feasisol: # when feasible solution exists        
        'calculate the attributes of the best feasible solution'
        load,traveldis,stime,trace=calSol(feasisol)        
        x, y = numpy.hsplit(numpy.array(Coordinates),2)
        routes = [[] for i in range(Vehicles)]  # routes for plotting purpose
        result = [[] for i in range(Vehicles)]
        
        'plot the solution in the figure'               
        plt.figure(2)
        plt.subplot(121) # solution from algorithm
        for j in range(Vehicles):
            result[j] = Coordinates[trace[j]]
            xxx, yyy = numpy.hsplit(result[j], 2)
            plt.plot(xxx, yyy, '-*', linewidth = 2) #, linestyle='-', marker='*'
        plt.xlabel('x', fontproperties='SimHei')
        plt.ylabel('y', fontproperties='SimHei')
        plt.title('The best ABC solution')
        plt.grid(True)
        plt.legend(name,loc=1)
        plt.axis('equal')
        
        plt.subplot(122) # the best known solution
        for i in range(Vehicles):
            routes[i] = Coordinates[Solroutes[i]]
            xx, yy = numpy.hsplit(routes[i], 2)
            plt.plot(xx, yy, '--')            
        plt.plot(x[0], y[0],  '.', color='green', markersize=6, label='Start-End')
        plt.scatter(x[1:len(x)-1],y[1:len(y)-1], color='black', label='Pick-up Location')                                
        plt.xlabel('x', fontproperties='SimHei')
        plt.ylabel('y', fontproperties='SimHei')
        plt.title('The best known solution')
        plt.grid(True)
        plt.legend(name,loc=1)
        plt.axis('equal')
        plt.savefig(str(fname) + '\\solutions-algorithm' + str(algorithm) + '-run' + str(itt+1) +'.jpg')
        plt.show()
        
        'print the results'
        print('the objective value of best solution：%s' % (feasibest[len(feasibest)-1]))
        for car in range(Vehicles): # trace of each vehicle
            print('the trace of vehicle %s：%s' %(car+1,trace[car]))            
        for car in range(Vehicles): # load of each vehicle
            print('the load of vehicle %s：%s' %(car+1,load[car]))           
        for car in range(Vehicles): # travel distance of each vehicle
            print('the distance of vehicle %s：%s' %(car+1,traveldis[car]))
        for car in range(Vehicles): # service time of each vehicle
            print('the service time of vehicle %s：%s' %(car+1,stime[car]))
    else:
        print('cannot find the feasible solution')
