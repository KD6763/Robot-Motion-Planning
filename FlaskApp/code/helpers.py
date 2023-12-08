from __future__ import division
from math import pi, sqrt, atan2, acos, atan
from code.class_list import Point

T = 10**9
T2 = 180 * T / pi


def euclidean_distance(p1, p2):
    """Return the Euclidean distance between two Points."""
    return sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)


def visible_vertices(point, graph, destination):
    edges = graph.get_edges()

    points = graph.get_points()

    if destination:
        points.append(destination)

    # Sort points based on angle and distance from the reference point
    points.sort(key=lambda p: (angle(point, p), euclidean_distance(point, p)))
    # points.sort(key=lambda p: (angle(point, p)))

    # Initialize open_edges with any intersecting edges on the half line
    # from point along the positive x-axis
    open_edges = OpenEdges()
    point_inf = Point(9999999, point.y)

    for edge in edges:
        if point in edge:
            continue
        if edge_intersect(point, point_inf, edge):
            if on_segment(point, edge.p1, point_inf):
                continue
            if on_segment(point, edge.p2, point_inf):
                continue
            open_edges.insert(point, point_inf, edge)

    visible = []
    prev = None
    prev_visible = None

    for p in points:
        if p == point:
            continue
        if angle(point, p) > pi:
            break

        # Update open_edges - remove clockwise edges incident on p
        if open_edges:
            for edge in graph[p]:
                if ccw(point, p, edge.get_adjacent(p)) == -1:
                    open_edges.delete(point, p, edge)

        # Check if p is visible from point
        is_visible = False

        # Non-collinear points
        if prev is None or ccw(point, prev, p) != 0 or not on_segment(point, prev, p):
            if len(open_edges) == 0:
                is_visible = True
            elif not edge_intersect(point, p, open_edges.smallest()):
                is_visible = True

        # For collinear points
        elif not prev_visible:
            is_visible = False

        # For collinear points, check that the edge from prev to p
        # does not intersect any open edge
        else:
            is_visible = True
            for edge in open_edges:
                if prev not in edge and edge_intersect(prev, p, edge):
                    is_visible = False
                    break
            if is_visible and edge_in_polygon(prev, p, graph):
                is_visible = False

        # Check if the visible edge is interior to its polygon
        if is_visible and p not in graph.get_adjacent_points(point):
            is_visible = not edge_in_polygon(point, p, graph)

        if is_visible:
            visible.append(p)

        # Update open_edges - Add counterclockwise edges incident on p
        for edge in graph[p]:
            if point not in edge and ccw(point, p, edge.get_adjacent(p)) == 1:
                open_edges.insert(point, p, edge)

        prev = p
        prev_visible = is_visible

    return visible


def polygon_crossing(p1, poly_edges):

    p2 = Point(9999999, p1.y)
    intersect_count = 0

    for edge in poly_edges:
        # Skip edges that don't intersect with the horizontal line passing through p1
        if not (min(edge.p1.y, edge.p2.y) <= p1.y <= max(edge.p1.y, edge.p2.y) and p1.x <= max(edge.p1.x, edge.p2.x)):
            continue

        # Deal with points collinear to p1
        edge_p1_collinear = ccw(p1, edge.p1, p2) == 0
        edge_p2_collinear = ccw(p1, edge.p2, p2) == 0

        if edge_p1_collinear and edge_p2_collinear:
            continue

        if edge_p1_collinear or edge_p2_collinear:
            collinear_point = edge.p1 if edge_p1_collinear else edge.p2
            if edge.get_adjacent(collinear_point).y > p1.y:
                intersect_count += 1
        elif edge_intersect(p1, p2, edge):
            intersect_count += 1

    return intersect_count % 2 != 0


def edge_in_polygon(p1, p2, graph):
    if p1.polygon_id != p2.polygon_id:
        return False
    if p1.polygon_id == -1 or p2.polygon_id == -1:
        return False
    mid_point = Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
    return polygon_crossing(mid_point, graph.polygons[p1.polygon_id])


def intersect_point(p1, p2, edge):
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
        return euclidean_distance(p1, ip)
    return 0


def angle(center, point):
    dx = point.x - center.x
    dy = point.y - center.y

    if dx == 0 and dy < 0:
        return pi * 3 / 2
    elif dx == 0 and dy >= 0:
        return pi / 2
    else:
        return atan2(dy, dx) % (2 * pi)
    # dx = point.x - center.x
    # dy = point.y - center.y
    # if dx == 0:
    #     if dy < 0:
    #         return pi * 3 / 2
    #     return pi / 2
    # if dy == 0:
    #     if dx < 0:
    #         return pi
    #     return 0
    # if dx < 0:
    #     return pi + atan(dy / dx)
    # if dy < 0:
    #     return 2 * pi + atan(dy / dx)
    # return atan(dy / dx)


def angle2(point_a, point_b, point_c):
    a = (point_c.x - point_b.x) ** 2 + (point_c.y - point_b.y) ** 2
    b = (point_c.x - point_a.x) ** 2 + (point_c.y - point_a.y) ** 2
    c = (point_b.x - point_a.x) ** 2 + (point_b.y - point_a.y) ** 2

    cos_value = (a + c - b) / (2 * sqrt(a) * sqrt(c))
    angle_rad = acos(round(cos_value, 10))  # Rounding to handle precision issues
    return round(angle_rad * T2 / pi)  # Convert to degrees and round for precision


def ccw(A, B, C):
    slope_AB = (B.y - A.y) * (C.x - A.x)
    slope_AC = (C.y - A.y) * (B.x - A.x)

    if slope_AB == slope_AC:
        return 0
    elif slope_AB < slope_AC:
        return 1
    else:
        return -1


def on_segment(p, q, r):
    if min(p.x, r.x) <= q.x <= max(p.x, r.x) and min(p.y, r.y) <= q.y <= max(p.y, r.y):
        return True
    return False


def edge_intersect(p1, q1, edge):
    p2, q2 = edge.p1, edge.p2
    o1, o2 = ccw(p1, q1, p2), ccw(p1, q1, q2)
    o3, o4 = ccw(p2, q2, p1), ccw(p2, q2, q1)

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


class OpenEdges(object):
    def __init__(self):
        self._open_edges = []

    def insert(self, p1, p2, edge):
        self._open_edges.insert(self._index(p1, p2, edge), edge)

    def delete(self, p1, p2, edge):
        index = self._index(p1, p2, edge) - 1
        if self._open_edges[index] == edge:
            del self._open_edges[index]

    def smallest(self):
        return self._open_edges[0]

    def _less_than(self, p1, p2, edge1, edge2):
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
        hi = len(self._open_edges)
        while lo < hi:
            mid = (lo+hi)//2
            if self._less_than(p1, p2, edge, self._open_edges[mid]):
                hi = mid
            else:
                lo = mid + 1
        return lo

    def __len__(self):
        return len(self._open_edges)

    def __getitem__(self, index):
        return self._open_edges[index]