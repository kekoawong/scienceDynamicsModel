from Evolution import Evolution

env = Evolution()

env.evolve(timeSteps=20)

env.saveEvolutionWithPickle('models/evolution.env')


print(f'Topics: {env.getTopics()}')
print(f'Papers: {env.getPapers()}')
print(f'Authors: {env.getAuthors()}')

print(env)

# test = {
#     1: [1,2,3],
#     2: [0, 1, 2, 4, 7, 10],
#     3: [0, 1, 2, 4, 7, 10],
# }

# for k, val in test.items():
#     val.append('hi')