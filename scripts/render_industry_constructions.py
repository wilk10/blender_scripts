import argparse
import common
import construction
import sheet

COLLECTIONS = {
    'coal_mine': ['Mine'],
    'depot': ['Warehouse'],
    'harbour': ['Harbour'],
    'industrial_farm_with_fields': ['Ground', 'Farm'],
    'iron_ore_mine': ['IronOreMine'],
    'local_farm_with_fields': ['Ground', 'WholeFarm'],
    'logging_camp': ['House'],
    'train_station': ['Station', 'SingleRail', 'GoingTopRightRail', 'SingleRail.002', 'GoingBottomLeftRail', 'SingleRail.004'],
    'steel_works': ['Factory'],
    'stonemason': ['Stonemason']
}

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('item', type=str, help='name of the folder in world_map')
    parser.add_argument('filename', type=str, help='name of the file where the model is')
    parser.add_argument('--n_frames', type=int, default=24)
    parser.add_argument('--render_animations', action='store_true')
    parser.add_argument('--render_sheet', action='store_true')
    return parser.parse_args()


def main():
    args = parse_arguments()
    model_path = common.get_model_path(args.item, args.filename)
    renders_dir = common.get_or_create_renders_dir(args.item, args.filename)
    degree_paths = []
    for degree in common.DEGREES:
        output_dir = renders_dir.joinpath(f'{degree}')
        degree_path = construction.render_animations(
            args.item,
            model_path,
            output_dir,
            degree,
            args.render_animations,
            args.n_frames,
            COLLECTIONS[args.item],
        )
        degree_paths.append(degree_path)
    render_filenames = common.prepare_frame_filenames(args.n_frames)
    sprite_sheet = sheet.Sheet(
        item=args.item,
        version=args.filename,
        render_sheet=args.render_sheet,
        n_cols=args.n_frames,
        n_rows=len(common.DEGREES),
        render_dirs=degree_paths,
        render_filenames=render_filenames,
        is_animation=True,
        atlas_kind=construction.ATLAS_CONSTRUCTION
    )
    sprite_sheet.make_render_and_copy()


if __name__ == "__main__":
    main()
