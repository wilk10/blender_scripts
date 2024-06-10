import argparse
import bpy
import common
import os
import sheet


ATLAS_MOVING = "moving"
N_DIRECTIONS = 12

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('item', type=str, help='name of the WorldItem')
    parser.add_argument('version', type=str, help='folder where the models are')
    parser.add_argument('--n_frames', type=int, default=24)
    parser.add_argument('--render_animations', action='store_true')
    parser.add_argument('--render_sheet', action='store_true')
    return parser.parse_args()

def render_blender_file(file, root_output_dir, render_animations, n_frames):
    directions = file.split(".")[0][-5:]
    output_dir = root_output_dir.joinpath(f'{directions}')
    print(f'output_dir: {output_dir}')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=False)

    if render_animations:
        bpy.ops.wm.open_mainfile(filepath=file)
        bpy.context.scene.render.filepath = f'{output_dir.as_posix()}/'
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = n_frames
        bpy.ops.render.render(animation=True)
        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    return output_dir


def main():
    args = parse_arguments()
    renders_dir = common.get_or_create_renders_dir(args.item, args.version)
    files_to_render = common.find_files_to_render(args.item, args.version)
    direction_paths = []
    for file in files_to_render:
        direction_path = render_blender_file(
            file,
            renders_dir,
            args.render_animations,
            args.n_frames
        )
        direction_paths.append(direction_path)
    render_filenames = common.prepare_frame_filenames(args.n_frames)
    sprite_sheet = sheet.Sheet(
        item=args.item,
        version=args.version,
        render_sheet=args.render_sheet,
        n_cols=args.n_frames,
        n_rows=N_DIRECTIONS,
        render_dirs=direction_paths,
        render_filenames=render_filenames,
        is_animation=True,
        atlas_kind=ATLAS_MOVING
    )
    sprite_sheet.make_render_and_copy()


if __name__ == "__main__":
    main()
