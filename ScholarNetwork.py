import networkx as nx
from igraph import Graph as modularityGraph
import random

'''
Inherited Graph class from networkx with methods used for scholar evolution
Definitions:
    Discipline: defines the top topic of the author, i.e. the topic with the most papers
'''
class Graph(nx.Graph):

    def getAuthorDiscipline(self, authorID):
        '''
        Function returns a list containing the discipline(s) of the author
        For each author, the topic that contains the most papers would be their assigned discipline
            If there is a tie, then the function returns all discipline IDs
        '''
        maxVal = 0
        disciplines = []
        for top, papers in self.nodes[authorID]["data"].items():
            numPapers = len(papers)
            if numPapers == maxVal:
                disciplines.append(top)
            elif numPapers > maxVal:
                maxVal = numPapers
                disciplines = [top]

        return disciplines

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

    def getDisciplineAuthors(self, topicID):
        '''
        Returns a list of authors who would be in the discipline of the topicID
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
            
            # determine if in specific community
            if topicID == max(authorTopics, key=authorTopics.get):
                communityAuthors.append(auth)

        return communityAuthors

    def splitCommunity(self, authors, numClusters=2):
        '''
        Function will take the list of authors in the community, numClusters is how many clusters to split into
            It will then test if it should split the community or not
        Returns True if split community, False otherwise while updating network
        '''
        # split into two communities
        subGraph = self.subgraph(authors)
        newGraph = modularityGraph.from_networkx(subGraph)

        # create subgraph and split
        clusters = newGraph.community_leading_eigenvector(clusters=numClusters)

        # compare unweighted modularity of new communities to the initial, return if there should not be change in community structure
        if newGraph.modularity(set(subGraph.nodes())) > clusters.modularity or len(clusters) != 2:
            return False

        # update the newComm number
        # must know all the groups and community names and pick different ones
        newComm = max(dict(network.nodes.data('label')).values()) + 1
        # choose which cluster is new one, based off of community size
        index = 1 if len(clusters[1]) < len(clusters[0]) else 0
        for node in clusters[index]:
            network.update(nodes=[(node, {"label": newComm})])

        return True