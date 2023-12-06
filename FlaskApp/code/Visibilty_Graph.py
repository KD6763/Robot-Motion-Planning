from typing import List
from sortedcontainers import SortedListWithKey


from code.ClassList import Point, HalfLine, LineSegment, Polygon, VisibilityGraph
import code.helpers as helpers


def rotational_plane_sweep(s: Point, t: Point, obstacles: List[Polygon],
                           verbose=True) -> VisibilityGraph:
    def log_print(*args, **kwargs):
        if verbose:
            print(*args, **kwargs)

    graph = VisibilityGraph(s, t)
    points = [s, t]

    # Add all obstacle edges to the graph
    for obs in obstacles:
        for e in obs.edges:
            graph.add_segment(e)
        for p in obs.vertices:
            if p not in points:
                points.append(p)

    for i, p in enumerate(points[:-1]):
        # Sort other points by positive-x angle and distance to p
        others = points[:]
        others.remove(p)
        others.sort(key=lambda x: LineSegment(p, x).length)
        others.sort(key=lambda x: HalfLine.from_points(p, x).angle)

        # Construct search tree
        point2edge, point2poly = {}, {}
        point2edge[s] = []
        point2edge[t] = []
        xline = HalfLine(p, 0.)
        tree = SortedListWithKey(key=lambda x: VisitOrder(p, x))
        vis = [False for _ in range(len(others))]

        # Add intersecting edges along with their visit order to the search tree
        tobs = None
        for obs in obstacles:
            if p in obs.vertices:
                tobs = obs

            for e in obs.edges:
                # Map vertices to their edges
                for v in (e.p1, e.p2):
                    point2poly[v] = obs
                    if v not in point2edge.keys():
                        point2edge[v] = [e]
                    else:
                        point2edge[v].append(e)

                if p not in e:
                    ips = helpers.hl_intersect_point(xline, e)
                    if ips is not None:
                        tree.add(e)

        if tobs is not None:
            for j, op in enumerate(others):
                if op in tobs.vertices:
                    vis[j] = True

        # Find visible vertices
        log_print('# Current point:', p)
        for j, op in enumerate(others):
            log_print('## Sweeping: ', op)
            if _visible(p, op, tree, point2poly, others, vis, j) and points.index(op) > i:
                log_print('  VISIBLE')
                graph.add_segment(LineSegment(p, op))
                vis[j] = True
            else:
                vis[j] = False

            # Decide whether to insert or delete each edge
            for e in point2edge[op]:
                rp = list(filter(lambda x: x != op, [e.p1, e.p2]))[0]
                if rp == p:
                    continue

                its = helpers.hl_intersect_point(xline, e)
                a0 = HalfLine.from_points(p, op).angle
                a1 = HalfLine.from_points(p, rp).angle
                if its is not None:
                    before = False
                else:
                    before = a1 <= a0

                if before:
                    log_print('  Removing %s' % str(e))
                    tree.discard(e)
                else:
                    log_print('  Adding %s' % str(e))
                    tree.add(e)

    return graph


def brute_force(s: Point, t: Point, obstacles: List[Polygon],
                verbose=False) -> VisibilityGraph:
    graph = VisibilityGraph(s, t)

    # Get vertex list
    verts = [s, t]
    for obs in obstacles:
        verts.extend(obs.vertices)

    for i, v1 in enumerate(verts[:-1]):
        for j, v2 in enumerate(verts[i+1:]):
            if v1 == v2:
                continue
            segment = LineSegment(v1, v2)

            # Check for impact to each obstacle
            visible = True
            for obs in obstacles:
                if segment in obs:
                    break
                if v1 in obs and v2 in obs:
                    visible = False
                    if verbose:
                        print('  %s: POLYGON DIAGONAL' % segment)
                    break
                else:
                    impacts = obs.impact_points(segment)
                    if impacts is None:
                        continue
                    for ip in impacts:
                        if ip != v1 and ip != v2:
                            visible = False
                            if verbose:
                                print('  %s: POLYGON IMPACT' % segment)
                            break

            if visible:
                graph.add_segment(segment)
                if verbose:
                    print('  %s: VISIBLE' % segment)

    return graph

def _visible(origin: Point, p: Point, tree: SortedListWithKey,
             point2poly: dict, others: list, vis: list, idx: int):
    pw = LineSegment(origin, p)

    def has_impact_points(point):
        try:
            val = helpers.impact_points(point2poly[point], pw)
            return val is not None and len(val) > 1
        except KeyError:
            return False

    if has_impact_points(p) or has_impact_points(origin):
        return False

    if idx == 0 or others[idx - 1] not in pw:
        e = tree[0] if len(tree) > 0 else None

        def intersects_with_tree_element():
            nonlocal e
            val = helpers.intersect_point(pw, e)
            print(e)
            return val is not None and val != p

        return False if e and intersects_with_tree_element() else True
    elif not vis[idx - 1]:
        return False
    else:
        ww = LineSegment(p, others[idx - 1])
        val = binary_search(tree, ww)
        return False if val is not None else True


def binary_search(tree: SortedListWithKey, edge: LineSegment):
    left, right = 0, len(tree) - 1
    it = None

    while left <= right:
        mid = (left + right) // 2
        current = tree[mid]
        it = helpers.intersect_point(current, edge)

        if it is not None:
            return it  # Intersection found, return the point

        # Adjust the search range based on the comparison
        if current < edge:
            left = mid + 1
        else:
            right = mid - 1

    return it


class VisitOrder:
    def __init__(self, origin: Point, line: LineSegment):
        self._origin = origin
        self._line = line
        self.__calculate()

    def __calculate(self):
        baseline = HalfLine(self._origin)
        cp = helpers.hl_intersect_point(baseline, self._line)
        hl1 = HalfLine.from_points(self._origin, self._line.p1)
        hl2 = HalfLine.from_points(self._origin, self._line.p2)

        if cp is not None:
            self._is_cut = True
            self._cut_dist = LineSegment(cp, self._origin).length
            self._max_angle = max(hl1.angle, hl2.angle)
            self._min_angle = None
            self._min_dist = None
        else:
            self._is_cut = False
            self._cut_dist = None
            self._max_angle = max(hl1.angle, hl2.angle)
            self._min_angle = min(hl1.angle, hl2.angle)

            if hl1.angle < hl2.angle:
                _l = LineSegment(self._origin, self._line.p1)
            else:
                _l = LineSegment(self._origin, self._line.p2)
            self._min_dist = _l.length

    @property
    def min_angle(self):
        return self._min_angle

    @property
    def max_angle(self):
        return self._max_angle

    @property
    def min_dist(self):
        return self._min_dist

    @property
    def is_cut(self):
        return self._is_cut

    @property
    def cut_dist(self):
        return self._cut_dist

    def __str__(self):
        if self.is_cut:
            return 'Order(CUT, dist=%.2f)' % self.cut_dist
        else:
            return 'Order(NOCUT, angle=%.2f, dist=%.2f)' % (self.min_angle, self.min_dist)

    def __eq__(self, other):
        return self._is_cut == other.is_cut and self._cut_dist == other.cut_dist and\
            self.min_angle == other.min_angle and self.min_dist == other.min_dist

    def __ne__(self, other):
        return not self == other


    def __gt__(self, other):
        if self.is_cut:
            if other.is_cut:
                return self.cut_dist > other.cut_dist
            else:
                if other.min_angle <= 180.:
                    return False
                else:
                    return self.max_angle > other.min_angle
        else:
            if other.is_cut:
                if self.min_angle <= 180.:
                    return True
                else:
                    return self.min_angle > other.max_angle
            else:
                if self.min_dist != other.min_dist:
                    return self.min_dist > other.min_dist
                else:
                    return self.min_angle > other.min_angle

    def __ge__(self, other):
        return self > other or self == other

    def __lt__(self, other):
        if self.is_cut:
            if other.is_cut:
                return self.cut_dist < other.cut_dist
            else:
                if other.min_angle <= 180.:
                    return True
                else:
                    return self.max_angle < other.min_angle
        else:
            if other.is_cut:
                if self.min_angle <= 180.:
                    return False
                else:
                    return self.min_angle < other.max_angle
            else:
                if self.min_dist != other.min_dist:
                    #return self.min_angle < other.min_angle
                    return self.min_dist < other.min_dist
                else:
                    #return self.min_dist < other.min_dist
                    return self.min_angle < other.min_angle


    def __le__(self, other):
        return self < other or self == other