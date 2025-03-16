import pygame
import math

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption('Circle with 10 Points as Polygon')

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Circle settings
center = (200, 200)  # Center of the circle
radius = 200         # Radius of the circle
num_points = 100      # Number of points

# Calculate the points on the circle
points = []
for i in range(num_points):
    angle = 2 * math.pi * i / num_points  # Angle for the point
    x = center[0] + radius * math.cos(angle)
    y = center[1] + radius * math.sin(angle)
    points.append((x, y))

time = 1000*0.5

def shrink(t, p):
    new_points = []
    target_radius = 20
    for point in p:
        angle_to_target = math.atan2(point[1] - t[1], point[0] - t[0])
        distance_to_move = math.dist(point, t) - target_radius
        new_points.append((point[0] - math.cos(angle_to_target) * (distance_to_move / time), point[1] - math.sin(angle_to_target) * (distance_to_move / time)))

    return new_points

target = (150, 150)

clock = pygame.time.Clock()

# Draw the polygon
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

    points = shrink(target, points)

    # Draw the polygon by connecting the points
    pygame.draw.polygon(screen, BLUE, points, 2)

    # Draw the center of the circle for reference
    pygame.draw.circle(screen, (255, 0, 0), center, 5)
    pygame.draw.circle(screen, (0, 255, 0), target, 5)

    pygame.display.flip()

# Quit Pygame
pygame.quit()
