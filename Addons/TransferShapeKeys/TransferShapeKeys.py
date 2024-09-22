
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Transfer Shapekeys",
    "blender": (4, 2, 0),
    "category": "Tool",
    "author": "Stefan Petrov",    
}

import bpy

class TransferShapekeysPanel(bpy.types.Panel):
    bl_label = "Transfer Shapekeys"
    bl_idname = "PT_TransferShapekeys"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout

        layout.prop_search(context.scene, "shapekeys_source", context.scene, "objects", text="Source")
        layout.prop_search(context.scene, "shapekeys_target", context.scene, "objects", text="Target")
        layout.operator("object.shapekey_transfer", text="Transfer Shapekeys")

class TransferShapekeysOperator(bpy.types.Operator):
    bl_idname = "object.shapekey_transfer"
    bl_label = "Transfer Shapekeys"
    bl_description = "Transfer shapekeys from source to target object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        source_object = context.scene.shapekeys_source
        target_object = context.scene.shapekeys_target

        if source_object is None or target_object is None:
            self.report({'ERROR'}, "Please select both source and target objects.")
            return {'CANCELLED'}

        # Check if the source object has shape keys
        if not source_object.data.shape_keys:
            self.report({'ERROR'}, f"'{source_object.name}' does not have shape keys.")
            return {'CANCELLED'}
        
        
        bpy.ops.object.select_all(action='DESELECT')
        ##bpy.data.objects[target_object.name].select_set(True)
        ##target_object.modifiers.add(type='SURFACE_DEFORM')

        mod = target_object.modifiers.new(name='SurfaceDeform', type="SURFACE_DEFORM")
        ## if source_object != target_object
        mod.target = source_object
        bpy.ops.object.surfacedeform_bind(modifier = mod.name)
        
        ##for o in source_object:
            
        if source_object.type == "MESH":
            if source_object.data.shape_keys:
                for sk in source_object.data.shape_keys.key_blocks:
                    if sk.name != "Basis":
                        print(sk.name)
                        sk.value = 1
                        bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=True, modifier=mod.name, report=False)
                        target_object.data.shape_keys.key_blocks[mod.name].name = sk.name
                        sk.value = 0
        
        bpy.ops.object.surfacedeform_bind(modifier = mod.name)

        

        self.report({'INFO'}, f"Shape keys copied from '{source_object.name}' to '{target_object.name}'. All shape key values set to 0.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(TransferShapekeysPanel)
    bpy.utils.register_class(TransferShapekeysOperator)
    bpy.types.Scene.shapekeys_source = bpy.props.PointerProperty(type=bpy.types.Object, name="Source Object")
    bpy.types.Scene.shapekeys_target = bpy.props.PointerProperty(type=bpy.types.Object, name="Target Object")

def unregister():
    bpy.utils.unregister_class(ShapekeyTransferPanel)
    bpy.utils.unregister_class(TransferShapekeysOperator)
    del bpy.types.Scene.shapekeys_source
    del bpy.types.Scene.shapekeys_target

if __name__ == "__main__":
    register()
