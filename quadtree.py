from random import uniform

from visualizers import QuadtreeVisualizer

class Point2D:
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
        self.subtree_points = []
    

    def _subdivide(self, visualizer):
        lower_left_point, upper_right_point = self.boundary
        mid_point = Point2D((lower_left_point.x + upper_right_point.x) / 2, (upper_right_point.y + lower_left_point.y) / 2)

        self.top_left = _QuadtreeNode((Point2D(lower_left_point.x, mid_point.y), Point2D(mid_point.x, upper_right_point.y)))
        self.top_right = _QuadtreeNode((mid_point, upper_right_point))
        self.bot_right = _QuadtreeNode((Point2D(mid_point.x, lower_left_point.y), Point2D(upper_right_point.x, mid_point.y)))
        self.bot_left = _QuadtreeNode((lower_left_point, mid_point))
        if visualizer is not None:
            visualizer.add_boundary(self.boundary)
        self.divided = True


    def _intersects(self, range):
        lower_left_boundary, upper_right_boundary = self.boundary
        lower_left_range, upper_right_range = range
        return lower_left_boundary.precedes(upper_right_range) and lower_left_range.precedes(upper_right_boundary)

    def _completely_intersects(self, range):
        lower_left_boundary, upper_right_boundary = self.boundary
        lower_left_range, upper_right_range = range
        return lower_left_range.precedes(lower_left_boundary) and upper_right_range.follows(upper_right_boundary)

    def _query_range(self, Quadtree, range, visualizer):
        if not self._intersects(range):
            return

        if self._completely_intersects(range):
            Quadtree.query_res.extend(self.subtree_points)
            if Quadtree.visualizer is not None:
                Quadtree.visualizer.update_query_visualization(range, self.boundary, Quadtree.query_res, self.subtree_points)
            return

        lower_left_range, upper_right_range = range
        added_points = []
        for point in self.points:
            if point.precedes(upper_right_range) and point.follows(lower_left_range):
                Quadtree.query_res.append((point.x, point.y))
                added_points.append((point.x, point.y))
        
        if Quadtree.visualizer is not None:
            Quadtree.visualizer.update_query_visualization(range, self.boundary, Quadtree.query_res, added_points)

        if self.divided:
            self.top_left._query_range(Quadtree, range, visualizer)
            self.top_right._query_range(Quadtree, range, visualizer)
            self.bot_right._query_range(Quadtree, range, visualizer)
            self.bot_left._query_range(Quadtree, range, visualizer)


    def __contains__(self, point):
        lower_left_range, upper_right_range = self.boundary
        return point.precedes(upper_right_range) and point.follows(lower_left_range)
    


class Quadtree:
    def __init__(self, points, boundary, capacity, visualize = None):
        self.boundary = Point2D(boundary[0][0], boundary[0][1]), Point2D(boundary[1][0], boundary[1][1])
        self.capacity = capacity
        self.visualizer = None
        self.query_res = []
        if visualize:
            self.visualizer = QuadtreeVisualizer(points)
            self.visualizer.add_starting_boundary(self.boundary)

        self.root = self._build_tree(map(lambda x: Point2D(x[0], x[1]), points))
        
    
    def insert(self, QTNode, point):
        if not QTNode or point not in QTNode:
            return False

        QTNode.subtree_points.append(point)
        if len(QTNode.points) < self.capacity:
            QTNode.points.append(point)
            if self.visualizer is not None:
                self.visualizer.add_point(point)
            return True
        elif not QTNode.divided:
            QTNode._subdivide(self.visualizer)
            
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
        self.query_res = []
        range = Point2D(range[0][0], range[0][1]), Point2D(range[1][0], range[1][1])

        if self.visualizer is not None:
            self.visualizer.update_query_visualization(range)
        
        self.root._query_range(self, range, self.visualizer)

        if self.visualizer is not None:
            self.visualizer.update_query_visualization(range, None, self.query_res)
        
        return self.query_res