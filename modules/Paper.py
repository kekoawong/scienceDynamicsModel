

class Paper:
    '''
    Class defines the papers and their corresponding methods
    '''
    def __init__(self, id, topics=[], authors=[]):

        self.id = id
        self.topics = list(set(topics))
        self.authors = list(set(authors))

    def addAuthor(self, authID):
        if authID not in self.authors:
            self.authors.append(authID)

    def addTopics(self, topicID):
        if topicID not in self.topics:
            self.topics.append(topicID)

