# scienceDynamicsModel
A model of science dynamics in the science of science field.

## Data Structures

### Authors:
In network node data
{
    TopicID1: [PaperIDs],
    TopicID2: [PaperIDs],
}

### Papers
{
    PaperID1: ([TopicIDs], [AuthorIDs]),
    PaperID2: ([TopicIDs], [AuthorIDs]),
}

### Topics
{
    TopicID1: [PaperIDs],
    TopicID2: [PaperIDs]
}


### Network Visualizations


PyVis Node Properties: https://visjs.github.io/vis-network/docs/network/nodes.html 

Scaling: done by how many papers the author has been a part of
Title: should be done to show the author table
    
Edges: thickness for how many they have done together