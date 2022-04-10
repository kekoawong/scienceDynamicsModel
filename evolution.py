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
        self.initialPaper = 0

        '''Initialize network with one author, one paper, and one topic'''
        initialTopic = 0
        self.network.add_node(self.newAuthor, data={initialTopic: [self.initialPaper]})
        self.papers[self.initialPaper] = (initialTopic, [self.newAuthor])
        self.topics[initialTopic] = [self.initialPaper]
        self.initialPaper += 1

    def evolve(self, timeSteps=25):
        '''
        Function will continue evolution for the inputted timesteps
        '''
        for newPaper in range(self.initialPaper, self.initialPaper + timeSteps):

            # Randomly select author from network, will be used as first author or first coauthor
            currNodes = list(self.network.nodes())
            authors = [random.choice(currNodes)]

            # with probability, add new author to network set as main author with the coauthor
            if random.random() < self.probNewAuthor:
                # generate new author, add as the first author
                self.newAuthor += 1
                authors.insert(0, self.newAuthor)
                # add node without data, disciplines will be added after paper is completed
                self.network.add_node(self.newAuthor, data={})
                self.network.add_edge(self.newAuthor, authors[1], weight=1, width=1)

            # Add new paper, calling function
            paper = self.network.biasedRandomWalk(authors, self.probStop, newPaper)
            # print(f'Paper: {paper}')
            self.papers[newPaper] = paper

            # add paper to corresponding topic
            if paper[0] not in self.topics:
                self.topics[paper[0]] = []
            self.topics[paper[0]].append(newPaper)

            # split random discipline with prob pd
            if random.random() < self.probSplit:
                communityAuthors = self.network.getDisciplineAuthors(random.choice(list(self.topics.keys())))
                newCommunity = self.network.splitCommunity(communityAuthors)
                print(newCommunity)

            # merge random discipline with prob pm
            if random.random() < self.probMerge:
                pass

        self.initialPaper += timeSteps
        # print(f'Authors: {self.network.nodes(data=True)}')
        # print(f'Papers: {self.papers}')
        # print(f'Topics: {self.topics}')
        # print(f'Initial Paper: {self.initialPaper}')

    def saveEvolutionWithPickle(self, fileName='evolution.env'):
        with open(fileName, 'wb') as outfile:
            pickle.dump(self, outfile)

    def saveNetworkWithPickle(self, fileName='evolutionNetwork.net'):
        with open(fileName, 'wb') as outfile:
            pickle.dump(self.network, outfile)