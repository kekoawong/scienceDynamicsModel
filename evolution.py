from pyvis.network import Network
import matplotlib.pyplot as plt
import networkx as nx
import random
from helpers import getCommNodes, splitCommunity, genGraphFeatures, getTopic


# define time steps
timeSteps = 50

'''PROBABILITIES'''
# probability that you generate new author
probNewAuthor = 0.5
# probability that you stop at a given node when generating papers
probStop = 0.7
# probability that a split event occurs
probSplit = 0.5
# probability that a merge event occurs
probMerge = 0.5

# define initial scholars, will be in form (id, scholartopic, color)
scholarTopic = 0
nodeID = 0
paperID = 0


network = nx.Graph()
network.add_node(nodeID, label=scholarTopic, color="red")

# initialize Topics and papers data structures
papers = {}
topics = {}

# go through time steps, add new scholar and paper at each step
for i in range(1, timeSteps):

    # Choose first author, sets initially as random scholar (can be overridden with new scholar later)
    currNodes = list(network.nodes())
    authors = [random.choice(currNodes)]

    # with probability, add new author to network set as main author with a coauthor
    if random.random() < probNewAuthor:
        # generate author and Topic
        nodeID += 1
        author = nodeID

        # generate random coauthor from currNodes,
        coauthorID = random.choice(currNodes)

        # add node with Topic being the co-author's Topic
        # THIS NEEDS TO BE CHANGED TO MAJORITY OF PAPER
        scholarTopic = network.nodes[coauthorID]["label"]
        network.add_node(author, label=scholarTopic, color="red")
        network.add_edge(author, coauthorID, weight=1, width=1)

        # update authors list
        authors = [author, coauthorID]

    # Add new paper, calling function
    paper = createPaper(network, authors, probStop)
    print(paper)
    papers[paperID] = paper

    # add paper to corresponding topic
    if paper[0] not in topics:
        topics[paper[0]] = []
    topics[paper[0]].append(paperID)
    paperID += 1

    # split random discipline with prob pd
    if random.random() < probSplit:
        commNodes = getCommNodes(network, random.choice(list(topics.keys())))
        splitCommunity(network, commNodes)

    # merge random discipline with prob pm
    if random.random() < probMerge:
        pass
