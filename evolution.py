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
        self.papers[self.initialPaper] = ([initialTopic], [self.newAuthor])
        self.topics[initialTopic] = [self.initialPaper]
        self.initialPaper += 1

    def updateNewCommunity(self, communityAuthors):
        '''
        Function will take in the list of authors in the new community
        Will update the topics, papers, and authors
        '''
        # set variables
        newTopic = max(self.topics.keys()) + 1
        comAuthorsSet = set(communityAuthors)
        allPapers = self.papers.items()

        # loop through all the papers, checking to see the field of majority of their authors
        for pap, (topics, authors) in allPapers:

            # get intersection, check to see if majority of authors in new community
            intersectionAuths = comAuthorsSet.intersection(set(authors))

            # relabel papers if in new topic
            if len(intersectionAuths) >= (len(authors) // 2):
                self.papers[pap][0].append(newTopic)
                # add to new topics 
                if newTopic not in self.topics:
                    self.topics[newTopic] = []
                self.topics[newTopic].append(pap)
            
                # remove paper from old topics if strictly in new topic
                if len(intersectionAuths) > (len(authors) // 2):
                    # update papers data structure
                    self.papers[pap][0].clear()
                    self.papers[pap][0].append(newTopic)
                    # update topics data structure
                    for oldTopic in topics:
                        self.topics[oldTopic].remove(pap)

                # update authors in network with papers
                self.network.updatePaperInNetwork(pap, (topics, authors))    

    def evolve(self, timeSteps=25):
        '''
        Function will continue evolution for the inputted timesteps
        '''
        for newPaperID in range(self.initialPaper, self.initialPaper + timeSteps):

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
            paper = self.network.biasedRandomWalk(authors, self.probStop, newPaperID)
            self.papers[newPaperID] = paper

            # add paper to corresponding topics
            paperTopics = paper[0]
            for top in paperTopics:
                if top not in self.topics:
                    self.topics[top] = []
                self.topics[top].append(newPaperID)

            # split random discipline with prob pd
            if random.random() < self.probSplit:
                communityAuthors = self.network.getDisciplineAuthors(random.choice(list(self.topics.keys())))
                newCommunity = self.network.splitCommunity(communityAuthors)
                # update the papers, topics, and authors
                if newCommunity:
                    self.updateNewCommunity(newCommunity)
                print(f'NewCommunity: {newCommunity}')

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