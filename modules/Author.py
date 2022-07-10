import pandas as pd

class Author:
    '''
    Class defines the author in a given network
    '''
    def __init__(self, id, birthIteration, initialData={}):

        # identification
        self.id = id
        self.name = 'Something'

        # used to infer age
        self.birthIteration = birthIteration

        '''
        Main data collection, stored in the following format:
            {
                TopicID1: [PaperIDs],
                TopicID2: [PaperIDs],
            }
        '''
        self.collection = initialData

        # credit accumulation
        self.credit = 1
        self.type = None

        # measures
        self.numPapers = 0
        self.numTopics = 0

    def getData(self):
        return self.collection

    def getAge(self, currentIteration):
        return currentIteration - self.birthIteration

    def getType(self):
        return self.type

    def getID(self):
        return self.id

    def getCredit(self):
        return self.credit

    def getNumPapers(self):
        return self.numPapers

    def getNumTopics(self):
        return self.numTopics

    def getNumDisciplines(self):
        return len(self.getAuthorDiscipline())
    
    def getAuthorPapers(self):
        '''
        Returns a list of all author papers
        '''
        allPapers = set()
        for top, papers in self.collection.items():
            allPapers.update(papers)
        return list(allPapers)

    def getAuthorDiscipline(self):
        '''
        Function returns a list containing the discipline(s) of the author
        For each author, the topic that contains the most papers would be their assigned discipline
            If there is a tie, then the function returns all discipline IDs
        '''
        maxVal = 0
        disciplines = []
        for top, papers in self.collection.items():
            numPapers = len(papers)
            if numPapers == maxVal:
                disciplines.append(top)
            elif numPapers > maxVal:
                maxVal = numPapers
                disciplines = [top]
        return disciplines

    '''Print Methods'''
    def getAuthorPapersStr(self):
        formattedData = [[x, ','.join(map(str, y))] for x, y in self.collection.items()]
        dfTopics = pd.DataFrame(data=formattedData, columns=["Topic", "Papers"])
        return dfTopics.to_string(index=False)

    # def printAuthor(self):
    #     '''Function will print the data associated with the author'''
    #     # print papers
    #     print(self.getAuthorPapersStr())

    #     # print neighbors
    #     formattedData = [[x, self.get_edge_data(authorID, x)["weight"]] for x in self.neighbors(authorID)]
    #     dfNeighbors = pd.DataFrame(data=formattedData, columns=["Neighbor", "Weight"])
    #     print(dfNeighbors.to_string(index=False))

    def addCredit(self, creditAmount):
        self.credit += creditAmount

    def setType(self, type):
        self.type = type

    def insertPaper(self, paperID, topics):
        '''
        Function will insert a new paper into the author
        '''
        for topicID in topics:
            if topicID not in self.collection:
                self.collection[topicID] = []
            if paperID not in self.collection[topicID]:
                self.collection[topicID].append(paperID)
        # update measures
        self.numPapers += 1
        self.numTopics = len(self.collection.keys())

    def updateAuthor(self, paperID, paperTopics):
        '''
        Function will update an author when a paper's topics are changed
        '''
        # remove paper from old topics
        for topID, papers in self.collection.items():
            if paperID in papers:
                papers.remove(paperID)

        # add paper to new topics, subtract self.numPapers since paper exists
        self.numPapers -= 1
        self.insertPaper(paperID, paperTopics)
        
        # Remove topics from author that are empty
        self.collection = {k: papers for k, papers in self.collection.items() if len(papers) > 0}

        # update measure
        self.numTopics = len(self.collection.keys())

    def __repr__(self):
        print('Not implemented')