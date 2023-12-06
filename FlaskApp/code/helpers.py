from code.ClassList import *


def intersect_point(l1, l2):
    a1, b1, c1 = l1.coeffs
    a2, b2, c2 = l2.coeffs

    A = np.asarray([[a1, b1], [a2, b2]])
    b = np.asarray([[-c1], [-c2]])

    try:
        x = np.linalg.solve(A, b)
        x = np.around(x, 5)
    except np.linalg.LinAlgError:
        return None

    x1, x2 = x[0, 0], x[1, 0]
    p = Point(x1, x2)

    return p if (p in l1 and p in l2) else None


def hl_intersect_point(hl, ls):
    a1, b1, c1 = hl.coeffs
    a2, b2, c2 = ls.coeffs

    A = np.asarray([[a1, b1], [a2, b2]])
    b = np.asarray([[-c1], [-c2]])

    try:
        x = np.linalg.solve(A, b)
        x = np.around(x, 5)
    except np.linalg.LinAlgError:
        return None

    x1, x2 = x[0, 0], x[1, 0]
    p = Point(x1, x2)

    return p if (p in ls and p in hl) else None


def hl_polygon_intersections(hl, polygon):
    points = []

    for e in polygon.edges:
        p = hl_intersect_point(hl, e)
        if p is not None:
            points.append(p)

    return points if len(points) > 0 else None


def impact_points(polygon, segment):
    """
    Calculates points where a polygon and a line segment meets.
    :param polygon: A Polygon object
    :param segment: A LineSegment object
    :return: A set of Coordinate of impact points, or None if there are none.
    """

    points = set()
    for p in [segment.p1, segment.p2]:
        if p in polygon.vertices:
            points.add(p)

    for edge in polygon.edges:
        p = intersect_point(segment, edge)
        if p is not None:
            points.add(p)

    return points if len(points) > 0 else None


def path_length(path):
    """
    Calculates the length of a path
    :param path: A list of Coordinates
    :return: The path's length
    """
    length = 0.
    for prev, current in zip(path[:-1], path[1:]):
        length += LineSegment(prev, current).length
    return length