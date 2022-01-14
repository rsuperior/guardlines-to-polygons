from functools import cmp_to_key

class Rect:
    def __init__(self, x, y, w, h, name=None):
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __repr__(self):
        return '<Rect %d,%d,%d,%d name=%s>' % \
                (self.x, self.y, self.w, self.h, self.name)

    def __eq__(self, other):
        return self.x == other.x and \
                self.y == other.y and \
                self.w == other.w and \
                self.h == other.h

    def left(self):
        return self.x

    def right(self):
        return self.x + self.w

    def top(self):
        return self.y

    def bottom(self):
        return self.y + self.h

    def intersects(self, other):
        return (
            other.left() < self.right() and \
            self.left() < other.right() and \
            other.top() < self.bottom() and \
            self.top() < other.bottom()
        )

    def adjoins(self, other):
        """ I have a feeling this could be simpler """

        return (
            (self.left() == other.right() and \
                other.top() < self.bottom() and \
                self.top() < other.bottom()
            ) or \
            (self.right() == other.left() and \
                other.top() < self.bottom() and \
                self.top() < other.bottom()
            ) or \
            (self.bottom() == other.top() and
                other.left() < self.right() and \
                self.left() < other.right()
            ) or \
            (self.top() == other.bottom() and
                other.left() < self.right() and \
                self.left() < other.right()
            )
        )

    def polygon(self):
        return (
            (self.x, self.y),
            (self.x + self.w, self.y),
            (self.x + self.w, self.y + self.h), 
            (self.x, self.y + self.h)
        )

    def corners(self):
        return (
            (self.left(), self.top()),
            (self.right(), self.bottom())
        )


def group_adjacent_rects(rects):
    rects = rects.copy()
    groups = []

    while rects:
        rect = rects.pop()
        group = [rect]
        indexes_to_remove = []
        group_index = 0

        while group_index < len(group):
            for i in range(len(rects)):
                if rects[i].adjoins(group[group_index]):
                    group.append(rects[i])
                    indexes_to_remove.append(i)

            if indexes_to_remove:
                for i in reversed(indexes_to_remove):
                    del rects[i]
                indexes_to_remove.clear()

            group_index += 1

        groups.append(group)

    return groups


def find_intersections_in_rects(rects):
    intersections = []
    start_at = 0

    for r in rects:
        for s in rects[start_at:]:
            if r == s:
                continue
            elif r.intersects(s):
                intersections.append((r, s))

        start_at += 1

    return intersections


def adjacent_rects_corners_to_polygons(rects_corners):
    """ This function has only trivial differences from a very helpful Stack
        Overflow post - https://stackoverflow.com/a/13851341 """
        
    points = set()
    for (x1, y1), (x2, y2) in rects_corners:
        for pt in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
            if pt in points: # Shared vertex, remove it.
                points.remove(pt)
            else:
                points.add(pt)
    points = list(points)

    def y_then_x(a, b):
        if a[1] < b[1] or (a[1] == b[1] and a[0] < b[0]):
            return -1
        elif a == b:
            return 0
        else:
            return 1

    sort_x = sorted(points)
    sort_y = sorted(points, key=cmp_to_key(y_then_x))

    edges_h = {}
    edges_v = {}

    i = 0
    while i < len(points):
        curr_y = sort_y[i][1]
        while i < len(points) and sort_y[i][1] == curr_y:
            edges_h[sort_y[i]] = sort_y[i + 1]
            edges_h[sort_y[i + 1]] = sort_y[i]
            i += 2
    i = 0
    while i < len(points):
        curr_x = sort_x[i][0]
        while i < len(points) and sort_x[i][0] == curr_x:
            edges_v[sort_x[i]] = sort_x[i + 1]
            edges_v[sort_x[i + 1]] = sort_x[i]
            i += 2

    # Get all the polygons.
    polygons = []
    while edges_h:
        # We can start with any point.
        polygon = [(edges_h.popitem()[0], 0)]
        while True:
            curr, e = polygon[-1]
            if e == 0:
                next_vertex = edges_v.pop(curr)
                polygon.append((next_vertex, 1))
            else:
                next_vertex = edges_h.pop(curr)
                polygon.append((next_vertex, 0))
            if polygon[-1] == polygon[0]:
                # Closed polygon
                polygon.pop()
                break
        # Remove implementation-markers from the polygon.
        poly = [point for point, _ in polygon]
        for vertex in poly:
            if vertex in edges_h: edges_h.pop(vertex)
            if vertex in edges_v: edges_v.pop(vertex)

        polygons.append(poly)

    return polygons
