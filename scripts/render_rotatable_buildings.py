import argparse
import bpy
import common
import math
import os
import sheet


ATLAS_VARIETY = "variety"

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('item', type=str, help='name of the WorldItem')
    parser.add_argument('filename', type=str, help='name of the file to use')
    parser.add_argument('--render_degrees', action='store_true')
    parser.add_argument('--render_sheet', action='store_true')
    return parser.parse_args()

def render_model(model_path, renders_dir, degree, render_degrees):
    output_filename = f'{degree:03d}.png'
    render_path = os.path.join(renders_dir, output_filename)
    print(f'output_dir: {render_path}')

    if render_degrees:
        bpy.ops.wm.open_mainfile(filepath=model_path)
        bpy.context.scene.render.filepath = render_path

        common.set_object_as_active(common.EMPTY_ORIGIN)
        bpy.context.active_object.rotation_euler[2] = math.radians(degree)

        bpy.ops.render.render(write_still=True)
        if degree == common.DEGREES[-1]:
            bpy.context.active_object.rotation_euler[2] = math.radians(0)
        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    return output_filename


def main():
    args = parse_arguments()
    model_path =common.get_model_path(args.item, args.filename)
    renders_dir = common.get_or_create_renders_dir(args.item, args.filename)
    degree_filenames = []
    for degree in common.DEGREES:
        degree_filename = render_model(
            model_path,
            renders_dir,
            degree,
            args.render_degrees,
        )
        degree_filenames.append(degree_filename)
    sprite_sheet = sheet.Sheet(
        item=args.item,
        version=args.filename,
        render_sheet=args.render_sheet,
        n_cols=1,
        n_rows=len(common.DEGREES),
        render_dirs=[renders_dir],
        render_filenames=degree_filenames,
        is_animation=False,
        atlas_kind=ATLAS_VARIETY
    )
    sprite_sheet.make_render_and_copy()


if __name__ == "__main__":
    main()
