"""
file: environment.py
description: This program create random obstacles(polygons) based on given
configuration settings
language: python3
author: Anurag Kallurwar, ak6491@rit.edu
"""


import math as m
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
random.seed(99)
from code.ClassList import *


def partition(num_partitions: int):
    factorize = lambda num: {factor for i in range(1, int(m.sqrt(num)) + 1)
                               if num % i == 0 for factor in [i, num // i]}
    factors = sorted(factorize(num_partitions))
    random_index = random.choices(range(0, len(factors)), weights = None,
                                  k = 1)[0]
    partitions = (factors[random_index], factors[-random_index - 1])
    return partitions


def orient(pointP: tuple, pointQ: tuple, pointR):
    """
    Get the orientation between three points
    :param pointP: Point P
    :param pointQ: Point Q
    :param pointR: Point R
    :return: Integer
    """
    result = (pointQ[0] * pointR[1] - pointR[0] * pointQ[1]) - \
             (pointP[0] * pointR[1] - pointR[0] * pointP[1]) + \
             (pointP[0] * pointQ[1] - pointQ[0] * pointP[1])
    if result > 0: # Counter-Clockwise
        return 1
    elif result < 0: # Clockwise
        return -1
    return 0 # Collinear


def half_hull(points: list):
    """
    Creates half a hull from given points
    :param points: input points
    :return: Half hull
    """
    stack = []
    stack.append(points[0])
    stack.append(points[1])
    for index in range(2, len(points)):
        while len(stack) >= 2 and orient(points[index], stack[-1], stack[-2])\
                <= 0:
            stack.pop()
        stack.append(points[index])
    return stack


def polar_angle(point: tuple, centroid: tuple):
    """
    Get the polar angle of point with respect to centroid
    :param point: input point
    :param centroid: calculated centroid for inputs
    :return: float polar angle
    """
    return m.atan2(point[1] - centroid[1], point[0] - centroid[0])


def sort_counter_clockwise(points: list):
    """
    Sort the given points in counter clockwise order
    :param points: input points
    :return: points in counter clockwise order
    """
    centroid_x = (sum(x for x, y in points)) / len(points)
    centroid_y = (sum(y for x, y in points)) / len(points)
    centroid = (centroid_x, centroid_y)
    counter_clockwise = sorted(points, key=lambda point: polar_angle(point,
                                                                centroid))
    return counter_clockwise


def graham_scan(num_points: int, points: list):
    """
    Creates convex hull using graham scan algorithm
    :param num_points: number of points
    :param points: input points
    :return: convex hull points
    """
    if num_points < 3:
        return "Convex Hull not possible"
    sorted_by_x = sorted(points, key = lambda point : point[0])
    convex_hull = half_hull(sorted_by_x) + half_hull(sorted_by_x[::-1])[1:-1]
    return convex_hull[::-1]


def create_obstacles(num_obstacles: int, coord_range: tuple, convex: bool = True):
    partitions = partition(num_obstacles)
    x_splits = [200] + sorted(random.sample(range(200, coord_range[0] - 1),
                                          partitions[0] - 1)) + [coord_range[0]]
    partition_areas = []
    for i in range(len(x_splits) - 1):
        y_splits = [200] + sorted(random.sample(range(200, coord_range[1] - 1),
                                               partitions[1] - 1)) + [
            coord_range[1]]
        for j in range(len(y_splits) - 1):
            partition_areas += [((x_splits[i], x_splits[i + 1]),
                                 (y_splits[j], y_splits[j + 1]))]
    obstacles = []
    for area in partition_areas:
        num_points = random.randint(3, 6)
        points = [(random.randint(area[0][0], area[0][1]), random.randint(
            area[1][0], area[1][1])) for i in range(num_points)]
        obstacle = sort_counter_clockwise(points)
        if convex:
            obstacle = graham_scan(num_points, points)
        obstacles.append(obstacle)
    return obstacles


def build_polygons(obstacles):
    polygons = []
    for point_list in obstacles:
        polygon = Polygon([Point(x, y) for x, y in point_list])
        polygons.append(polygon)
    start = Point(0, 0)
    end = Point(1000, 1000)
    return start, end, polygons


def plot_output(obstacles: list):
    """
    Plot the points and convex hull
    :param points: input points
    :param convex_hull: convex hull
    :return: None
    """
    fig, ax = plt.subplots()
    ax.set_title("Environment")
    for obstacle in obstacles:
        random_color = "#{:02X}{:02X}{:02X}".format(random.randint(1, 255),
                                                    random.randint(1, 255),
                                                    255)
        polygon = patches.Polygon(obstacle, closed=True, edgecolor='black',
                                  facecolor=random_color)
        ax.add_patch(polygon)
    ax.scatter([0], [0], c='r', label="Start")
    ax.scatter([1000], [1000], c='g', label="Destination")
    ax.scatter([0], [0], c='b', label="Point Robot", marker='*', s=10)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_aspect('equal', adjustable='box')
    ax.legend(bbox_to_anchor=(1.0, 1), loc='upper left', fontsize=7)
    plt.tight_layout()
    plt.show()
