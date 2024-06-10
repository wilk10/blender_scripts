import argparse
import bpy
import bpy_extras
import common
import math
import mathutils
import os


CAMERA = "Camera"
SMOKE_DATA_ASSETS = "assets/smoke_data/static"
SMOKE_EMITTERS = "SmokeEmitters"
SMOKE_OUTPUT_EXTENSION = "static_smoke.json"

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('item', type=str, help='name of the folder in world_map')
    parser.add_argument('filename', type=str, help='name of the file where the model is')
    return parser.parse_args()

def get_camera_view_coords(scene, active_camera, emitter):
    location = emitter.matrix_world.to_translation()
    full_coords = bpy_extras.object_utils.world_to_camera_view(scene, active_camera, location)
    coords = mathutils.Vector((full_coords.x, full_coords.y))
    return coords

def extract_dict_from_target_files(file_path, item):
    output_dict = { "".join(["degree_", str(degree)]): [] for degree in common.DEGREES }
    sprite = common.SpriteSize(item)

    bpy.ops.wm.open_mainfile(filepath=file_path)
    for degree in common.DEGREES:
        common.set_object_as_active(common.EMPTY_ORIGIN)
        bpy.context.active_object.rotation_euler[2] = math.radians(degree)

        common.set_object_as_active(CAMERA)
        emitters = bpy.data.collections.get(SMOKE_EMITTERS)
        for emitter in emitters.objects:
            smoke_emitter_coords = get_camera_view_coords(bpy.context.scene, bpy.context.object, emitter)
            emitter_coords_on_sprite = smoke_emitter_coords * mathutils.Vector((sprite.width, sprite.height))
            key = "".join(["degree_", str(degree)])
            output_dict[key].append(list(emitter_coords_on_sprite))

        if degree == common.DEGREES[-1]:
            bpy.context.active_object.rotation_euler[2] = math.radians(0)
    return output_dict

def main():
    args = parse_arguments()
    model_path = common.get_model_path(args.item, args.filename)
    output_dict = extract_dict_from_target_files(model_path, args.item)
    common.save_smoke_dict_to_path(
        args.item,
        args.filename,
        SMOKE_DATA_ASSETS,
        SMOKE_OUTPUT_EXTENSION,
        output_dict
    )


if __name__ == "__main__":
    main()
