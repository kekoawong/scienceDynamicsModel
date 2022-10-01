from multiprocessing import Pool
# from modules.Evolution import Evolution
from modules.HTMLPage import Page

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
    model = Page(Pn=simulationObj['Pn'], Pw=simulationObj['Pw'], Pd=simulationObj['Pd'])

    # evolve criteria
    if 'newPapers' in simulationObj:
        model.evolve(newPapers=simulationObj['newPapers'])
    else:
        model.evolve(newAuthors=simulationObj['newAuthors'])

    # save html page of output
    model.writeHTMLPage(simName=simulationObj['simulationName'], numPaps=simulationObj['newPapers'], numTops=str(model.getNumTopics()), numTypes='2', 
                        Pn=simulationObj['Pn'], Pw=simulationObj['Pw'], Pd=simulationObj['Pd'], numRuns='1', directory='./docs/outputs/')
    # model.plotCreditDistr(saveToFile='outputs/' + simulationObj['simulationName'] + '-' + str(simulationObj['index']))

    print(f'Done with simulation ' + simulationObj['simulationName'])
    return

if __name__ == "__main__":

    RUNS = 3

    # declare simulations
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
    # assign bibsonomy simulations
    for i in range(RUNS):
        simulations.append({**bibsonomy, 'simulationName': bibsonomy['simulationName'] + '-' + str(i)})

    # run all the model simulations through multiple cores
    pool = Pool(RUNS * 3)
    pool.map(runSimulation, simulations)
    pool.close()

    # generate main html page, putting in all the simulations links
