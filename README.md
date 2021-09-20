# Origami Fold Blender Add-on
This is a simple add-on for Blender 2.90+ that adds some commands to the mesh 'edge' sub-menu for creating armatures that simulate paper folding around an edge.

Presently you can create armatures that:
- Fold the "left" side of the edge
- Fold the "right" side of the edge
- Fold both sides simultaneously (like 'mountain' or 'valley' folds)
  - Just a pre-linked left & right fold

Other features available:
- Link any new fold to the one previously created so they fold at the same time
- Create new folds as parents of previously created folds
  - Left parents to left, right parents to right

Possible future features:
- Bevel edge to give fold some thickness
- More than 1 axis of symmetry (e.g. more than left vs right)
- Think about IK for squash and inside-reverse folds
- Support for other advanced 3d fold types

## How it Works
The concept behind this add-on was largely inspired by the following Youtube Video:
- [How to make animation of Paper Airplane in Blender](https://www.youtube.com/watch?v=pNek1tRkhqg)

I automate placement of bones and avoid multiple armatures by:
- Using vector math to compute orientations that are perpendicular to the edge
- Painting weights automatically using an internal plane equation with the edge and the paper's surface normal
  - Some vertex weighting is not needed due to parented bones
- If a bone moves an edge containing another bone, it becomes that bone's parent
  - This avoids needing multiple armatures

## Basic Workflow (for very simple models like paper planes)
Here's a basic workflow to create an animation similar to the one above:

*Prepare your paper:*
- Create a plane/quad aligned with XY-plane of the proper dimensions.
- Cut edges into the plane with the knife or subdivision tool to match the crease pattern of your target model.
- Ensure there is only one vertex at each edge endpoint (merge duplicates)

*Create your folds:*
- Select all edges segments (along a single fold)
- In the 'edge' menu (View3D, edit mode) select Origami Fold
- Add the fold type desired

*Tips:*
- Think about dependencies as you create your folds
  - If two folds are a mirror image, consider using the 'linked' feature
  - If fold will move the bone of one coming later, make the LATER one first and then use the 'parent' feature
- The order you create folds matters when using the 'linked' and 'parent' features

## Examples
(coming soon)
