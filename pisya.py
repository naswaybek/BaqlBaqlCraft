

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader


app = Ursina()
bg_music = Audio("mirasssong.mp3", loop=True, autoplay=True)
# Define a Voxel class.
# By setting the parent to scene and the model to 'cube' it becomes a 3d button.
Entity.default_shader = lit_with_shadows_shader
class Voxel(Button):
    def __init__(self, position=(0,0,0)):
        super().__init__(parent=scene,
            position=position,
            model='cube',
            origin_y=.5,
            texture='grass',
            color=color.hsv(0, 0, random.uniform(.9, 1.0)),
            highlight_color=color.lime,
        )

for z in range(5):
    for x in range(5):
        voxel = Voxel(position=(x,0,z))


def input(key):
    if key == 'left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit:
            Voxel(position=hit_info.entity.position + hit_info.normal)
    if key == 'right mouse down' and mouse.hovered_entity:
        destroy(mouse.hovered_entity)
    if key == "q":
        quit()
sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
Sky()
player =FirstPersonController()
app.run()

