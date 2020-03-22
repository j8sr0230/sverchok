import numpy as np

from mathutils import Matrix, Vector
import bpy
from bpy.props import FloatProperty, EnumProperty, BoolProperty, IntProperty

from sverchok.node_tree import SverchCustomTreeNode, throttled
from sverchok.data_structure import updateNode, zip_long_repeat, fullList

class SvExCurveCurvatureNode(bpy.types.Node, SverchCustomTreeNode):
        """
        Triggers: Curve Curvature
        Tooltip: Calculate curvature of the curve
        """
        bl_idname = 'SvExCurveCurvatureNode'
        bl_label = 'Curve Curvature'
        bl_icon = 'CURVE_NCURVE'

        def sv_init(self, context):
            self.inputs.new('SvExCurveSocket', "Curve").display_shape = 'DIAMOND'
            self.inputs.new('SvStringsSocket', "T")
            self.outputs.new('SvStringsSocket', "Curvature")
            self.outputs.new('SvStringsSocket', "Radius")
            self.outputs.new('SvMatrixSocket', 'Center')

        def process(self):
            if not any(socket.is_linked for socket in self.outputs):
                return

            curve_s = self.inputs['Curve'].sv_get()
            ts_s = self.inputs['T'].sv_get()

            center_out = []
            curvature_out = []
            radius_out = []
            for curve, ts in zip_long_repeat(curve_s, ts_s):
                ts = np.array(ts)

                verts = curve.evaluate_array(ts)

                curvatures = curve.curvature_array(ts)
                radiuses = 1.0 / curvatures

                tangents = curve.tangent_array(ts)
                tangents = tangents / np.linalg.norm(tangents, axis=1)[np.newaxis].T
                binormals = curve.binormal_array(ts)
                normals = curve.main_normal_array(ts)

                radius_vectors = radiuses[np.newaxis].T * normals
                centers = verts + radius_vectors

                matrices_np = np.dstack((-normals, tangents, binormals))
                matrices_np = np.transpose(matrices_np, axes=(0,2,1))
                matrices_np = np.linalg.inv(matrices_np)

                new_matrices = []
                for matrix_np, center in zip(matrices_np, centers):
                    matrix = Matrix(matrix_np.tolist()).to_4x4()
                    matrix.translation = Vector(center)
                    new_matrices.append(matrix)

                center_out.append(new_matrices)
                radius_out.append(radiuses.tolist())
                curvature_out.append(curvatures.tolist())

            self.outputs['Center'].sv_set(center_out)
            self.outputs['Curvature'].sv_set(curvature_out)
            self.outputs['Radius'].sv_set(radius_out)

def register():
    bpy.utils.register_class(SvExCurveCurvatureNode)

def unregister():
    bpy.utils.unregister_class(SvExCurveCurvatureNode)

