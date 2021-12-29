import functools

import numpy as np

Point = list[np.float64]
Rectangle = tuple[Point, Point]


class KDTNode:
    def __init__(self, val):
        self.value = val
        self.left = None
        self.right = None


class KDTree:
    def __int__(self, dimensions: int, points: list[Point]):
        # self.root = KDTNode(None)
        self.dimensions = dimensions

        self.root = self._build_tree(points, 0)

    def _build_tree(self, points: list[Point], depth: int):
        if len(points) == 1:
            return KDTNode(points[0])

        coordinate_number = depth % self.dimensions
        points.sort(key=functools.cmp_to_key(lambda a, b: a[coordinate_number] - b[coordinate_number]))

        median_i = len(points) // 2
        division_val = points[median_i][coordinate_number]

        new_node = KDTNode(division_val)

        new_node.left = self._build_tree(points[:median_i], depth + 1)
        new_node.right = self._build_tree(points[median_i:], depth + 1)

        return new_node

    def does_rectangle_include(self, includes: Rectangle, is_included: Rectangle):
        for i in range(self.dimensions):
            if includes[0][i] > is_included[0][i]:
                return False

            if includes[1][i] < is_included[1][i]:
                return False

        return False

    def get_minimal_point(self):
        curr = self.root
        while curr.left is not None and curr.right is not None:
            curr = curr.left

        return curr.value

    def get_maximal_point(self):
        curr = self.root
        while curr.left is not None and curr.right is not None:
            curr = curr.right

        return curr.value

    def get_intersection(self, area1: Rectangle, area2: Rectangle) -> Rectangle or None:
        first_point = [max(cor1, cor2) for cor1, cor2 in zip(area1[0], area2[0])]
        second_point = [min(cor1, cor2) for cor1, cor2 in zip(area1[1], area2[1])]

        for i in range(self.dimensions):
            if first_point[i] > second_point[i]:
                return None

        return first_point, second_point

    def get_all_leaves_in_subtree(self, root: KDTNode):
        if root is None:
            return []
        if root.left is None and root.right is None:
            return [root.value]

        return self.get_all_leaves_in_subtree(root.left) + self.get_all_leaves_in_subtree(root.right)

    def _find_points_util(self, searched_region: Rectangle, root: KDTNode, current_region: Rectangle,
                          depth: int) -> list:
        if root.left is None and root.right is None:
            return [root.value]

        ans = []

        right_child_region_left_limit = current_region[0].copy()
        right_child_region_left_limit[depth % self.dimensions] = root.value
        left_child_region_right_limit = current_region[1].copy()
        left_child_region_right_limit[depth % self.dimensions] = root.value
        left_region = (current_region[0], left_child_region_right_limit)
        right_region = (right_child_region_left_limit, current_region[1])

        if self.does_rectangle_include(searched_region, left_region):
            return self.get_all_leaves_in_subtree(root.left)
        elif self.get_intersection(searched_region, left_region) is not None:
            ans += self._find_points_util(searched_region, root.left, left_region, depth + 1)

        if self.does_rectangle_include(searched_region, right_region):
            return self.get_all_leaves_in_subtree(root.right)
        elif self.get_intersection(searched_region, right_region) is not None:
            ans += self._find_points_util(searched_region, root.right, right_region, depth + 1)

        return ans

    def find_points_in_area(self, area: Rectangle):
        min_point = self.get_minimal_point()
        max_point = self.get_maximal_point()
        return self._find_points_util(area, self.root, (min_point, max_point), 0)
