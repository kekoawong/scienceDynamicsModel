from modules.Evolution import Evolution
import os
import sys
from multiprocessing import Pool

'''
This script attempts to follow replicate the results from the following paper: https://www.nature.com/articles/srep01069

Uses multiprocessing
'''
# declare amount of runs to average
RUNS = 1

def runSimulation(simulationName, simulationObj):
    '''
    simulationObj must contain the following parameters:
    {
        'Pn': float
        'Pw': float
        'Pd': float
        'newAuthors' or 'newPapers': int
    }
    '''
    model = Evolution(Pn=simulationObj['Pn'], Pw=simulationObj['Pw'], Pd=simulationObj['Pd'])
    if 'newPapers' in simulationObj:
        model.evolve(newPapers=simulationObj['newPapers'])
    else:
        model.evolve(newAuthors=simulationObj['newAuthors'])
    print(f'Done with simulation {simulationName}')
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
    for d in descrList:
        for key, vals in d.items():
            descr[key].extend(vals)

    return descr

print(os.cpu_count())

# Declare the Nanobank simulation
# initialize quant descriptors
# TODO: add number of scholars, papers, disciplines to the descr and graph
descr = {
    'Ap': [],
    'Pa': [],
    'Ad': [],
    'Da': [],
    'Pd': [],
    'Dp': []
}
for i in range(RUNS):
    model = Evolution(Pn=0.9, Pw=0.28, Pd=0)
    model.evolve(newAuthors=1000)
    descr = model.getQuantDistr(initialDescr=descr)
    print(f'Done with run {i+1} with nanobank')
model.plotDescriptorsDistr(saveToFile='outputs/nanobankPlots.png', ylogBase=10, xlogBase=10, data=descr)

# Declare the Scholarometer simulation
# initialize quant descriptors
descr = {
    'Ap': [],
    'Pa': [],
    'Ad': [],
    'Da': [],
    'Pd': [],
    'Dp': []
}
for i in range(RUNS):
    model = Evolution(Pn=0.04, Pw=0.35, Pd=0.01)
    model.evolve(newAuthors=1000)
    descr = model.getQuantDistr(initialDescr=descr)
    print(f'Done with run {i+1} with scholarometer')
model.plotDescriptorsDistr(saveToFile='outputs/scholarometerPlots.png', ylogBase=10, xlogBase=10, data=descr)

# Declare the Bibsonomy simulation
# initialize quant descriptors
descr = {
    'Ap': [],
    'Pa': [],
    'Ad': [],
    'Da': [],
    'Pd': [],
    'Dp': []
}
for i in range(RUNS):
    model = Evolution(Pn=0.80, Pw=0.71, Pd=0.50)
    model.evolve(newPapers=1000)
    descr = model.getQuantDistr(initialDescr=descr)
    print(f'Done with run {i+1} with bibsonomy')
model.plotDescriptorsDistr(saveToFile='outputs/bibsonomyPlots.png', ylogBase=10, xlogBase=10, data=descr)
