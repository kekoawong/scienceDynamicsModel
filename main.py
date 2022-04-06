from Evolution import Evolution

env = Evolution()

env.evolve(timeSteps=20)

test = {1: [14,15], 2: [18]}
v = max(len(x) for x in test.items())
print(v)