from ScholarNetwork import Graph
import random
import pickle

class Evolution:

    def __init__(self, probNewAuthor=0.5, probStop=0.7, probSplit=0.5, probMerge=0.5):
        '''Define Probabilites'''
        # probability that you generate new author
        self.probNewAuthor = probNewAuthor
        # probability that you stop at a given node when generating papers
        self.probStop = probStop
        # probability that a split event occurs
        self.probSplit = probSplit
        # probability that a merge event occurs
        self.probMerge = probMerge
        
        '''Data Structures'''
        self.network = Graph()
        self.papers = {}
        self.topics = {}

        '''Inital Parameters'''
        self.newAuthor = 0

        '''Initialize network with one author, one paper, and one topic'''
        initialPaper = 0
        initialTopic = 0
        self.network.add_node(self.newAuthor, data={initialTopic: [initialPaper]})
        self.papers[initialPaper] = (initialTopic, [self.newAuthor])
        self.topics[initialTopic] = [initialPaper]

    def evolve(self, timeSteps=25):
        '''
        Function will continue evolution for the inputted timesteps
        '''
        pass

    def saveEvolutionWithPickle(self, fileName='evolution.env'):
        with open(fileName, 'wb') as outfile:
            pickle.dump(self, outfile)

    def saveNetworkWithPickle(self, fileName='evolutionNetwork.net'):
        with open(fileName, 'wb') as outfile:
            pickle.dump(self.network, outfile)