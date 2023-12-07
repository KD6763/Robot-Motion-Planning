from code.class_list import Graph, Edge
from code.helpers import visible_vertices


class VisGraph(object):
    def __init__(self):
        self.graph = None
        self.visgraph = None
        self.updated_visgraph = None

    def build(self, start, end, polygon):
        self._initialize_graphs(polygon)
        self._build_visgraph(start, end)

    def _initialize_graphs(self, polygon):
        self.graph = Graph(polygon)
        self.visgraph = Graph([])
        self.updated_visgraph = Graph([])

    def _build_visgraph(self, start, end):
        points = self.graph.get_points()
        points.insert(0, start)

        for edge in self._generate_vis_edges(points, end):
            self.visgraph.add_edge(edge)

    def _generate_vis_edges(self, points, end):
        visible_edges = []
        for p1 in points:
            for p2 in visible_vertices(p1, self.graph, end):
                visible_edges.append(Edge(p1, p2))
        return visible_edges
