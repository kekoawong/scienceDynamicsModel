import networkx as nx
from igraph import Graph as modularityGraph
import random
import pandas as pd
import matplotlib.pyplot as plt
from sympy import false

'''
Inherited Graph class from networkx with methods used for scholar evolution
Definitions:
    Discipline: defines the top topic of the author, i.e. the topic with the most papers
'''
class Graph(nx.Graph):

    '''Access Methods'''
    def getAuthors(self):
        return self.nodes.data("data")

    '''Print Methods'''
    def printAuthor(self, authorID):
        '''Function will print the data associated with the author'''
        # print papers
        print(self.nodes[authorID]["data"])
        formattedData = [[x, ','.join(map(str, y))] for x, y in self.nodes[authorID]["data"].items()]
        dfTopics = pd.DataFrame(data=formattedData, columns=["Topic", "Papers"])
        print(dfTopics.to_string(index=False))

        # print neighbors
        formattedData = [[x, self.get_edge_data(authorID, x)["weight"]] for x in self.neighbors(authorID)]
        dfNeighbors = pd.DataFrame(data=formattedData, columns=["Neighbor", "Weight"])
        print(dfNeighbors.to_string(index=False))

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

    def updateAuthorPapers(self, authors, topics, paperID):
        '''
        Function will update the topics and papers of all authors
        '''
        for author in authors:
            for topicID in topics:
                if topicID not in self.nodes[author]["data"]:
                    self.nodes[author]["data"][topicID] = []
                self.nodes[author]["data"][topicID].append(paperID)

    def determinePaperTopic(self, authors):
        '''
        Returns the list, containing the paper topic(s)
        Function will loop through all the authors, getting their disciplines
            If this is a tie, then the paper is added to both disciplines
                This is not a strict rule and could be modified
        '''

        topics = {}
        for author in authors:
            for top in self.getAuthorDiscipline(author):
                if top not in topics:
                    topics[top] = 0
                topics[top] += 1

        paperTopics = []
        maxVal = 0
        for id, num in topics.items():
            if num == maxVal:
                paperTopics.append(id)
            elif num > maxVal:
                maxVal = num
                paperTopics = [id]

        # returns the topic that represents the disciplines that most authors are in
        return paperTopics
    
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
            topics = self.determinePaperTopic(authors)
            # update the papers for all authors
            self.updateAuthorPapers(authors, topics, newPaperID)

            return topics, authors
        
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
        for auth in self.nodes:
            if topicID in self.getAuthorDiscipline(auth):
                communityAuthors.append(auth)

        return communityAuthors

    def splitCommunity(self, authors, numClusters=2):
        '''
        Function will take the list of authors in the community, numClusters is how many clusters to split into
            It will then test if it should split the community or not
        Arguments:
            authors: list of authors in the whole community
            numTopics: number of total topics so far
            numClusters: number of clusters to testing splitting community into
        Returns a list of authors in the new community if community is split, False otherwise
        '''
        # split into two communities
        subGraph = self.subgraph(authors)
        newGraph = modularityGraph.from_networkx(subGraph)

        # create subgraph and split
        clusters = newGraph.community_leading_eigenvector(clusters=numClusters)

        # compare unweighted modularity of new communities to the initial, return if there should not be change in community structure
        if newGraph.modularity(set(subGraph.nodes())) > clusters.modularity or len(clusters) != 2:
            return False

        # choose which cluster is new one, based off of community size
        index = 1 if len(clusters[1]) < len(clusters[0]) else 0

        return clusters[index]


    def updatePaperInNetwork(self, paperID, paperData):
        '''
        Function will update the author network with the paper
        PaperID: int
        paperData: ([topics], [authors])
        '''
        paperTopics = paperData[0]
        paperAuthors = paperData[1]

        for auth, authData in self.nodes.data("data"):
            # can just update the authors of the paper
            if auth in paperAuthors:
                # remove from old topics
                for topID, papers in authData.items():
                    if paperID in papers:
                        papers.remove(paperID)

                # add paper to new topics in author data structure
                for topID in paperTopics:
                    if topID not in authData:
                        authData[topID] = []
                    authData[topID].append(paperID)

                # Remove topics from author that are empty
                authData = {k: papers for k, papers in authData.items() if len(papers) > 0}

    def genGraphFeatures(self):
        '''
        Will return the dictionary for node labels and list of colors for plotting
        Used for labels and colors in networkx graph drawing: https://networkx.org/documentation/latest/reference/generated/networkx.drawing.nx_pylab.draw_networkx.html?highlight=draw_networkx
        '''
        labels = {}
        colors = []
        for nodeID, data in self.nodes.data("data"):
            disciplines = self.getAuthorDiscipline(nodeID)
            labels[nodeID] = str(disciplines)
            colors.append(4 * disciplines[0])
        return labels, colors
    
    def plotNetwork(self):
        nodeLabels, nodeColors = self.genGraphFeatures()
        # spring layout
        pos = nx.spring_layout(self, seed=3068)  # Seed layout for reproducibility
        nx.draw(self, pos=pos, with_labels=True, labels=nodeLabels, node_color=nodeColors)
        plt.show()

        # shell layout
        pos = nx.shell_layout(self)  # Seed layout for reproducibility
        nx.draw(self, pos=pos, with_labels=True, labels=nodeLabels, node_color=nodeColors)
        plt.show()