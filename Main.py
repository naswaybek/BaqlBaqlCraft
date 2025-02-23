# Alllll libraries :D
from ursina import *
from perlin_noise import PerlinNoise
from ursina.prefabs.first_person_controller import FirstPersonController
import random
from ursina.lights import AmbientLight

# Initialize the game
app = Ursina()
window.exit_button.visible = False


# Load textures and sounds (I stole them)
textures = {
    "grass": load_texture("textures/grass.png"),
    "dirt": load_texture("textures/dirt.png"),
    "stone": load_texture("textures/stone.png"),
    "brick": load_texture("textures/brick.png"),
    "wood": load_texture("textures/wood.png"),
    "bedrock": load_texture("textures/bedrock.png"),
    "enemy": load_texture("textures/miras.png"),
}

break_sound = Audio("sounds/punch.wav", autoplay=False)
hit_sound = Audio("sounds/hit.wav", autoplay=False)
enemy_death_sound = Audio("sounds/miras_death.wav", autoplay=False)
enemy_sound = Audio("sounds/miras_sound.wav", autoplay=False)
music = Audio("sounds/music.mp3", autoplay=True, loop=True)

# Load sky
sky = Entity(model="sphere", texture=load_texture("textures/sky.png"), scale=1000, double_sided=True)

# Default values
player = None
block_pick = "grass"

# World generation settings and chunk settings
noise = PerlinNoise(octaves=2, seed=2023)
chunk_size = 5
render_distance = 2

# Storing things
chunk_dict = {}

removed_blocks = set()
placed_blocks = {}

mobs = []

# When game starts this function is called
def start_game():
    global player
    menu.enabled = False
    title.enabled = False
    player = FirstPersonController()
    player.position = (0, 10, 0)
    update_chunks()
    spawn_mobs()
    sky.enabled = True
    DirectionalLight().look_at(Vec3(1, -1, -1))

# Starts generating chunks
# Btw I have no idea how it works but it works
def generate_chunk(cx, cz):
    if (cx, cz) in chunk_dict:
        return
    chunk_dict[(cx, cz)] = []
    for x in range(chunk_size):
        for z in range(chunk_size):
            world_x = cx * chunk_size + x
            world_z = cz * chunk_size + z
            if (world_x, 0, world_z) in removed_blocks:
                continue
            voxel = Voxel(position=(world_x, 0, world_z), texture=textures["bedrock"], unbreakable=True)
            chunk_dict[(cx, cz)].append(voxel)
            y = int(noise([world_x / 24, world_z / 24]) * 6) + 1
            if (world_x, y, world_z) in removed_blocks:
                continue
            voxel = Voxel(position=(world_x, y, world_z), texture=textures["grass"])
            chunk_dict[(cx, cz)].append(voxel)

# Unloads chunks that are too far from the player ()
def unload_far_chunks():
    if not player:
        return
    player_chunk_x = int(player.x // chunk_size)
    player_chunk_z = int(player.z // chunk_size)
    to_remove = [(cx, cz) for cx, cz in chunk_dict.keys()
                 if abs(cx - player_chunk_x) > render_distance or abs(cz - player_chunk_z) > render_distance]
    for chunk in to_remove:
        for block in chunk_dict[chunk]:
            destroy(block)
        del chunk_dict[chunk]

# Updates the chunks
def update_chunks():
    if not player:
        return
    player_chunk_x = int(player.x // chunk_size)
    player_chunk_z = int(player.z // chunk_size)
    for cx in range(player_chunk_x - render_distance, player_chunk_x + render_distance + 1):
        for cz in range(player_chunk_z - render_distance, player_chunk_z + render_distance + 1):
            generate_chunk(cx, cz)
    unload_far_chunks()

# Terrain's blocks
class Voxel(Button):
    def __init__(self, position=(0, 0, 0), texture=textures["grass"], unbreakable=False):
        super().__init__(
            parent=scene,
            model="models/block",
            texture=texture,
            position=position,
            scale=0.5,
            color=color.white  # Ensures the block isn’t darkened
        )
        self.unbreakable = unbreakable
        self.disable_shading = True  # Prevents lighting issues


# What happens when inputs are given
    def input(self, key):
        if self.hovered:
            if key == "right mouse down" and block_pick != "sword":
                placed_blocks[tuple(self.position + mouse.normal)] = textures[block_pick]
                Voxel(position=self.position + mouse.normal, texture=textures[block_pick])
            if key == "left mouse down" and not self.unbreakable and block_pick != "sword":
                break_sound.play()
                removed_blocks.add(tuple(self.position))
                destroy(self)

# MIRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAS
class Mob(Entity):
    def __init__(self, position=(0, 5, 0)):
        super().__init__(parent=scene, model="cube", texture=textures["enemy"], position=position, scale=0.6)
        self.speed = 0.02

    def update(self):
        if player and distance(self.position, player.position) < 10:
            if not enemy_sound.playing:
                enemy_sound.play()
            direction = (player.position - self.position).normalized()
            self.position += direction * self.speed
            self.look_at(player.position)
        else:
            enemy_sound.stop()
# Random spawn of Miras nearby player
def spawn_mobs():
    for _ in range(3):
        x = random.randint(int(player.x) - 10, int(player.x) + 10)
        z = random.randint(int(player.z) - 10, int(player.z) + 10)
        mobs.append(Mob(position=(x, 1, z)))

# Some kind of inventory. I'm too lazy for good inventory system :D
def input(key):
    global block_pick
    if key in ["1", "2", "3", "4", "5"]:
        block_pick = ["grass", "dirt", "stone", "brick", "wood"][int(key) - 1]
    if key == "6":
        block_pick = "sword"
    if key in ["q", "escape"]:
        quit()

# Sword system, and I know it is bad
def update():
    update_chunks()
    if block_pick == "sword" and held_keys["left mouse"]:
        for mob in mobs[:]:
            if distance(player.position, mob.position) < 2:
                hit_sound.play()
                enemy_death_sound.play()
                destroy(mob)
                mobs.remove(mob)

# Main Menu
title = Entity(model='quad', texture='textures/baqlbaqlcraft.png', scale=(13.5, 7.8), position=(0, 2, 0))
menu = Entity()
start_button = Button(text="Start Game", scale=(5.4, 1.1), position=(0, -0.1), parent=menu, text_size=2, on_click=start_game)
quit_button = Button(text="Quit", scale=(5.4, 1.1), position=(0, -2), parent=menu, text_size=2, on_click=application.quit)

# Lights
ambient_light = AmbientLight(color=color.rgb(200, 200, 200))

# GAME IS RUNNING :DDDDDDDDD
app.run()
