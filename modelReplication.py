from modules.Evolution import Evolution

'''
This script attempts to follow replicate the results from the following paper: https://www.nature.com/articles/srep01069

'''

# Declare the Nanobank simulation
model = Evolution(Pn=0.9, Pw=0.28, Pd=0)
model.evolve(newAuthors=1000)
model.plotDescriptorsDistr(saveToFile='outputs/nanobankPlots.png', logBase=10)

# Declare the Scholarometer simulation
model = Evolution(Pn=0.04, Pw=0.35, Pd=0.01)
model.evolve(newAuthors=1000)
model.plotDescriptorsDistr(saveToFile='outputs/scholarometerPlots.png', logBase=10)

# Declare the Bibsonomy simulation
model = Evolution(Pn=0.80, Pw=0.71, Pd=0.50)
model.evolve(newPapers=1000)
model.plotDescriptorsDistr(saveToFile='outputs/bibsonomyPlots.png', logBase=10)
