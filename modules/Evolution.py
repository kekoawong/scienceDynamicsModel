from operator import xor
from .ScholarNetwork import Graph
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
        self.newAuthor = 0
        self.newPaper = 0

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
        initialTopic = 0
        self.network.addAuthor(self.newAuthor, initialData={initialTopic: [self.newPaper]})
        self.papers[self.newPaper] = ([initialTopic], [self.newAuthor])
        self.topics[initialTopic] = [self.newPaper]
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
        s = f'Evolution network with a total of {self.getNumAuthors()} authors, {self.getNumPapers()} papers, and {self.getNumTopics()} disciplines/topics.\n'
        for authID, authClass in self.getAuthorsClasses():
            authID = authClass.getID()
            s += f'   Author {authID} primary disciplines: {self.network.getAuthorDiscipline(authID)}\n'
            for topicID, papers in authClass.getData().items():
                for pap in papers:
                    s += f'      Paper {pap} with the topics {self.papers[pap][0]}\n'
        return s
    
    def printAuthor(self, authorID):
        self.network.printAuthor(authorID)

    def printPaper(self, paperID):
        topics = ','.join(map(str, self.papers[paperID][0]))
        authors = ','.join(map(str, self.papers[paperID][1]))
        print(f'Paper {paperID} topics: {topics}')
        print(f'Paper {paperID} authors: {authors}')

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

            # Add new paper, calling function
            paper = self.network.biasedRandomWalk(authors, self.probStop, self.newPaper)
            self.papers[self.newPaper] = paper

            # add paper to corresponding topics
            paperTopics = paper[0]
            for top in paperTopics:
                if top not in self.topics:
                    self.topics[top] = []
                self.topics[top].append(self.newPaper)

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

            # increment
            self.newAuthor += 1
            self.newPaper += 1
            ind += 1
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