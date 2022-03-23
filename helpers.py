import networkx as nx
from pyvis.network import Network
import random
from igraph import Graph

# recursive function that will traverse the nodes, creating a paper
def createPaper(network, authors, probStop):
    '''
    Will take network, list of authors, and probStop as input
    '''
    currAuthorID = authors[-1]
    newNeighbors = set(network.neighbors(currAuthorID)).difference(set(authors))

    # base condition: stop at node if probStop hit or there are no new neighbors to traverse
    if random.random() < probStop or len(newNeighbors) == 0:
        return
    
    # create list representing probabilities for the neighboring nodes of the current coauthor
    probs = []
    for neighbor in newNeighbors:
        nData = network.get_edge_data(currAuthorID, neighbor)
        probs.extend([neighbor] * nData["weight"])

    # Select coauthor from neighbors probabilities list
    coauthorID = random.choice(probs)

    # update all edges of coauthors to this new author
    for author in authors:
        # if there is not an edge, create one
        if not network.has_edge(author, coauthorID) and author != coauthorID:
            network.add_edge(author, coauthorID, weight=0, width=1)
        newWeight = network.get_edge_data(author, coauthorID)["weight"] + 1
        #network.update(edges=[ (author, coauthorID, {"weight": newWeight, "width": newWeight//2}) ])
        network.update(edges=[ (author, coauthorID, {"weight": newWeight}) ])

    # call function recursively with coauthor
    authors.append(coauthorID)
    createPaper(network, authors, probStop)

# function will return new community number and color
def getNewCC(network):
    colors = ["red", "blue", "green", "orange", "purple"]
    print(max(dict(network.nodes.data('label')).values()))
    newComm = max(dict(network.nodes.data('label')).values()) + 1
    return newComm, random.choice(colors)

def getCommNodes(network, communityNum):
    '''Returns a list of nodes associated with the community'''
    nodes = []
    for nodeID, comm in network.nodes.data('label'):
        if comm == communityNum:
            nodes.append(nodeID)
    return nodes

def genGraphFeatures(network):
    '''
    Will return the dictionary for node labels and list of colors
    Used for labels and colors in networkx graph drawing: https://networkx.org/documentation/latest/reference/generated/networkx.drawing.nx_pylab.draw_networkx.html?highlight=draw_networkx
    '''
    labels = {}
    colors = []
    for nodeID, data in network.nodes.data():
        labels[nodeID] = data["label"]
        #colors.append(data["color"])
        colors.append(data["label"])
    return labels, colors

def splitCommunity(network, nodes):
    '''
    Function will take the networkx network as input and the list of nodes in the community
        It will then test if it should split the community or not
    Returns nothing, will update the network
    '''
    # split into two communities
    subGraph = network.subgraph(nodes)
    newGraph = Graph.from_networkx(subGraph)

    # create subgraph and split
    clusters = newGraph.community_leading_eigenvector(clusters=2)

    # compare unweighted modularity of new communities to the initial, return if there should not be change in community structure
    # Q: modularity of just the partition or the whole graph with the new partition?
    if newGraph.modularity(set(subGraph.nodes())) > clusters.modularity or len(clusters) != 2:
        return

    # update the colors and group name of the nodes in the smaller sub-community
    # must know all the groups and community names and pick different ones
    newComm, color = getNewCC(network)
    index = 1 if len(clusters[1]) < len(clusters[0]) else 0
    for node in clusters[index]:
        network.update(nodes=[(node, {"label": newComm, "color": color})])
    # update the papers? Need a data structure of the papers