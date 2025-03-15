import pygame as pg
from scipy.interpolate import splprep, splev
from math import atan2, cos, sin
from typing import List, Sequence, Tuple

"""
MOST OF THIS IS CHATGPT :(
"""

# <3 ChatGPT
def generate_smooth_track(points: List[Sequence[int]], closed: bool = True, resolution: int = 1000) -> List[Sequence[int]]:
    # Convert points into separate x and y lists
    x, y = zip(*points)
    
    # Prepare spline (no NumPy involved)
    tck, u = splprep([list(x), list(y)], s=0, per=closed)
    
    # Generate smooth curve points
    u_fine = [i / resolution for i in range(resolution)]
    x_smooth, y_smooth = splev(u_fine, tck)

    return list(zip(x_smooth, y_smooth))  # Convert back to list of (x, y) pairs

def offset_point(x: float, y: float, angle: float, distance: float) -> Tuple[float]:
    dx = cos(angle) * distance
    dy = sin(angle) * distance

    return (x + dx, y + dy)

# Function to create inner and outer track boundaries
# <3 ChatGPT
def create_offset_track(points: List[Sequence[int]], offset_distance: int) -> Tuple[List[Sequence[float]]]:
    inner_track = []
    outer_track = []

    # Loop through the points and calculate offsets
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        
        # Calculate angle of the line between consecutive points
        angle = atan2(p2[1] - p1[1], p2[0] - p1[0])

        # Offset points
        inner_point = offset_point(p1[0], p1[1], angle + 3.14 / 2, offset_distance)
        outer_point = offset_point(p1[0], p1[1], angle - 3.14 / 2, offset_distance)

        inner_track.append(inner_point)
        outer_track.append(outer_point)

    # For the last point, repeat the same logic to close the loop
    p1 = points[-1]
    p2 = points[0]  # Closing the loop

    angle = atan2(p2[1] - p1[1], p2[0] - p1[0])

    inner_point = offset_point(p1[0], p1[1], angle + 3.14 / 2, offset_distance)
    outer_point = offset_point(p1[0], p1[1], angle - 3.14 / 2, offset_distance)

    inner_track.append(inner_point)
    outer_track.append(outer_point)

    return inner_track, outer_track

def draw_curb(surface: pg.Surface, track: List[Sequence[int]], curb_width: int = 5):
    for i in range(len(track) - 1):
        x1, y1 = track[i]
        x2, y2 = track[i + 1]

        half_width = (x2 - x1) / 2
        half_height = (y2 - y1) / 2
        
        pg.draw.line(surface, (255, 255, 255), (x1, y1), (x2-half_width, y2-half_height), width=curb_width)

        pg.draw.line(surface, (255, 0, 0), (x1+half_width, y1+half_height), (x2, y2), width=curb_width)

def load_track(filename: str) -> pg.Surface:
    with open(filename, "r") as f:
        points = eval(f.read())

    smooth_track = generate_smooth_track(points)
    inner_track, outer_track = create_offset_track(smooth_track, offset_distance=20)

    track_surface = pg.Surface((1000, 1000), pg.SRCALPHA)

    pg.draw.polygon(track_surface, (100, 100, 100), inner_track)
    pg.draw.polygon(track_surface, (100, 255, 0), outer_track)

    draw_curb(track_surface, outer_track, 5)
    draw_curb(track_surface, inner_track, 5)

    return track_surface