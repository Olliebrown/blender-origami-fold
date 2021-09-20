import bpy
import mathutils

from . import bboxUtils

def getSelectedVertices(obMesh):
    # Find all selected vertices
    selectedVerts = [v for v in obMesh.vertices if v.select]

    # If there were no selected vertices, look for an edge instead
    if len(selectedVerts) != 2:
        # Get selected edges
        selectedEdges = [e for e in obMesh.edges if e.select]

        # If there was only one, extract its endpoints
        if len(selectedEdges) == 1:
            edge = selectedEdges[0]
            selectedVerts = [
                obMesh.vertices[edge.vertices[0]],
                obMesh.vertices[edge.vertices[1]]
            ]

        # If more than 1, find the absolute endpoints
        elif len(selectedEdges) > 1:
            # Gather all the vertices
            allVerts = []
            for edge in selectedEdges:
                allVerts.append(obMesh.vertices[edge.vertices[0]])
                allVerts.append(obMesh.vertices[edge.vertices[1]])
            
            # Compute the bounding box
            bboxVal, bboxCorners = bboxUtils.computeBBox(allVerts)

            # DEBUG: Output bounding box details
            # print('BBox coords:')
            # print('\tX: [', bboxVal[0], 'to', bboxVal[1], ']')
            # print('\tY: [', bboxVal[2], 'to', bboxVal[3], ']')
            # print('BBox Corners:', bboxCorners)

            # Use corners as selected verts
            if len(bboxCorners) == 2:
                selectedVerts = [
                    obMesh.vertices[bboxCorners[0]],
                    obMesh.vertices[bboxCorners[1]]
                ]

    # Return what we found
    return selectedVerts

def computeWorldPlane(obRoot, v0, v1, vertNorm):
    midPoint = (v0 + v1) / 2.0

    # Construct plane equation along fold and mesh vert normal in world coords
    worldQ = midPoint @ obRoot.matrix_world

    worldV0 = v0 @ obRoot.matrix_world
    worldV1 = v1 @ obRoot.matrix_world
    worldFoldVec = (worldV1 - worldV0).normalized()

    worldVertNorm = vertNorm.to_4d()
    worldVertNorm.w = 0
    worldVertNorm = (worldVertNorm @ obRoot.matrix_world).to_3d()

    worldNorm = worldFoldVec.cross(worldVertNorm).normalized()

    return worldQ, worldNorm

def groupVertices(obRoot, selectedVertex0, selectedVertex1, eps = 1e-4):
    # Get world space plane equation
    worldQ, worldNorm = computeWorldPlane(obRoot, selectedVertex0.co, selectedVertex1.co, selectedVertex0.normal)

    # Ensure the plane normal aligns roughly with -X or +Y
    facing = worldNorm.dot(mathutils.Vector([-1, 0, 0]))
    if abs(facing) < 1e-2: # Too close to perpendicular, use Y instead
        facing = worldNorm.dot(mathutils.Vector([0, 1, 0]))
    
    # Flip plane normal if required
    if facing < 0:
        worldNorm = worldNorm * -1

    # Test all verts to find groups
    planer, left, right = [[], [], []]
    for v in obRoot.data.vertices:
        # Compute signed distance to plane
        worldVert = v.co @ obRoot.matrix_world
        signedDist = worldNorm.dot(worldVert - worldQ)

        # Group based on signed distance
        if signedDist > eps:
            left.append(v)
        elif signedDist < -eps:
            right.append(v)
        else:
            planer.append(v)
    
    # Return group lists
    return [planer, left, right, worldQ, worldNorm]

def makeArmature(armatureName, headPos):
    # Create a new armature
    armature = bpy.data.armatures.new(armatureName)
    armatureObj = bpy.data.objects.new(name=(armatureName + ' Armature'), object_data=armature)

    # Set proper head position and orientation
    armatureObj.location = headPos
    armatureObj.rotation_mode = 'QUATERNION'

    # Return the armature
    return armatureObj

def addBoneToArmature(armatureObj, boneName, head, direction):
    # Ensure armature is selected and in edit mode
    armatureObj.select_set(True)
    bpy.context.view_layer.objects.active = armatureObj
    bpy.ops.object.editmode_toggle()

    # Add one edit bone
    bone = armatureObj.data.edit_bones.new(boneName)

    # Position the tail and head of the bone
    bone.head = head
    bone.tail = head + direction

    # Exit edit mode
    bpy.ops.object.editmode_toggle()

def setupPoseBone(armatureObj, boneName):
    # Switch to pose mode
    armatureObj.select_set(True)
    bpy.context.view_layer.objects.active = armatureObj
    bpy.ops.object.posemode_toggle()

    # Retrieve pose bone and add constraint
    poseBone = armatureObj.pose.bones.get(boneName)
    if poseBone != None:
        rotationConstraint = poseBone.constraints.new('LIMIT_ROTATION')    
        rotationConstraint.owner_space = 'LOCAL'
        rotationConstraint.use_limit_y = True
        rotationConstraint.use_limit_z = True

    # Exit pose mode
    bpy.ops.object.posemode_toggle()

def bevelSelectedFold(size = 0.003, segments = 3):
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.bevel(offset=size, offset_pct=0, segments=segments, affect='EDGES')
    bpy.ops.object.editmode_toggle()

def linkPoseBones(armatureObj, boneNameA, boneNameB):
    # Switch to pose mode
    armatureObj.select_set(True)
    bpy.context.view_layer.objects.active = armatureObj
    bpy.ops.object.posemode_toggle()

    # Retrieve pose bone and add constraint
    poseBoneB = armatureObj.pose.bones.get(boneNameB)
    if poseBoneB != None:
        copyRotationConstraint = poseBoneB.constraints.new('COPY_ROTATION')    
        copyRotationConstraint.target = armatureObj
        copyRotationConstraint.subtarget = boneNameA
        copyRotationConstraint.use_y = False
        copyRotationConstraint.use_z = False
        copyRotationConstraint.target_space = 'LOCAL'
        copyRotationConstraint.owner_space = 'LOCAL'

    # Exit pose mode
    bpy.ops.object.posemode_toggle()

def parentBones(armatureObj, childBoneName, parentBoneName):
    # Switch to edit mode
    armatureObj.select_set(True)
    bpy.context.view_layer.objects.active = armatureObj
    bpy.ops.object.editmode_toggle()

    # Retrieve edit bone references
    parentBone = armatureObj.data.edit_bones[parentBoneName]
    childBone = armatureObj.data.edit_bones[childBoneName]

    # Setup parent relationship with offset
    if parentBone != None and childBone != None:
        childBone.use_connect = False
        childBone.use_inherit_rotation = True
        childBone.inherit_scale = 'FULL'
        childBone.parent = parentBone

    # Exit edit mode
    bpy.ops.object.editmode_toggle()

def createVertexGroup(obRoot, verts, boneName, unique):    
    # Get list of just vertex indexes
    # If unique, leave out ones already in another vertex group
    vertexIndexList = []
    for v in verts:
        if not unique or len(v.groups.items()) == 0:
            vertexIndexList.append(v.index)
    
    # Create the vertex group
    newVertexGroup = obRoot.vertex_groups.new(name=boneName)
    newVertexGroup.add(vertexIndexList, 1.0, 'ADD')

def addSingleFoldArmature(foldCount, obRoot, dir, verts, headPos, direction, linkTo = '', asParent = False):
    # Generate name using count
    name = 'Fold %03d' % foldCount

    # Does this mesh already have an armature parent?
    armatureObj = obRoot.parent
    if armatureObj == None or obRoot.parent_type != 'ARMATURE':
        # Create a new armature with proper location and orientation
        armatureObj = makeArmature(name, obRoot.location)
        bpy.data.collections['Collection'].objects.link(armatureObj)

    # Add a single bone
    boneName = name + ' ' + dir + ' Bone'
    tailDir = direction
    if dir == 'RIGHT':
        tailDir = tailDir * -1
    addBoneToArmature(armatureObj, boneName, headPos, tailDir)

    # Make sure paper is parented to armature
    if obRoot.parent != armatureObj:
        obRoot.parent = armatureObj
        obRoot.parent_type = 'ARMATURE'
        obRoot.matrix_parent_inverse = armatureObj.matrix_world.inverted()

    # Make an appropriate vertex group named for the bone
    createVertexGroup(obRoot, verts, boneName, True)

    # Create pose bone and set constraints
    setupPoseBone(armatureObj, boneName)

    # Optionally link bone to another bone
    if linkTo != '':
        if asParent:
            parentBones(armatureObj, linkTo, boneName)
        else:
            linkPoseBones(armatureObj, linkTo, boneName)

    # Return bone name for use in linking as well as armature object
    return boneName, armatureObj
