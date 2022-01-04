from random import uniform

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def precedes(self, point):
        return self.x <= point.x and self.y <= point.y

    def follows(self, point):
        return self.x >= point.x and self.y >= point.y

    def __str__(self):
        return f"({self.x}, {self.y})"



class _QuadtreeNode:
    def __init__(self, boundary):
        self.top_left = None
        self.top_right = None
        self.bot_left = None
        self.bot_right = None

        self.divided = False
        self.boundary = boundary
        self.points = []
    

    def _subdivide(self):
        lower_left_point, upper_right_point = self.boundary
        mid_point = Point((lower_left_point.x + upper_right_point.x) / 2, (upper_right_point.y + lower_left_point.y) / 2)

        self.top_left = _QuadtreeNode((Point(lower_left_point.x, mid_point.y), Point(mid_point.x, upper_right_point.y)))
        self.top_right = _QuadtreeNode((mid_point, upper_right_point))
        self.bot_right = _QuadtreeNode((Point(mid_point.x, lower_left_point.y), Point(upper_right_point.x, mid_point.y)))
        self.bot_left = _QuadtreeNode((lower_left_point, mid_point))
        self.divided = True


    def _intersects(self, range):
        lower_left_boundary, upper_right_boundary = self.boundary
        lower_left_range, upper_right_range = range
        return lower_left_boundary.precedes(upper_right_range) and lower_left_range.precedes(upper_right_boundary)


    def _query_range(self, range):
        points_in_range = []

        if not self._intersects(range):
            return []

        lower_left_range, upper_right_range = range
        for point in self.points:
            if point.precedes(upper_right_range) and point.follows(lower_left_range):
                points_in_range.append(point)

        if self.divided:
            points_in_range.extend(self.top_left._query_range(range))
            points_in_range.extend(self.top_right._query_range(range))
            points_in_range.extend(self.bot_right._query_range(range))
            points_in_range.extend(self.bot_left._query_range(range))

        return points_in_range


    def __contains__(self, point):
        lower_left_range, upper_right_range = self.boundary
        return point.precedes(upper_right_range) and point.follows(lower_left_range)
    


class Quadtree:
    def __init__(self, points, boundary, capacity):
        self.capacity = capacity
        self.boundary = boundary
        self.root = self._build_tree(points)
        
    
    def insert(self, QTNode, point):
        if not QTNode or point not in QTNode:
            return False

        if len(QTNode.points) < self.capacity:
            QTNode.points.append(point)
            return True
        elif not QTNode.divided:
            QTNode._subdivide()
            
        if self.insert(QTNode.top_left, point): return True
        if self.insert(QTNode.top_right, point): return True
        if self.insert(QTNode.bot_right, point): return True
        if self.insert(QTNode.bot_left, point): return True

    
    def _build_tree(self, points):
        node = _QuadtreeNode(self.boundary)

        for point in points:
            self.insert(node, point)
        
        return node
    

    def query_range(self, range):
        return self.root._query_range(range)



if __name__ == "__main__":
    points = [Point(round(uniform(0, 10), 3), round(uniform(0, 10), 3)) for _ in range(10)]
    quadtree = Quadtree(points, (Point(0, 0), Point(10, 10)), 4)
    
    print("All points")
    [print(point) for point in points]
    print()

    print("Found points")
    boundary = (Point(2, 2), Point(8, 8))
    [print(point) for point in quadtree.query_range(boundary)]