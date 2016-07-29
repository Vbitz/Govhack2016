import networkx as nx
import matplotlib.pyplot as pyp
import csv, sys, os
from os.path import abspath as path_absoulte
from os.path import join as path_join

BASE_PATH = path_absoulte("../../data/private/bgpRoutes")
NODES_FILENAME = path_join(BASE_PATH, "NZ_BGP_Map_Nodes.csv")
EDGES_FILENAME = path_join(BASE_PATH, "NZ_BGP_Map_Edges.csv")
SAVE_PATH = path_absoulte("../../pub/bgpData/graph.png")

def read_csv_dict(filename):
    f = open(filename, "rb")
    reader = csv.DictReader(f)
    rows = [row for row in reader]
    f.close()
    return rows

if __name__ == "__main__":
    nodeList = read_csv_dict(NODES_FILENAME)
    edgeList = read_csv_dict(EDGES_FILENAME)
    print "loaded", "nodes=", len(nodeList), "edges=", len(edgeList)

    G = nx.Graph()

    for node in nodeList:
        G.add_node(node["ASN"], short_name=node["ASN Short Name"])

    print "added nodes"

    for edge in edgeList:
        G.add_edge(edge["Source Node"], edge["Destination Node"])

    print "added edges"

    nx.draw_networkx(G)
    pyp.show()