import pandas as pd

class Author:
    '''
    Class defines the author in a given network
    '''
    def __init__(self, id):

        # identification
        self.id = id
        self.name = 'Something'

        # data
        self.allTopics = []
        self.disciplines = []
        self.numPapers = 0

    def getAuthorPapers(self):
        '''
        Returns a list of all author papers
        '''
        allPapers = set()
        for top, papers in self.nodes[authID]["data"].items():
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
        for top, papers in self.nodes[authorID]["data"].items():
            numPapers = len(papers)
            if numPapers == maxVal:
                disciplines.append(top)
            elif numPapers > maxVal:
                maxVal = numPapers
                disciplines = [top]

        return disciplines

    '''Print Methods'''
    def getAuthorPapersStr(self):
        formattedData = [[x, ','.join(map(str, y))] for x, y in self.nodes[authorID]["data"].items()]
        dfTopics = pd.DataFrame(data=formattedData, columns=["Topic", "Papers"])
        return dfTopics.to_string(index=False)

    def printAuthor(self):
        '''Function will print the data associated with the author'''
        # print papers
        print(self.getAuthorPapersStr(authorID))

        # print neighbors
        formattedData = [[x, self.get_edge_data(authorID, x)["weight"]] for x in self.neighbors(authorID)]
        dfNeighbors = pd.DataFrame(data=formattedData, columns=["Neighbor", "Weight"])
        print(dfNeighbors.to_string(index=False))

    def getAuthorDiscipline(self):
        '''
        Function returns a list containing the discipline(s) of the author
        For each author, the topic that contains the most papers would be their assigned discipline
            If there is a tie, then the function returns all discipline IDs
        '''
        maxVal = 0
        disciplines = []
        for top, papers in self.nodes[authorID]["data"].items():
            numPapers = len(papers)
            if numPapers == maxVal:
                disciplines.append(top)
            elif numPapers > maxVal:
                maxVal = numPapers
                disciplines = [top]

        return disciplines

    def updateAuthorPapers(self, authors, topics, paperID):
        '''
        Function will update the topics and papers of all authors
        '''
        for author in authors:
            for topicID in topics:
                if topicID not in self.nodes[author]["data"]:
                    self.nodes[author]["data"][topicID] = []
                self.nodes[author]["data"][topicID].append(paperID)