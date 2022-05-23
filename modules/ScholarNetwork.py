import networkx as nx
from .Author import Author
from networkx.algorithms.community import modularity as nx_modularity
import community
from igraph import Graph as modularityGraph
import random
import pandas as pd
from pyvis.network import Network as ntvis
import matplotlib.pyplot as plt
from copy import deepcopy
import sys

'''
Inherited Graph class from networkx with methods used for scholar evolution
Definitions:
    Discipline: defines the top topic of the author, i.e. the topic with the most papers
'''
class Graph(nx.Graph):

    '''Access Methods'''
    def getNetworkData(self):
        return self.nodes.data("data")

    def getAuthorIDs(self): 
        return list(self.nodes)

    def getAuthorPapers(self, authID):
        '''
        Returns a list of all author papers
        '''
        return self.nodes[authID]["data"].getAuthorPapers()

    def getAuthorData(self, authID):
        return self.nodes[authID]["data"].getData()

    '''Add Author Method'''
    def addAuthor(self, authID, initialData={}):
        '''
        Will add the author with the authID to the network
        data is the initial data to declare the author with
        '''
        self.add_node(authID, data=Author(authID, initialData=initialData))

    '''Print Methods'''
    def printAuthor(self, authID):
        '''Function will print the data associated with the author'''
        # print papers
        print(self.nodes[authID]["data"].getAuthorPapersStr())

        # print neighbors
        formattedData = [[x, self.get_edge_data(authID, x)["weight"]] for x in self.neighbors(authID)]
        dfNeighbors = pd.DataFrame(data=formattedData, columns=["Neighbor", "Weight"])
        print(dfNeighbors.to_string(index=False))

    def getAuthorDiscipline(self, authID):
        '''
        Function returns a list containing the discipline(s) of the author
        For each author, the topic that contains the most papers would be their assigned discipline
            If there is a tie, then the function returns all discipline IDs
        '''
        return self.nodes[authID]["data"].getAuthorDiscipline()

    def updateAuthorPapers(self, authors, topics, paperID):
        '''
        Function will update the topics and papers of all authors
        '''
        for authID in authors:
            self.nodes[authID]["data"].insertPaper(paperID, topics)

    def determinePaperTopic(self, authors):
        '''
        Returns the list, containing the paper topic(s)
        Function will loop through all the authors, getting their disciplines
            If this is a tie, then the paper is added to both disciplines
                This is not a strict rule and could be modified
        '''
        # count all the author disciplines, put them in topics
        topics = {}
        for authID in authors:
            for top in self.getAuthorDiscipline(authID):
                if top not in topics:
                    topics[top] = 0
                topics[top] += 1

        # get the topics with the maximum value, append them to the paper topics
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
        for authID in self.nodes:
            if topicID in self.getAuthorDiscipline(authID):
                communityAuthors.append(authID)

        return communityAuthors

    def getAuthorswithTopic(self, topicID):
        '''
        Returns a list of authors who would have the given topic
        '''
        topicAuthors = []
        for authID, authClass in self.nodes.data('data'):
            if topicID in authClass.getData():
                topicAuthors.append(authID)

        return topicAuthors


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
        
        # coms = {}
        # for i, clust in enumerate(clusters):
        #     d = dict.fromkeys(clust, i)
        #     coms = coms | d
        # test = community.modularity(coms, subGraph, weight=None)
        # print(f'Test: {test}')
        # print(f'Real: {clusters.modularity}')

        # coms = dict.fromkeys(list(subGraph.nodes()), 1)
        # print(coms)
        # test = community.modularity(coms, subGraph, weight=None)
        # print(f'test2: {test}')
        # print(f'Results: {newGraph.modularity(set(subGraph.nodes()))}')

        # choose new cluster as the smaller one
        index = 1 if len(clusters[1]) < len(clusters[0]) else 0

        return clusters[index]


    def mergeCommunities(self, com1=[], com2=[]):
        '''
        Function will take the two communities as a list of authorIDs
        Will check modularity and merge them 
        Returns list of authors in merged community if merged, False otherwise
        '''

        # merge communities 
        newCom = set(com1 + com2)
        # return if no new commmunity
        if len(newCom) == 0:
            return False
        subGraphMerged = self.subgraph(list(newCom))

        # calculate modularities
        try:
            mergedMod = nx_modularity(subGraphMerged, [newCom], weight=None)
        except ZeroDivisionError:
            print(f'New Community: {newCom}')
            print(f'Com1: {com1} and Com2: {com2}')
            self.plotPyvisGraph(filename='outputs/ErrorGraph.html', network=subGraphMerged)
            sys.exit('Error with merging')
        # merge, authors that are in both communities will just be a part of the first
        coms = dict.fromkeys(com1, 0) | dict.fromkeys(com2, 1)
        unMergedMod = community.modularity(coms, subGraphMerged, weight=None)
        # print(f'Mergining communities: {com1} and {com2}')
        # print(f'Merged: {mergedMod}')
        # print(f'Unmerged: {unMergedMod}')

        if mergedMod < unMergedMod:
            return False

        return list(newCom)


    def updatePaperInNetwork(self, paperID, paperData):
        '''
        Function will update the author network with the paper
        PaperID: int
        paperData: ([topics], [authors])
        '''
        paperTopics = paperData[0]
        paperAuthors = paperData[1]

        for authID, authClass in self.nodes.data("data"):
            # can just update the authors of the paper
            if authID in paperAuthors:
                authClass.updateAuthor(paperID, paperTopics)

    '''Plotting Related Functions'''
    def genHTMLtable(self, authorID, width='500px'):
        html = '''
            <style>
                table {font-family: arial, sans-serif;border-collapse: collapse;}
                td, th {border: 1px solid #dddddd;text-align: left;padding: 8px;}
                th {background-color:#22A7F0}
                tr:nth-child(even) {background-color: #dddddd;}
            </style>
            ''' + f'<div style="overflow-x:auto; width:{width}"><table>'
        html += f'<tr><caption><b>Main Author Disciplines:</b> ' + ','.join(map(str, self.getAuthorDiscipline(authorID))) + '</caption></tr>'
        for topicID, papers in self.nodes[authorID]["data"].getData().items():
            html += f'<tr><th>{topicID}</th><td>'
            html += '</td><td>'.join(map(str, papers))
            html += '</td></tr>'
        html += '</table></div>'
        return html
    
    def genPyvisGraph(self):

        # create copy
        graph = deepcopy(self)

        # create groups for coloring
        groups = {}
        gid = 1

        for authID in graph.getAuthorIDs():

            # add labels
            graph.nodes[authID]['label'] = f'Author {authID}'
            disciplines = ','.join(map(str, graph.getAuthorDiscipline(authID)))
            graph.nodes[authID]['title'] = graph.genHTMLtable(authID)

            # add scaling
            graph.nodes[authID]["value"] = len(graph.getAuthorPapers(authID))

            if disciplines not in groups:
                groups[disciplines] = gid
                gid += 1

            graph.nodes[authID]["group"] = groups[disciplines]

            # delete auth class since it is not compatible with PyVis
            graph.nodes[authID]["data"] = None

        return graph

    def plotPyvisGraph(self, filename='pyvis.html', network=None, notebook=False):
        
        net = self.genPyvisGraph() if not network else network.genPyvisGraph()
        visNetwork = ntvis(notebook=notebook)
        visNetwork.from_nx(net)
        output = visNetwork.show(filename)
        print(f'Plot saved to {filename} successfully!')
        return output
        

    def genGraphFeatures(self):
        '''
        Will return the dictionary for node labels and list of colors for plotting
        Used for labels and colors in networkx graph drawing: https://networkx.org/documentation/latest/reference/generated/networkx.drawing.nx_pylab.draw_networkx.html?highlight=draw_networkx
        '''
        labels = {}
        colors = []
        for authID in self.nodes:
            disciplines = self.getAuthorDiscipline(authID)
            labels[authID] = f'{authID}: ' + ','.join(map(str, disciplines))
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