class Type:
    '''
    Class defined the type of the author, used to determine the amount of credit that they get for papers
    '''

    def __init__(self, id, discAuthors=[]):

        self.id = id
        
        # authors with the type
        self.authors = list(set(discAuthors))
        
        # credit
        # TODO: Need some sort of credit function that determines how successful this discipline is
        self.totalCredit = 0 # will represent how much accumulated credit for the whole type

    def getAuthors(self):
        return self.authors

    def getTotalCredit(self):
        return self.totalCredit

    def addAuthor(self, authID):
        if authID not in self.authors:
            self.authors.append(authID)

    def rule(self):
        '''
        Defines the rule for collaboration between different types
        '''
        return