class Topic:
    '''
    Class defines the papers and their corresponding methods
    '''
    def __init__(self, id, papers=[], discAuthors=[]):

        self.id = id
        self.papers = list(set(papers))

        # list of authors who count topic as one of their main disciplines
        self.disciplineAuthors = list(set(discAuthors))

    def getPapers(self):
        return self.papers
    
    def getNumPapers(self):
        return len(self.papers)

    def getAuthors(self):
        return self.disciplineAuthors

    def getNumDiscAuthors(self):
        return len(self.disciplineAuthors)

    def addPaper(self, paperID):
        if paperID not in self.papers:
            self.papers.append(paperID)

    def addAuthorToDiscipline(self, authorClass):
        if authorClass not in self.disciplineAuthors:
            self.disciplineAuthors.append(authorClass)

    def removeAuthorFromDiscipline(self, authID):
        self.disciplineAuthors.remove(authID)

    def removePaper(self, paperID):
        self.papers.remove(paperID)

    def __repr__(self):
        # return f'{{"id": {self.id}\n, "authors": {self.disciplineAuthors}\n, "papers": {self.papers}\n}}'
        return f'Topic {self.id} has {self.getNumPapers()} papers and {self.getNumDiscAuthors()} authors\n'
    