import bpy
import bmesh

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy_extras.object_utils import object_data_add
from bpy.types import Operator


from mathutils import Vector
from itertools import zip_longest
import json


def read_some_data(context, filepath, use_some_setting):
    print("running read_some_data...")
    # would normally load the data here
    with open(filepath, 'r', encoding='utf-8') as f:
        data = f.read()
    return data

def grouper(iterable, n, fillvalue=0):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def objectify(model, m):
    m_data = model['vertices'][m['mesh']]
    all_vertices = m_data['position']['data']
    mesh = model['meshes'][m['mesh']]
    indices = mesh['indices']
    verts = [i for i in grouper(all_vertices, 3)]
    edges = []
    faces = [i for i in grouper(indices, 3)]
    return verts, edges, faces


def add_object(self, context, data, filename):
    m_inst = data['model']['meshInstances']
    model = data['model']

    for m in m_inst:
        active_node = model['nodes'][m['node']]

        name = active_node['name'].replace(' ', '_')
        position = active_node['position']
        rotation = active_node['rotation']
        scale = active_node['scale']

        try:
            verts, edges, faces = objectify(model, m)
            # verts = [[i[0]* scale[0], i[1]* scale[1], i[2]* scale[2]] for i in verts]

            clean_filename = ''.join(filename.split('.')[0])

            mesh = bpy.data.meshes.new(name=f"{name}")
            mesh.from_pydata(verts, edges, faces)
            mesh.validate()

            # Update mesh geometry after adding stuff.
            mesh.update()

            # useful for development when the mesh may be invalid.
            # mesh.validate(verbose=True)
            context.area.ui_type = 'VIEW_3D'

            object_data_add(context, mesh, operator=None)

            obj = bpy.context.active_object
            mesh['position'] = position
            obj.location = position
            obj.scale = scale
        except:
            # Possible dissolve fails for some edges, but don't fail silently in case this is a real bug.
            import traceback
            traceback.print_exc()



class ImportSomeData(Operator, ImportHelper):
    """Import PlayCanvas json model"""
    bl_idname = "import_json.some_data"  # important since its how bpy.ops.import_json.some_data is constructed
    bl_label = "Import Some Data"

    # ImportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    type: EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(
            ('OPT_A', "First Option", "Description one"),
            ('OPT_B', "Second Option", "Description two"),
        ),
        default='OPT_A',
    )

    def execute(self, context):
        # Ok we should create the collection if it doesn't exist
        # add the collection TODO: get better name
        # polaris = bpy.data.collections.new('Polaris')
        # bpy.ops.object.collection_instance_add(collection=polaris.name)
        # link collections ?
        # bpy.context.scene.collection.original.children.link(collection)
        filename = self.filepath.split('/')[-1].split('.')[0]
        data = read_some_data(context, self.filepath, self.use_setting)
        data = json.loads(data)
        add_object(self, context, data, filename)
        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text="Json Import Operator")


def register():
    bpy.utils.register_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_json.some_data('INVOKE_DEFAULT')
