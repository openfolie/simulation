import networkx as nx


class Relations:
    def __init__(self):
        self.__graph = nx.Graph()
        self.relations = []

    def add_agent(self, a):
        self.__graph.add_node(a)

    def connect(self, a, b, relation, weight):
        if relation not in self.relations:
            self.relations.append(relation)
        self.__graph.add_edge(a, b, relation=relation, weight=weight)

    def get_relation(self, a, relation):
        pass
        # self.__graph.
