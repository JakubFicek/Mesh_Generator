import csv

from PIL import Image, ImageDraw
import numpy as np


class Node:
    def __init__(self, matrix, num, x1, y1, x2, y2):
        self.matrix = np.array(matrix)
        self.children = []
        self.min_size = num
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def subdivide(self):
        # zapisanie części macierzy w osobnych macierzach
        sub_matrices = np.array_split(self.matrix, 2, axis=0)
        sub_matrices = [np.array_split(m, 2, axis=1) for m in sub_matrices]

        matrix1, matrix2 = sub_matrices[0][0], sub_matrices[0][1]
        matrix3, matrix4 = sub_matrices[1][0], sub_matrices[1][1]

        # Lewa gora
        self.children.append(Node(matrix1, self.min_size, self.x1, self.y1, self.x1 + len(self.matrix[0]) / 2,
                                  self.y1 + len(self.matrix) / 2))
        # Prawa gora
        self.children.append(Node(matrix2, self.min_size, self.x1 + len(self.matrix[0]) / 2, self.y1, self.x2,
                                  self.y1 + len(self.matrix) / 2))
        # Lewy dol
        self.children.append(
            Node(matrix3, self.min_size, self.x1, self.y1 + len(self.matrix) / 2, self.x1 + len(self.matrix[0]) / 2,
                 self.y2))
        # Prawy dol
        self.children.append(
            Node(matrix4, self.min_size, self.x1 + len(self.matrix[0]) / 2, self.y1 + len(self.matrix) / 2, self.x2,
                 self.y2))

    def check_for_elements(self):
        objects = 0
        max_objects = len(self.matrix) * len(self.matrix[0])
        for row in self.matrix:
            for value in row:
                if value == 1:
                    objects += 1

        if objects == max_objects:
            return 0

        return objects

    def is_not_leaf(self):
        if self.children:
            return True
        else:
            return False

    def build_tree_recursive(self):
        objects = self.check_for_elements()
        if objects > 4:
            # Dodatkowe sprawdzenie, zeby kwadraty nie byly za male, bo staja sie nieczytelne
            if self.matrix.shape[0] > 4 * self.min_size and self.matrix.shape[1] > 4 * self.min_size:
                self.subdivide()
                self.children[0].build_tree_recursive()
                self.children[1].build_tree_recursive()
                self.children[2].build_tree_recursive()
                self.children[3].build_tree_recursive()

    def print_tree_recursive(self, image):
        # określenie koloru linii
        draw = ImageDraw.Draw(image)
        draw_node(draw, self)
        for child in self.children:
            draw_node(draw, child)
            if child.is_not_leaf():
                child.print_tree_recursive(image)
            else:
                draw_line(draw, child)

        return image

    def get_points(self, points):
        for child in self.children:
            if child.is_not_leaf():
                child.get_points(points)
            else:
                p1 = (child.x1, child.y1)
                p2 = (child.x2, child.y2)
                p3 = (child.x2, child.y1)
                p4 = (child.x1, child.y2)
                set1 = set(points)
                set2 = {p1, p2, p3, p4}

                points_to_add = set2 - set1
                points.extend(points_to_add)

        return points

    def get_triangles(self, triangles, points):
        for child in self.children:
            if child.is_not_leaf():
                child.get_triangles(triangles, points)
            else:
                p1 = (child.x1, child.y1)
                p2 = (child.x2, child.y2)
                p3 = (child.x2, child.y1)
                p4 = (child.x1, child.y2)
                if child.check_for_elements() >= 0.7 * len(child.matrix) * len(child.matrix[0]):
                    t1 = (points.index(p1), points.index(p2), points.index(p3), 1)
                    t2 = (points.index(p1), points.index(p2), points.index(p4), 1)
                else:
                    t1 = (points.index(p1), points.index(p2), points.index(p3), 0)
                    t2 = (points.index(p1), points.index(p2), points.index(p4), 0)

                triangles.extend({t1, t2})

        return triangles

    def save_to_txt(self, filename):
        points = []
        triangles = []
        points = self.get_points(points)
        triangles = self.get_triangles(triangles, points)

        with open(filename, 'w') as file:
            file.write("Nodes: (ID, X, Y)\n")
            for i, (x, y) in enumerate(points):
                file.write(f"{i} {x} {y}\n")

            file.write("\nTriangles: (ID, node1ID, node2ID, node3ID, OsnowaOrNot)\n")
            for i, (node1, node2, node3, osnowa) in enumerate(triangles):
                file.write(f"{i} {node1} {node2} {node3} {osnowa}\n")


def draw_node(draw, node):
    draw.rectangle(((node.x1, node.y1), (node.x2, node.y2)), outline=160, fill=None, width=1)


def draw_line(draw, node):
    draw.line(((node.x1, node.y1), (node.x2, node.y2)), fill=160, width=2)


class QuadTree:
    def __init__(self, matrix, filename, num):
        self.matrix = matrix
        self.filename = filename
        self.image = Image.open(filename)
        self.root = Node(matrix, num, 0, 0, self.image.width - 1, self.image.height - 1)
        self.min_size = num

    def build_tree(self):
        self.root.build_tree_recursive()

    def print_tree(self):
        return self.root.print_tree_recursive(self.image)

    def save_to_txt(self):
        self.root.save_to_txt("QuadTreeMesh.txt")
