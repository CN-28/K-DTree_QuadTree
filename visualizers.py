import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mcoll
from matplotlib.widgets import Button
import json as js

from geometric_types import *

TOLERANCE = 0.15


def dist(point1, point2):
    return np.sqrt(np.power(point1[0] - point2[0], 2) + np.power(point1[1] - point2[1], 2))


def upper_right(point1: Point, point2: Point):
    return [max(cor1, cor2) for cor1, cor2 in zip(point1, point2)]


def lower_left(point1: Point, point2: Point):
    return [min(cor1, cor2) for cor1, cor2 in zip(point1, point2)]


def upper_left(point1: Point, point2: Point):
    return [min(point1[0], point2[0]), max(point1[1], point2[1])]


def lower_right(point1: Point, point2: Point):
    return [max(point1[0], point2[0]), min(point1[1], point2[1])]


class _ButtonCallback(object):
    def __init__(self, scenes):
        self.i = 0
        self.scenes = scenes
        self.adding_points = False
        self.added_points = []
        self.adding_lines = False
        self.added_lines = []
        self.adding_rects = False
        self.added_rects = []
        self.ax = None
        self.new_line_point = None
        self.rect_points = None

    def set_axes(self, ax):
        self.ax = ax

    def next(self, event):
        self.i = (self.i + 1) % len(self.scenes)
        self.draw(autoscaling=True)

    def prev(self, event):
        self.i = (self.i - 1) % len(self.scenes)
        self.draw(autoscaling=True)

    def add_point(self, event):
        self.adding_points = not self.adding_points
        self.new_line_point = None
        if self.adding_points:
            self.adding_lines = False
            self.adding_rects = False
            self.added_points.append(PointsCollection([]))

    def add_line(self, event):
        self.adding_lines = not self.adding_lines
        self.new_line_point = None
        if self.adding_lines:
            self.adding_points = False
            self.adding_rects = False
            self.added_lines.append(LinesCollection([]))

    def add_rect(self, event):
        self.adding_rects = not self.adding_rects
        self.new_line_point = None
        if self.adding_rects:
            self.adding_points = False
            self.adding_lines = False
            self.new_rect()

    def new_rect(self):
        self.added_rects.append(LinesCollection([]))
        self.rect_points = []

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        new_point = (event.xdata, event.ydata)
        if self.adding_points:
            self.added_points[-1].add_points([new_point])
            self.draw(autoscaling=False)
        elif self.adding_lines:
            if self.new_line_point is not None:
                self.added_lines[-1].add([self.new_line_point, new_point])
                self.new_line_point = None
                self.draw(autoscaling=False)
            else:
                self.new_line_point = new_point
        elif self.adding_rects:
            if len(self.rect_points) == 0:
                self.rect_points.append(new_point)
            elif len(self.rect_points) == 1:
                self.added_rects[-1].add([self.rect_points[-1], new_point])
                self.rect_points.append(new_point)
                self.draw(autoscaling=False)
            elif len(self.rect_points) > 1:
                if dist(self.rect_points[0], new_point) < (
                        np.mean([self.ax.get_xlim(), self.ax.get_ylim()]) * TOLERANCE):
                    self.added_rects[-1].add([self.rect_points[-1], self.rect_points[0]])
                    self.new_rect()
                else:
                    self.added_rects[-1].add([self.rect_points[-1], new_point])
                    self.rect_points.append(new_point)
                self.draw(autoscaling=False)

    def draw(self, autoscaling=True):
        if not autoscaling:
            x_lim = self.ax.get_xlim()
            y_lim = self.ax.get_ylim()
        self.ax.clear()
        for collection in (self.scenes[self.i].points + self.added_points):
            if len(collection.points) > 0:
                self.ax.scatter(*zip(*(np.array(collection.points))), **collection.kwargs)
        for collection in (self.scenes[self.i].lines + self.added_lines + self.added_rects):
            self.ax.add_collection(collection.get_collection())
        self.ax.autoscale(autoscaling)
        if not autoscaling:
            self.ax.set_xlim(x_lim)
            self.ax.set_ylim(y_lim)
        plt.draw()


# %% md


class Scene:
    def __init__(self, points=None, lines=None):
        self.points = points or []
        self.lines = lines or []


class PointsCollection:
    def __init__(self, points, **kwargs):
        self.points = points
        self.kwargs = kwargs

    def add_points(self, points):
        self.points = self.points + points


class LinesCollection:
    def __init__(self, lines, **kwargs):
        self.lines = lines
        self.kwargs = kwargs

    def add(self, line):
        self.lines.append(line)

    def get_collection(self):
        return mcoll.LineCollection(self.lines, **self.kwargs)


class Plot:
    def __init__(self, scenes=None, points=None, lines=None, json=None):
        if points is None:
            points = []
        if lines is None:
            lines = []
        self.callback = None
        self.widgets = None
        if json is None:
            self.scenes = scenes or [Scene()]
            if points or lines:
                self.scenes[0].points = points
                self.scenes[0].lines = lines
        else:
            self.scenes = [Scene([PointsCollection(pointsCol) for pointsCol in scene["points"]],
                                 [LinesCollection(linesCol) for linesCol in scene["lines"]])
                           for scene in js.loads(json)]

    def __configure_buttons(self):
        plt.subplots_adjust(bottom=0.2)
        ax_prev = plt.axes([0.6, 0.05, 0.15, 0.075])
        ax_next = plt.axes([0.76, 0.05, 0.15, 0.075])
        ax_add_point = plt.axes([0.44, 0.05, 0.15, 0.075])
        ax_add_line = plt.axes([0.28, 0.05, 0.15, 0.075])
        ax_add_rect = plt.axes([0.12, 0.05, 0.15, 0.075])
        b_next = Button(ax_next, 'Next')
        b_next.on_clicked(self.callback.next)
        b_prev = Button(ax_prev, 'Previous')
        b_prev.on_clicked(self.callback.prev)
        b_add_point = Button(ax_add_point, 'Add point')
        b_add_point.on_clicked(self.callback.add_point)
        b_add_line = Button(ax_add_line, 'Add line')
        b_add_line.on_clicked(self.callback.add_line)
        b_add_rect = Button(ax_add_rect, 'Add figure')
        b_add_rect.on_clicked(self.callback.add_rect)
        return [b_prev, b_next, b_add_point, b_add_line, b_add_rect]

    def add_scene(self, scene):
        self.scenes.append(scene)

    def add_scenes(self, scenes):
        self.scenes = self.scenes + scenes

    def toJson(self):
        return js.dumps([{"points": [np.array(pointCol.points).tolist() for pointCol in scene.points],
                          "lines": [linesCol.lines for linesCol in scene.lines]}
                         for scene in self.scenes])

    def get_added_points(self):
        if self.callback:
            return self.callback.added_points
        else:
            return None

    def get_added_lines(self):
        if self.callback:
            return self.callback.added_lines
        else:
            return None

    def get_added_figure(self):
        if self.callback:
            return self.callback.added_rects
        else:
            return None

    def get_added_elements(self):
        if self.callback:
            return Scene(self.callback.added_points, self.callback.added_lines + self.callback.added_rects)
        else:
            return None

    def draw(self):
        plt.close()
        fig = plt.figure()
        self.callback = _ButtonCallback(self.scenes)
        self.widgets = self.__configure_buttons()
        ax = plt.axes(autoscale_on=False)
        self.callback.set_axes(ax)
        fig.canvas.mpl_connect('button_press_event', self.callback.on_click)
        plt.show()
        self.callback.draw()

    @staticmethod
    def save_to_file(self, file_name: str):
        plt.savefig(file_name + '.png' if file_name.find('.') == -1 else file_name)


class KDTree2DVisualizer:
    def __init__(self, all_points: list[Point]):
        self.scenes = []
        self.points = all_points
        self.highlighted_points = []
        self.lines = []
        self.current_rectangle_lines = []
        self.searched_rectangle_lines = []
        self.tree_building_scenes = []
        self.searches = []

        self.scenes.append(self._create_scene())

    def get_tree_building_plot(self):
        return Plot(self.tree_building_scenes)

    def get_searching_plot(self, i: int = -1):
        if len(self.searches) <= 0:
            return Plot()

        return Plot(self.searches[i])

    def end_tree_building(self):
        self.tree_building_scenes = self.scenes
        self.scenes = []

    def end_searching(self):
        self.searches.append(self.scenes)
        self.scenes = []

    def add_split(self, line: Line):
        self.lines.append(line)
        self.scenes.append(self._create_scene())

    def _create_scene(self):
        return Scene(
            points=[
                PointsCollection(
                    points=self.points,
                    color='black'
                ),
                PointsCollection(
                    points=self.highlighted_points,
                    color='orange'),
            ],
            lines=[
                LinesCollection(
                    lines=self.lines.copy(),
                    color='blue'
                ),
                LinesCollection(
                    lines=self.current_rectangle_lines.copy(),
                    color='green'
                ),
                LinesCollection(
                    lines=self.searched_rectangle_lines.copy(),
                    color='red'
                )
            ]
        )

    def highlight_points(self, points: list[Point]):
        self.highlighted_points = points
        self.scenes.append(self._create_scene())

    def set_current_rectangle(self, rectangle: Rectangle):
        self.current_rectangle_lines.clear()
        for line in self._convert_rectangle_to_lines(rectangle):
            self.current_rectangle_lines.append(line)

        self.scenes.append(self._create_scene())

    def set_searched_rectangle(self, rectangle: Rectangle):
        self.searched_rectangle_lines.clear()
        for line in self._convert_rectangle_to_lines(rectangle):
            self.searched_rectangle_lines.append(line)

        self.scenes.append(self._create_scene())

    @staticmethod
    def _convert_rectangle_to_lines(rectangle: Rectangle):
        rectangle_lines = [(lower_left(*rectangle), lower_right(*rectangle)),
                           (lower_left(*rectangle), upper_left(*rectangle)),
                           (lower_right(*rectangle), upper_right(*rectangle)),
                           (upper_left(*rectangle), upper_right(*rectangle))]

        return rectangle_lines



class QuadtreeVisualizer:
    def __init__(self, points):
        self.lines = []
        self.scenes = [Scene([PointsCollection(points)])]
        self.points = []
        self.scenes_query = []
       
        
    def create_build_plot(self):
        return Plot(self.scenes)

    def create_query_plot(self):
        return Plot(self.scenes_query)

    def _update_scenes(self):
        self.scenes.append(Scene([PointsCollection(self.points.copy())], [LinesCollection(self.lines.copy())]))
    

    def add_point(self, point):
        self.points.append((point.x, point.y))
        self._update_scenes()


    def add_boundary(self, boundary):
        lower_left_point, upper_right_point = boundary
        mid_point = ((lower_left_point.x + upper_right_point.x) / 2, (upper_right_point.y + lower_left_point.y) / 2)

        self._add_boundary_util(((lower_left_point.x, mid_point[1]), (mid_point[0], upper_right_point.y)))
        self._add_boundary_util((mid_point, (upper_right_point.x, upper_right_point.y)))
        self._add_boundary_util(((mid_point[0], lower_left_point.y), (upper_right_point.x, mid_point[1])))
        self._add_boundary_util(((lower_left_point.x, lower_left_point.y), mid_point))

        self._update_scenes()


    def add_starting_boundary(self, boundary):
        lower_left_point, upper_right_point = boundary
        self._add_boundary_util(((lower_left_point.x, lower_left_point.y), (upper_right_point.x, upper_right_point.y)))
        self._update_scenes()


    def _add_boundary_util(self, boundary):
        lower_left_point, upper_right_point = boundary
        upper_left_point = (lower_left_point[0], upper_right_point[1])
        lower_right_point = (upper_right_point[0], lower_left_point[1])

        self.lines.append([lower_left_point, lower_right_point])
        self.lines.append([lower_left_point, upper_left_point])
        self.lines.append([upper_left_point, upper_right_point])
        self.lines.append([upper_right_point, lower_right_point])


    def update_query_visualization(self, searched_area_boundary, node_boundary = None, points_in_range = None, added_points = None):
        lower_left_area_point, upper_right_area_point = (searched_area_boundary[0].x, searched_area_boundary[0].y), (searched_area_boundary[1].x, searched_area_boundary[1].y)
        upper_left_area_point, lower_right_area_point = (lower_left_area_point[0], upper_right_area_point[1]), (upper_right_area_point[0], lower_left_area_point[1])
        searched_area_lines = [[lower_left_area_point, lower_right_area_point], [lower_left_area_point, upper_left_area_point], [upper_left_area_point, upper_right_area_point], [upper_right_area_point, lower_right_area_point]]

        if searched_area_boundary is not None and node_boundary is None and points_in_range is None:
            self.scenes_query.append(Scene([PointsCollection(self.points.copy())], [LinesCollection(self.lines.copy()), LinesCollection(searched_area_lines.copy(), color = "green")]))

        elif node_boundary is None:
            self.scenes_query.append(Scene([PointsCollection(self.points.copy()), PointsCollection(points_in_range.copy(), color = "green")], [LinesCollection(self.lines.copy()), LinesCollection(searched_area_lines.copy(), color = "green")]))

        else:
            lower_left_boundary_point, upper_right_boundary_point = (node_boundary[0].x, node_boundary[0].y), (node_boundary[1].x, node_boundary[1].y)
            upper_left_boundary_point, lower_right_boundary_point = (lower_left_boundary_point[0], upper_right_boundary_point[1]), (upper_right_boundary_point[0], lower_left_boundary_point[1])
            node_boundary_lines = [[lower_left_boundary_point, lower_right_boundary_point], [lower_left_boundary_point, upper_left_boundary_point], [upper_left_boundary_point, upper_right_boundary_point], [upper_right_boundary_point, lower_right_boundary_point]]
            self.scenes_query.append(Scene([PointsCollection(self.points.copy()), PointsCollection(points_in_range.copy(), color = "green"), PointsCollection(added_points.copy(), color = "red")], [LinesCollection(self.lines.copy()), LinesCollection(node_boundary_lines.copy(), color = "red"), LinesCollection(searched_area_lines.copy(), color = "green")]))