from multiprocessing.pool import RUN
import sys
from modules.Evolution import Evolution
from modules.HTMLPage import Page
import pickle
from multiprocessing import Pool

'''
This script attempts to follow replicate the results from the following paper: https://www.nature.com/articles/srep01069

Uses multiprocessing
'''

# declare amount of runs to average
RUNS = 3
index = 0

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
    model = Evolution(Pn=simulationObj['Pn'], Pw=simulationObj['Pw'], Pd=simulationObj['Pd'])
    if 'newPapers' in simulationObj:
        model.evolve(newPapers=simulationObj['newPapers'])
    else:
        model.evolve(newAuthors=simulationObj['newAuthors'])
    model.plotCreditDistr(saveToFile='outputs/' + simulationObj['simulationName'] + '-' + str(simulationObj['index']))
    print(f'Done with simulation ' + simulationObj['simulationName'])
    return model.getQuantDistr(), model.getNumAuthors(), model.getNumPapers(), model.getNumTopics(), model.getDegreeDistribution(), model.getCreditDistribution(), model.getDisciplineTypeDistribution(), simulationObj

def getData(simData):
    '''
    Function will aggragate all the data from the different runs
    '''
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
    degreeDistrib = []
    creditDistr = {}
    disciplineTypeDistribs = [{}, {}]

    for des, numAuths, numPaps, numTops, deg, credit, disciplineTypeObj, simObj in simData:
        for key, vals in des.items():
            descr[key].extend(vals)
        sumAuths += numAuths
        sumPaps += numPaps
        sumTops += numTops
        degreeDistrib.extend(deg)

        # append credit to distributions in dict
        for key, val in credit.items():
            if key not in creditDistr:
                creditDistr[key] = []
            creditDistr[key].extend(val)

        # append displineType objects
        for i, distribution in enumerate(disciplineTypeObj):
            for key, val in distribution.items():
                if key not in disciplineTypeDistribs[i]:
                    disciplineTypeDistribs[i][key] = []
                disciplineTypeDistribs[i][key].extend(val)

    return descr, sumAuths//len(simData), sumPaps//len(simData), sumTops//len(simData), degreeDistrib, creditDistr, disciplineTypeDistribs, simObj

def saveToFile(fileName, descr, numAuthors, numPapers, numTopics):
    '''
    Function used to save data to pickle file
    '''
    with open(fileName, 'wb') as outfile:
        pickle.dump({
            'descr': descr,
            'numAuthors': numAuthors,
            'numPapers': numPapers,
            'numTopics': numTopics 
        }, outfile)

def saveResults(simName, simData):
    '''
    Function used to save outputs to html file and pickle file
    '''
    htmlPage = Page()

    descr, numAuths, numPaps, numTops, degreeDistrib, creditDistr, disciplineObj, simObj = getData(simData)
    saveToFile(fileName=f'outputs/{simName}Data.pi', descr=descr, numAuthors=numAuths, numPapers=numPaps, numTopics=numTops)
    htmlPage.writeHTMLPage(simName=simName, descr=descr, creditDistr=creditDistr, degreeDistrib=degreeDistrib, displineTypeObj=disciplineObj, numAuths=numAuths, numPaps=numPaps, 
                        numTops=numTops, numTypes=2, Pn=simObj['Pn'], Pw=simObj['Pw'], Pd=simObj['Pd'], numRuns=simObj['runs'], directory='./docs/outputs/')

if __name__ == "__main__":

    # Declare the simulation objects
    nanobank = {
        'Pn': 0.90,
        'Pw': 0.28,
        'Pd': 0.0,
        'newPapers': int(102),
        # 'newPapers': int(2.9*10**5),
        'simulationName': 'Nanobank',
        'runs': RUNS
    }
    scholarometer = {
        'Pn': 0.04,
        'Pw': 0.35,
        'Pd': 0.01,
        'newAuthors': int(500),
        # 'newAuthors': int(2.2*10**4),
        'simulationName': 'Scholarometer',
        'runs': RUNS
    }
    bibsonomy = {
        'Pn': 0.80,
        'Pw': 0.71,
        'Pd': 0.50,
        'newPapers': int(1000),
        # 'newPapers': int(2.9*10**5),
        'simulationName': 'Bibsonomy',
        'runs': RUNS
    }


    # declare multiprocessing
    pool = Pool(RUNS * 3)

    # create simulations object
    simulations = []
    for i in range(RUNS):
        simulations.append({**nanobank, **{ 'index': i }})
    for i in range(RUNS):
        simulations.append({**scholarometer, **{ 'index': i }})
    for i in range(RUNS):
        simulations.append({**bibsonomy, **{ 'index': i }})

    data = pool.map(runSimulation, simulations)
    pool.close()
    data = list(data)

    # get nanobank results and save
    saveResults('nanobankCredit', data[:RUNS])

    # get scholarometer results and save
    saveResults('scholarometerCredit', data[RUNS:2*RUNS])

    # get bibsonomy results
    saveResults('bibsonomyCredit', data[2*RUNS:])