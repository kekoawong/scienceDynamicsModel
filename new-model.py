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
        'simulationName': str,
        'runs': int
        modelType: 0 | 1 | 2 | 3
    }
    '''
    print(f'Starting simulation ' + simulationObj['simulationName'])
    # initialize model
    model = Page(Pn=simulationObj['Pn'], Pw=simulationObj['Pw'], Pd=simulationObj['Pd'])

    # evolve criteria
    if 'newPapers' in simulationObj:
        model.evolve(modelType=simulationObj['modelType'], newPapers=simulationObj['newPapers'])
    else:
        model.evolve(modelType=simulationObj['modelType'], newAuthors=simulationObj['newAuthors'])

    # save html page of output
    if 'newPapers' in simulationObj:
        model.writeHTMLPage(simName=simulationObj['simulationName'], numPaps=simulationObj['newPapers'], numTops=str(model.getNumTopics()), numTypes='2', 
                        Pn=simulationObj['Pn'], Pw=simulationObj['Pw'], Pd=simulationObj['Pd'], numRuns='1', directory=f"./docs/outputs/model-{simulationObj['modelType']}/")
    elif 'newAuthors' in simulationObj:
        model.writeHTMLPage(simName=simulationObj['simulationName'], numAuths=simulationObj['newAuthors'], numTops=str(model.getNumTopics()), numTypes='2', 
                        Pn=simulationObj['Pn'], Pw=simulationObj['Pw'], Pd=simulationObj['Pd'], numRuns='1', directory=f"./docs/outputs/model-{simulationObj['modelType']}/")
    # model.plotCreditDistr(saveToFile='outputs/' + simulationObj['simulationName'] + '-' + str(simulationObj['index']))

    print(f'Done with simulation ' + simulationObj['simulationName'])
    return

if __name__ == "__main__":

    RUNS = 3

    # declare simulations
    nanobank = {
        'Pn': 0.90,
        'Pw': 0.28,
        'Pd': 0.0,
        'newPapers': int(102),
        # 'newPapers': int(2.9*10**5),
        'simulationName': 'Nanobank',
        'runs': RUNS,
        'modelType': 0
    }
    scholarometer = {
        'Pn': 0.04,
        'Pw': 0.35,
        'Pd': 0.01,
        'newAuthors': int(500),
        # 'newAuthors': int(2.2*10**4),
        'simulationName': 'Scholarometer',
        'runs': RUNS,
        'modelType': 0
    }
    bibsonomy = {
        'Pn': 0.80,
        'Pw': 0.71,
        'Pd': 0.50,
        'newPapers': int(1000),
        # 'newPapers': int(2.9*10**5),
        'simulationName': 'Bibsonomy',
        'runs': RUNS,
        'modelType': 0
    }

    # generate the simulation object list
    simulations = [{**nanobank}, {**scholarometer}, {**bibsonomy}]
    # assign bibsonomy simulations for different model types
    for modelType in range(1, 4):
        for i in range(RUNS):
            simulations.append({**bibsonomy, 
                'simulationName': bibsonomy['simulationName'] + '-' + str(i),
                'modelType': modelType
            })

    # run all the model simulations through multiple cores
    pool = Pool(RUNS * 3)
    pool.map(runSimulation, simulations)
    pool.close()

    # generate main html page, putting in all the simulations links
