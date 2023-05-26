import math
from math import sqrt

import numpy as np
import matplotlib.pyplot as plt


def create_super_triangle(pointList):
    min_x = min(point[0] for point in pointList)
    max_x = max(point[0] for point in pointList)
    min_y = min(point[1] for point in pointList)
    max_y = max(point[1] for point in pointList)

    width = max_x - min_x
    height = max_y - min_y

    p1 = (min_x - width, min_y - height)
    p2 = (max_x + 2 * width, min_y - height)
    p3 = (min_x + width, max_y + 2 * height)

    return p1, p2, p3


def circumcenter(triang):
    ax, ay = triang[0]
    bx, by = triang[1]
    cx, cy = triang[2]
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))

    if abs(d) < 1e-8:
        # print("Points are inline. Can't calculate a Circumcenter in this case.")
        return None

    c_x = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    c_y = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d

    radius = sqrt((c_x - ax) ** 2 + (c_y - ay) ** 2)

    return (round(c_x, 5), round(c_y, 5)), round(radius, 5)


def isInCircumcenter(_triang, _pt):
    center_result = circumcenter(_triang)
    if center_result is None:
        return True
    else:
        center, radius = center_result
        dist = sqrt((center[0] - _pt[0]) ** 2 + (center[1] - _pt[1]) ** 2)
        if dist < radius:
            return True
        else:
            return False


def is_edge_shared(edge, TR, current_triangle):
    for triangle in TR:
        if triangle == current_triangle:
            continue
        triangle_edges = [(triangle[0], triangle[1]), (triangle[1], triangle[2]), (triangle[2], triangle[0])]
        for triangle_edge in triangle_edges:
            if edge[0] in triangle_edge and edge[1] in triangle_edge:
                return True
    return False


def BW_Delaunay_Triangulation(points):
    superTriangle = create_super_triangle(points)
    T = [superTriangle]
    for p in points:
        TR = []
        for t in T:
            if isInCircumcenter(t, p):
                TR.append(t)
        polygon = []
        for t in TR:
            triangle_edges = [(t[0], t[1]), (t[1], t[2]), (t[2], t[0])]
            for edge in triangle_edges:
                if not is_edge_shared(edge, TR, t):
                    polygon.append(edge)
        for t in TR:
            T.remove(t)
        for edge in polygon:
            T.append((edge[0], p, edge[1]))
    new_T = []
    for t in T:
        p1, p2, p3 = superTriangle
        if not (p1 in t or p2 in t or p3 in t):
            new_T.append(t)

    T = new_T

    return T


# # Przykładowe użycie
# points = [
#     (0, 0),
#     (1, 0),
#     (0.5, 0.5),
#     (0, 1),
#     (1, 1),
# ]
#
#
# def draw_triangle(p1, p2, p3):
#     x_values = [p1[0], p2[0], p3[0], p1[0]]  # Dodajemy pierwszy punkt na koniec, aby zamknąć trójkąt
#     y_values = [p1[1], p2[1], p3[1], p1[1]]  # Dodajemy pierwszy punkt na koniec, aby zamknąć trójkąt
#
#     # Rysowanie krawędzi trójkąta
#     plt.plot(x_values, y_values, 'b-')
#
#     # Wypełnienie trójkąta kolorem
#     plt.fill(x_values, y_values, 'b', alpha=0.2)
#
#
# triangles = BW_Delaunay_Triangulation(points)
# for triangle in triangles:
#     draw_triangle(triangle[0], triangle[1], triangle[2])
# print(triangles)
# plt.axis('equal')  # Ustawienie równych skal na osiach x i y
# plt.show()
