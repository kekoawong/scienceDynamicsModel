import networkx as nx
import random
from statistics import mode

'''
Inherited Graph class from networkx with methods used for scholar evolution
'''
class Graph(nx.Graph):

    def determinePaperTopic(self, authors):
        '''
        Returns the main topicID, looping through the author data
        '''
        topics = {}
        for author in authors:
            print(self.nodes[author]["data"])
            for top, papers in self.nodes[author]["data"].items():
                if top not in topics:
                    topics[top] = 0
                topics[top] += len(papers)

        # returns the topic with the most combined papers from all the authors
        return max(topics, key=topics.get)
    
    def biasedRandomWalk(self, authors, probStop):
        '''
        Recursive function that takes the current list of authors and probStop as input
        Returns paper tuple with (topicID, [authors])
        '''

        currAuthorID = authors[-1]
        newNeighbors = set(self.neighbors(currAuthorID)).difference(set(authors))

        # base condition: stop at node if probStop hit or there are no new neighbors to traverse
        if random.random() < probStop or len(newNeighbors) == 0:
            topic = self.determinePaperTopic(authors)
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
        return self.biasedRandomWalk(authors, probStop)