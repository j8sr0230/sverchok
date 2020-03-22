
import numpy as np

import bpy
from bpy.props import FloatProperty, EnumProperty, BoolProperty, IntProperty

from sverchok.node_tree import SverchCustomTreeNode, throttled
from sverchok.data_structure import updateNode, zip_long_repeat
from sverchok_extra.data.surface import SvExDeformedByFieldSurface

class SvExApplyFieldToSurfaceNode(bpy.types.Node, SverchCustomTreeNode):
        """
        Triggers: Apply field to surface
        Tooltip: Apply vector field to surface
        """
        bl_idname = 'SvExApplyFieldToSurfaceNode'
        bl_label = 'Apply Field to Surface'

        coefficient : FloatProperty(
                name = "Coefficient",
                default = 1.0,
                update=updateNode)

        def sv_init(self, context):
            self.inputs.new('SvExVectorFieldSocket', "Field").display_shape = 'CIRCLE_DOT'
            self.inputs.new('SvExSurfaceSocket', "Surface").display_shape = 'DIAMOND'
            self.inputs.new('SvStringsSocket', "Coefficient").prop_name = 'coefficient'
            self.outputs.new('SvExSurfaceSocket', "Surface").display_shape = 'DIAMOND'

        def process(self):
            if not any(socket.is_linked for socket in self.outputs):
                return

            surface_s = self.inputs['Surface'].sv_get()
            field_s = self.inputs['Field'].sv_get()
            coeff_s = self.inputs['Coefficient'].sv_get()

            surface_out = []
            for surface, field, coeff in zip_long_repeat(surface_s, field_s, coeff_s):
                if isinstance(coeff, (list, tuple)):
                    coeff = coeff[0]

                new_surface = SvExDeformedByFieldSurface(surface, field, coeff)
                surface_out.append(new_surface)

            self.outputs['Surface'].sv_set(surface_out)

def register():
    bpy.utils.register_class(SvExApplyFieldToSurfaceNode)

def unregister():
    bpy.utils.unregister_class(SvExApplyFieldToSurfaceNode)

