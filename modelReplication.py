from multiprocessing.pool import RUN
from modules.Evolution import Evolution
import os
import sys
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


if __name__ == "__main__":

    # Declare the simulation objects
    nanobank = {
        'Pn': 0.90,
        'Pw': 0.28,
        'Pd': 0.0,
        'newAuthors': int(2.9*10**5),
        'simulationName': 'Nanobank'
    }
    scholarometer = {
        'Pn': 0.04,
        'Pw': 0.35,
        'Pd': 0.01,
        'newAuthors': int(2.2*10**4),
        'simulationName': 'Scholarometer'
    }
    bibsonomy = {
        'Pn': 0.80,
        'Pw': 0.71,
        'Pd': 0.50,
        'newPapers': int(2.9*10**5),
        'simulationName': 'Bibsonomy'
    }


    print(os.cpu_count())
    # declare amount of runs to average
    RUNS = 10

    # declare multiprocessing
    pool = Pool()

    data = pool.map(runSimulation, [nanobank] * RUNS)
    pool.close()
    data = list(data)

    # get nanobank results
    descr, numAuths, numPaps, numTops = combineDescr(data[:RUNS])
    Evolution().plotDescriptorsDistr(saveToFile='outputs/nanobankPlots.png', ylogBase=10, xlogBase=10, data=descr, 
                                    numAuthors=numAuths, numPapers=numPaps, numTopics=numTops)