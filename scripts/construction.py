import bpy
import common
import math
import os


ATLAS_CONSTRUCTION = 'construction'
CONSTRUCTION_CUBE = 'ConstructionCube'
DEFAULT_COLLECTION = 'DefaultSetUp'
MAX_Z = {
    'city': 5.8,
    'coal_mine': 6.0,
    'depot': 6.0,
    'harbour': 5.9,
    'industrial_farm_with_fields': 5.8,
    'iron_ore_mine': 6.4,
    'local_farm_with_fields': 5.5,
    'logging_camp': 5.5,
    'steel_works': 7.8,
    'stonemason': 6.3,
    'suburbs': 5.5,
    'town': 4.8,
    'train_station': 6.4,
}
SPAWN_Z = 4.025

def render_animations(
        item_name,
        model_path, 
        output_dir, 
        degree, 
        do_render, 
        n_frames,
        collection_names,
    ):
    print(f'output_dir: {output_dir}')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=False)

    if do_render:
        bpy.ops.wm.open_mainfile(filepath=model_path)
        bpy.context.scene.render.filepath = f'{output_dir.as_posix()}/'
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = n_frames

        common.set_object_as_active(common.EMPTY_ORIGIN)
        bpy.context.active_object.rotation_euler[2] = math.radians(degree)
        default_collection = bpy.context.scene.collection.children.get(DEFAULT_COLLECTION)

        bpy.ops.mesh.primitive_cube_add(location=(0,0,SPAWN_Z), scale=(6,6,4))
        cube = bpy.context.view_layer.objects.active
        for collection in cube.users_collection:
            if collection.name in bpy.data.collections.keys():
                bpy.data.collections[collection.name].objects.unlink(cube)
        default_collection.objects.link(cube)
        cube.name = CONSTRUCTION_CUBE
        cube.hide_render = True
        cube.lineart.usage = 'EXCLUDE'

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide(number_cuts=21)
        bpy.ops.object.mode_set(mode='OBJECT')

        cube.keyframe_insert(data_path='location', frame=1)
        cube.location.z = MAX_Z[item_name]
        cube.keyframe_insert(data_path='location', frame=n_frames)

        for collection_name in collection_names:
            collection = bpy.data.collections[collection_name]
            for object in collection.all_objects:
                if object.type == 'MESH':
                    modifier = object.modifiers.new(type='BOOLEAN', name='Construction')
                    modifier.object = cube
                    modifier.operation = 'DIFFERENCE'

        bpy.ops.render.render(animation=True)
        temp_filepath = os.path.join(output_dir, f'temp.blend')
        bpy.ops.wm.save_as_mainfile(filepath=temp_filepath)
    return output_dir