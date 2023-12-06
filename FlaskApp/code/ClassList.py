from typing import List, Tuple, Dict
from collections import namedtuple
from reprit.base import generate_repr

import sys
import numpy as np
import math

class Point:
    def __init__(self, x=0., y=0.):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False

        eps = 1e-4
        return abs(self.x - other.x) <= eps and abs(self.y - other.y) <= eps

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return 'Point(x=%.3f, y=%.3f)' % (self.x, self.y)

    def __repr__(self):
        return str(self)


class HalfLine:
    def __init__(self, origin: Point, angle=0.):
        self._origin = origin
        self._angle = angle % 360.

    @property
    def origin(self) -> Point:
        return self._origin

    @property
    def angle(self) -> float:
        return self._angle

    @property
    def incl_angle(self) -> float:
        agl = self.angle % 180.
        if agl > 90:
            agl = - (180 - agl)
        return agl

    @property
    def coeffs(self):
        """
        Calculates a, b, c for the line equation ax + by + c = 0
        :return: A tuple (a, b, c)
        """
        if self.incl_angle == 90. or self.incl_angle == -90.:
            return 1., 0., -self.origin.x
        else:
            slope = math.tan(math.radians(self.incl_angle))
            k = slope * self.origin.x - self.origin.y
            return -slope, 1., k

    def __contains__(self, item: Point):
        if item == self.origin:
            return True

        hl = HalfLine.from_points(self.origin, item)
        return abs(self.angle - hl.angle) <= 1e-3

    @classmethod
    def from_points(cls, origin: Point, target: Point):
        if origin == target:
            raise ValueError('Cannot create half line from 2 identical points')
        line = LineSegment(origin, target)

        if origin.y > target.y:
            if origin.x == target.x:
                angle = 90.
            elif origin.x < target.x:
                angle = math.degrees(math.asin((origin.y - target.y) / line.length))
            else:
                angle = 90. + math.degrees(math.acos((origin.y - target.y) / line.length))
        elif origin.y < target.y:
            if origin.x == target.x:
                angle = 270.
            elif origin.x > target.x:
                angle = 180. + math.degrees(math.asin((target.y - origin.y) / line.length))
            else:
                angle = 270. + math.degrees(math.acos((target.y - origin.y) / line.length))
        else:
            if origin.x > target.x:
                angle = 180.
            else:
                angle = 0.
        return cls(origin, angle)


class LineSegment:
    def __init__(self, p1: Point, p2: Point):
        self._p1 = p1
        self._p2 = p2

    @property
    def p1(self) -> Point:
        return self._p1

    @property
    def p2(self) -> Point:
        return self._p2

    @property
    def coeffs(self):
        """
        Calculates a, b, c for the line equation ax + by + c = 0
        :return: A tuple (a, b, c)
        """
        try:
            _a = (self.p1.y - self.p2.y) / (self.p1.x - self.p2.x)
            _b = self.p1.y - _a * self.p1.x
            a, b, c = _a, -1, _b
            return a, b, c
        except ZeroDivisionError:
            return 1, 0, -self.p1.x

    @property
    def length(self):
        """
        :return: The segment's length, a.k.a the Euclidean distance between its endpoints.
        """
        ln = math.sqrt((self.p1.x - self.p2.x) ** 2 + (self.p1.y - self.p2.y) ** 2)
        return ln

    def __eq__(self, other):
        if not isinstance(other, LineSegment):
            return False
        return (self.p1 == other.p1 and self.p2 == other.p2) or (self.p1 == other.p2 and self.p2 == other.p1)

    def __repr__(self):
        return 'LineSegment(%s, %s)' % (self.p1, self.p2)

    # noinspection PyTypeChecker
    def __contains__(self, p: Point):
        eps = 1e-3
        if p == self.p1 or p == self.p2:
            return True

        # Round out input to avoid alignment mistakes
        p = Point(np.around(p.x, 5), np.around(p.y, 5))

        a, b, c = self.coeffs
        inx = min(self.p1.x, self.p2.x) - eps <= p.x <= max(self.p1.x, self.p2.x) + eps
        iny = min(self.p1.y, self.p2.y) - eps <= p.y <= max(self.p1.y, self.p2.y) + eps
        aligned = abs(a * p.x + b * p.y + c) <= eps
        return inx and iny and aligned

class Polygon:
    def __init__(self, vertices: List[Point]):
        """
        Initialize a new Polygon from a list of Points. Polygons are immutable.
        :param vertices: A list of Point that describes how to construct the Polygon.
        """
        if vertices[0] == vertices[-1]:
            vertices = vertices[:-1]
        self._vertices = vertices

        # Construct edge list from vertices
        self._edges = []
        for prev, current in zip(vertices[:-1], vertices[1:]):
            self._edges.append(LineSegment(prev, current))
        self._edges.append(LineSegment(vertices[-1], vertices[0]))

    __repr__ = generate_repr(__init__)

    def __contains__(self, item):
        return item in self.edges or item in self.vertices

    @property
    def vertices(self) -> Tuple[Point, ...]:
        return tuple(self._vertices)

    @property
    def edges(self) -> Tuple[LineSegment, ...]:
        return tuple(self._edges)

    def impact_points(self, line: LineSegment):
        """
        Calculates points where the polygon and a line segment meets.
        :param line: A line segment
        :return: A set of Coordinate of impact points, or None if there are none.
        """
        import helpers
        return helpers.impact_points(self, line)


_AdjacentNode = namedtuple('Node', ['coord', 'w'])


class VisibilityGraph:
    def __init__(self, s: Point, t: Point, segments=None):
        self._s, self._t = s, t
        self._segments = list() if segments is None else segments
        self._adj = None
        self._vertices = None

    def construct_adj_list(self):
        """
        Constructs the graph's adjacency list based on its segments.
        Should be done after the graph's segments have been fully added.
        """
        if self.constructed:
            print('WARNING: Overriding existing edge list.', file=sys.stderr)

        self._vertices = set()
        for s in self._segments:
            self._vertices.add(s.p1)
            self._vertices.add(s.p2)
        self._vertices = list(self._vertices)

        self._adj = {}
        for v in self._vertices:
            self._adj[v] = []

        for s in self._segments:
            self._adj[s.p1].append(_AdjacentNode(coord=s.p2, w=s.length))
            self._adj[s.p2].append(_AdjacentNode(coord=s.p1, w=s.length))

    @property
    def segments(self) -> Tuple[LineSegment]:
        return tuple(self._segments)

    def add_segment(self, segment: LineSegment):
        """
        Adds a segment to the graph. No op if the segment is already in the graph.
        :param segment: A LineSegment
        """
        if segment not in self.segments:
            self._segments.append(segment)

    @property
    def constructed(self) -> bool:
        return self._adj is not None and self._vertices is not None

    @property
    def adjacent_list(self) -> Dict[Point, _AdjacentNode]:
        return self._adj

    @property
    def vertices(self) -> Tuple[Point]:
        return tuple(self._vertices)

    @property
    def start(self) -> Point:
        return self._s

    @property
    def end(self) -> Point:
        return self._t
