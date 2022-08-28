class Type:
    '''
    Class defined the type of the author, used to determine the amount of credit that they get for papers
    '''

    def __init__(self, id, name, discAuthors=[]):

        self.id = id
        self.name = name

        # authors with the type
        self.authors = list(set(discAuthors))
        
        # credit
        self.scalar = id + 1
        # TODO: Need some sort of credit function that determines how successful this discipline is
        self.totalCredit = 0 # will represent how much accumulated credit for the whole type

    def getAuthors(self):
        return self.authors

    def getTotalCredit(self):
        return self.totalCredit

    def addAuthor(self, authID):
        if authID not in self.authors:
            self.authors.append(authID)

    def getCreditAmount(self, baseCredit):
        '''
        Defines the rule for collaboration between different types
        '''
        self.totalCredit += baseCredit * self.scalar
        return baseCredit * self.scalar