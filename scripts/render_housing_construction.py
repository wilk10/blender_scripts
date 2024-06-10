import argparse
import common
import construction
import sheet


HOUSES_COLLECTION = 'Houses'

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('item', type=str, help='name of the folder in world_map')
    parser.add_argument('folder', type=str, help='name of the folder where the files are')
    parser.add_argument('--n_frames', type=int, default=24)
    parser.add_argument('--render_animations', action='store_true')
    parser.add_argument('--render_sheet', action='store_true')
    return parser.parse_args()


def main():
    args = parse_arguments()
    renders_dir = common.get_or_create_renders_dir(args.item, args.folder)
    files_to_render = common.find_files_to_render(args.item, args.folder)
    variety_paths = []
    for file_path in files_to_render:
        variety = file_path.split(".")[0][-1:]
        output_dir = renders_dir.joinpath(f'{variety}')
        variety_path = construction.render_animations(
            args.item,
            file_path, 
            output_dir, 
            0, 
            args.render_animations, 
            args.n_frames,
            [HOUSES_COLLECTION],
        )
        variety_paths.append(variety_path)
    render_filenames = common.prepare_frame_filenames(args.n_frames)
    sprite_sheet = sheet.Sheet(
        item=args.item,
        version=args.folder,
        render_sheet=args.render_sheet,
        n_cols=args.n_frames,
        n_rows=len(variety_paths),
        render_dirs=variety_paths,
        render_filenames=render_filenames,
        is_animation=True,
        atlas_kind=construction.ATLAS_CONSTRUCTION
    )
    sprite_sheet.make_render_and_copy()


if __name__ == "__main__":
    main()
