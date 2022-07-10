class Topic:
    '''
    Class defines the papers and their corresponding methods
    '''
    def __init__(self, id, papers=[], discAuthors=[]):

        self.id = id
        self.papers = list(set(papers))

        # list of authors who count topic as one of their main disciplines
        self.disciplineAuthors = list(set(discAuthors))

    def getNumPapers(self):
        return len(self.papers)

    def getAuthors(self):
        return self.disciplineAuthors

    def getNumDiscAuthors(self):
        return len(self.disciplineAuthors)

    def addPaper(self, paperID):
        if paperID not in self.papers:
            self.papers.append(paperID)

    def addAuthorToDiscipline(self, authID):
        if authID not in self.disciplineAuthors:
            self.disciplineAuthors.append(authID)

    def removeAuthorFromDiscipline(self, authID):
        self.disciplineAuthors.remove(authID)

    def removePaper(self, paperID):
        self.papers.remove(paperID)

    def __repr__(self):
        print('Not implemented')
    