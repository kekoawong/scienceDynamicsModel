class Topic:
    '''
    Class defines the papers and their corresponding methods
    '''
    def __init__(self, id, papers=[]):

        self.id = id
        self.papers = list(set(papers))

    def addPaper(self, paperID):
        if paperID not in self.papers:
            self.papers.append(paperID)

    def removePaper(self, paperID):
        self.papers.remove(paperID)

    