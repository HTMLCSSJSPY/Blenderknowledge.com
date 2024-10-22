import bpy
import json
import random
import math
import os
from collections import Counter

bl_info = {
    "name": "Advanced Text to 3D Model Generator",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Text to 3D",
    "description": "Generate complex 3D models from text input with self-learning",
    "category": "Object",
}

# Initialize with existing data
INITIAL_DATA = [
    {"input": "cube"},
    {"input": "red cube"},
    {"input": "blue car"},
    {"input": "large red cube up smooth subdivide"},
    {"input": "large green icosphere"},
    {"input": "large green icosphere"},
    {"input": "large red metallic sphere with bevel up"},
    {"input": "large red metallic sphere with bevel down"},
    {"input": "sphere"},
    {"input": "green sphere"},
    {"input": "red cube"},
    {"input": "green sphere"},
    {"input": "blue icosphere"},
    {"input": "orange cyclinder"},
    {"input": "orange cone"},
    {"input": "yellow cone"},
    {"input": "yellow cone 10m"}
]

class TEXT_TO_3D_PT_panel(bpy.types.Panel):
    bl_label = "Text to 3D Model"
    bl_idname = "TEXT_TO_3D_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Text to 3D"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "user_input")
        layout.operator("object.generate_model")

class OBJECT_OT_generate_model(bpy.types.Operator):
    bl_idname = "object.generate_model"
    bl_label = "Generate Model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        user_input = context.scene.user_input.lower()
        self.generate_model_from_text(user_input)
        self.save_user_data(user_input)
        return {'FINISHED'}

    def generate_model_from_text(self, text):
        words = text.split()
        main_shape = self.create_main_shape(words)
        self.modify_shape(main_shape, words)
        self.apply_materials(main_shape, words)
        self.add_modifiers(main_shape, words)
        self.position_object(main_shape, words)

    def create_main_shape(self, words):
        shapes = {
            "cube": self.create_cube,
            "sphere": self.create_sphere,
            "cylinder": self.create_cylinder,
            "cone": self.create_cone,
            "torus": self.create_torus,
            "plane": self.create_plane,
            "circle": self.create_circle,
            "icosphere": self.create_icosphere,
            "suzanne": self.create_suzanne,
            "text": self.create_text,
        }

        # Use self-learning to determine the most likely shape
        shape_counts = Counter(word for data in INITIAL_DATA for word in data['input'].split() if word in shapes)
        most_common_shape = shape_counts.most_common(1)[0][0] if shape_counts else "cube"

        for word in words:
            if word in shapes:
                return shapes[word]()
        
        return shapes[most_common_shape]()  # Use the most common shape as default

    def modify_shape(self, obj, words):
        size = next((word for word in words if word in ["tiny", "small", "large", "huge"]), "medium")
        sizes = {"tiny": 0.25, "small": 0.5, "medium": 1, "large": 2, "huge": 4}
        obj.scale = (sizes[size],) * 3

        if "thin" in words:
            obj.scale.x *= 0.5
        if "wide" in words:
            obj.scale.x *= 2
        if "tall" in words:
            obj.scale.z *= 2
        if "short" in words:
            obj.scale.z *= 0.5

        if "rotate" in words:
            obj.rotation_euler = (random.uniform(0, math.pi), random.uniform(0, math.pi), random.uniform(0, math.pi))

        # Check for specific size in meters
        for word in words:
            if word.endswith('m') and word[:-1].isdigit():
                size_in_meters = float(word[:-1])
                obj.scale = (size_in_meters,) * 3

    def apply_materials(self, obj, words):
        colors = {
            "red": (1, 0, 0), "green": (0, 1, 0), "blue": (0, 0, 1),
            "yellow": (1, 1, 0), "cyan": (0, 1, 1), "magenta": (1, 0, 1),
            "white": (1, 1, 1), "black": (0, 0, 0), "gray": (0.5, 0.5, 0.5),
            "orange": (1, 0.5, 0), "purple": (0.5, 0, 0.5), "pink": (1, 0.75, 0.8),
        }

        # Use self-learning to determine the most likely color
        color_counts = Counter(word for data in INITIAL_DATA for word in data['input'].split() if word in colors)
        most_common_color = color_counts.most_common(1)[0][0] if color_counts else "gray"

        color = next((colors[word] for word in words if word in colors), colors[most_common_color])
        
        mat = bpy.data.materials.new(name=f"Material")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs[0].default_value = (*color, 1)
        
        if "metallic" in words:
            bsdf.inputs[4].default_value = 1.0
        if "glass" in words:
            bsdf.inputs[15].default_value = 1.0
            bsdf.inputs[7].default_value = 0.1
        
        obj.data.materials.append(mat)

    def add_modifiers(self, obj, words):
        if "smooth" in words:
            bpy.ops.object.shade_smooth()
        
        if "subdivide" in words:
            subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
            subsurf.levels = 2
        
        if "bevel" in words:
            bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
            bevel.width = 0.02
        
        if "array" in words:
            array = obj.modifiers.new(name="Array", type='ARRAY')
            array.count = 3
        
        if "twist" in words:
            twist = obj.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
            twist.deform_method = 'TWIST'
            twist.angle = math.radians(90)

    def position_object(self, obj, words):
        positions = {"up": (0, 0, 2), "down": (0, 0, -2), "left": (-2, 0, 0), "right": (2, 0, 0),
                     "front": (0, 2, 0), "back": (0, -2, 0)}
        
        for word, pos in positions.items():
            if word in words:
                obj.location = pos
                break

    # Shape creation methods
    def create_cube(self):
        bpy.ops.mesh.primitive_cube_add()
        return bpy.context.active_object

    def create_sphere(self):
        bpy.ops.mesh.primitive_uv_sphere_add()
        return bpy.context.active_object

    def create_cylinder(self):
        bpy.ops.mesh.primitive_cylinder_add()
        return bpy.context.active_object

    def create_cone(self):
        bpy.ops.mesh.primitive_cone_add()
        return bpy.context.active_object

    def create_torus(self):
        bpy.ops.mesh.primitive_torus_add()
        return bpy.context.active_object

    def create_plane(self):
        bpy.ops.mesh.primitive_plane_add()
        return bpy.context.active_object

    def create_circle(self):
        bpy.ops.mesh.primitive_circle_add()
        return bpy.context.active_object

    def create_icosphere(self):
        bpy.ops.mesh.primitive_ico_sphere_add()
        return bpy.context.active_object

    def create_suzanne(self):
        bpy.ops.mesh.primitive_monkey_add()
        return bpy.context.active_object

    def create_text(self):
        bpy.ops.object.text_add()
        text_obj = bpy.context.active_object
        text_obj.data.body = "3D"
        return text_obj

    def save_user_data(self, user_input):
        INITIAL_DATA.append({"input": user_input})

def register():
    bpy.types.Scene.user_input = bpy.props.StringProperty(name="Description")
    bpy.utils.register_class(TEXT_TO_3D_PT_panel)
    bpy.utils.register_class(OBJECT_OT_generate_model)

def unregister():
    del bpy.types.Scene.user_input
    bpy.utils.unregister_class(TEXT_TO_3D_PT_panel)
    bpy.utils.unregister_class(OBJECT_OT_generate_model)

if __name__ == "__main__":
    register()
