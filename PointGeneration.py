from itertools import chain

import numpy as np


def generate_points(matrix, num):
    matrix = np.array(matrix)
    # Wymiary macierzy
    rows, cols = matrix.shape
    # Macierz etykiet o takim samym rozmiarze jak macierz wejściowa
    labels = np.zeros_like(matrix)

    # Licznik etykiet
    label_counter = 1

    # Funkcja rekurencyjna do etykietowania obszaru
    def label_object(matrix, labels, i, j, label):
        stack = [(i, j)]

        while stack:
            x, y = stack.pop()

            if x < 0 or x >= rows or y < 0 or y >= cols or matrix[x, y] == 0 or labels[x, y] != 0:
                continue

            labels[x, y] = label

            stack.append((x - 1, y))
            stack.append((x + 1, y))
            stack.append((x, y - 1))
            stack.append((x, y + 1))

    # Przechodzenie po macierzy i etykietowanie obszarów
    for i in range(rows):
        for j in range(cols):
            # Jeśli piksel jest czarny (1) i nie został jeszcze oznaczony
            if matrix[i, j] == 1 and labels[i, j] == 0:
                # Wywołanie funkcji oznaczającej obszar
                label_object(matrix, labels, i, j, label_counter)
                # Zwiększenie licznika etykiet
                label_counter += 1

    # Zdefiniowanie listy punktów dla macierzy
    contour_points = []

    for label in range(1, label_counter):
        label_points = []
        for i in range(rows):
            for j in range(cols):
                if labels[i, j] == label:
                    label_points.append((j, i))  # Dodanie punktu (x, y)
        contour_points.append(label_points)

    # Usunięcie punktów, które nie sąsiadują z wartością 0 w macierzy, nie są konturami - na konturach wiecej pkt
    contour_points_filtered = []
    for points in contour_points:
        filtered_points = []
        for point in points:
            x, y = point
            if x == cols-1 or y == rows-1:
                filtered_points.append(point)
                continue
            if (
                    matrix[y - 1, x] == 0 or
                    matrix[y + 1, x] == 0 or
                    matrix[y, x - 1] == 0 or
                    matrix[y, x + 1] == 0
            ):
                filtered_points.append(point)
        contour_points_filtered.append(filtered_points)

    # Lista punktów zawierających zarówno points, jak i points_filtered
    combined_points = []
    for points_filtered, points in zip(contour_points_filtered, contour_points):
        new_points = []
        new_points.extend(points_filtered[::7])
        new_points.extend(points[::num])
        combined_points.append(new_points)

    return combined_points


def generate_points_for_solo(matrix, num):
    return generate_points(matrix, num)


def generate_all_points_with_addition(matrix, step_size):
    matrix = np.array(matrix)
    # Wymiary macierzy
    rows, cols = matrix.shape
    # Generowanie punktów na krawędziach
    edge_points = []
    for i in range(0, rows, step_size):
        edge_points.append((0, i))  # Lewa krawędź
        edge_points.append((cols - 1, i))  # Prawa krawędź

    for j in range(0, cols, step_size):
        edge_points.append((j, 0))  # Górna krawędź
        edge_points.append((j, rows - 1))  # Dolna krawędź

    if not edge_points.__contains__((cols-1, rows-1)):
        edge_points.append((cols - 1, rows - 1))
    if edge_points.__contains__((0, rows - 1)):
        edge_points.remove((0, rows - 1))

    # Generowanie punktów wewnątrz z minimalną odległością 20 od krawędzi
    points = []
    half = int(step_size / 2)
    min_distance_from_edge = half

    for i in range(step_size, rows - min_distance_from_edge, step_size):
        for j in range(step_size, cols - min_distance_from_edge, step_size):
            if matrix[i, j] == 0:
                points.append((j, i))

    # Kombinowanie wszystkich punktów
    all_points = edge_points + points
    combined_points = generate_points(matrix, 250)
    combined_points = list(chain.from_iterable(combined_points))
    combined_points.extend(all_points)

    return combined_points
