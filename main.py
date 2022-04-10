from Evolution import Evolution

env = Evolution()

env.evolve(timeSteps=20)

test = {
    4: [],
    0: [1,2,3,4,5],
    1: [1,2,3],
    2: [1,2,3,4,5]
}

maxVal = 0
disciplines = []
for top, papers in test.items():
    numPapers = len(papers)
    if numPapers == maxVal:
        disciplines.append(top)
    elif numPapers > maxVal:
        maxVal = numPapers
        disciplines = [top]

print(f'topics: {disciplines}')