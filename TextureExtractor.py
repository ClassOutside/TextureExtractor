import bpy
import os

bl_info = {
    "name": "Merge Bake and Save Texture",
    "blender": (2, 80, 0),
    "category": "Object",
    "version": (1, 0, 0),
    "location": "3D View > Object Context Menu",
    "description": "Your addon description here.",
    "author": "Your Name",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Object",
}

class OBJECT_OT_StartTextureBakeOperator(bpy.types.Operator):
    bl_idname = "object.start_texture_bake"
    bl_label = "Start Texture Bake Process"
    
    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        resolution = addon_prefs.resolution
        inflation = addon_prefs.inflation
        # resolution = 256
        # inflation = .005

        source_object = bpy.context.active_object
        object_name = source_object.name.replace(".", "_")  # Replace periods with underscores
        self.new_object = self.create_duplicate_object(context, object_name)
        self.apply_scale(self.new_object)
        self.remove_doubles(self.new_object)
#        self.prepare_object(self.new_object) #Method used for optional changes like setting normals to outside, and shading smooth
        self.perform_smart_uv_project(self.new_object)
        self.set_origin_to_geometry(self.new_object)
        self.remove_all_materials(self.new_object)
        new_material = self.create_diffuse_material(object_name)
        self.configure_material_nodes(new_material, object_name, resolution)
        self.assign_material_to_object(self.new_object, new_material)
        cage_object = self.create_cage_object(self.new_object)
        self.inflate_cage(cage_object, inflation_factor= inflation)
        self.bake_textures(source_object, self.new_object, cage_object)
        self.save_baked_image(object_name)
        self.new_object.name = object_name.lstrip("destination_")
        self.delete_objects(source_object, cage_object)
        self.print_completion_message()

        return {'FINISHED'}
    
    def apply_scale(self, obj):
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(scale=True)
    
    def delete_objects(self, *objects):
        for obj in objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    
    def perform_smart_uv_project(self, obj):
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')

    def save_baked_image(self, object_name):
        image_name = f"texture_{object_name}.png"
        blend_file_path = bpy.data.filepath
        texture_output_folder = os.path.join(os.path.dirname(blend_file_path), "Texture Output")
        image_path = os.path.join(texture_output_folder, image_name)

        # Ensure the image node is the active one
        bpy.context.view_layer.objects.active = self.new_object
        image_node = self.new_object.active_material.node_tree.nodes.get("Image Texture")
        if image_node:
            image = image_node.image
            if image:
                image.filepath_raw = image_path
                image.file_format = 'PNG'
                image.save()
    
    def check_and_create_texture_output_folder(self):
        blend_file_path = bpy.data.filepath
        texture_output_folder = os.path.join(os.path.dirname(blend_file_path), "Texture Output")
        if not os.path.exists(texture_output_folder):
            os.makedirs(texture_output_folder)
            print(f"Created 'Texture Output' folder in {os.path.dirname(blend_file_path)}")
    
    def bake_textures(self, source_object, target_object, cage_object):
        bpy.context.scene.render.bake.use_selected_to_active = True
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.bake_type = 'DIFFUSE'
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True

        bpy.ops.object.select_all(action='DESELECT')
        target_object.select_set(True)
        source_object.select_set(True)

        bpy.context.view_layer.objects.active = target_object
        
        bpy.context.scene.render.bake.use_cage = True
        bpy.context.scene.render.bake.cage_object = bpy.data.objects[cage_object.name]
        
        bpy.ops.object.bake(type='DIFFUSE')

    
    def create_cage_object(self, obj):
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.duplicate(linked=False)
        cage_object = bpy.context.active_object
        cage_object.name = "cage_" + cage_object.name
        bpy.ops.object.select_all(action='DESELECT')
        return cage_object

    def inflate_cage(self, cage_obj, inflation_factor=1.1):
        bpy.context.view_layer.objects.active = cage_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.transform.shrink_fatten(value=inflation_factor)
        
        bpy.ops.object.mode_set(mode='OBJECT')


    def create_duplicate_object(self, context, object_name):
        bpy.ops.object.duplicate(linked=False)
        new_object = context.active_object
        new_object.name = "destination_" + object_name
        bpy.context.view_layer.objects.active = new_object
        new_object.select_set(True)
        return new_object

    def remove_doubles(self, obj):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode='OBJECT')

    def prepare_object(self, obj):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.data.use_auto_smooth = False
        bpy.ops.object.shade_smooth()
        bpy.ops.object.shade_flat()

    def set_origin_to_geometry(self, obj):
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    def remove_all_materials(self, obj):
        bpy.ops.object.material_slot_remove()

    def create_diffuse_material(self, object_name):
        material_name = "material_" + object_name
        new_material = bpy.data.materials.new(name=material_name)
        new_material.use_nodes = True
        return new_material

    def configure_material_nodes(self, material, object_name, resolution):
        material.node_tree.nodes.clear()

        image_texture = material.node_tree.nodes.new(type='ShaderNodeTexImage')
        image_texture.image = bpy.data.images.new(name="texture_" + object_name, width=resolution, height=resolution)

        principled_bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        material_output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')

        material.node_tree.links.new(principled_bsdf.inputs['Base Color'], image_texture.outputs['Color'])
        material.node_tree.links.new(material_output.inputs['Surface'], principled_bsdf.outputs['BSDF'])

    def assign_material_to_object(self, obj, material):
        obj.data.materials.clear()
        obj.data.materials.append(material)

    def print_completion_message(self):
        print("Texture baking process completed")

def menu_func(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator("object.start_texture_bake")

class OBJECT_PT_TextureBakePreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    resolution: bpy.props.IntProperty(
        name="Default Resolution",
        default=2048,
        min=1,
        description="Default resolution for texture baking",
    )
    
    inflation: bpy.props.FloatProperty(
        name="Default Inflation",
        default=0.5,  
        min=0.001,   
        description="Default inflation for cage mesh",
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Default Settings")
        layout.prop(self, "resolution")
        layout.prop(self, "inflation")
        
def register():
    bpy.utils.register_class(OBJECT_OT_StartTextureBakeOperator)
    bpy.utils.register_class(OBJECT_PT_TextureBakePreferences)
    bpy.types.VIEW3D_MT_object_context_menu.append(menu_func)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_StartTextureBakeOperator)
    bpy.utils.unregister_class(OBJECT_PT_TextureBakePreferences)
    bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)

if __name__ == "__main__":
    register()
