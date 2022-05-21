from .ScholarNetwork import Graph
from .Paper import Paper
from .Topic import Topic
import matplotlib.pyplot as plt
import numpy as np
import random
import pickle
import sys

class Evolution:

    def __init__(self, Pn=0.6, Pw=0.3, Pd=0.5):
        '''
        The probabilities are as follows:
            Pn: probability of a new author being added to a network at a time step (used in evolve)
            Pw: probability that a random walk will stop at a given node (used in random walk)
            Pd: probability that a split and merge event will occur
        '''
        '''Define Probabilites'''
        # probability that you generate new author
        self.probNewAuthor = Pn
        # probability that you stop at a given node when generating papers
        self.probStop = Pw
        # probability that a split and merge event occurs
        self.probEvent = Pd
        
        '''Data Structures'''
        self.network = Graph()
        self.papers = {}
        self.topics = {}

        '''Inital Parameters'''
        self.newAuthor = 1
        self.newPaper = 1

        '''Initialize network with one author, one paper, and one topic'''
        initialTopic = 1
        self.network.addAuthor(self.newAuthor, initialData={initialTopic: [self.newPaper]})
        self.papers[self.newPaper] = Paper(self.newPaper, topics=[initialTopic], authors=[self.newAuthor])
        self.topics[initialTopic] = Topic(initialTopic, papers=[self.newPaper])
        self.newAuthor += 1
        self.newPaper += 1

    '''Access Functions'''
    def getNetwork(self):
        return self.network

    def getPapers(self):
        return self.papers

    def getTopics(self):
        return self.topics

    def getAuthorIDs(self):
        return self.network.getAuthorIDs()

    def getNumTopics(self):
        return len(self.topics.keys())

    def getNumPapers(self):
        return len(self.papers.keys())

    def getNumAuthors(self):
        return len(self.getAuthorIDs())

    def getQuantDistr(self):
        '''
        Will return the Quantitative distributions of the evolution network in the following factors
            Ap: Authors per paper - calculated by averaging number of authors in each new paper that is created (method in paper Class)
            Pa: Papers per author - calculated by looping through all scholars and averaging their number of papers (from method in Author class)
            Ad: Authors per discipline - calculated by looping through all disciplines and averaging their number of scholars (would need to put authors in topics)
            Da: Disciplines per author - calculated by looping through all scholars and averaging their number of disciplines (method in place in author class)
            Pd: Papers per discipline - calculated by looping through all disciplines and averaging their number of papers (method in place in topic class)
            Dp: Disciplines per paper - calculated by looping through all papers and averaging their number of disciplines (method in place in paper class)
        in the form:
        {
            'Ap': list
            'Pa': list
            'Ad': list
            'Da': list
            'Pd': list
            'Dp': list
        }
        '''
        descr = {
            'Ap': [],
            'Pa': [],
            'Ad': [],
            'Da': [],
            'Pd': [],
            'Dp': []
        }
        # get paper parameters distribution
        for paper in self.papers.values():
            descr['Ap'].append(paper.getNumAuthors())
            descr['Dp'].append(paper.getNumTopics())

        # get author distributions
        for authID, authClass in self.network.getNetworkData():
            descr['Pa'].append(authClass.getNumPapers())
            disciplines = authClass.getAuthorDiscipline()
            descr['Da'].append(len(disciplines))
            # update disciplines for discipline parameters
            self.updateDisciplineAuthors(authID, disciplines)

        # get discipline distributions
        for topic in self.topics.values():
            descr['Pd'].append(topic.getNumPapers())
            descr['Ad'].append(topic.getNumDiscAuthors())
        
        return descr

    def updateDisciplineAuthors(self, authID, disciplines):
        for discID in disciplines:
            self.topics[discID].addAuthorToDiscipline(authID)

    '''Printing and Plotting Functions'''
    def __repr__(self):
        return f'Evolution network with a total of {self.getNumAuthors()} authors, {self.getNumPapers()} papers, and {self.getNumTopics()} disciplines/topics.\n'
    
    def printAuthor(self, authorID):
        self.network.printAuthor(authorID)

    def printPaper(self, paperID):
        print(self.papers[paperID])

    def plotNetwork(self):
        self.network.plotNetwork()

    def updateNewCommunity(self, communityAuthors):
        '''
        Function will take in the list of authors in the new community
        Will update the topics, papers, and authors
        '''
        # set variables
        newTopic = max(self.topics.keys()) + 1
        comAuthorsSet = set(communityAuthors)

        # loop through all the papers, checking to see the field of majority of their authors
        for paperID, paperClass in self.papers.items():

            # get intersection, check to see if majority of authors in new community
            intersectionAuths = comAuthorsSet.intersection(set(paperClass.getAuthors()))

            # relabel papers if in new topic
            numIntersectAuths = len(intersectionAuths)
            numHalfAuths = len(paperClass.getAuthors()) // 2
            if numIntersectAuths >= numHalfAuths:
                paperClass.addTopic(newTopic)

                # add to topics 
                if newTopic not in self.topics:
                    self.topics[newTopic] = Topic(newTopic)
                self.topics[newTopic].addPaper(paperID)
            
                # remove paper from old topics if strictly in new topic
                if numIntersectAuths > numHalfAuths:
                    # update papers data structure
                    paperClass.clearTopics()
                    paperClass.addTopic(newTopic)
                    # update topics data structure
                    for oldTopic in paperClass.getTopics():
                        self.topics[oldTopic].removePaper(paperID)

                # update authors in network with papers
                self.network.updatePaperInNetwork(paperID, (paperClass.getTopics(), paperClass.getAuthors()))

    def randomNeighboringCommunities(self):
        '''
        Function used to get two random neighboring communities for merge event
        Returns a tuple of the two communities or None if network not big enough
            ([authorIDs in community 1], [authorIDs in community 2])
        '''

        # choose random author with at least two disciplines
        allAuthors = self.getAuthorIDs()
        while len(allAuthors) > 0:
            authID = random.choice(allAuthors)
            allAuthors.remove(authID)
            authData = self.network.getAuthorData(authID)
            if len(authData.keys()) > 1:
                break
            authID = None

        # select two random disciplines from author
        if not authID:
            return None
        allTopics = list(authData.keys())
        top1 = random.choice(allTopics)
        allTopics.remove(top1)
        top2 = random.choice(allTopics)


        # print(f'Random author {author} with Topic {top1} with authors {self.network.getAuthorswithTopic(top1)}, Topic {top2} with authors {self.network.getAuthorswithTopic(top2)}')

        return self.network.getAuthorswithTopic(top1), self.network.getAuthorswithTopic(top2)

    def evolve(self, newPapers=None, newAuthors=None):
        '''
        Function will continue evolution for the inputted timesteps
        '''
        # use XOR to make sure either newPapers or newAuthors is inputted, but not both
        if bool(newPapers) == bool(newAuthors):
            sys.exit('Must input either newPapers or newAuthors to constrain how many evolution steps, but not both.')

        ind = self.newPaper if newPapers else self.newAuthor
        increments = (ind + newPapers) if newPapers else (ind + newAuthors)
        # subtract one if this is the first evolution, to account for initialized author, topic, and paper
        increments = (increments - 1) if ind <= 2 else increments

        while ind < increments:
            # Randomly select author from network, will be used as first author or first coauthor
            currNodes = list(self.network.nodes())
            authors = [random.choice(currNodes)]

            # with probability, add new author to network set as main author with the coauthor
            if random.random() < self.probNewAuthor:
                # generate new author, add as the first author
                authors.insert(0, self.newAuthor)
                # add node without data, disciplines will be added after paper is completed
                self.network.addAuthor(self.newAuthor, initialData={})
                self.network.add_edge(self.newAuthor, authors[1], weight=1, width=1)
                # increment new authorID
                self.newAuthor += 1

            # Add new paper, calling function
            paperTopics, paperAuthors = self.network.biasedRandomWalk(authors, self.probStop, self.newPaper)
            self.papers[self.newPaper] = Paper(self.newPaper, topics=paperTopics, authors=paperAuthors)

            # add paper to corresponding topics
            for topicID in paperTopics:
                if topicID not in self.topics:
                    self.topics[topicID] = Topic(topicID)
                self.topics[topicID].addPaper(self.newPaper)

            # split random discipline with prob pd
            if random.random() < self.probEvent:
                communityAuthors = self.network.getDisciplineAuthors(random.choice(list(self.topics.keys())))
                newCommunity = self.network.splitCommunity(communityAuthors)
                # update the papers, topics, and authors
                if newCommunity:
                    self.updateNewCommunity(newCommunity)

            # merge random discipline with prob pm
            if random.random() < self.probEvent:
                disciplines = self.randomNeighboringCommunities()
                if disciplines:
                    self.network.mergeCommunities(com1=disciplines[0], com2=disciplines[1])

            # increment papers, update ind
            self.newPaper += 1
            ind = self.newPaper if newPapers else self.newAuthor
            # print(f'ind: {ind} increments: {increments}')

            if ind % 100 == 0:
                print(f'{self.newPaper} papers and {self.newAuthor} authors')
        # print(f'Authors: {self.network.nodes(data=True)}')
        # print(f'Papers: {self.papers}')
        # print(f'Topics: {self.topics}')
        # print(f'Initial Paper: {self.initialPaper}')

    '''Plotting methods'''
    def plotDescriptorsDistr(self, saveToFile=None, logBase=None):
        '''
        Method will take the descriptors dictionary returned from getQuantDescriptors method and plot subplots
        '''
        fig = plt.figure(figsize=(9, 7))
        # make plot with 3 rows, 2 columns
        axs = fig.subplots(3,2)

        # loop through and make subplots
        descr = list(self.getQuantDistr().items())

        # print(descr)
        for row in axs:
            for axis in row:
                lab, data = descr.pop(0)
                binVals, binEdges = np.histogram(data, bins=min(20, len(data)), density=True)
                # binVals, binEdges, patches = plt.hist(x=data, density=True, align='mid', bottom=5)
                binsMean = [0.5 * (binEdges[i] + binEdges[i+1]) for i in range(len(binVals))]
                axis.scatter(binsMean, binVals)
                axis.set_ylabel(f'Density of {lab}', fontweight='bold')
                axis.set_xlabel(f'{lab}', fontweight='bold')
                if logBase:
                    axis.set_yscale('log',base=logBase) 

        # figure styling
        fig.suptitle('Science Network Descriptors')
        fig.tight_layout()

        if saveToFile:
            fig.savefig(saveToFile)
            print(f'Saved to {saveToFile} successfully!')
        
        return fig, axs

    '''Saving Methods'''
    def saveEvolutionWithPickle(self, fileName='evolution.env'):
        with open(fileName, 'wb') as outfile:
            pickle.dump(self, outfile)
        print(f'Saved to {fileName} successfully!')

    def saveNetworkWithPickle(self, fileName='evolutionNetwork.net'):
        with open(fileName, 'wb') as outfile:
            pickle.dump(self.network, outfile)
        print(f'Saved to {fileName} successfully!')