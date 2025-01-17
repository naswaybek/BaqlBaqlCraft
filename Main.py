import pygame
from pygame.locals import *
import random

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Improved Procedural Map with Mobs")

# Colors
WHITE = (255, 255, 255)
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
DIRT_BROWN = (139, 69, 19)
STONE_GRAY = (112, 128, 144)
TREE_BROWN = (160, 82, 45)
LEAF_GREEN = (50, 205, 50)
BLACK = (0, 0, 0)
WATER_BLUE = (0, 105, 148)

# Constants
BLOCK_SIZE = 40
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
ROWS, COLS = SCREEN_HEIGHT // BLOCK_SIZE, SCREEN_WIDTH // BLOCK_SIZE
RENDER_DISTANCE = 12
CHUNK_SIZE = 16  # Number of columns in one chunk

# Player attributes
player_x, player_y = SCREEN_WIDTH // 2, (ROWS // 2 - 1) * BLOCK_SIZE
player_speed = 5
vertical_velocity = 0
is_jumping = False
GRAVITY = 1

# Initialize the map
chunks = {}
mobs = []

class Mob:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.choice([-1, 1])  # -1 for left, 1 for right

    def move(self):
        if random.random() < 0.1:  # 10% chance to change direction
            self.direction *= -1
        self.x += self.direction * BLOCK_SIZE // 2
        self.x = max(0, self.x)

        # Gravity for mobs
        if not is_colliding(self.x, self.y + BLOCK_SIZE):
            self.y += BLOCK_SIZE

# Generate terrain

def generate_chunk(chunk_x):
    chunk = {}
    for col in range(chunk_x * CHUNK_SIZE, (chunk_x + 1) * CHUNK_SIZE):
        # Base height and terrain layers
        surface_height = random.randint(ROWS // 2, ROWS // 2 + 3)
        stone_layer_start = surface_height + random.randint(3, 5)
        for row in range(surface_height, ROWS):
            if row < stone_layer_start:
                chunk[(col, row)] = DIRT_BROWN
            elif row < ROWS - 2:
                chunk[(col, row)] = STONE_GRAY
            else:  # Deep stone or bedrock
                chunk[(col, row)] = BLACK

        # Add trees on the surface
        if random.random() < 0.15 and surface_height - 4 > 0:  # 15% chance for trees
            chunk[(col, surface_height - 1)] = TREE_BROWN
            for tree_row in range(surface_height - 4, surface_height - 1):
                chunk[(col, tree_row)] = TREE_BROWN
            for leaf_col in range(col - 2, col + 3):
                for leaf_row in range(surface_height - 5, surface_height - 2):
                    if random.random() < 0.8:  # Make the leaves a bit scattered
                        chunk[(leaf_col, leaf_row)] = LEAF_GREEN

        # Add caves
        if random.random() < 0.08:  # 8% chance for a cave in a column
            if stone_layer_start <= ROWS - 5:  # Ensure valid range
                cave_start = random.randint(stone_layer_start, ROWS - 5)
                cave_height = random.randint(2, 5)
                for cave_row in range(cave_start, cave_start + cave_height):
                    if (col, cave_row) in chunk:
                        del chunk[(col, cave_row)]

        # Add water pools on surface occasionally
        if random.random() < 0.05 and surface_height < ROWS - 2:  # 5% chance for water
            for water_row in range(surface_height, surface_height + 2):
                chunk[(col, water_row)] = WATER_BLUE

    return chunk

# Helper functions
def get_chunk(chunk_x):
    """Retrieve or generate a chunk."""
    if chunk_x not in chunks:
        chunks[chunk_x] = generate_chunk(chunk_x)
    return chunks[chunk_x]

def is_colliding(x, y):
    """Check if a position collides with the terrain."""
    col, row = x // BLOCK_SIZE, y // BLOCK_SIZE
    chunk_x = col // CHUNK_SIZE
    chunk = get_chunk(chunk_x)
    return (col, row) in chunk

def render_visible_area():
    """Render all visible chunks and blocks within render distance."""
    start_col = (player_x // BLOCK_SIZE) - RENDER_DISTANCE
    end_col = (player_x // BLOCK_SIZE) + RENDER_DISTANCE
    start_chunk = start_col // CHUNK_SIZE
    end_chunk = end_col // CHUNK_SIZE

    for chunk_x in range(start_chunk, end_chunk + 1):
        chunk = get_chunk(chunk_x)
        for (col, row), color in chunk.items():
            if start_col <= col <= end_col and 0 <= row < ROWS:
                rect = pygame.Rect(col * BLOCK_SIZE - camera_x, row * BLOCK_SIZE - camera_y, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)  # Outline for blocks

def render_mobs():
    """Render all mobs on the screen."""
    for mob in mobs:
        rect = pygame.Rect(mob.x - camera_x, mob.y - camera_y, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(screen, (255, 0, 0), rect)  # Draw mobs in red

# Initialize mobs
for _ in range(5):  # Spawn 5 mobs at random positions
    mob_x = random.randint(0, SCREEN_WIDTH)
    mob_y = random.randint(0, SCREEN_HEIGHT // 2) * BLOCK_SIZE
    mobs.append(Mob(mob_x, mob_y))

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(SKY_BLUE)

    # Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False

        elif event.type == MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            col, row = (mouse_x + camera_x) // BLOCK_SIZE, (mouse_y + camera_y) // BLOCK_SIZE
            chunk_x = col // CHUNK_SIZE
            chunk = get_chunk(chunk_x)
            if event.button == 1:  # Left click to break block
                if (col, row) in chunk:
                    del chunk[(col, row)]
            elif event.button == 3:  # Right click to place block
                if (col, row) not in chunk:
                    chunk[(col, row)] = DIRT_BROWN

    # Movement keys
    keys = pygame.key.get_pressed()
    if keys[K_a] and not is_colliding(player_x - player_speed, player_y):
        player_x -= player_speed
    if keys[K_d] and not is_colliding(player_x + player_speed + BLOCK_SIZE - 1, player_y):
        player_x += player_speed
    if keys[K_w] and not is_jumping and is_colliding(player_x, player_y + BLOCK_SIZE):
        vertical_velocity = -15
        is_jumping = True

    # Gravity
    vertical_velocity += GRAVITY
    player_y += vertical_velocity

    if vertical_velocity > 0 and is_colliding(player_x, player_y + BLOCK_SIZE):  # Landing
        player_y = (player_y // BLOCK_SIZE) * BLOCK_SIZE
        vertical_velocity = 0
        is_jumping = False

    if vertical_velocity < 0 and is_colliding(player_x, player_y):  # Hitting ceiling
        player_y = (player_y // BLOCK_SIZE + 1) * BLOCK_SIZE
        vertical_velocity = 0

    # Update camera position
    camera_x = player_x - SCREEN_WIDTH // 2
    camera_y = player_y - SCREEN_HEIGHT // 2

    # Update mobs
    for mob in mobs:
        mob.move()

    # Render visible area and mobs
    render_visible_area()
    render_mobs()

    # Draw the player
    pygame.draw.rect(screen, (0, 0, 255), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BLOCK_SIZE, BLOCK_SIZE))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
