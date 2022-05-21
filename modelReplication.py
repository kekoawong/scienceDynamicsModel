from modules.Evolution import Evolution

'''
This script attempts to follow replicate the results from the following paper: https://www.nature.com/articles/srep01069

'''

# Declare the Nanobank simulation
nanobank = Evolution(Pn=0.9, Pw=0.28, Pd=0)
nanobank.evolve(newAuthors=300)
nanobank.plotDescriptorsDistr(saveToFile='outputs/nanobankPlots.png')

# Declare the Scholarometer simulation
scholarometer = Evolution(Pn=0.04, Pw=0.35, Pd=0.01)
scholarometer.evolve(newAuthors=300)
scholarometer.plotDescriptorsDistr(saveToFile='outputs/scholarometerPlots.png')

# Declare the Bibsonomy simulation
bibsonomy = Evolution(Pn=0.80, Pw=0.71, Pd=0.50)
bibsonomy.evolve(newPapers=300)
bibsonomy.plotDescriptorsDistr(saveToFile='outputs/bibsonomyPlots.png')
