import argparse
import bpy
import bpy_extras
import common
import mathutils
import os


CAMERA = "Camera.001"
DIRECTION_REFERENCE = "DirectionReference"
DIRECTIONS_MAP = {
    "BL-BR": "BottomLeftBottomRight",
    "BL-TL": "BottomLeftTopLeft",
    "BL-TR": "BottomLeftTopRight",
    "BR-BL": "BottomRightBottomLeft",
    "BR-TL": "BottomRightTopLeft",
    "BR-TR": "BottomRightTopRight",
    "TL-BL": "TopLeftBottomLeft",
    "TL-BR": "TopLeftBottomRight",
    "TL-TR": "TopLeftTopRight",
    "TR-BL": "TopRightBottomLeft",
    "TR-BR": "TopRightBottomRight",
    "TR-TL": "TopRightTopLeft",
}
SMOKE_DATA_ASSETS = "assets/smoke_data/moving"
SMOKE_EMITTER = "SmokeEmitter"
SMOKE_OUTPUT_EXTENSION = "moving_smoke.json"

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('item', type=str, help='name of the folder in world_map')
    parser.add_argument('version', type=str, help='name of the file where the model is')
    parser.add_argument('--n_frames', type=int, default=24)
    return parser.parse_args()

def find_target_files(item, version):
    blender_dir = common.get_blender_dir()
    animations = blender_dir.joinpath(f'{common.MODELS}/{common.WORLD_MAP}/{item}/{version}/')
    target_files = []
    for root, _directories, files in os.walk(animations, topdown=False):
        for name in files:
            if name[-6:] == ".blend":
                target_files.append(os.path.join(root, name))
    return target_files

def get_camera_view_coords(scene, active_camera, name):
    object = bpy.context.scene.objects[name]
    location = object.matrix_world.to_translation()
    full_coords = bpy_extras.object_utils.world_to_camera_view(scene, active_camera, location)
    coords = mathutils.Vector((full_coords.x, full_coords.y))
    return coords

def extract_dict_from_target_files(target_files, n_frames, item):
    output_dict = { "direction_frames": [] }
    sprite = common.SpriteSize(item)

    for file in target_files:
        travel_directions = file.split(".")[0][-5:]
        print(f'travel_directions: {travel_directions}')

        bpy.ops.wm.open_mainfile(filepath=file)
        common.set_object_as_active(CAMERA)

        frames_data = []

        for frame in range(n_frames):
            blender_frame_id = frame + 1
            print(f'blender_frame_id: {blender_frame_id}')
            bpy.context.scene.frame_set(blender_frame_id)

            smoke_emitter_coords = get_camera_view_coords(bpy.context.scene, bpy.context.object, SMOKE_EMITTER)
            direction_ref_coords = get_camera_view_coords(bpy.context.scene, bpy.context.object, DIRECTION_REFERENCE)

            emitter_coords_on_sprite = smoke_emitter_coords * mathutils.Vector((sprite.width, sprite.height))
            smoke_direction = direction_ref_coords - smoke_emitter_coords
            smoke_data_this_frame = {
                "frame": frame,
                "emitter_coords": list(emitter_coords_on_sprite),
                "smoke_direction": list(smoke_direction)
            }
            frames_data.append(smoke_data_this_frame)

        direction_frame = {
            "pair": {
                "diagonal_pair": DIRECTIONS_MAP[travel_directions]
            },
            "frames": frames_data
        }
        output_dict["direction_frames"].append(direction_frame)
    return output_dict


def main():
    args = parse_arguments()
    target_files = find_target_files(args.item, args.version)
    output_dict = extract_dict_from_target_files(target_files, args.n_frames, args.item)
    common.save_smoke_dict_to_path(
        args.item,
        args.version,
        SMOKE_DATA_ASSETS,
        SMOKE_OUTPUT_EXTENSION,
        output_dict
    )


if __name__ == "__main__":
    main()
