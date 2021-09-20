# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
bl_info = {
    "name" : "Origami Fold",
    "author" : "Seth Berrier",
    "description" : "Several new operators that automate creating armatures for paper folding",
    "blender" : (2, 90, 0),
    "version" : (0, 1, 0),
    "location": "View3D > Edit Mode > Edge",
    "warning" : "",
    "category" : "Mesh",
    "doc_url" : "",
    "tracker_url" : ""
}

import bpy

from OrigamiFold import foldOps, foldMenus
modules = [foldOps, foldMenus]

def draw_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("VIEW3D_MT_edit_origami_fold_menu")

def register():
    for m in modules:
        m.register()
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(draw_menu)

def unregister():
    for m in modules:
        m.unregister()
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(draw_menu)

# Call register when run as a script
if __name__ == "__main__":
    register()
