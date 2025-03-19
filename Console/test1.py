import pygame
from shapely.geometry import Polygon, box
from shapely.affinity import translate

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Efficiently Drawing Visible Polygon")

# Define the player position (this is the center of the viewport)
player_pos = pygame.Vector2(0, 0)  # Start player at the origin (or adjust as needed)

# Define the large polygon (a simple square for the example)
polygon_points = [
    (-500, -500),
    (500, -500),
    (500, 500),
    (-500, 500)
]

# Create a Shapely Polygon object
polygon = Polygon(polygon_points)

# Function to get the camera's viewport as a Shapely box
def get_camera_viewport():
    # Camera is centered on the player's position, with the viewport size equal to screen size
    # In Shapely, the Y-axis increases upwards, so we need to adjust the Y-coordinates
    return box(player_pos.x - screen_width // 2, -player_pos.y - screen_height // 2,
               player_pos.x + screen_width // 2, -player_pos.y + screen_height // 2)

def draw_polygon():
    # Get the visible area of the polygon by intersecting with the camera's viewport
    camera_viewport = get_camera_viewport()
    visible_polygon = polygon.intersection(camera_viewport)
    
    if visible_polygon.is_empty:
        return  # No visible polygon
    
    # Convert the Shapely polygon to a list of points for Pygame drawing
    pygame_polygon_points = [(x, y) for x, y in visible_polygon.exterior.coords]
    
    # Draw the visible portion of the polygon
    pygame.draw.polygon(screen, (255, 0, 0), pygame_polygon_points)

def main():
    global player_pos
    
    clock = pygame.time.Clock()
    
    # Game loop
    running = True
    while running:
        screen.fill((0, 0, 0))  # Clear the screen with black
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update player position (for testing purposes, we'll move the player with arrow keys)
        keys = pygame.key.get_pressed()
        
        # Move player left/right
        if keys[pygame.K_LEFT]:
            player_pos.x -= 5
        if keys[pygame.K_RIGHT]:
            player_pos.x += 5
        
        # Move player up/down with the Y-axis inversion corrected
        if keys[pygame.K_UP]:
            player_pos.y -= 5  # Invert the Y-axis here for correct behavior
        if keys[pygame.K_DOWN]:
            player_pos.y += 5  # Invert the Y-axis here for correct behavior
        
        # Draw the visible portion of the polygon
        draw_polygon()
        
        # Update the screen
        pygame.display.flip()
        
        # Maintain the frame rate
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
