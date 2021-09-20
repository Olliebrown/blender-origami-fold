eps = 1e-6

def computeBBox(verts):
    # Val will hold min/max coords, idx will hold index of verts with those cords
    bboxVal = [float('inf'), -float('inf'), float('inf'), -float('inf')]
    bboxIdx = [[], [], [], []]

    # Loop over verts and search for the max/min coordinate values
    for vert in verts:
        # Check min-x
        if vert.co.x <= bboxVal[0]:
            if abs(vert.co.x - bboxVal[0]) < eps:
                bboxIdx[0].append(vert.index)
            else:
                bboxVal[0] = vert.co.x
                bboxIdx[0] = [vert.index]

        # Check max-x
        if vert.co.x >= bboxVal[1]:
            if abs(vert.co.x - bboxVal[1]) < eps:
                bboxIdx[1].append(vert.index)
            else:
                bboxVal[1] = vert.co.x
                bboxIdx[1] = [vert.index]
        
        # Check min-y
        if vert.co.y <= bboxVal[2]:
            if abs(vert.co.y - bboxVal[2]) < eps:
                bboxIdx[2].append(vert.index)
            else:
                bboxVal[2] = vert.co.y
                bboxIdx[2] = [vert.index]

        # Check max-y
        if vert.co.y >= bboxVal[3]:
            if abs(vert.co.y - bboxVal[3]) < eps:
                bboxIdx[3].append(vert.index)
            else:
                bboxVal[3] = vert.co.y
                bboxIdx[3] = [vert.index]
    
    # Debug: Print edge indexes
    # print('BBox Edges:')
    # print('\t  Left:', bboxIdx[0])
    # print('\t Right:', bboxIdx[1])
    # print('\tBottom:', bboxIdx[2])
    # print('\t   Top:', bboxIdx[3])

    # Check four corners (only two of these should pass)
    corners = []
    for idx in bboxIdx[0]:
        # Top-left
        if idx in bboxIdx[3]:
            corners.insert(0, idx)
    
        # Bottom-left
        if idx in bboxIdx[2]:
            corners.append(idx)

    for idx in bboxIdx[1]:
        # Top-right
        if idx in bboxIdx[3]:
            corners.insert(0, idx)

        # Bottom-right
        if idx in bboxIdx[2]:
            corners.append(idx)

    # Return bbox coords and the corner
    return [bboxVal, corners]
