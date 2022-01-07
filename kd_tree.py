import functools
from typing import Optional

from geometric_types import *
from visualizers import KDTree2DVisualizer

import numpy as np


class KDTNode:
    def __init__(self, val, points: Optional[list[Point]]):
        self.value = val
        self.points = points or []
        self.left = None
        self.right = None

    def __str__(self):
        if self.value is None:
            return "leaf " + str(self.points)
        return "split " + str(self.value)

    def __repr__(self):
        return str(self)


class KDTree:
    def __init__(self, dimensions: int, points: list[Point], visualize: bool = False):
        if dimensions != 2 and visualize:
            raise IndexError("I can visualize only 2 dimensions")
        if len(points) == 0:
            raise IndexError("Can't create empty KD-Tree")

        self.visualizer: Optional[KDTree2DVisualizer] = None
        if visualize:
            self.visualizer = KDTree2DVisualizer(points)

        self.dimensions = dimensions

        lower_left_point = functools.reduce(self._lower_left, points)
        upper_right_point = functools.reduce(self._upper_right, points)

        self.points_area = (lower_left_point, upper_right_point)

        self.root = self._build_tree(points, 0, lower_left_point, upper_right_point)
        if self.visualizer is not None:
            self.visualizer.end_tree_building()

    @staticmethod
    def _upper_right(point1: Point, point2: Point):
        return [max(cor1, cor2) for cor1, cor2 in zip(point1, point2)]

    @staticmethod
    def _lower_left(point1: Point, point2: Point):
        return [min(cor1, cor2) for cor1, cor2 in zip(point1, point2)]

    @staticmethod
    def _is_inside_area(point: Point, area: Rectangle):
        return all(map(lambda x: x[0] <= x[1] <= x[2], zip(area[0], point, area[1])))

    def _build_tree(self, points: list[Point], depth: int, lower_left: Point, upper_right: Point):
        if len(points) <= 1:
            return KDTNode(None, points)

        coordinate_number = depth % self.dimensions
        coordinates_values = np.array(list(map(lambda x: x[coordinate_number], points)))
        partially_sorted = np.partition(
            coordinates_values,
            kth=(len(points) // 2 - 1, len(points) // 2),
        )
        v1 = partially_sorted[len(points) // 2 - 1]
        v2 = partially_sorted[len(points) // 2]

        division_val = (v1 + v2) / 2
        
        new_upper_right = upper_right.copy()
        new_upper_right[coordinate_number] = division_val
        new_lower_left = lower_left.copy()
        new_lower_left[coordinate_number] = division_val
        if self.visualizer is not None:
            smaller_split_point = lower_left.copy()
            greater_split_point = upper_right.copy()
            smaller_split_point[depth % self.dimensions] = division_val
            greater_split_point[depth % self.dimensions] = division_val
            self.visualizer.add_split((smaller_split_point, greater_split_point))

        left_points = [p for p in points if p[coordinate_number] <= division_val]
        right_points = [p for p in points if p[coordinate_number] > division_val]

        new_node = KDTNode(division_val, points)

        new_node.left = self._build_tree(left_points, depth + 1, lower_left, new_upper_right)
        new_node.right = self._build_tree(right_points, depth + 1, new_lower_left, upper_right)

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

    @staticmethod
    def get_all_points_in_subtree(root: KDTNode):
        if root is None:
            return []
        return root.points

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

        if self.visualizer is not None:
            self.visualizer.set_current_rectangle(current_region)
        if root.left is None and root.right is None:
            return list(filter(lambda p: self._is_inside_area(p, searched_region), root.points))

        result_points = []

        right_child_region_left_limit = current_region[0].copy()
        right_child_region_left_limit[depth % self.dimensions] = root.value
        left_child_region_right_limit = current_region[1].copy()
        left_child_region_right_limit[depth % self.dimensions] = root.value
        left_region = (current_region[0], left_child_region_right_limit)
        right_region = (right_child_region_left_limit, current_region[1])

        if self.does_rectangle_include(searched_region, left_region):
            result_points += self.get_all_points_in_subtree(root.left)
        elif self.get_intersection(searched_region, left_region) is not None:
            result_points += self._find_points_util(searched_region, root.left, left_region, depth + 1)

            if self.visualizer is not None:
                self.visualizer.set_current_rectangle(current_region)

        if self.does_rectangle_include(searched_region, right_region):
            result_points += self.get_all_points_in_subtree(root.right)
        elif self.get_intersection(searched_region, right_region) is not None:
            result_points += self._find_points_util(searched_region, root.right, right_region, depth + 1)

            if self.visualizer is not None:
                self.visualizer.set_current_rectangle(current_region)

        return result_points

    def find_points_in_area(self, area: Rectangle):
        if self.visualizer is not None:
            self.visualizer.set_searched_rectangle(area)

        points = self._find_points_util(area, self.root, self.points_area, 0)
        if self.visualizer is not None:
            self.visualizer.highlight_points(points)
            self.visualizer.end_searching()

        return points


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
