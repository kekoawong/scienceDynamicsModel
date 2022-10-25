from multiprocessing import Pool
import pickle
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
    distrib1 = []
    distrib2Dict = {}
    distrib3 = []
    if 'newPapers' in simulationObj:
        distrib1, distrib2Dict, distrib3 = model.writeHTMLPage(simName=simulationObj['simulationName'], numPaps=simulationObj['newPapers'], numTops=str(model.getNumTopics()), numTypes='2', 
                        Pn=simulationObj['Pn'], Pw=simulationObj['Pw'], Pd=simulationObj['Pd'], numRuns='1', directory=f"./docs/outputs/model-{simulationObj['modelType']}/")
    elif 'newAuthors' in simulationObj:
        distrib1, distrib2Dict, distrib3 = model.writeHTMLPage(simName=simulationObj['simulationName'], numAuths=simulationObj['newAuthors'], numTops=str(model.getNumTopics()), numTypes='2', 
                        Pn=simulationObj['Pn'], Pw=simulationObj['Pw'], Pd=simulationObj['Pd'], numRuns='1', directory=f"./docs/outputs/model-{simulationObj['modelType']}/")
    # model.plotCreditDistr(saveToFile='outputs/' + simulationObj['simulationName'] + '-' + str(simulationObj['index']))

    print(f'Done with simulation ' + simulationObj['simulationName'])
    return distrib1, distrib2Dict, distrib3, model.getNumAuthors(), model.getNumPapers(), model.getNumTopics()

def combineResults(modelName, results, simulationObj):
    print(f'Compiling results for {modelName}')
    distrib1 = []
    distrib2Dict = {}
    distrib3 = []
    numAuthors = 0
    numPapers = 0
    numTopics = 0
    for distribution in results:
        distrib1 = distrib1 + distribution[0]
        # combine the dictionary distrib
        for key in distribution[1].keys():
            if key in distrib2Dict:
                distrib2Dict[key] = distrib2Dict[key] + distribution[1][key]
            else:
                distrib2Dict[key] = [*distribution[1][key]]
        distrib3 = distrib3 + distribution[2]
        numAuthors += distribution[3]
        numPapers += distribution[4]
        numTopics += distribution[5]
    # initialize model page
    model = Page(Pn=simulationObj['Pn'], Pw=simulationObj['Pw'], Pd=simulationObj['Pd'])

    model.writeHTMLPage(simName=f'combined-results-{modelName}', plotDescr=False, degreeDistrib=distrib1, creditDistr=distrib2Dict, creditTypeDistr=distrib3,
                        numPaps=str(numPapers), numAuths=str(numAuthors), numTops=str(numTopics), numTypes='2', 
                        Pn=simulationObj['Pn'], Pw=simulationObj['Pw'], Pd=simulationObj['Pd'], numRuns='10', directory=f"./docs/outputs/{modelName}/")
    
    return [distrib1, distrib2Dict, distrib3, numAuthors, numPapers, numTopics]

if __name__ == "__main__":

    RUNS = 10

    # declare simulations
    nanobank = {
        'Pn': 0.90,
        'Pw': 0.28,
        'Pd': 0.0,
        'newPapers': int(1000),
        # 'newPapers': int(2.9*10**5),
        'simulationName': 'Nanobank',
        'runs': RUNS,
        'modelType': 0
    }
    scholarometer = {
        'Pn': 0.04,
        'Pw': 0.35,
        'Pd': 0.01,
        'newAuthors': int(1000),
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
    # simulations = [{**nanobank}, {**scholarometer}, {**bibsonomy}]
    simulations = []
    # assign bibsonomy simulations for different model types
    for modelType in range(1, 4):
        for i in range(RUNS):
            simulations.append({**bibsonomy, 
                'simulationName': bibsonomy['simulationName'] + '-' + str(i),
                'modelType': modelType
            })

    # run all the model simulations through multiple cores
    pool = Pool()
    results = pool.map(runSimulation, simulations)
    pool.close()

    results1 = combineResults("model-1", results[:RUNS], bibsonomy)
    filename = 'pickle-outputs/model-1.pi'
    with open(filename, 'wb') as file:
        print(f'Saving to file {filename}')
        # A new file will be created
        pickle.dump(results1, file)
    results2 = combineResults("model-2", results[RUNS:RUNS*2], bibsonomy)
    filename = 'pickle-outputs/model-2.pi'
    with open(filename, 'wb') as file:
        print(f'Saving to file {filename}')
        # A new file will be created
        pickle.dump(results2, file)
    results3 = combineResults("model-3", results[RUNS*2:RUNS*3], bibsonomy)
    filename = 'pickle-outputs/model-3.pi'
    with open(filename, 'wb') as file:
        print(f'Saving to file {filename}')
        # A new file will be created
        pickle.dump(results3, file)

    # save results in a file

    # generate main html page, putting in all the simulations links
