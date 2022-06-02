from multiprocessing.pool import RUN
from modules.Evolution import Evolution
import pickle
from multiprocessing import Pool

'''
This script attempts to follow replicate the results from the following paper: https://www.nature.com/articles/srep01069

Uses multiprocessing
'''
def runSimulation(simulationObj):
    '''
    simulationObj must contain the following parameters:
    {
        'Pn': float
        'Pw': float
        'Pd': float
        'newAuthors' or 'newPapers': int
        'simulationName': str
    }
    '''
    model = Evolution(Pn=simulationObj['Pn'], Pw=simulationObj['Pw'], Pd=simulationObj['Pd'])
    if 'newPapers' in simulationObj:
        model.evolve(newPapers=simulationObj['newPapers'])
    else:
        model.evolve(newAuthors=simulationObj['newAuthors'])
    print(f'Done with simulation ' + simulationObj['simulationName'])
    return model.getQuantDistr(), model.getNumAuthors(), model.getNumPapers(), model.getNumTopics()

def combineDescr(descrList):
    descr = {
        'Ap': [],
        'Pa': [],
        'Ad': [],
        'Da': [],
        'Pd': [],
        'Dp': []
    }
    sumAuths = 0
    sumPaps = 0
    sumTops = 0
    for des, numAuths, numPaps, numTops in descrList:
        for key, vals in des.items():
            descr[key].extend(vals)
        sumAuths += numAuths
        sumPaps += numPaps
        sumTops += numTops

    return descr, sumAuths//len(descrList), sumPaps//len(descrList), sumTops//len(descrList)

def saveToFile(fileName, descr, numAuthors, numPapers, numTopics):
    with open(fileName) as outfile:
        pickle.dump({
            'descr': descr,
            'numAuthors': numAuthors,
            'numPapers': numPapers,
            'numTopics': numTopics 
        }, outfile)

if __name__ == "__main__":

    # Declare the simulation objects
    nanobank = {
        'Pn': 0.90,
        'Pw': 0.28,
        'Pd': 0.0,
        'newPapers': int(500),
        # 'newPapers': int(2.9*10**5),
        'simulationName': 'Nanobank'
    }
    scholarometer = {
        'Pn': 0.04,
        'Pw': 0.35,
        'Pd': 0.01,
        'newAuthors': int(300),
        # 'newAuthors': int(2.2*10**4),
        'simulationName': 'Scholarometer'
    }
    bibsonomy = {
        'Pn': 0.80,
        'Pw': 0.71,
        'Pd': 0.50,
        'newPapers': int(500),
        # 'newPapers': int(2.9*10**5),
        'simulationName': 'Bibsonomy'
    }


    # declare amount of runs to average
    RUNS = 10

    # declare multiprocessing
    pool = Pool(10)

    simulations = [nanobank] * RUNS + [scholarometer] * RUNS + [bibsonomy] * RUNS

    data = pool.map(runSimulation, simulations)
    pool.close()
    data = list(data)

    # get nanobank results and save
    descr, numAuths, numPaps, numTops = combineDescr(data[:RUNS])
    saveToFile(fileName='outputs/nanobanksData.pi', descr=descr, numAuthors=numAuths, numPapers=numPaps, numTopics=numTops)
    Evolution().plotDescriptorsDistr(saveToFile='outputs/nanobankPlots.png', ylogBase=10, xlogBase=10, data=descr, 
                                    numAuthors=numAuths, numPapers=numPaps, numTopics=numTops)

    # get scholarometer results and save
    descr, numAuths, numPaps, numTops = combineDescr(data[RUNS:2*RUNS])
    saveToFile(fileName='outputs/scholarometerData.pi', descr=descr, numAuthors=numAuths, numPapers=numPaps, numTopics=numTops)
    Evolution().plotDescriptorsDistr(saveToFile='outputs/scholarometerPlots.png', ylogBase=10, xlogBase=10, data=descr, 
                                    numAuthors=numAuths, numPapers=numPaps, numTopics=numTops)
    # get bibsonomy results
    descr, numAuths, numPaps, numTops = combineDescr(data[2*RUNS:])
    saveToFile(fileName='outputs/bibsonomyData.pi', descr=descr, numAuthors=numAuths, numPapers=numPaps, numTopics=numTops)
    Evolution().plotDescriptorsDistr(saveToFile='outputs/bibsonomyPlots.png', ylogBase=10, xlogBase=10, data=descr, 
                                    numAuthors=numAuths, numPapers=numPaps, numTopics=numTops)