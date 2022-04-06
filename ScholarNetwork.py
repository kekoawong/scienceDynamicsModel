import networkx as nx
import random

'''
Inherited Graph class from networkx with methods used for scholar evolution
'''
class Graph(nx.Graph):

    def updateAuthorPapers(self, authors, topicID, paperID):
        '''
        Function will update the topics and papers of all authors
        '''
        for author in authors:
            if topicID not in self.nodes[author]["data"]:
                self.nodes[author]["data"][topicID] = []
            self.nodes[author]["data"][topicID].append(paperID)

    def determinePaperTopic(self, authors):
        '''
        Returns the main topicID
        Function will loop through all the authors, determining which field is most prevelant
        '''
        topics = {}
        for author in authors:
            for top, papers in self.nodes[author]["data"].items():
                if top not in topics:
                    topics[top] = 0
                topics[top] += len(papers)

        # returns the topic with the most combined papers from all the authors
        return max(topics, key=topics.get)
    
    def biasedRandomWalk(self, authors, probStop, newPaperID):
        '''
        Recursive function that takes the current list of authors and probStop as input
        Returns paper tuple with (topicID, [authors])
        '''

        currAuthorID = authors[-1]
        newNeighbors = set(self.neighbors(currAuthorID)).difference(set(authors))

        # base condition: stop at node if probStop hit or there are no new neighbors to traverse
        if random.random() < probStop or len(newNeighbors) == 0:
            # determine the paper topic
            topic = self.determinePaperTopic(authors)
            # update the papers for all authors
            self.updateAuthorPapers(authors, topic, newPaperID)

            return topic, authors
        
        # create list representing probabilities for the neighboring nodes of the current coauthor
        probs = []
        for neighbor in newNeighbors:
            nData = self.get_edge_data(currAuthorID, neighbor)
            probs.extend([neighbor] * nData["weight"])

        # Select next coauthor from neighbors probabilities list
        coauthorID = random.choice(probs)

        # update all edges of coauthors to this new author
        for author in authors:
            # if there is not an edge, create one
            if not self.has_edge(author, coauthorID) and author != coauthorID:
                self.add_edge(author, coauthorID, weight=0, width=1)
            
            newWeight = self.get_edge_data(author, coauthorID)["weight"] + 1
            self.update(edges=[ (author, coauthorID, {"weight": newWeight}) ])

        # add author to list and call function recursively
        authors.append(coauthorID)
        return self.biasedRandomWalk(authors, probStop, newPaperID)

    def getCommunityAuthors(self, topicID):
        '''
        Returns a list of authors who would be classified as a community
        A community is defined as follows: Every author who has a majority of one topic in their papers
        '''

        communityAuthors = []
        for auth, data in self.nodes.data('data'):

            # count the author papers
            authorTopics = {}
            for top, papers in data.items():
                if top not in authorTopics:
                    authorTopics[top] = 0
                authorTopics[top] += len(papers)
            
            # determine if specific community
            if topicID == max(authorTopics, key=authorTopics.get):
                communityAuthors.append(auth)

        return communityAuthors