import functools
from typing import Optional

import numpy as np

from geometric_types import *
from visualizers import KDTree2DVisualizer


class KDTNode:
    def __init__(self, val):
        self.value = val
        self.left = None
        self.right = None

    def __str__(self):
        node_type = "leaf" if isinstance(self.value, list) else "split"
        return node_type + " " + str(self.value)

    def __repr__(self):
        return str(self)


class KDTree:
    def __init__(self, dimensions: int, points: list[Point], visualizer: Optional[KDTree2DVisualizer] = None):
        if dimensions > 2 and visualizer is not None:
            raise ValueError("Can't visualize more than 2 dimensions")

        self.visualizer: Optional[KDTree2DVisualizer] = visualizer

        self.dimensions = dimensions

        lower_left_point = functools.reduce(self._lower_left, points)
        upper_right_point = functools.reduce(self._upper_right, points)

        self.points_area = (lower_left_point, upper_right_point)

        self.root = self._build_tree(points, 0)

    @staticmethod
    def _upper_right(point1: Point, point2: Point):
        return [max(cor1, cor2) for cor1, cor2 in zip(point1, point2)]

    @staticmethod
    def _lower_left(point1: Point, point2: Point):
        return [min(cor1, cor2) for cor1, cor2 in zip(point1, point2)]

    @staticmethod
    def _is_inside_area(point: Point, area: Rectangle):
        return all(map(lambda x: x[0] <= x[1] <= x[2], zip(area[0], point, area[1])))

    def _build_tree(self, points: list[Point], depth: int):
        if len(points) == 0:
            return KDTNode(None)
        if len(points) == 1:
            return KDTNode(points[0])

        coordinate_number = depth % self.dimensions
        v1 = np.partition(points, len(points) // 2 - 1, axis=coordinate_number)[len(points) // 2 - 1][coordinate_number]
        v2 = np.partition(points, len(points) // 2, axis=coordinate_number)[len(points) // 2][coordinate_number]

        division_val = (v1 + v2) / 2

        if self.visualizer is not None:
            mini = min(map(lambda x: x[(depth + 1) % self.dimensions], points))
            maxi = max(map(lambda x: x[(depth + 1) % self.dimensions], points))
            smaller_split_point = [mini, mini]
            greater_split_point = [maxi, maxi]
            smaller_split_point[depth % self.dimensions] = division_val
            greater_split_point[depth % self.dimensions] = division_val
            self.visualizer.add_split((smaller_split_point, greater_split_point))

        left_points = [p for p in points if p[coordinate_number] <= division_val]
        right_points = [p for p in points if p[coordinate_number] > division_val]

        new_node = KDTNode(division_val)

        new_node.left = self._build_tree(left_points, depth + 1)
        new_node.right = self._build_tree(right_points, depth + 1)

        return new_node

    def does_rectangle_include(self, includes: Rectangle, is_included: Rectangle):
        for i in range(self.dimensions):
            if includes[0][i] > is_included[0][i]:
                return False

            if includes[1][i] < is_included[1][i]:
                return False

        return True

    def get_intersection(self, area1: Rectangle, area2: Rectangle) -> Rectangle or None:
        first_point = self._upper_right(area1[0], area2[0])
        second_point = self._lower_left(area1[1], area2[1])

        for i in range(self.dimensions):
            if first_point[i] > second_point[i]:
                return None

        return first_point, second_point

    def get_all_leaves_in_subtree(self, root: KDTNode):
        if root is None or root.value is None:
            return []
        if root.left is None and root.right is None:
            return [root.value]

        return self.get_all_leaves_in_subtree(root.left) + self.get_all_leaves_in_subtree(root.right)

    def _find_points_util(self,
                          searched_region: Rectangle,
                          root: KDTNode,
                          current_region: Rectangle,
                          depth: int) -> list:
        if root.left is None and root.right is None:
            if root.value is None or not self._is_inside_area(root.value, searched_region):
                return []
            return [root.value]

        ans = []

        right_child_region_left_limit = current_region[0].copy()
        right_child_region_left_limit[depth % self.dimensions] = root.value
        left_child_region_right_limit = current_region[1].copy()
        left_child_region_right_limit[depth % self.dimensions] = root.value
        left_region = (current_region[0], left_child_region_right_limit)
        right_region = (right_child_region_left_limit, current_region[1])

        if self.does_rectangle_include(searched_region, left_region):
            ans += self.get_all_leaves_in_subtree(root.left)
        elif self.get_intersection(searched_region, left_region) is not None:
            ans += self._find_points_util(searched_region, root.left, left_region, depth + 1)

        if self.does_rectangle_include(searched_region, right_region):
            ans += self.get_all_leaves_in_subtree(root.right)
        elif self.get_intersection(searched_region, right_region) is not None:
            ans += self._find_points_util(searched_region, root.right, right_region, depth + 1)

        return ans

    def find_points_in_area(self, area: Rectangle):
        return self._find_points_util(area, self.root, self.points_area, 0)


if __name__ == '__main__':
    def conv_to_np_float64_points(points: list[list]) -> list[Point]:
        for p in points:
            for i in range(len(p)):
                p[i] = np.float64(p[i])

        return points


    pts = conv_to_np_float64_points([
        [0, 0], [1, 1], [1, 2], [2, 1],
        # [4, 0], [3, 1], [2, 2], [3, 3]
    ])
    tree = KDTree(2, pts)

    print(tree.find_points_in_area(([np.float64(0), np.float64(0)], [np.float64(1), np.float64(2)])))
