from modules.Evolution import Evolution

'''
This script attempts to follow replicate the results from the following paper: https://www.nature.com/articles/srep01069

'''

# declare amount of runs to average
RUNS = 10


# Declare the Nanobank simulation
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
    model = Evolution(Pn=0.9, Pw=0.28, Pd=0)
    model.evolve(newAuthors=1000)
    descr = model.getQuantDistr(initialDescr=descr)
model.plotDescriptorsDistr(saveToFile='outputs/nanobankPlots.png', logBase=10, data=list(descr.items()))

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
model.plotDescriptorsDistr(saveToFile='outputs/scholarometerPlots.png', logBase=10, data=list(descr.items()))

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
model.plotDescriptorsDistr(saveToFile='outputs/bibsonomyPlots.png', logBase=10, data=list(descr.items()))
