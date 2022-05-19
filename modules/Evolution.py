from .ScholarNetwork import Graph
import random
import pickle

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
        self.initialPaper = 0

        '''Initialize network with one author, one paper, and one topic'''
        initialTopic = 0
        self.network.addAuthor(self.newAuthor, data={initialTopic: [self.initialPaper]})
        self.papers[self.initialPaper] = ([initialTopic], [self.newAuthor])
        self.topics[initialTopic] = [self.initialPaper]
        self.initialPaper += 1

    '''Access Functions'''
    def getNetwork(self):
        return self.network

    def getPapers(self):
        return self.papers

    def getTopics(self):
        return self.topics

    def getAuthors(self):
        return self.network.getAuthors()

    def getNumTopics(self):
        return len(self.topics.keys())

    def getNumPapers(self):
        return len(self.papers.keys())

    def getNumAuthors(self):
        return len(self.getAuthors())

    '''Printing and Plotting Functions'''
    def __repr__(self):
        s = f'Evolution network with a total of {self.getNumAuthors()} authors, {self.getNumPapers()} papers, and {self.getNumTopics()} disciplines/topics.\n'
        for authorID, data in self.getAuthors():
            s += f'   Author {authorID} primary disciplines: {self.network.getAuthorDiscipline(authorID)}\n'
            for topicID, papers in data.items():
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
        allAuthors = self.getAuthors()
        while len(allAuthors) > 0:
            author = random.choice(allAuthors)
            allAuthors.remove(author)
            if len(author[1].keys()) > 1:
                break
            author = None

        # select two random disciplines from author
        if not author:
            return None
        allTopics = list(author[1].keys())
        top1 = random.choice(allTopics)
        allTopics.remove(top1)
        top2 = random.choice(allTopics)


        # print(f'Random author {author} with Topic {top1} with authors {self.network.getAuthorswithTopic(top1)}, Topic {top2} with authors {self.network.getAuthorswithTopic(top2)}')

        return self.network.getAuthorswithTopic(top1), self.network.getAuthorswithTopic(top2)

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
                self.network.addAuthor(self.newAuthor)
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

            # merge random discipline with prob pm
            if random.random() < self.probMerge:
                disciplines = self.randomNeighboringCommunities()
                if disciplines:
                    self.network.mergeCommunities(com1=disciplines[0], com2=disciplines[1])

        self.initialPaper += timeSteps
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