import random

import numpy as np

from systems.systems_util import get_futures_list, get_settings

np.random.seed(42)
random.seed(42)


def myTradingSystem(CLOSE, settings):
    """
    Trading system that uses the genetic algorithm to predict future changes in price.
    """
    nMarkets = len(settings['markets'])
    lookback = settings['lookback']
    n_pop = settings['population_size']
    tournament_size = settings['tournament_size']
    crossover_rate = settings['crossover_rate']
    mutation_rate = settings['mutation_rate']
    n_iter = settings['n_iter']
    init_budget = settings['budget']

    def fitness(gen):
        # calculate profit
        profit = [CLOSE[-1, market] - CLOSE[-2, market] for market in range(nMarkets)]

        # fitness function is total portfolio value after taking the value
        diff = np.nansum([market * pos for market, pos in zip(profit, gen)])

        return diff

    def selection(pop, scores, tournament_size=tournament_size):
        rand_selection = np.random.randint(len(pop))
        for s in np.random.randint(0, len(pop), tournament_size - 1):
            if scores[s] > scores[rand_selection]:
                rand_selection = s
        return pop[rand_selection]

    def crossover(p1, p2, r_cross=crossover_rate):
        # children are copies of parents by default
        c1, c2 = p1.copy(), p2.copy()
        # check for recombination
        if np.random.rand() < r_cross:
            # select crossover point that is not on the end of the string
            pt = np.random.randint(1, len(p1) - 2)
            # perform crossover
            c1 = p1[:pt] + p2[pt:]
            c2 = p2[:pt] + p1[pt:]
        return [c1, c2]

    def mutation(bitstring, r_mut=mutation_rate):
        for i in range(len(bitstring)):
            # check for a mutation
            if np.random.rand() < r_mut:
                # change the bit
                poss_values = [-1, 0, 1]
                poss_values.remove(bitstring[i])
                bitstring[i] = random.choice(poss_values)

    pop = [np.random.randint(-1, 2, size=nMarkets).tolist() for _ in range(n_pop)]
    best, best_eval = pop[0], fitness(pop[0])

    for gen in range(n_iter):
        scores = [fitness(gen) for gen in pop]
        for i in range(n_pop):
            if scores[i] > best_eval:
                best = pop[i]
                best_eval = scores[i]

        # select the parents
        selected = [selection(pop, scores) for _ in range(n_pop)]
        # use the parents to create children
        children = []
        for i in range(0, n_pop, 2):
            p1, p2 = selected[i], selected[i + 1]
            # crossover 
            cross = crossover(p1, p2)
            # mutation
            for child in cross:
                mutation(child)
                children.append(child)

        # the population become the children
        pop = children
        print(f"At iter {gen}, The best score is {best_eval}")

    best = np.array(best)
    # best =  best/np.nansum(abs(best))
    return best, settings


def mySettings():
    settings = get_settings()
    futures_list = get_futures_list(filter_insignificant_lag=2)
    settings["markets"] = ["CASH", *futures_list]

    # Set parameters for GA
    settings['population_size'] = 100
    settings['tournament_size'] = 5
    settings['crossover_rate'] = 0.3
    settings['mutation_rate'] = 0.02
    settings['n_iter'] = 100

    return settings


if __name__ == '__main__':
    import quantiacsToolbox

    results = quantiacsToolbox.runts(__file__)
