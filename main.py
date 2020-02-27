"""
Main

Environment: Python 3.7.3, IDE: Spyder, CPU: 3.00GHz
"""

import os
import time
import numpy as np

from instances import verifyPara, dealData, loadSolution, saveResult, Timer
import functions as f

'''******************************MAIN******************************************
Aims:
    apply artificial bee colony algorithm for capacited vehicle routing problem
Inputs:
    1.  sets (int) - number of instance set, acceptable values: 1, 2. set 1 is 
        14 classical instances and set 2 is 20 large scale instances
    2.  instances (int) - instance number, for set 1, acceptable values: 1-14, 
        and for set 2, acceptable values: 1-20
    3.  algorithms (list) - a combination of algorithm, acceptable values: 
        1, 2, 3. 1 original 2 semi-enhanced and 3 enhanced, format [1, 2, 3]
    4.  operators (list) - a combination of neighborhood operators, acceptable
        values: 1-7, format [1, 2, 3], default [1, 5, 6]
    5.  Size (int) - size of employed bee, half of colony size, default 25
    6.  Runs (int) - experiment runs, default 20
    7.  Limit (int) - the consecutive limit iterations before a food source 
        is abandoned, default 50n, n is customers size in instance
    8.  initalpha (float) - coefficient alpha of cost function, default 0.1
    9.  initbeta (float) - coefficient beta of cost function, default 0.1
    10. delta (float) - coefficient delta of cost function, default 0.001 
Outputs:
    1.  results files of objective value and solution of each run in the
        experiment
    2.  figures of converging process of objective value and solution
    3.  time records of each run in the experiment, for calculate CPU run time
Key words in comments:
    1.  current solutions - solutions where the employed bee is
    2.  new solutions - solutions generated by neighborhood operator based on
        current solutions
    3.  objective value - travel distance of solution
    4.  fitness - objective value plus penalty value of capacity and duration constraints
    5.  cost function - the combination of objective function and penalty 
        function for calculating the fitness
****************************************************************************'''

'''----------------------------------------------------------------------------
Please set the inputs of the experiment
----------------------------------------------------------------------------'''
sets = 2 # choose instances set, set 1 is 14 classical instances and set 2 is 20 large scale instances
instances = 5 # instance number, for classical set 1-14, and for large scale set 1-20
algorithms = [1, 2, 3] # a combination of algorithm, 1 original 2 semi-enhanced and 3 enhanced, format: [1, 2, 3]
operators = [1, 5, 6] # a combination of neighborhood operators, any from 7 neighborhood operators, format: [1, 2, 3]

'verify the inputs is valid'
verifyPara(sets, instances, algorithms, operators)

'Load contents of the studied instance and its best known solution'
BestKnown, Dimension, Capacity, Duration, ServiceTime, Vehicles, Coordinates, Distance, Demand, File = dealData(sets, instances)
Solroutes = loadSolution(sets, instances)
# BestKnown (int) - the objective value of best known solution
# Dimension (int) - the total number of customers and depot
# Capacity (int) - the capacity constraint
# Duration (int) - the duration constraint
# ServiceTime (int) - the service time for each customer
# Vehicles (int) - the total number of vehicles
# Coordinates (list) - all the coordinates of customers, [[x1, y1], [x2, y2], ..., [xi, yi]]
# Distance (list) - distances between each pair of customers and depot,
#                  [[d1, d2, ..., di], [d1, d2, ..., di], ..., [d1, d2, ..., di]]
# Demand (list) - demand of each customer, [1, 2, ..., i]
# File (string) - name of instance file
# Solroutes (list) - the vehicle trace of best known solution, [[0, 1, 0], [0, 2, 0], ..., [0, i, 0]]

Size = 25 # the number of food sources
Runs = 20 # experiment runs
Iterations = 2000*(Dimension-1) # converge iterations

Limit = 50*(Dimension-1) # the consecutive limit iterations before a food source is abandoned
initalpha = 0.1 # coefficient of cost function, initial alpha
initbeta = 0.1 # coefficient of cost function, initial beta
delta = 0.001 # coefficient of cost function, constant delta

def main():
    
    '''------------------------------------------------------------------------
    Initial the experiment
    ------------------------------------------------------------------------'''    
    'create a folder for expriment results'
    fname = 'Results\\Instance_' + str(sets) + '_' + str(instances) + '\\' + time.strftime("%Y%m%d %H%M%S", time.localtime())     
    os.makedirs(fname) 
    
    algoName = {1: "original", 2: "semi-enhanced", 3: "enhanced"} # algorithm name and number as index
    
    'print information about the instance and experiment'
    print('Instance: %s\nBest known solution：%s\nNumber of customers：%s\nCapacity：%s\nDuration：%s\nService time：%s\nNumber of vehicles：%s' 
          % (File, BestKnown, Dimension-1, Capacity, Duration, ServiceTime, Vehicles))
    print('solutionsize = %s\nlimit = %s\niterations = %s\nruns = %s\ninitial alpha = %s\ninitial beta = %s\ndelta = %s' 
          % (Size, Limit, Iterations, Runs, initalpha, initbeta, delta))
    
    '''------------------------------------------------------------------------
    Apply different algorithms in the experiment
    ------------------------------------------------------------------------'''
    for ii in range(len(algorithms)):
        timers = [] # record the start time of every run
        algorithm = algorithms[ii]
        algoname = algoName.get(algorithm, None)
        print('****************************************\nalgorithm:', algoname)
        
        '''--------------------------------------------------------------------
        Start each run
        --------------------------------------------------------------------'''        
        for itt in range(Runs):            
            timers.append(time.process_time())
            print('Run', itt+1)
            alpha = 0.1 # update the initial value of alpha at each run
            beta = 0.1 # update the initial value of beta at each run
           
            feasibest = [] # the best objective value during each iteration
            feasisol = [] # feasible solution with the best objective value during all iterations
            infeasibest = [] # the best fitness of all solutions
            infeasisol = [] # solution with the best fitness 
            
            solutions = [] # set of solutions
            solutionfit = [] # fitness of solutions
            newsolutions = [] # new solutions generated by neighborhood operator
            nsolutionfit = [] # fitness of new solutions
            
            capvio = [] # the violation of capacity constraint of current solutions
            durvio = [] # the violation of duration constraint of current solutions
            ncapvio = [] # the violation of capacity constraint of new solutions
            ndurvio = [] # the violation of duration constraint of new solutions
            
            lcount = list(np.arange(Size)*0) # count when neighbor solution failed to replace the current solution 
        
            'Generate a set of initial solutions and calculate its objective value'
            solutions = f.initial(Size) # generate a set of initial solutions
            solutionfit, capvio, durvio = f.fun(solutions, alpha, beta) # calculate its fitness
            feasibest.append(min(solutionfit)) # store the minimum objective value of current iteration
            infeasibest.append(min(solutionfit)) # store the minimum fitness of current iteration

            '''----------------------------------------------------------------
            Start each iteration
            ----------------------------------------------------------------'''         
            for it in range(Iterations):

                '''------------------------------------------------------------
                Exploitation process
                ------------------------------------------------------------'''
                'apply neighborhood operator of current solutions and calculate its fitness'
                newsolutions = solutions[:]
                for j in range(Size):
                    newsolutions[j] = f.change(solutions[j], operators) # neighborhood operators
                nsolutionfit, ncapvio, ndurvio = f.fun(newsolutions, alpha, beta) # calculate fitness

                'replace with neighbor solutions or keep the current solutions based on their fitness'
                solutions, solutionfit, lcount, capvio, durvio = f.renewal1(solutionfit, nsolutionfit, solutions, newsolutions, 
                                                                            lcount, capvio, durvio, ncapvio, ndurvio)

                '''------------------------------------------------------------
                Exploration process
                ------------------------------------------------------------'''
                'select a current solution using the fitness-based roulette wheel selection method'
                newsolutions, sourceID = f.choose(solutionfit, solutions)
                
                'apply neighborhood operator of current solutions and calculate its fitness'
                for j in range(Size):
                    newsolutions[j] = f.change(newsolutions[j], operators)
                nsolutionfit, ncapvio, ndurvio = f.fun(newsolutions, alpha, beta)

                for j in range(Size):
                    if j in sourceID:
                        'generate neighbor solution set of respective current solutions'
                        minGi, locGi = f.generateGi(j, nsolutionfit, sourceID)
                        
                        'replace with neighbor solutions or keep the current solutions based on their fitness'
                        if algorithm == 1 or algorithm == 2: # for original ABC algorithm and semi-enhanced ABC algorithm
                            solutions, solutionfit, lcount, capvio, durvio = f.renewal2(j, minGi, locGi, solutionfit, solutions, nsolutionfit, 
                                                                                         newsolutions, lcount, capvio, durvio, ncapvio, ndurvio)
                        elif algorithm == 3: # for enhanced ABC algorithm
                            solutions, solutionfit, lcount, capvio, durvio = f.renewal3(j, minGi, locGi, solutionfit, solutions, nsolutionfit, 
                                                                                        newsolutions, lcount, capvio, durvio, ncapvio, ndurvio)

                '''------------------------------------------------------------
                Replace the solutions when reaching limit and update the coefficients
                ------------------------------------------------------------'''              
                'replace those solutions without improvement for consecutive limit iterations'
                if algorithm == 1: # for Original ABC algorithm
                    solutions, solutionfit, capvio, durvio, lcount = f.renewal4(lcount, solutions, solutionfit, capvio, 
                                                                                durvio, alpha, beta) 
                elif algorithm == 2 or algorithm == 3: # for semi-enhanced ABC algorithm and enhanced ABC algorithm               
                    solutions, solutionfit, capvio, durvio, lcount = f.renewal5(lcount, solutions, solutionfit, capvio, 
                                                                                durvio, alpha, beta, operators) 
                
                'update alpha and beta, and find out the best solution of current iteration'
                solutionfit, alpha, beta, infeasibest, infeasisol, feasibest, feasisol = f.update(solutions, solutionfit, alpha, beta, infeasibest, 
                                                                                                  infeasisol, feasibest, feasisol, capvio, durvio)

                'print current iteration results'
                if it < Iterations - 1:                
                    if it % (Iterations/10) == 0:
                        print('the best solution of %s/%s iteration：%s' % (it+1, Iterations, infeasibest[len(infeasibest)-1]))
                        print('the best feasible solution of %s/%s iteration：%s' % (it+1, Iterations, feasibest[len(feasibest)-1]))
                elif it == Iterations - 1: # final iterations
                    print('the best solution of %s/%s iteration：%s' % (it+1, Iterations, infeasibest[len(infeasibest)-1]))
                    print('the best feasible solution of %s/%s iteration：%s' % (it+1, Iterations, feasibest[len(feasibest)-1]))

            '''----------------------------------------------------------------
            Visualize the final results and save it
            ----------------------------------------------------------------'''
            'plot coverging process of objective value and trace of vehicles'
            f.visualize(feasibest, infeasibest, feasisol, Iterations, fname, algorithm, itt, Solroutes)
            'save results of objective values and solutions'            
            saveResult(fname, itt, algorithm, infeasibest, infeasisol, feasibest, feasisol)        
            'save the time records of each run'
            Timer(timers, algorithm, fname, Iterations, Size)
   
if __name__ == '__main__':
    main()