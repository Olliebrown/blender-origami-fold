import bpy

class VIEW3D_MT_edit_origami_fold_menu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_edit_origami_fold_menu"
    bl_label = "Origami Folds"

    def draw(self, context):
        layout = self.layout.column(heading="Origami Folds")
        layout.operator("object.create_fold_left")
        layout.operator("object.create_fold_linked_left")
        layout.operator("object.create_fold_parent_left")
        layout.separator()
        layout.operator("object.create_fold_right")
        layout.operator("object.create_fold_linked_right")
        layout.operator("object.create_fold_parent_right")
        layout.separator()
        layout.operator("object.create_fold_dual")
        layout.operator("object.create_parent_fold_dual")
        layout.operator("object.create_inverse_parent_fold_dual")

# Auto generate register and unregister methods
classes = [VIEW3D_MT_edit_origami_fold_menu]
register, unregister = bpy.utils.register_classes_factory(classes)
