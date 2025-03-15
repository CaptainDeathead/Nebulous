import pygame as pg
import matplotlib.pyplot as plt
import os
from scipy.interpolate import splprep, splev
from math import dist
from time import time

pg.init()

track_path = input(f"Enter track name (blank for empty): {os.getcwd()}$ ")

if track_path.strip() == "":
    points = []
else:
    with open(track_path, "r") as f:
        points_raw = f.read()

    points = eval(points_raw)

drag_point_index = None 

screen = pg.display.set_mode((1000, 1000))

# Function to generate smooth track without NumPy
def generate_smooth_track(points, closed=True, resolution=1000):
    # Convert points into separate x and y lists
    x, y = zip(*points)
    
    # Prepare spline (no NumPy involved)
    tck, u = splprep([list(x), list(y)], s=0, per=closed)
    
    # Generate smooth curve points
    u_fine = [i / resolution for i in range(resolution)]
    x_smooth, y_smooth = splev(u_fine, tck)

    return list(zip(x_smooth, y_smooth))  # Convert back to list of (x, y) pairs

while 1:
    screen.fill((0, 0, 0))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()

        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                selected_point = False

                for point in points:
                    if dist(point, event.pos) < 15:
                        drag_point_index = points.index(point)
                        selected_point = True

                if not selected_point:
                    if drag_point_index is None:
                        index = 0
                    else:
                        index = drag_point_index

                    points.insert(index, list(event.pos))
                    drag_point_index = index

            elif event.button == 3:
                if drag_point_index is not None:
                    points.pop(drag_point_index)

                    if len(points) > 1:
                        drag_point_index = -1
                    else:
                        drage_point = None

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                with open(f"track_{int(time())}.track", "w") as f:
                    f.write(str(points))

    if pg.mouse.get_pressed()[0]:
        if drag_point_index is not None:
            points[drag_point_index][0] = pg.mouse.get_pos()[0]
            points[drag_point_index][1] = pg.mouse.get_pos()[1]

    try:
        smooth_track = generate_smooth_track(points)
        pg.draw.aalines(screen, (0, 255, 0), True, smooth_track)
    except:
        ...

    for point in points:
        pg.draw.circle(screen, (255, 255, 255), point, 5)

    if drag_point_index is not None:
        pg.draw.circle(screen, (255, 0, 0), points[drag_point_index], 5)

    pg.display.flip()