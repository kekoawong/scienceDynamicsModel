from ScholarNetwork import Graph
import random
from helpers import getCommNodes, splitCommunity, createPaper
import pickle

'''
DEFINE PARAMETERS
'''
# define time steps
timeSteps = 50

# PROBABILITIES
# probability that you generate new author
probNewAuthor = 0.5
# probability that you stop at a given node when generating papers
probStop = 0.7
# probability that a split event occurs
probSplit = 0.5
# probability that a merge event occurs
probMerge = 0.5

# define initial scholar and topic params
newTopic = 0
newAuthor = 0
initialPaper = 0

'''
CREATE MODEL
'''

# initialize data structures
network = Graph()
papers = {}
topics = {}

# add first node and paper to network
network.add_node(newAuthor, data={newTopic: [initialPaper]})
papers[initialPaper] = (newTopic, [newAuthor])
topics[newTopic] = [initialPaper]

# go through time steps, add new scholar and paper at each step
for newPaper in range(1, timeSteps):

    # Randomly select author from network, will be used as first author or first coauthor
    currNodes = list(network.nodes())
    authors = [random.choice(currNodes)]

    # with probability, add new author to network set as main author with the coauthor
    if random.random() < probNewAuthor:
        # generate new author, add as the first author
        newAuthor += 1
        authors.insert(0, newAuthor)
        # add node without data, disciplines will be added after paper is completed
        network.add_node(newAuthor, data={})
        network.add_edge(newAuthor, authors[1], weight=1, width=1)

    # Add new paper, calling function
    paper = createPaper(network, authors, probStop)
    papers[newPaper] = paper

    # add paper to corresponding topic
    if paper[0] not in topics:
        topics[paper[0]] = []
    topics[paper[0]].append(newPaper)

    # split random discipline with prob pd
    if random.random() < probSplit:
        commNodes = getCommNodes(network, random.choice(list(topics.keys())))
        splitCommunity(network, commNodes)

    # merge random discipline with prob pm
    if random.random() < probMerge:
        pass

# save network as pickle object
with open('evolution.net', 'wb') as outfile:
    pickle.dump(network, outfile)