class Type:
    '''
    Class defined the type of the author, used to determine the amount of credit that they get for papers
    '''

    def __init__(self, id, authors=[]):

        self.id = id
        
        # authors with the type
        self.authors = authors
        
        # credit
        # TODO: Need some sort of credit function that determines how successful this discipline is
        self.totalCredit = 0 # will represent how much accumulated credit for the whole type

    def getTypeAuthors(self):
        return self.authors

    def getTotalCredit(self):
        return self.totalCredit

    def addAuthor(self, authID):
        self.authors.append(authID)