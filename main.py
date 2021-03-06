from modules.Evolution import Evolution

env = Evolution(Pn=.8)

env.evolve(newAuthors=1000)

# env.printAuthor(0)
# env.printPaper(1)

env.network.getAuthorPapers(1)

# env.network.plotPyvisGraph(filename='outputs/pyvis.html')

env.saveEvolutionWithPickle('outputs/evolution.env')
# env.evolve(timeSteps=20)


# env.printAuthor(0)
# env.printPaper(1)

# env.network.getAuthorPapers(0)

# env.network.plotPyvisGraph(filename='outputs/pyvisNext.html')

# env.saveEvolutionWithPickle('outputs/evolution.env')
env.plotDescriptorsDistr(saveToFile='outputs/creditAccumulation.png', xlogBase=10, ylogBase=10, 
                            numAuthors=env.getNumAuthors(), numPapers=env.getNumPapers(), numTopics=env.getNumTopics(), networkName='Credit accumulation')
print(f'num authors: {env.getNumAuthors()}')
# print(env)

# test = {
#     1: [1,2,3],
#     2: [0, 1, 2, 4, 7, 10],
#     3: [0, 1, 2, 4, 7, 10],
# }

# for k, val in test.items():
#     val.append('hi')