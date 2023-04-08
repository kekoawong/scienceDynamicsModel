from multiprocessing import Pool
import pickle
import csv
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
    csvFile = f"./csv/model-{simulationObj['modelType']}/{simulationObj['simulationName']}.csv"
    print(f'Saving to ' + csvFile)

    authorIDs = model.getAuthorIDs()
    numAuthors = len(authorIDs)
    lenDistrib = len(distrib3[0])
    print(f'{numAuthors} {lenDistrib}')
    with open(csvFile, 'w') as writeFile:
        write = csv.writer(writeFile)
        write.writerow(["Number of Authors:", numAuthors])
        write.writerow(["Number of Papers:", model.getNumPapers()])
        write.writerow(["Number of Topics:", model.getNumTopics()])
        write.writerow(["author-id", 'author-degree', 'author-credit', 'author-type', "", "percent-marg-x", "avg-credit-y", "num-authors"])
        for rowNum in range(max(numAuthors, lenDistrib)):
            cell1 = None if rowNum >= numAuthors else authorIDs[rowNum]
            cell2 = None if rowNum >= numAuthors else model.getNetwork().degree[authorIDs[rowNum]]
            cell3 = None if rowNum >= numAuthors else model.getNetwork().getAuthorClass(authorIDs[rowNum]).getCredit()
            cell4 = None if rowNum >= numAuthors else model.getNetwork().getAuthorClass(authorIDs[rowNum]).getType().name
            cell5 = None
            cell6 = None if rowNum >= lenDistrib else distrib3[0][rowNum]
            cell7 = None if rowNum >= lenDistrib else distrib3[1][rowNum]
            cell8 = None if rowNum >= lenDistrib else distrib3[2][rowNum]
            write.writerow([cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8])
    print(f'Completed writing to {csvFile}')

    return distrib1, distrib2Dict, distrib3, model.getNumAuthors(), model.getNumPapers(), model.getNumTopics()

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
        'newPapers': int(10000),
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

    # generate main html page, putting in all the simulations links
