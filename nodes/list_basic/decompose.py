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
from bpy.props import BoolProperty, IntProperty, StringProperty

from node_tree import SverchCustomTreeNode
from data_structure import (levelsOflist, multi_socket, changable_sockets,
                            get_socket_type_full, SvSetSocket, SvGetSocketAnyType)


class SvListDecomposeNode(bpy.types.Node, SverchCustomTreeNode):
    ''' List devided to multiple sockets in some level '''
    bl_idname = 'SvListDecomposeNode'
    bl_label = 'List Decompose'
    bl_icon = 'OUTLINER_OB_EMPTY'

    # two veriables for multi socket input
    base_name = 'data'
    multi_socket_type = 'StringsSocket'

    # two veriables for adaptive socket
    typ = StringProperty(name='typ',
                         default='')
    newsock = BoolProperty(name='newsock',
                           default=False)

    level = IntProperty(name='level',
                        default=1, min=0)

    def draw_buttons(self, context, layout):
        col = layout.column(align=True)
        col.prop(self, 'level')

    def sv_init(self, context):
        # initial socket, is defines type of output
        self.inputs.new('StringsSocket', "data", "data")
        # adaptive multy socket
        self.outputs.new('StringsSocket', "data", "data")

    def update(self):
        if 'data' in self.inputs and self.inputs['data'].links:
            # get any type socket from input:
            data = SvGetSocketAnyType(self, self.inputs['data'])

            # Process data
            leve = min((levelsOflist(data)-2), self.level)
            result = self.beat(data, leve, leve)

            # multisocket - from util(formula node)
            multi_socket(self, min=1, start=2, breck=True, output=len(result))

            # adaptive socket - from util(mask list node)
            # list to pack and change type of multysockets in output... maybe not so quick
            outputsocketname = [socket.name for socket in self.outputs]
            changable_sockets(self, 'data', outputsocketname)
            self.multi_socket_type = get_socket_type_full(self, 'data')

            # how to assign correct property to adaptive output:
            # in nearest future with socket's data' dictionary we will send
            # only node_name+layout_name+socket_name in str() format
            # and will make separate definition to easyly assign and
            # get and recognise data from dictionary
            for i, out in enumerate(result):
                SvSetSocket(self.outputs[i], out)
                if i >= 32: break

    def beat(self, data, level, left):
        out = []
        if left:
            for objects in data:
                out.extend(self.beat(objects, level, left-1))
        elif level:
            if type(data) not in (int, float):
                for objects in data:
                    out.append([self.beat(objects, level-1, 0)])
            else:
                return data
        else:
            out.extend([data])
        return out


def register():
    bpy.utils.register_class(SvListDecomposeNode)


def unregister():
    bpy.utils.unregister_class(SvListDecomposeNode)


