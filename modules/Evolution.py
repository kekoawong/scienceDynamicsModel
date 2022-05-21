from .ScholarNetwork import Graph
from .Paper import Paper
from .Topic import Topic
import random
import pickle
import sys

class Evolution:

    def __init__(self, probNewAuthor=0.6, probStop=0.3, probSplit=0.5, probMerge=0.5):
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
        self.newAuthor = 1
        self.newPaper = 1

        '''
        Quantitative Descriptors
            Ap: Authors per paper
            Pa: Papers per author
            Ad: Authors per discipline
            Da: Disciplines per author
            Pd: Papers per discipline
            Dp: Disciplines per paper
        '''
        self.Ap = None # calculated by averaging number of authors in each new paper that is created (updated in evolve method)
        self.Pa = None # calculated by looping through all scholars and averaging their number of papers (in getQuantDescriptors method)
        self.Ad = None # calculated by looping through all disciplines and averaging their number of scholars
        self.Da = None # calculated by looping through all scholars and averaging their number of disciplines
        self.Pd = None # calculated by looping through all disciplines and averaging their number of papers
        self.Dp = None # calculated by looping through all papers and averaging their number of disciplines

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

    def getQuantDescriptors(self):
        '''
        Will return the Quantitative Descriptors of the evolution network
            Ap: Authors per paper
            Pa: Papers per author
            Ad: Authors per discipline
            Da: Disciplines per author
            Pd: Papers per discipline
            Dp: Disciplines per paper
        in the form:
        {
            'Ap': float
            'Pa': float
            'Ad': float
            'Da': float
            'Pd': float
            'Dp': float
        }
        '''
        return None

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
                # increment
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
            if random.random() < self.probSplit:
                communityAuthors = self.network.getDisciplineAuthors(random.choice(list(self.topics.keys())))
                newCommunity = self.network.splitCommunity(communityAuthors)
                # update the papers, topics, and authors
                if newCommunity:
                    self.updateNewCommunity(newCommunity)

            # merge random discipline with prob pm
            if random.random() < self.probMerge:
                disciplines = self.randomNeighboringCommunities()
                if disciplines:
                    self.network.mergeCommunities(com1=disciplines[0], com2=disciplines[1])

            # increment papers, update ind
            self.newPaper += 1
            ind = self.newPaper if newPapers else self.newAuthor
            # print(f'ind: {ind} increments: {increments}')
        # print(f'Authors: {self.network.nodes(data=True)}')
        # print(f'Papers: {self.papers}')
        # print(f'Topics: {self.topics}')
        # print(f'Initial Paper: {self.initialPaper}')

    '''Saving Methods'''
    def saveEvolutionWithPickle(self, fileName='evolution.env'):
        with open(fileName, 'wb') as outfile:
            pickle.dump(self, outfile)
        print(f'Saved to {fileName} successfully!')

    def saveNetworkWithPickle(self, fileName='evolutionNetwork.net'):
        with open(fileName, 'wb') as outfile:
            pickle.dump(self.network, outfile)
        print(f'Saved to {fileName} successfully!')