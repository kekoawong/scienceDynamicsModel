

class Paper:
    '''
    Class defines the papers and their corresponding methods
    '''
    def __init__(self, id, topics=[], authors=[]):

        self.id = id
        self.topics = list(set(topics))
        self.authors = list(set(authors))

    '''GET Methods'''
    def getID(self):
        return self.id
    
    def getTopics(self):
        return self.topics

    def getAuthors(self):
        return self.authors

    def clearTopics(self):
        self.topics = []

    def addTopic(self, topicID):
        if topicID not in self.topics:
            self.topics.append(topicID)

    def addAuthor(self, authID):
        if authID not in self.authors:
            self.authors.append(authID)

    def __repr__(self):
        topics = ','.join(map(str, self.topics))
        authors = ','.join(map(str, self.authors))
        print(f'Paper {self.id} topics: {topics}')
        print(f'Paper {self.id} authors: {authors}')

