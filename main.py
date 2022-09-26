from multiprocessing import Pool
from modules.Evolution import Evolution

def runSimulation(simulationObj):
    '''
    Function will be passed to pool to map the different processes
    simulationObj must contain the following parameters:
    {
        'Pn': float
        'Pw': float
        'Pd': float
        'newAuthors' or 'newPapers': int
        'simulationName': str
    }
    '''
    print(f'Starting simulation ' + simulationObj['simulationName'])
    # initialize model
    model = Evolution(Pn=simulationObj['Pn'], Pw=simulationObj['Pw'], Pd=simulationObj['Pd'])

    # evolve criteria
    if 'newPapers' in simulationObj:
        model.evolve(newPapers=simulationObj['newPapers'])
    else:
        model.evolve(newAuthors=simulationObj['newAuthors'])

    # save html page of output
    model.plotCreditDistr(saveToFile='outputs/' + simulationObj['simulationName'] + '-' + str(simulationObj['index']))
    print(f'Done with simulation ' + simulationObj['simulationName'])
    return

if __name__ == "__main__":

    RUNS = 3

    bibsonomy = {
        'Pn': 0.80,
        'Pw': 0.71,
        'Pd': 0.50,
        'newPapers': int(1000),
        # 'newPapers': int(2.9*10**5),
        'simulationName': 'Bibsonomy',
        'runs': RUNS
    }

    # generate the simulation object list
    simulations = []
    for i in range(RUNS):
        bibsonomy['simulationName'] = bibsonomy['simulationName'] + '-' + str(i)
        simulations.append(bibsonomy)

    # run all the model simulations through multiple cores
    pool = Pool(RUNS * 3)
    pool.map(runSimulation, simulations)
    pool.close()

    # generate main html page, putting in all the simulations links
