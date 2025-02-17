# -*- coding: utf-8 -*-
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

import bpy

from sverchok.utils.sv_logging import sv_logger


class SvSocketReplacement(bpy.types.PropertyGroup):
    """
    Utility class for mapping old socket name to new socket name.
    """
    old_name: bpy.props.StringProperty(name="Name of socket in the old node")
    new_name: bpy.props.StringProperty(name="Name of socket in the new node")

def set_inputs_mapping(operator, mapping):
    operator.inputs_mapping.clear()
    if mapping:
        for old, new in mapping.items():
            item = operator.inputs_mapping.add()
            item.old_name = old
            item.new_name = new

def set_outputs_mapping(operator, mapping):
    operator.outputs_mapping.clear()
    if mapping:
        for old, new in mapping.items():
            item = operator.outputs_mapping.add()
            item.old_name = old
            item.new_name = new

class SvReplaceNode(bpy.types.Operator):
    """
    Replace selected node with another node.

    This operator removes old node and creates a new node.
    It tries to preserve all links and properties that old
    node had. For cases when new node has other names of
    inputs and/or outputs, it is possible to define mapping.
    In the end, this operator calls `migrate_from' method
    of the new node, so the new node can copy it's settings
    from correct places of old node.
    """
    bl_idname = "node.sv_replace_node"
    bl_label = "Replace selected node with another"
    bl_options = {'INTERNAL'}

    old_node_name: bpy.props.StringProperty(name="Old node name")
    new_bl_idname: bpy.props.StringProperty(name="New node bl_idname")

    inputs_mapping: bpy.props.CollectionProperty(
        name="Input sockets names mapping", type=SvSocketReplacement)

    outputs_mapping: bpy.props.CollectionProperty(
        name="Output sockets names mapping", type=SvSocketReplacement)

    def get_new_input_name(self, old_name):
        print("x",self.inputs_mapping)
        for item in self.inputs_mapping:
            if item.old_name == old_name:
                return item.new_name
        return old_name

    def get_new_output_name(self, old_name):
        for item in self.outputs_mapping:
            if item.old_name == old_name:
                return item.new_name
        return old_name

    def execute(self, context):
        if not self.old_node_name:
            self.report({'ERROR'}, "Old node name is not provided")
            return {'CANCELLED'}

        if not self.new_bl_idname:
            self.report({'ERROR'}, "New node bl_idname is not provided")
            return {'CANCELLED'}

        tree = context.space_data.edit_tree

        old_node = tree.nodes[self.old_node_name]
        new_node = tree.nodes.new(self.new_bl_idname)
        # Copy UI properties
        ui_props = ['location', 'height', 'width', 'label', 'hide']
        for prop_name in ui_props:
            setattr(new_node, prop_name, getattr(old_node, prop_name))
        # Copy ID properties
        for prop_name, prop_value in old_node.items():
            if hasattr(new_node, prop_name):
                new_node[prop_name] = old_node[prop_name]

        # get the node ready for linking
        if hasattr(new_node, "migrate_props_pre_relink"):
            new_node.migrate_props_pre_relink(old_node)

        # remove old links and create new ones
        if hasattr(new_node, "migrate_links_from"):
            new_node.migrate_links_from(old_node, self)

        if hasattr(new_node, "migrate_from"):
            # Allow new node to copy what generic code could not.
            new_node.migrate_from(old_node)


        msg = "Node `{}' ({}) has been replaced with new node `{}' ({})".format(
            old_node.name, old_node.bl_idname,
            new_node.name, new_node.bl_idname)
        sv_logger.info(msg)
        self.report({'INFO'}, msg)


        if old_node.parent and old_node.parent.label == "Deprecated node!":
            if old_node.parent.parent:
                new_node.parent = old_node.parent.parent
            tree.nodes.remove(old_node.parent)
        tree.nodes.remove(old_node)

        return {'FINISHED'}

classes = [
        SvSocketReplacement,
        SvReplaceNode,
    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
