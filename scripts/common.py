import bpy
import os
import json
import pathlib


BLENDER = "game/blender/"
DEGREES = [0, 90, 180, 270]
EMPTY_ORIGIN = "Origin"
ITEM_DIMS = {
    'big_carriage': [1, 1, 1],
    'cart': [1, 1, 1],
    'city': [1, 1, 1],
    'coal_mine': [1, 2, 1],
    'depot': [1, 2, 1],
    'harbour': [2, 3, 1],
    'harbour_mask': [2, 3, 1],
    'industrial_farm_with_fields': [2, 3, 1],
    'iron_ore_mine': [1, 2, 1],
    'local_farm_with_fields': [2, 2, 1],
    'locomotive': [1, 1, 1],
    'logging_camp': [1, 1, 1],
    'ship': [1, 1, 1],
    'steel_works': [2, 2, 1],
    'stonemason': [1, 1, 1],
    'suburbs': [1, 1, 1],
    'town': [1, 1, 1],
    'train_station': [3, 2, 1],
    'truck': [1, 1, 1],
    'wagon': [1, 1, 1],
}
MODELS = """3d models"""
RENDERS = "renders"
WORLD_MAP = "world_map"

class SpriteSize:
    DEFAULT_SCALE = 1
    SHIP = "ship"
    SHIP_SCALE = 2
    TILE_WIDTH = 64
    TILE_HEIGHT = 32

    def __init__(self, item: str, extra_scale: int=1):
        sprite_scale = self.get_sprite_scale(item, extra_scale)
        item_dims = ITEM_DIMS[item]
        self.width = int(self.calculate_sprite_width(item_dims) * sprite_scale)
        self.height = int(self.calculate_sprite_height(item_dims) * sprite_scale)

    def get_sprite_scale(self, item, extra_scale):
        if item == self.SHIP:
            sprite_scale = self.SHIP_SCALE * extra_scale
        else:
            sprite_scale = self.DEFAULT_SCALE * extra_scale
        return sprite_scale

    def calculate_sprite_width(self, item_dims):
        x = item_dims[0]
        y = item_dims[1]
        sprite_width = (self.TILE_WIDTH / 2) * (x + y)
        return sprite_width

    def calculate_sprite_height(self, item_dims):
        sprite_width = self.calculate_sprite_width(item_dims)
        z = item_dims[2]
        sprite_height = (sprite_width / 2) + (self.TILE_HEIGHT * z)
        return sprite_height

def get_blender_dir():
    current_dir = pathlib.Path(os.getcwd())
    gamedev = current_dir.parent.parent.parent
    return gamedev.joinpath(f'{BLENDER}')

def get_or_create_renders_dir(item, version):
    blender_dir = get_blender_dir()
    renders_dir = blender_dir.joinpath(f'{RENDERS}/{WORLD_MAP}/{item}/{version}/')
    if not os.path.exists(renders_dir):
        os.makedirs(renders_dir, exist_ok=False)
    print(f'renders_dir: {renders_dir}')
    return renders_dir

def get_model_path(item, filename):
    blender_dir = get_blender_dir()
    model_dir = blender_dir.joinpath(f'{MODELS}/{WORLD_MAP}/{item}/')
    model_path = os.path.join(model_dir, f'{filename}.blend')
    return model_path

def find_files_to_render(item, version):
    blender_dir = get_blender_dir()
    animations = blender_dir.joinpath(f'{MODELS}/{WORLD_MAP}/{item}/{version}/')
    output_files = []
    for root, _dirs, files in os.walk(animations, topdown=False):
        for name in files:
            if name[-6:] == ".blend":
                output_files.append(os.path.join(root, name))
    return output_files

def prepare_frame_filenames(n_frames):
    filenames = []
    for id in range(n_frames):
        frame_id = id + 1
        filename = f'{frame_id:04d}.png'
        filenames.append(filename)
    return filenames

def set_object_as_active(name):
    object = bpy.context.scene.objects[name]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = object
    object.select_set(True)

def save_smoke_dict_to_path(item, version, target_dir, extension, dict_to_save):
    current_dir = pathlib.Path(os.getcwd())
    target_dir = current_dir.joinpath(f'{target_dir}/')
    print(f'target_dir: {target_dir}')

    output_filename =  f'{item}_{version}.{extension}'
    print(f'output_filename: {output_filename}')

    target_path = os.path.join(target_dir, output_filename)
    print(f'target_path: {target_path}')

    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(dict_to_save, f, ensure_ascii=False, indent=4)
