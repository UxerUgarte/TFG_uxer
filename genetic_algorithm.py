
import copy
import random
import multiprocessing
import os
import time
import pickle as pc

def launch(command):
    os.system(command)


def create_individual():
   
    info_radius = random.uniform(0.65, 2)
    bandwith_cluster = random.uniform(0.1, 2)
    eta = random.uniform(0.3, 2.0)
    geta = random.uniform(0.3, 2.0)
    hysteresis_radius = random.uniform(0.5, 10.0)
    individual = [info_radius, bandwith_cluster, eta, geta, hysteresis_radius]
    return individual


def create_population(pop_size):

    population = list()
    for i in range(pop_size):
        population.append(create_individual())
    return population

def select(fit_values, num_individuals):
    ind_list = list()
    fit_copy = copy.deepcopy(fit_values)
    best_fits = sorted(fit_copy)[len(fit_copy)-num_individuals:]
    for i in range(len(fit_values)):
        if fit_values[i] in best_fits:
            ind_list.append(i)
    return ind_list

def select_worsts(fit_values, num_individuals):
    ind_list = list()
    fit_copy = copy.deepcopy(fit_values)
    worst_fits = sorted(fit_copy)[:num_individuals]
    for i in range(len(fit_values)):
        if fit_values[i] in worst_fits:
            ind_list.append(i)
    return ind_list

def cross(parent1, parent2):
    
    new_individual = []
    kont1 = 0
    kont2 = 0
    for i in range(len(parent1)):
        random_num = random.random()
        if random_num > 0.5:
            new_individual.append(parent1[i])
            kont1 += 1
        else:
            new_individual.append(parent2[i])
            kont2 += 1
    
    if kont1 == len(parent1):
        random_n = random.randint(0, 4)
        new_individual[random_n] = parent2[random_n]
    
    if kont2 == len(parent2):
        random_n = random.randint(0, 4)
        new_individual[random_n] = parent1[random_n]
    
    return new_individual

def mutation(individual, gen_kop, ranges):
    gen_ind = random.sample([0, 1, 2, 3, 4], gen_kop)
    for i in gen_ind:
        individual[i] = random.uniform(ranges[i][0], ranges[i][1])
    return individual

def evaluate(individual, path1, path2, max_time, max_cells):

    my_data = {}

    my_data['info_radius'] = individual[0]
    my_data['bandwith_cluster'] = individual[1]
    my_data['eta'] = individual[2]
    my_data['geta'] = individual[3]
    my_data['hysteresis_radius'] = individual[4]

    f = open(path1, 'wb')
    pc.dump(my_data, f)
    f.close()

    launch1 = 'roslaunch ros_multi_tb3 single_tb2_house_teb_third_floor.launch'
    launch2 = 'roslaunch rrt_exploration turtlebot_exploration.launch info_radius:='+str(individual[0])+' bandwith_cluster:=' + str(individual[1]) + ' eta:=' + str(individual[2]) + ' Geta:=' + str(individual[3]) + ' hysteresis_radius:=' + str(individual[4]) + ' max_changed_cells:=' + str(max_cells) + ' max_run_time:=' + str(max_time) + ' filename:=' + path1 + ' filename2:=' + path2

    p1 = multiprocessing.Process(target=launch, args = (launch1,))
    p2 = multiprocessing.Process(target=launch, args = (launch2,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    #Load the data
    f = open(path1, 'rb')
    my_data = pc.load(f)
    f.close()

    if 'changed_cells' in my_data and 'time' in my_data:
        fitness = my_data['changed_cells'] - my_data['time']
    else:
        os.system('rosnode kill -a')
        fitness = 0

    return fitness

def main(pop_size, mut_prob, cross_num, num_gen):
    #Nodes parameters
    path1 = "/home/uxer/Escritorio/probak/"
    path2 = "/home/uxer/Escritorio/probak/"
    max_time = 10
    max_cells = 190000


    evaluated = list(range(pop_size))
    num_parents = 6
    best_five = []
    num_proba = 3

    ranges = [(0.65, 2), (0.1, 2), (0.3, 2.0), (0.3, 2.0), (0.5, 10.0)]
    fitness_vals = list(range(pop_size))
    population = create_population(pop_size)
    num_generation = 0
    

    for i in range(len(population)):
        fit = 0
        for j in range(num_proba):
            path_aux2=path2 + "maps/map" + str(num_generation) + "_" + str(i) + "_" + str(j)
            path_aux1=path1 + "params/proba" + str(num_generation) + "_" + str(i) + "_" + str(j) + ".data"
            fit += evaluate(population[i], path_aux1, path_aux2, max_time, max_cells)
            
            time.sleep(1)
        fitness_vals[i] = fit/num_proba
        evaluated[i] = True
        if len(best_five)<=5:
            best_five.append((population[i], fitness_vals[i], num_generation, i))
        else:
            best_five = sorted(best_five)
            if fitness_vals[i] > best_five[0][1]:
                best_five[0] = (population[i], fitness_vals[i], num_generation, i)
        
    best_five = sorted(best_five)
    num_generation += 1
    for i in range(1, num_gen):

        ind_best = select(fitness_vals, num_parents)
        ind_worst = select_worsts(fitness_vals, cross_num)
        print(ind_best)
        print(ind_worst)
        print(len(population))
        print(len(fitness_vals))
        for j in range(cross_num):
            parents = random.sample(ind_best, 2)
            new_individual = cross(population[parents[0]], population[parents[1]])
            evaluated[ind_worst[j]] = False
            
            population[ind_worst[j]] = new_individual
        
        for j in range(len(population)):
            if j not in ind_worst:
                if random.random()<mut_prob:
                    evaluated[j] = False
                    new_individual = mutation(population[j], random.randint(1, 5))
                    population[j] = new_individual
        
        for j in range(len(population)):
            fit = 0
            if not evaluated[j]:
                for k in range(num_proba):
                    path_aux2=path2 + "maps/map" + str(i) + "_" + str(j) + "_" + str(k)
                    path_aux1=path1 + "params/proba" + str(i) + "_" + str(j) + "_" + str(k) + ".data"
                    fit += evaluate(population[j], path_aux1, path_aux2, max_time, max_cells)
                    time.sleep(1)
                
                fitness_vals[j] = fit/num_proba
                evaluated[j] = True
                if fitness_vals[j] > best_five[0][1]:
                    best_five[0] = (population[j], fitness_vals[j], num_generation, i)
                    best_five = sorted(best_five)
    

    path3 = "/home/uxer/Escritorio/probak/best_five.data"
    f = open(path3, 'wb')
    pc.dump(best_five, f)
    f.close()


        

if __name__ == "__main__":
    #Genetic_algorithm parameters
    pop_size = 10
    mut_prob = 0.05
    cross_num = 5
    num_gen = 2
    main(pop_size, mut_prob, cross_num, num_gen)