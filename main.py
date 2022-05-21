from modules.Evolution import Evolution

env = Evolution(probMerge=.8)

env.evolve(newAuthors=10)

# env.printAuthor(0)
# env.printPaper(1)

env.network.getAuthorPapers(1)

env.network.plotPyvisGraph(filename='outputs/pyvis.html')

env.saveEvolutionWithPickle('outputs/evolution.env')
# env.evolve(timeSteps=20)


# env.printAuthor(0)
# env.printPaper(1)

# env.network.getAuthorPapers(0)

# env.network.plotPyvisGraph(filename='outputs/pyvisNext.html')

# env.saveEvolutionWithPickle('outputs/evolution.env')

print(f'Topics: {env.getTopics()}')
print(f'num authors: {env.getNumAuthors()}')
# print(env)

# test = {
#     1: [1,2,3],
#     2: [0, 1, 2, 4, 7, 10],
#     3: [0, 1, 2, 4, 7, 10],
# }

# for k, val in test.items():
#     val.append('hi')