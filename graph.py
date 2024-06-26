import networkx as nx
from constants import (
    SENTIMENT_INTERMEDIATE_NUMBER,
    Messages,
    NodeAttributes,
    EdgeAttributes,
    GraphAttributes,
)
from graph_attributes import (
    add_graph_attributes,
)
from nodes_attributes import add_nodes_attributes


class Graph:
    def __init__(self, messages):
        self.graph = nx.DiGraph()
        self.messages = messages

        self.set_graph_attributes()

    def create_node(self, message):
        self.graph.add_node(
            message[Messages.UID],
            id=message[Messages.UID],
            label=message[Messages.NAME],
            sentiment=0,
            sentimentSum=0,
            sentimentCount=0,
            size=13,
            color="#e8e8e8",
            degree=0,
            outDegree=0,
            eccentricity=0,
            betweennessCentrality=0,
            closenessCentrality=0,
            EigenCentrality=0,
            PageRank=0,
        )

    def updateNode(self, message):
        node = self.graph.nodes[message[Messages.UID]]
        node[NodeAttributes.SENTIMENT_COUNT] += 1
        node[NodeAttributes.SIZE] += 1
        node[NodeAttributes.SENTIMENT_SUM] += round(
            message[Messages.SENTIMENT_SCORE], 2
        )
        node[NodeAttributes.SENTIMENT] = round(
            node[NodeAttributes.SENTIMENT_SUM] / node[NodeAttributes.SENTIMENT_COUNT], 2
        )
        if node[NodeAttributes.SENTIMENT] >= SENTIMENT_INTERMEDIATE_NUMBER:
            node[NodeAttributes.COLOR] = "#77bf38"
        elif node[NodeAttributes.SENTIMENT] <= -SENTIMENT_INTERMEDIATE_NUMBER:
            node[NodeAttributes.COLOR] = "#fb8281"
        else:
            node[NodeAttributes.COLOR] = "#e8e8e8"

    def create_edge(self, fromId, toId):
        self.graph.add_edge(
            fromId,
            toId,
            totalSentiment=0,
            sentiment=0,
            messages=[],
        )

    def updateEdgeAttributes(self, edge, newMessage):
        edge[EdgeAttributes.MESSAGES].append(newMessage[Messages.TEXT])
        edge[EdgeAttributes.TOTAL_SENTIMENT] += newMessage[Messages.SENTIMENT_SCORE]
        edge[EdgeAttributes.SENTIMENT] = edge[EdgeAttributes.TOTAL_SENTIMENT] / len(
            edge[EdgeAttributes.MESSAGES]
        )

        if edge[EdgeAttributes.SENTIMENT] >= SENTIMENT_INTERMEDIATE_NUMBER:
            edge[EdgeAttributes.TYPE] = "positive"
        elif edge[EdgeAttributes.SENTIMENT] <= -SENTIMENT_INTERMEDIATE_NUMBER:
            edge[EdgeAttributes.TYPE] = "negative"
        else:
            edge[EdgeAttributes.TYPE] = "natural"

    def set_graph_attributes(self):
        self.graph.graph[GraphAttributes.DIAMETER] = 0
        self.graph.graph[GraphAttributes.RADIUS] = 0
        self.graph.graph[GraphAttributes.DENSITY] = 0
        self.graph.graph[GraphAttributes.RECIPROCITY] = 0
        self.graph.graph[GraphAttributes.TRANSITIVITY] = 0
        self.graph.graph[GraphAttributes.PATH_LENGTH] = 0
        self.graph.graph[GraphAttributes.AVERAGE_CLUSTERING] = 0
        self.graph.graph[GraphAttributes.POSITIVE_EDGES] = 0
        self.graph.graph[GraphAttributes.NEGATIVE_EDGES] = 0
        self.graph.graph[GraphAttributes.NATURAL_EDGES] = 0

    def create_graph(self):
        # check if there are messages
        if len(self.messages) == 0:
            return nx.readwrite.json_graph.node_link_data(self.graph)

        if (
            self.messages[0][Messages.UID]
            == "RPLkPefjRdQ3WL3prDMQLTtwjZ02"  # ChitChat id
        ):
            self.messages.pop(0)

        for message, i in zip(self.messages, range(len(self.messages))):
            if message[Messages.UID] not in self.graph:
                self.create_node(message)
            self.updateNode(message)

            if i == 0:  # handle edge cases
                continue

            if not self.graph.has_edge(
                self.messages[i][Messages.UID], self.messages[i - 1][Messages.UID]
            ):
                self.create_edge(
                    self.messages[i][Messages.UID], self.messages[i - 1][Messages.UID]
                )

            self.updateEdgeAttributes(
                self.graph.edges[
                    self.messages[i][Messages.UID], self.messages[i - 1][Messages.UID]
                ],
                self.messages[i],
            )

        add_nodes_attributes(self.graph)
        add_graph_attributes(self.graph)

        return nx.readwrite.json_graph.node_link_data(self.graph)
