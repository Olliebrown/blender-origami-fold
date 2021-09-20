# Import system and blender modules
import bpy

# Import our own custom modules
from . import foldUtils

class CreateFoldMixin:
    """Create Fold Mixin Base"""

    # Static class level variable
    foldBones = []
    foldCount = 0

    def getSelectedVerts(self, context):
        # Switch to object mode to gather selected vertices
        bpy.ops.object.mode_set(mode='OBJECT')
        obRoot = context.active_object
        obMesh = context.active_object.data

        # Initialize selected vertices list
        selectedVerts = []

        # Is this a mesh?
        if obRoot.type == 'MESH':
            # Retrieve and verify selected vertices
            selectedVerts = foldUtils.getSelectedVertices(obMesh)

        # Return back the selected verts
        return selectedVerts

    def createSingleFold(self, context, dir, linked, asParent = False):
        # Advance count if needed
        if not linked:
            CreateFoldMixin.foldCount = CreateFoldMixin.foldCount + 1
        
        # Validate selection
        selectedVerts = self.getSelectedVerts(context)
        obRoot = context.active_object
        if len(selectedVerts) != 2:
            print("Must select 2+ vertices or 2+ edges in a mesh first")

        # Process the vertices
        else:
            # Group by position and compute fold plane
            planer, left, right, q, n = foldUtils.groupVertices(obRoot, selectedVerts[0], selectedVerts[1])

            # Create armature for requested direction (optionally linked as parent or copy)
            linkTo = ''
            newBoneName = ''
            if linked and not asParent:
                linkTo = CreateFoldMixin.foldBones[-1]

            armatureObj = None
            if dir == 'LEFT':
                newBoneName, armatureObj = foldUtils.addSingleFoldArmature(CreateFoldMixin.foldCount, obRoot, 'LEFT', left, q, n, linkTo, False)
            else:
                newBoneName, armatureObj = foldUtils.addSingleFoldArmature(CreateFoldMixin.foldCount, obRoot, 'RIGHT', right, q, n, linkTo, False)

            # Make Parent of all previously made bones
            if asParent:
                for childBone in CreateFoldMixin.foldBones:
                    foldUtils.parentBones(armatureObj, childBone, newBoneName)

                # Clear newly parented bones from list
                CreateFoldMixin.foldBones = []

            # Append new bone to list
            CreateFoldMixin.foldBones.append(newBoneName)

    def createDualFold(self, context, asParent, inverse = False):
        CreateFoldMixin.foldCount = CreateFoldMixin.foldCount + 1
        
        # Validate selection
        selectedVerts = self.getSelectedVerts(context)
        obRoot = context.active_object
        if len(selectedVerts) != 2:
            print("Must select 2+ vertices or 2+ edges in a mesh first")

        # Process the vertices
        else:
            # Group by position and compute fold plane
            planer, left, right, q, n = foldUtils.groupVertices(obRoot, selectedVerts[0], selectedVerts[1])

            # Create armature for both directions linked to one another
            leftBoneName, armatureObj = foldUtils.addSingleFoldArmature(CreateFoldMixin.foldCount, obRoot, 'LEFT', left, q, n)
            rightBoneName, _ = foldUtils.addSingleFoldArmature(CreateFoldMixin.foldCount, obRoot, 'RIGHT', right, q, n, leftBoneName)

            # Add parenting
            if asParent:
                for childBoneName in CreateFoldMixin.foldBones:
                    if 'LEFT' in childBoneName:
                        if inverse:
                            foldUtils.parentBones(armatureObj, childBoneName, rightBoneName)
                        else:
                            foldUtils.parentBones(armatureObj, childBoneName, leftBoneName)
                    else:
                        if inverse:
                            foldUtils.parentBones(armatureObj, childBoneName, leftBoneName)
                        else:
                            foldUtils.parentBones(armatureObj, childBoneName, rightBoneName)

                # Clear newly parented bones from list
                CreateFoldMixin.foldBones = []

            # Add bones to fold history
            CreateFoldMixin.foldBones.append(leftBoneName)
            CreateFoldMixin.foldBones.append(rightBoneName)

class CreateLeftFold(bpy.types.Operator, CreateFoldMixin):
    """Create left-side fold on selected edge"""
    bl_idname = "object.create_fold_left"
    bl_label = "Create Left Fold"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        self.createSingleFold(context, 'LEFT', False)

        # Indicate operator completed
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

class CreateLinkedLeftFold(bpy.types.Operator, CreateFoldMixin):
    """Create left-side fold on selected edge (linked to previous fold)"""
    bl_idname = "object.create_fold_linked_left"
    bl_label = "Create Linked Left Fold"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        self.createSingleFold(context, 'LEFT', True)

        # Indicate operator completed
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

class CreateParentLeftFold(bpy.types.Operator, CreateFoldMixin):
    """Create left-side fold on selected edge (as parent of all previous left folds)"""
    bl_idname = "object.create_fold_parent_left"
    bl_label = "Create Parent Left Fold"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        self.createSingleFold(context, 'LEFT', True, True)

        # Indicate operator completed
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

class CreateRightFold(bpy.types.Operator, CreateFoldMixin):
    """Create right-side fold on selected edge"""
    bl_idname = "object.create_fold_right"
    bl_label = "Create Right Fold"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        self.createSingleFold(context, 'RIGHT', False)

        # Indicate operator completed
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

class CreateLinkedRightFold(bpy.types.Operator, CreateFoldMixin):
    """Create right-side fold on selected edge (linked to previous fold)"""
    bl_idname = "object.create_fold_linked_right"
    bl_label = "Create Linked Right Fold"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        self.createSingleFold(context, 'RIGHT', True)

        # Indicate operator completed
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

class CreateParentRightFold(bpy.types.Operator, CreateFoldMixin):
    """Create right-side fold on selected edge (as parent all previous right folds)"""    
    bl_idname = "object.create_fold_parent_right"
    bl_label = "Create Parent Right Fold"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        self.createSingleFold(context, 'RIGHT', True)

        # Indicate operator completed
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

class CreateDualFold(bpy.types.Operator, CreateFoldMixin):
    """Create linked dual-fold on selected edge"""
    bl_idname = "object.create_fold_dual"
    bl_label = "Create Dual Fold"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        self.createDualFold(context)

        # Indicate operator completed
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

class CreateParentDualFold(bpy.types.Operator, CreateFoldMixin):
    """Create linked dual-fold on selected edge (as parents of all previous folds)"""
    bl_idname = "object.create_parent_fold_dual"
    bl_label = "Create Parent Dual Fold"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        self.createDualFold(context, True)

        # Indicate operator completed
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

class CreateInverseParentDualFold(bpy.types.Operator, CreateFoldMixin):
    """Create linked dual-fold on selected edge (as parents of all previous folds in reverse)"""
    bl_idname = "object.create_inverse_parent_fold_dual"
    bl_label = "Create Inverse Parent Dual Fold"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        self.createDualFold(context, True, True)

        # Indicate operator completed
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

# Setup self registration
classes = [CreateLeftFold, CreateLinkedLeftFold, CreateParentLeftFold,
    CreateRightFold, CreateLinkedRightFold, CreateParentRightFold,
    CreateDualFold, CreateParentDualFold, CreateInverseParentDualFold]
register, unregister = bpy.utils.register_classes_factory(classes)
