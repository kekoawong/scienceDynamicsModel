from cProfile import label
from modules.Type import Type
from .ScholarNetwork import Graph
from .Paper import Paper
from .Topic import Topic
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import math
import random
import pickle
import sys

class Evolution:

    def __init__(self, Pn=0.6, Pw=0.3, Pd=0.5, maxAge=1000):
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
        self.types = {}

        '''Inital Parameters'''
        self.newAuthor = 1
        self.newPaper = 1
        self.maxAge = maxAge

        '''Initialize network with one author, one paper, and one topic'''
        initialTopic = 1
        # add author, adding it to type
        self.network.addAuthor(self.newAuthor, birthIteration=self.newAuthor, initialData={initialTopic: [self.newPaper]})
        self.addAuthortoType(self.newAuthor)
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

    def getQuantDistr(self, initialDescr=None):
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

        Inputs:
            initalDescr: if averaging over many runs, input previous initialDescr to get the histogram of all values
        '''
        descr = initialDescr
        if not initialDescr:
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
            self.updateDisciplineAuthors(authClass, disciplines)

        # get discipline distributions
        print('topics')
        print(self.topics.values())
        for topic in self.topics.values():
            descr['Pd'].append(topic.getNumPapers())
            descr['Ad'].append(topic.getNumDiscAuthors())
        
        return descr

    def getDegreeDistribution(self):
        return sorted((d for n, d in self.network.degree()), reverse=True)

    def getCreditDistribution(self):
        '''
        Returns a dict of { typeKey: [authCredit, authCredit]}
        '''
        creditDistr = {}
        for typeClass in self.types.values():
            creditDistr[typeClass.name] = []
            for authID in typeClass.getAuthors():
                creditDistr[typeClass.name].append(self.network.getAuthorClass(authID).getCredit())
        return creditDistr

    def getDisciplineTypeDistribution(self):
        '''
            Will return the distribution of types in the disciplines
            Will return 2 object: the credit distribution and the type distribution
            { disiplineKey: [authType, authType] } 
            and 
            { disiplineKey: [authCredit, authCredit] } 
            
        '''
        types = {}
        credits = {}
        for id, discipline in self.topics.items():
            types[id] = []
            credits[id] = []
            for authorClass in discipline.getAuthors():
                types[id].append(authorClass.getType().name)
                credits[id].append(authorClass.getCredit())
        print(f'Num topics: {len(self.topics.keys())}')
        return types, credits

    def updateDisciplineAuthors(self, authorClass, disciplines):
        for discID in disciplines:
            if discID in self.topics:
                self.topics[discID].addAuthorToDiscipline(authorClass)

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
                    # update topics data structure
                    for oldTopic in paperClass.getTopics():
                        if paperID in self.topics[oldTopic].getPapers():
                            self.topics[oldTopic].removePaper(paperID)
                    # update papers data structure
                    paperClass.clearTopics()
                    self.topics[newTopic].addPaper(paperID)
                    paperClass.addTopic(newTopic)

                # update authors in network with papers
                self.network.updatePaperInNetwork(paperID, (paperClass.getTopics(), paperClass.getAuthors()))

    def randomNeighboringCommunities(self):
        '''
        Function used to get two random neighboring communities for merge event
        Returns a tuple of the two communities or None if network not big enough
            ([authorIDs in community 1], [authorIDs in community 2])
        '''

        # choose random author with at least two papers in different topics. 
        allAuthors = self.getAuthorIDs()
        while len(allAuthors) > 0:
            authID = random.choice(allAuthors)
            allAuthors.remove(authID)
            authData = self.network.getAuthorData(authID)
            if len(authData.keys()) > 1:
                break
            authID = None

        # select two random topics from author
        if not authID:
            return None
        allTopics = list(authData.keys())
        top1 = random.choice(allTopics)
        allTopics.remove(top1)
        top2 = random.choice(allTopics)


        # print(f'Random author {authID} with Topic {top1} with authors {self.network.getAuthorswithTopic(top1)}, Topic {top2} with authors {self.network.getAuthorswithTopic(top2)}')

        return self.network.getAuthorswithTopic(top1), self.network.getAuthorswithTopic(top2), top1, top2

    def addAuthortoType(self, authID):
        # define only two types for now
        typeID = 0 if random.random() < 0.5 else 1
        typeName = 'Marginalized' if typeID == 0 else 'Dominant'
        if typeID not in self.types:
            self.types[typeID] = Type(typeID, typeName)
        self.types[typeID].addAuthor(authID)
        self.network.getAuthorClass(authID).setType(self.types[typeID])

        return typeID

    def updateMergedCommunities(self, d1, d2):
        # add papers to new discipline without getting rid of old disciplines
        newTopic = max(self.topics.keys()) + 1
        if d1 in self.topics:
            for paperID in self.topics[d1].getPapers():
                paperClass = self.papers[paperID]
                if d1 in paperClass.getTopics():
                    paperClass.getTopics().remove(d1)
                paperClass.getTopics().append(newTopic)
                self.network.updatePaperInNetwork(paperID, (paperClass.getTopics(), paperClass.getAuthors()))
        
        if d2 in self.topics:
            for paperID in self.topics[d2].getPapers():
                paperClass = self.papers[paperID]
                if d2 in paperClass.getTopics():
                    paperClass.getTopics().remove(d2)
                paperClass.getTopics().append(newTopic)
                self.network.updatePaperInNetwork(paperID, (paperClass.getTopics(), paperClass.getAuthors()))

        return

    def evolve(self, modelType= 0 | 1 | 2 | 3, newPapers=None, newAuthors=None):
        '''
        Function will continue evolution for the inputted timesteps
        Inputs:
            newPapers: stopping point for amount of new papers
            newAuthors: stopping point for amount of new authors
        NOTE: input either newPapers or newAuthors stopping point, but not both

        modelType:
        0: base model, without any credit accumulation
        1: base model, with credit accumulation
        2: linking probabilities determined by reputation of author
        3: Matthew Effect, with linking probabilities and paper credit is a function of the author's reputation
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
                self.network.addAuthor(self.newAuthor, birthIteration=self.newPaper, initialData={})
                self.network.add_edge(self.newAuthor, authors[1], weight=1, width=1)
                # NOTE: add author to type, must be edited out for original model
                self.addAuthortoType(self.newAuthor)
                # increment new authorID
                self.newAuthor += 1

            # Add new paper, calling function
            if (modelType == 0):
                paperTopics, paperAuthors = self.network.biasedRandomWalk(authors, self.probStop, self.newPaper, self.maxAge, includeCredit=False)
            elif (modelType == 1):
                paperTopics, paperAuthors = self.network.biasedRandomWalk(authors, self.probStop, self.newPaper, self.maxAge, includeCredit=True)
            elif (modelType == 2):
                paperTopics, paperAuthors = self.network.creditWalk(authors, self.probStop, self.newPaper, maxAge=self.maxAge, useReputation=False)
            elif (modelType == 3):
                paperTopics, paperAuthors = self.network.creditWalk(authors, self.probStop, self.newPaper, maxAge=self.maxAge, useReputation=True)
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
                disciplinesObj = self.randomNeighboringCommunities()
                if disciplinesObj:
                    newCom = self.network.mergeCommunities(com1=disciplinesObj[0], com2=disciplinesObj[1])
                    if newCom:
                        # self.updateNewCommunity(newCom)
                        self.updateMergedCommunities(disciplinesObj[2], disciplinesObj[3])

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
    def plotCreditPaperTypeDistrib(self, saveToFile=None):
        '''
        Will Plot the Average credit per paper, separating by type
            Will create data structure for plotting like the following:
            {PaperID:
                {Type1: Average credit added, Type2: Average Credit Added}
            }
        '''
        paperCreditDistrib = {}
        types = {}
        for authID in self.network.getAuthorIDs():
            authorClass = self.network.getAuthorClass(authID)
            for paperID, creditAdded in authorClass.getPaperClassDict().items():
                authorType = authorClass.getType().name
                # add paper to dict if not there
                if paperID not in paperCreditDistrib:
                    paperCreditDistrib[paperID] = {}
                
                # add type to distribution if not there
                if authorType not in paperCreditDistrib[paperID]:
                    paperCreditDistrib[paperID][authorType] = creditAdded
                    types[authorType] = True
                
                # average the value in the paper credit dict
                paperCreditDistrib[paperID][authorType] = ( paperCreditDistrib[paperID][authorType] + creditAdded ) / 2

        # create scatter plot
        fig = plt.figure(figsize=(9, 7))
        axis = fig.add_subplot()

        # Add scatters for each type
        avgVals = list(paperCreditDistrib.values())
        avgVals.sort(key=lambda val: val.get(1, 0))
        for t in types.keys():
            x = [index for index, avgCredit in enumerate(avgVals) if t in avgCredit]
            y = [avgCredit[t] for avgCredit in avgVals if t in avgCredit]
            axis.scatter(x, y, label=str(t))
        
        # styling
        axis.set_ylabel(f'Average Credit Per Paper', fontweight='bold')
        axis.set_xlabel(f'Papers', fontweight='bold')
        fig.suptitle(f'''Credit Distribution by Paper''')
        plt.legend([str(x) for x in types.keys()], title="Type")
        fig.tight_layout()

        if saveToFile:
            fig.savefig(saveToFile)
            print(f'Saved to {saveToFile} successfully!')

        return fig, axis

    def plotDistibution(self, distribution, label='', ylogBase=10, xlogBase=10, ylim=10**-6, xlim=10**4, saveToFile=None):

        largestVal = max(distribution)
        maxVal = 10 if not largestVal else largestVal
        # declare figure and axis
        fig = plt.figure(figsize=(9, 7))
        axis = fig.add_subplot()

        # calculate bin values
        numDistribution = len(distribution)
        numBins = min(20, numDistribution) + 1
        logBinEdges = np.logspace(math.log(1, xlogBase), math.log(maxVal, xlogBase), numBins)
        binVals, binEdges = np.histogram(distribution, bins=logBinEdges, density=True)

        # convert to scatter
        xVals = [0.5 * (binEdges[i] + binEdges[i+1]) for i in range(len(binVals))]
        axis.scatter(xVals, binVals)

        # obtain m (slope) and b(intercept) of linear regression line
        m, b = np.polyfit(xVals, binVals, 1)
        # use red as color for regression line
        axis.plot([x for x in xVals], [m*x+b for x in xVals], color='red', label=f'y={round(m)}x + {round(b)}')

        # obtain regression line of degree 2
        a, m, b = np.polyfit(xVals, binVals, 2)
        # use red as color for regression line
        sortedX = sorted(xVals)
        axis.plot(sortedX, [a*(x**2) + m*x + b for x in sortedX], color='green', label=f'y={round(a)}x^2 + {round(m)}x + {round(b)}')

        axis.legend()

        # styling
        axis.set_ylabel(f'Density of {label}', fontweight='bold')
        axis.set_xlabel(f'{label}', fontweight='bold')

        # scale axis
        if ylogBase:
            axis.set_yscale('log', base=ylogBase) 
        if xlogBase:
            axis.set_xscale('log', base=xlogBase)

        # set limits
        axis.set_ylim(ylim, 1)
        axis.set_xlim(1, xlim)

        # figure styling
        fig.suptitle(f'''Network {label} distribution.''')
        fig.tight_layout()

        if saveToFile:
            fig.savefig(saveToFile)
            print(f'Saved to {saveToFile} successfully!')
        
        return fig, axis

    def plotDegreeDistr(self, degreeDistrib=None, label='Degree', ylogBase=10, xlogBase=10, ylim=10**-6, xlim=10**4, saveToFile=None):
        distrib = self.getDegreeDistribution() if not degreeDistrib else degreeDistrib
        return self.plotDistibution(distrib, label=label, ylogBase=ylogBase, xlogBase=xlogBase, ylim=ylim, xlim=xlim, saveToFile=saveToFile), distrib

    def plotCreditDistr(self, distr=None, ylogBase=1, xlogBase=1, saveToFile=None):
        # get data
        distribs = self.getCreditDistribution() if not distr else distr
        # xVals = distribs.values() if not distr else distr[0]
        # yVals = [str(x) for x in distribs.keys()] if not distr else distr[1]

        # declare figure and axis
        fig = plt.figure(figsize=(9, 7))
        axis = fig.add_subplot()

        axis.hist(distribs.values(), label=[str(x) for x in distribs.keys()], color=["blue", "orange"], density=True, bins='sqrt')

        # styling
        axis.set_ylabel(f'Density of credit', fontweight='bold')
        axis.set_xlabel(f'Author Credit', fontweight='bold')
        fig.suptitle(f'''Network credit distribution per type''')
        fig.tight_layout()
        plt.legend([str(x) for x in distribs.keys()], title="Type")

        if saveToFile:
            fig.savefig(saveToFile)
            print(f'Saved to {saveToFile} successfully!')
        return fig, axis, distribs

    def plotTypeDisciplineDistrib(self, distr=None, ylogBase=1, xlogBase=1, saveToFile=None):
        # get data from getDisciplineTypeDistribution method
        typeDistrib, creditDistrib = self.getDisciplineTypeDistribution() if not distr else distr

        # change orientation of distributions
        types = {}
        for displineID, distrib in typeDistrib.items():
            for typeID in distrib:
                if typeID not in types:
                    types[typeID] = []
                types[typeID].append(displineID)

        # declare figure and axis
        fig, (ax1, ax2) = plt.subplots(figsize=(9, 7), nrows=2, ncols=1)

        ax1.hist(types.values(), label=[str(x) for x in types.keys()], density=False, bins=len(typeDistrib.keys()), stacked=True)
        ax2.bar(creditDistrib.keys(), [sum(x)/len(x) if len(x) else 0 for x in creditDistrib.values()], label='Average Credit per Author')

        # styling
        ax1.set_ylabel(f'Number Authors', fontweight='bold')
        ax1.set_xlabel(f'Discipline', fontweight='bold')
        ax1.set_title(f'''Network Type Distribution throughout Disciplines''')
        ax1.legend([str(x) for x in types.keys()], title="Type")

        ax2.set_ylabel(f'Average Credit per Author', fontweight='bold')
        ax2.set_xlabel(f'Discipline', fontweight='bold')
        ax2.set_title(f'''Credit Distribution throughout Disciplines''')
        fig.tight_layout()

        if saveToFile:
            fig.savefig(saveToFile)
            print(f'Saved to {saveToFile} successfully!')
        return fig, (ax1, ax2)

    def plotDescriptorsDistr(self, saveToFile=None, ylogBase=10, xlogBase=10, data=None, numAuthors='NA', numPapers='NA', numTopics='NA', networkName=''):
        '''
        Method will take the descriptors dictionary returned from getQuantDescriptors method and plot subplots
        Inputs:
            saveToFile: string of a filename to save the plot to
            logBase: if you want to plot on a log scale on the yaxis, input the desired log base
            data: data to plot, defaults to the self.getQuantDistr() dict of the current Evolution class
        '''
        fig = plt.figure(figsize=(9, 7))
        # make plot with 3 rows, 2 columns
        axs = fig.subplots(3,2)

        # loop through and make subplots
        descr = data
        if not descr:
            descr = self.getQuantDistr()

        # turn dict into list
        descr = list(descr.items())

        # print(descr)
        for row in axs:
            for axis in row:
                label, labelData = descr.pop(0)

                # calculate bin values
                numBins = min(20, len(labelData)) + 1
                logBinEdges = np.logspace(math.log(1, xlogBase), math.log(max(labelData), xlogBase), numBins)
                binVals, binEdges = np.histogram(labelData, bins=logBinEdges, density=True)

                # create scatter
                xVals = [0.5 * (binEdges[i] + binEdges[i+1]) for i in range(len(binVals))]
                axis.scatter(xVals, binVals)
                axis.set_ylabel(f'Density of {label}', fontweight='bold')
                axis.set_xlabel(f'{label}', fontweight='bold')

                # scale axis
                if ylogBase:
                    axis.set_yscale('log', base=ylogBase) 
                if xlogBase:
                    axis.set_xscale('log', base=xlogBase)

                # set limits
                axis.set_ylim(10**-6, 1)
                axis.set_xlim(1, 10**4)

                # testing for pd
                # if label == 'Pd':
                #     print('Metrics for pd:')
                    
                #     print(labelData)
                #     print(f'Num disciplines in graph: {len(self.topics.keys())}')
                #     print(self.topics)

        # figure styling
        fig.suptitle(f'''{networkName} Network with {numAuthors} total authors, {numPapers} total papers, and {numTopics} total topics.
                    ''')
        fig.tight_layout()

        if saveToFile:
            fig.savefig(saveToFile)
            print(f'Saved to {saveToFile} successfully!')
        
        return fig, axs

    def plotCreditTypeDistribution(self, saveToFile=None, distrib=None):
        '''
        Plot will have the average credit per author on Y-Axis, % type 0 in discipline. Each data point will be a discipline
        distrib = [xVals, yVals]
        '''
        allDisciplines = {}
        for topic in self.topics.keys():
            # initialized data
            for authID in self.network.getDisciplineAuthors(topic):
                if topic not in allDisciplines:
                    allDisciplines[topic] = {
                        'credit': 0,
                        'numAuthors': 0,
                        'Marginalized': 0,
                        'Dominant': 0,
                    }
                authClass = self.network.getAuthorClass(authID)
                allDisciplines[topic]['credit'] += authClass.getCredit()
                allDisciplines[topic]['numAuthors'] += 1
                allDisciplines[topic][authClass.getType().name] += 1

        # add plot
        fig = plt.figure(figsize=(9, 7))
        axis = fig.add_subplot()

        typeName = 'Marginalized'
        xVals = [x[typeName]/x['numAuthors'] for x in allDisciplines.values()] if not distrib else distrib[0]
        yVals = [x['credit']/x['numAuthors'] for x in allDisciplines.values()] if not distrib else distrib[1]
        disciplineSizes = [x["numAuthors"] for x in allDisciplines.values()] if not distrib else distrib[2]
        axis.scatter(xVals, yVals)

        # sns.regplot(x=xVals, y=yVals, scatter=True, order=2)

        # styling
        axis.set_ylabel(f'Average credit per author in discipline.', fontweight='bold')
        axis.set_xlabel(f'% type {typeName} in discipline.', fontweight='bold')
        axis.set_title(f'''Credit and Type Distribution throughout Disciplines''')
        fig.tight_layout()

        # obtain m (slope) and b(intercept) of linear regression line
        m, b = np.polyfit(xVals, yVals, 1)
        # use red as color for regression line
        axis.plot(xVals, [m*x+b for x in xVals], color='red', label=f'y={round(m)}x + {round(b)}')

        # obtain regression line of degree 2
        a, m, b = np.polyfit(xVals, yVals, 2)
        # use red as color for regression line
        sortedX = sorted(xVals)
        axis.plot(sortedX, [a*(x**2) + m*x + b for x in sortedX], color='green', label=f'y={round(a)}x^2 + {round(m)}x + {round(b)}')

        axis.legend()
        
        if saveToFile:
            fig.savefig(saveToFile)
            print(f'Saved to {saveToFile} successfully!')

        return fig, axis, [xVals, yVals, disciplineSizes]

    '''Saving Methods'''
    def saveEvolutionWithPickle(self, fileName='evolution.env'):
        with open(fileName, 'wb') as outfile:
            pickle.dump(self, outfile)
        print(f'Saved to {fileName} successfully!')

    def saveNetworkWithPickle(self, fileName='evolutionNetwork.net'):
        self.network.saveNetworkWithPickle(fileName=fileName)