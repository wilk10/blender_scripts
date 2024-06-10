import bpy
import common
import os
import math
import pathlib
import shutil


class Sheet:
    SHEETS = "sprite_sheets"
    TEMPLATE = "template.blend"
    ASSET_TEXTURES = "assets/textures/"
    EXTRA_SCALE = 2

    def __init__(
            self, 
            item: str, 
            version: str, 
            render_sheet: bool, 
            n_cols: int, 
            n_rows: int, 
            render_dirs: list[str],
            render_filenames: list[str],
            is_animation: bool,
            atlas_kind: str,
        ):
        self.item = item
        self.version = version
        self.sprite_size = common.SpriteSize(item, self.EXTRA_SCALE)
        self.render_sheet = render_sheet
        self.n_cols = n_cols
        self.n_rows = n_rows
        self.render_dirs = render_dirs
        self.render_filenames = render_filenames
        # is_animation: if true, it uses the render_dirs as rows
        # and the filenames as cols.
        # if false, it uses render_dirs as cols (only one render dir)
        # and filenames as rows.
        self.is_animation = is_animation
        self.atlas_kind = atlas_kind

    def open_sprite_sheet_template(self):
        blender_dir = common.get_blender_dir()
        sheets_dir = blender_dir.joinpath(f'{self.SHEETS}/')
        template = os.path.join(sheets_dir, f'{self.TEMPLATE}')
        print(f'template: {template}')
        bpy.ops.wm.open_mainfile(filepath=template)

    def setup_camera_and_meshes(self):
        bpy.data.objects['Camera'].select_set(True)
        bpy.ops.object.delete()
        bpy.ops.object.camera_add(rotation=(math.radians(90), 0, 0))
        sprite_camera = bpy.context.active_object
        bpy.context.scene.camera = sprite_camera
        sprite_camera.data.type = 'ORTHO'

        bpy.ops.mesh.primitive_plane_add(rotation=(math.radians(90), 0, 0))
        plane = bpy.context.active_object

        previous_width = plane.dimensions.x
        # NOTE: this assumes that the height is always less the the width.
        # This holds if the item has z dimension (item_dimensions, from the game) of 1
        # but if I start making taller items (i doubt it), this may not hold true any more
        proportional_width = (plane.dimensions.y / self.sprite_size.height) * self.sprite_size.width
        plane.dimensions.x = proportional_width
        bpy.context.view_layer.update()

        delta_x = (proportional_width - previous_width) / 2
        plane.location.x += delta_x

        sprite_camera.data.ortho_scale = max(
            plane.dimensions.x * self.n_cols,
            plane.dimensions.y * self.n_rows
        )

        column_modifier = plane.modifiers.new(name='columns', type='ARRAY')
        column_modifier.count = self.n_cols

        row_modifier = plane.modifiers.new(name='rows', type='ARRAY')
        row_modifier.count = self.n_rows
        row_modifier.relative_offset_displace.x = 0
        row_modifier.relative_offset_displace.y = -1

        bpy.data.scenes[0].render.resolution_x = self.sprite_size.width * self.n_cols
        bpy.data.scenes[0].render.resolution_y = self.sprite_size.height * self.n_rows

        # camera location.x = n_cols * plane.dimesions.x / 2 (to center in the middle) - 1
        # (-1 becase the world centre is at the centre of the sprite in position 0,0)
        sprite_camera.location.x = self.n_cols * plane.dimensions.x / 2 - 1

        sprite_camera.location.y = -1

        # camera location.y = self.n_rows * plane.dimesions.y / 2 (to center in the middle) * (-1) + 1
        # (times -1 because the plane goes down (see array_modifier), but Y points up)
        # (+ 1 for the same reason as x (because of the centre of the world), but again, Y points up)
        sprite_camera.location.z = self.n_rows * plane.dimensions.y / 2 * (-1) + 1

        bpy.context.view_layer.objects.active = plane
        bpy.ops.object.modifier_apply(modifier=column_modifier.name)
        bpy.ops.object.modifier_apply(modifier=row_modifier.name)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.separate(type='LOOSE')

    def setup_materials(self):
        row = 0
        col = 0
        for _name, object in bpy.context.view_layer.objects.items():
            if object.type != 'MESH':
                continue

            object.name = f'{col},{row}'
            object.data.name = f'{col},{row}'

            material = bpy.data.materials.new(f'{col},{row}')
            material.blend_method = 'HASHED'
            object.data.materials.append(material)

            material.use_nodes = True
            nodes = material.node_tree.nodes
            node_principled = nodes.get('Principled BSDF')

            if self.is_animation:
                file_dir = self.render_dirs[row]
                file_name = self.render_filenames[col]
            else:
                file_dir = self.render_dirs[col]
                file_name = self.render_filenames[row]
            
            image_path = os.path.join(file_dir, file_name)
            print(f'image_path: {image_path}')

            node_texture = nodes.new('ShaderNodeTexImage')
            node_texture.image = bpy.data.images.load(image_path)

            node_output = nodes.get('Material Output')

            links = material.node_tree.links
            links.new(node_texture.outputs['Color'], node_principled.inputs['Base Color'])
            links.new(node_texture.outputs['Alpha'], node_principled.inputs['Alpha'])
            links.new(node_principled.outputs['BSDF'], node_output.inputs['Surface'])

            col += 1
            if col == self.n_cols:
                col = 0
                row += 1

    def render_sprite_sheet(self):
        blender_dir = common.get_blender_dir()
        item_dir = blender_dir.joinpath(f'{self.SHEETS}/{self.item}/')
        blender_file_name = f'{self.item}_{self.version}.blend'
        blender_file_path = os.path.join(item_dir, blender_file_name)
        print(f'blender_file_path: {blender_file_path}')

        sheet_file_name = f'{self.item}_{self.version}.png'
        sheet_file_path = os.path.join(item_dir, sheet_file_name)
        print(f'sheet_file_path: {sheet_file_path}')

        if self.render_sheet:
            bpy.context.scene.render.filepath = sheet_file_path
            bpy.ops.render.render(write_still=True)
            bpy.ops.wm.save_as_mainfile(filepath=blender_file_path)
        return sheet_file_path

    def copy_sprite_sheet_to_repo(self, sprite_sheet_path):
        current_dir = pathlib.Path(os.getcwd())
        target_dir = current_dir.joinpath(f'{self.ASSET_TEXTURES}/{self.atlas_kind}')
        print(f'target_dir: {target_dir}')

        item_filename = sprite_sheet_path.split("\\")[-1]
        print(f'item_filename: {item_filename}')

        target_path = os.path.join(target_dir, item_filename)
        print(f'target_path: {target_path}')

        shutil.copyfile(sprite_sheet_path, target_path)

    def make_render_and_copy(self):
        self.open_sprite_sheet_template()
        self.setup_camera_and_meshes()
        self.setup_materials()
        sprite_sheet_path = self.render_sprite_sheet()
        self.copy_sprite_sheet_to_repo(sprite_sheet_path)
