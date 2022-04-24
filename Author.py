

class Author:
    '''
    Class will have the methods to
    '''
    def __init__(self):
        pass

    def getAuthorDiscipline(self, authorID):
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