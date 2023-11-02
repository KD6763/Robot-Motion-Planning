from __future__ import division
from math import pi, sqrt, atan, acos


class Point(object):
    __slots__ = ('x', 'y', 'polygon_id')

    def __init__(self, x, y, polygon_id=-1):
        self.x = float(x)
        self.y = float(y)
        self.polygon_id = polygon_id

    def __eq__(self, point):
        return point and self.x == point.x and self.y == point.y

    def __ne__(self, point):
        return not self.__eq__(point)

    def __lt__(self, point):
        return hash(self) < hash(point)

    def __str__(self):
        return "(%.2f, %.2f)" % (self.x, self.y)

    def __hash__(self):
        return self.x.__hash__() ^ self.y.__hash__()

    def __repr__(self):
        return "Point(%.2f, %.2f)" % (self.x, self.y)


CCW = 1
CW = -1


def visible_vertices(point, graph, origin=None, destination=None, scan='full'):
    edges = graph.get_edges()
    points = graph.get_points()
    if origin: points.append(origin)
    if destination: points.append(destination)
    points.sort(key=lambda p: (angle(point, p), edge_distance(point, p)))

    # Initialize new_edges with any intersecting edges on the half line from
    # point along the positive x-axis
    new_edges = NewEdge()
    point_inf = Point(float('inf'), point.y)
    for edge in edges:
        if point in edge: continue
        if edge_intersect(point, point_inf, edge):
            if on_segment(point, edge.p1, point_inf): continue
            if on_segment(point, edge.p2, point_inf): continue
            new_edges.insert(point, point_inf, edge)

    visible = []
    prev = None
    prev_visible = None
    for p in points:
        if p == point: continue
        if scan == 'half' and angle(point, p) > pi: break

        # Update new_edges - remove clock wise edges incident on p
        if new_edges:
            for edge in graph[p]:
                if ccw(point, p, edge.get_adjacent(p)) == CW:
                    new_edges.delete(point, p, edge)

        # Check if p is visible from point
        is_visible = False
        # Non-collinear points
        if prev is None or ccw(point, prev, p) != 0 or not on_segment(point, prev, p):
            if len(new_edges) == 0:
                is_visible = True
            elif not edge_intersect(point, p, new_edges.smallest()):
                is_visible = True
        # For collinear points, if previous point was not visible, p is not
        elif not prev_visible:
            is_visible = False
        # For collinear points, if previous point was visible, need to check
        # that the edge from prev to p does not intersect any open edge.
        else:
            is_visible = True
            for edge in new_edges:
                if prev not in edge and edge_intersect(prev, p, edge):
                    is_visible = False
                    break
            if is_visible and edge_in_polygon(prev, p, graph):
                is_visible = False

        # Check if the visible edge is interior to its polygon
        if is_visible and p not in graph.get_adjacent_points(point):
            is_visible = not edge_in_polygon(point, p, graph)

        if is_visible: visible.append(p)

        # Update new_edges - Add counter clock wise edges incident on p
        for edge in graph[p]:
            if (point not in edge) and ccw(point, p, edge.get_adjacent(p)) == CCW:
                new_edges.insert(point, p, edge)

        prev = p
        prev_visible = is_visible
    return visible


def polygon_crossing(p1, poly_edges):
    p2 = Point(float('inf'), p1.y)
    intersect_count = 0
    for edge in poly_edges:
        if p1.y < edge.p1.y and p1.y < edge.p2.y: continue
        if p1.y > edge.p1.y and p1.y > edge.p2.y: continue
        if p1.x > edge.p1.x and p1.x > edge.p2.x: continue
        # Deal with points collinear to p1
        edge_p1_collinear = (ccw(p1, edge.p1, p2) == 0)
        edge_p2_collinear = (ccw(p1, edge.p2, p2) == 0)
        if edge_p1_collinear and edge_p2_collinear: continue
        if edge_p1_collinear or edge_p2_collinear:
            collinear_point = edge.p1 if edge_p1_collinear else edge.p2
            if edge.get_adjacent(collinear_point).y > p1.y:
                intersect_count += 1
        elif edge_intersect(p1, p2, edge):
            intersect_count += 1
    if intersect_count % 2 == 0:
        return False
    return True


def edge_in_polygon(p1, p2, graph):
    """Return true if the edge from p1 to p2 is interior to any polygon
    in graph."""
    if p1.polygon_id != p2.polygon_id:
        return False
    if p1.polygon_id == -1 or p2.polygon_id == -1:
        return False
    mid_point = Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
    return polygon_crossing(mid_point, graph.polygons[p1.polygon_id])


def point_in_polygon(p, graph):
    """Return true if the point p is interior to any polygon in graph."""
    for polygon in graph.polygons:
        if polygon_crossing(p, graph.polygons[polygon]):
            return polygon
    return -1


def unit_vector(c, p):
    magnitude = edge_distance(c, p)
    return Point((p.x - c.x) / magnitude, (p.y - c.y) / magnitude)


def closest_point(p, graph, polygon_id, length=0.001):
    polygon_edges = graph.polygons[polygon_id]
    close_point = None
    close_edge = None
    close_dist = None
    for i, e in enumerate(polygon_edges):
        num = ((p.x - e.p1.x) * (e.p2.x - e.p1.x) + (p.y - e.p1.y) * (e.p2.y - e.p1.y))
        denom = ((e.p2.x - e.p1.x) ** 2 + (e.p2.y - e.p1.y) ** 2)
        u = num / denom
        pu = Point(e.p1.x + u * (e.p2.x - e.p1.x), e.p1.y + u * (e.p2.y - e.p1.y))
        pc = pu
        if u < 0:
            pc = e.p1
        elif u > 1:
            pc = e.p2
        d = edge_distance(p, pc)
        if i == 0 or d < close_dist:
            close_dist = d
            close_point = pc
            close_edge = e

    if close_point in close_edge:
        c = close_edge.p1 if close_point == close_edge.p1 else close_edge.p2
        edges = list(graph[c])
        v1 = unit_vector(c, edges[0].get_adjacent(c))
        v2 = unit_vector(c, edges[1].get_adjacent(c))
        vsum = unit_vector(Point(0, 0), Point(v1.x + v2.x, v1.y + v2.y))
        close1 = Point(c.x + (vsum.x * length), c.y + (vsum.y * length))
        close2 = Point(c.x - (vsum.x * length), c.y - (vsum.y * length))
        if point_in_polygon(close1, graph) == -1:
            return close1
        return close2
    else:
        v = unit_vector(p, close_point)
        return Point(close_point.x + v.x * length, close_point.y + v.y * length)


def edge_distance(p1, p2):
    """Return the Euclidean distance between two Points."""
    return sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)


def intersect_point(p1, p2, edge):
    """Return intersect Point where the edge from p1, p2 intersects edge"""
    if p1 in edge: return p1
    if p2 in edge: return p2
    if edge.p1.x == edge.p2.x:
        if p1.x == p2.x:
            return None
        pslope = (p1.y - p2.y) / (p1.x - p2.x)
        intersect_x = edge.p1.x
        intersect_y = pslope * (intersect_x - p1.x) + p1.y
        return Point(intersect_x, intersect_y)

    if p1.x == p2.x:
        eslope = (edge.p1.y - edge.p2.y) / (edge.p1.x - edge.p2.x)
        intersect_x = p1.x
        intersect_y = eslope * (intersect_x - edge.p1.x) + edge.p1.y
        return Point(intersect_x, intersect_y)

    pslope = (p1.y - p2.y) / (p1.x - p2.x)
    eslope = (edge.p1.y - edge.p2.y) / (edge.p1.x - edge.p2.x)
    if eslope == pslope:
        return None
    intersect_x = (eslope * edge.p1.x - pslope * p1.x + p1.y - edge.p1.y) / (eslope - pslope)
    intersect_y = eslope * (intersect_x - edge.p1.x) + edge.p1.y
    return Point(intersect_x, intersect_y)


def point_edge_distance(p1, p2, edge):
    ip = intersect_point(p1, p2, edge)
    if ip is not None:
        return edge_distance(p1, ip)
    return 0


def angle(center, point):
    dx = point.x - center.x
    dy = point.y - center.y
    if dx == 0:
        if dy < 0:
            return pi * 3 / 2
        return pi / 2
    if dy == 0:
        if dx < 0:
            return pi
        return 0
    if dx < 0:
        return pi + atan(dy / dx)
    if dy < 0:
        return 2 * pi + atan(dy / dx)
    return atan(dy / dx)


def angle2(point_a, point_b, point_c):
    a = (point_c.x - point_b.x) ** 2 + (point_c.y - point_b.y) ** 2
    b = (point_c.x - point_a.x) ** 2 + (point_c.y - point_a.y) ** 2
    c = (point_b.x - point_a.x) ** 2 + (point_b.y - point_a.y) ** 2
    cos_value = (a + c - b) / (2 * sqrt(a) * sqrt(c))
    return acos(round(int(cos_value)))


def ccw(A, B, C):
    #  Rounding this way is faster than calling round()
    area = round(int(((B.x - A.x) * (C.y - A.y) - (B.y - A.y) * (C.x - A.x))))
    if area > 0: return 1
    if area < 0: return -1
    return 0


def on_segment(p, q, r):
    if (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)):
        if (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y)):
            return True
    return False


def edge_intersect(p1, q1, edge):
    p2 = edge.p1
    q2 = edge.p2
    o1 = ccw(p1, q1, p2)
    o2 = ccw(p1, q1, q2)
    o3 = ccw(p2, q2, p1)
    o4 = ccw(p2, q2, q1)

    if o1 != o2 and o3 != o4:
        return True
    if o1 == 0 and on_segment(p1, p2, q1):
        return True
    if o2 == 0 and on_segment(p1, q2, q1):
        return True
    if o3 == 0 and on_segment(p2, p1, q2):
        return True
    if o4 == 0 and on_segment(p2, q1, q2):
        return True
    return False


class NewEdge(object):
    def __init__(self):
        self._new_edges = []

    def insert(self, p1, p2, edge):
        self._new_edges.insert(self._index(p1, p2, edge), edge)

    def delete(self, p1, p2, edge):
        index = self._index(p1, p2, edge) - 1
        if self._new_edges[index] == edge:
            del self._new_edges[index]

    def smallest(self):
        return self._new_edges[0]

    def less_than(self, p1, p2, edge1, edge2):
        """Return True if edge1 is smaller than edge2, False otherwise."""
        if edge1 == edge2:
            return False
        if not edge_intersect(p1, p2, edge2):
            return True
        edge1_dist = point_edge_distance(p1, p2, edge1)
        edge2_dist = point_edge_distance(p1, p2, edge2)
        if edge1_dist > edge2_dist:
            return False
        if edge1_dist < edge2_dist:
            return True
        # If the distance is equal, we need to compare on the edge angles.
        if edge1_dist == edge2_dist:
            if edge1.p1 in edge2:
                same_point = edge1.p1
            else:
                same_point = edge1.p2
            angle_edge1 = angle2(p1, p2, edge1.get_adjacent(same_point))
            angle_edge2 = angle2(p1, p2, edge2.get_adjacent(same_point))
            if angle_edge1 < angle_edge2:
                return True
            return False

    def _index(self, p1, p2, edge):
        lo = 0
        hi = len(self._new_edges)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.less_than(p1, p2, edge, self._new_edges[mid]):
                hi = mid
            else:
                lo = mid + 1
        return lo

    def __len__(self):
        return len(self._new_edges)

    def __getitem__(self, index):
        return self._new_edges[index]
