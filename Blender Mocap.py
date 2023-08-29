
bl_info = {
    "name": "Blender Mocap",
    "author": "Daniel W",
    "version": (0, 1),
    "blender": (3, 60, 0),
    "location": "3D View > Sidebar > Blender Mocap",
    "description": "Motion capture",
    "category": "3D View"
}


import bpy
from bpy.types import Panel, Operator, PropertyGroup, FloatProperty, PointerProperty, StringProperty
from bpy.utils import register_class, unregister_class
from bpy_extras.io_utils import ExportHelper


body_names = [
"00 nose",
"01 left eye (inner)",
"02 left eye",
"03 left eye (outer)",
"04 right eye (inner)",
"05 right eye",
"06 right eye (outer)",
"07 left ear",
"08 right ear",
"09 mouth (left)",
"10 mouth (right)",
"11 left shoulder",
"12 right shoulder",
"13 left elbow",
"14 right elbow",
"15 left wrist",
"16 right wrist",
"17 left pinky",
"18 right pinky",
"19 left index",
"20 right index",
"21 left thumb",
"22 right thumb",
"23 left hip",
"24 right hip",
"25 left knee",
"26 right knee",
"27 left ankle",
"28 right ankle",
"29 left heel",
"30 right heel",
"31 left foot index",
"32 right foot index",
]



def install():
    """ Install MediaPipe and dependencies """
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "ensurepip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mediapipe"])


def body_setup():
    """ Setup tracking markers for body tracking """
    scene_objects = [n for n in bpy.context.scene.objects.keys()]
    setup = "Pose" in scene_objects

    if not setup:
        bpy.ops.object.add(radius=1.0, type='EMPTY')
        pose = bpy.context.active_object
        pose.name = "Pose"

        bpy.ops.object.add(radius=1.0, type='EMPTY')
        body = bpy.context.active_object
        body.name = "Body"
        body.parent = pose

        for k in range(33):
            bpy.ops.object.add(radius=1.0, type='EMPTY')
            box = bpy.context.active_object
            box.name = body_names[k]
            box.scale = (0.01, 0.01, 0.01)
            box.parent = body

    body = bpy.context.scene.objects["Body"]
    return body

# The bones that normally stretch to fit the drivers' locations
stretch_bones_influence = [
"DEF-shin.L",
"DEF-shin.R",
"DEF-shin.L.001",
"DEF-shin.R.001",
"DEF-foot.L",
"DEF-foot.R",
"DEF-thigh.L.001",
"DEF-thigh.R.001",
"DEF-thigh.R",
"DEF-thigh.L",
"DEF-upper_arm.L",
"DEF-upper_arm.R",
"DEF-upper_arm.L.001",
"DEF-upper_arm.R.001",
"DEF-forearm.L",
"DEF-forearm.R",
"DEF-forearm.L.001",
"DEF-forearm.R.001"
]

stretch_bones_ik = [
"MCH-shin_ik.L",
"MCH-shin_ik.R",
"MCH-forearm_ik.L",
"MCH-forearm_ik.R"

]

def delete_stretch():
    context = bpy.context
    scene = context.scene  
    mytool = scene.settings
    current_armature = (mytool.eyedropper)
    new_armature = bpy.data.objects[current_armature]
    for n in range(17):
        new_armature.pose.bones[stretch_bones_influence[n]].constraints["Stretch To"].influence = 0
    for k in range(4):
        new_armature.pose.bones[stretch_bones_ik[k]].constraints["IK"].use_stretch = False
        new_armature.pose.bones[stretch_bones_ik[k]].constraints["IK.001"].use_stretch = False



def full_delete():
    """ Deletes all objects associated with full capture """
    scene_objects = [n for n in bpy.context.scene.objects.keys()]
    pose = bpy.context.scene.objects["Pose"]

    if "Hand Left" in scene_objects:
        for c in  bpy.context.scene.objects["Hand Left"].children:
            bpy.data.objects[c.name].select_set(True)
            bpy.ops.object.delete()
        bpy.data.objects["Hand Left"].select_set(True)
        bpy.ops.object.delete()

    if "Hand Right" in scene_objects:
        for c in  bpy.context.scene.objects["Hand Right"].children:
            bpy.data.objects[c.name].select_set(True)
            bpy.ops.object.delete()
        bpy.data.objects["Hand Right"].select_set(True)
        bpy.ops.object.delete()

    if "Face" in scene_objects:
        for c in  bpy.context.scene.objects["Face"].children:
            bpy.data.objects[c.name].select_set(True)
            bpy.ops.object.delete()
        bpy.data.objects["Face"].select_set(True)
        bpy.ops.object.delete()

import numpy as np
import math


def run_body(file_path):
    try:
        import cv2
        import mediapipe as mp
    except Exception as e:
        # bpy.ops.message.messagebox('INVOKE_DEFAULT', 'Installing additional libraries, this may take a moment...')
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        install()
        import cv2
        import mediapipe as mp

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    head_rot_initial = 0

    body = body_setup()
    # Clean up hands and face if they were previously captured
    full_delete()

    context = bpy.context
    scene = context.scene  
    mytool = scene.settings
    
    selected_armature = scene.objects.get(mytool.eyedropper) 
    bpy.data.objects["Pose"].location = (selected_armature.location)  
    bpy.data.objects["Pose"].rotation_euler.z = (selected_armature.rotation_euler.z)
    #body.location = (selected_armature.location)
            
    

    if file_path == "None": cap = cv2.VideoCapture(0)
    else: cap = cv2.VideoCapture(file_path)

    with mp_pose.Pose(
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
        for n in range(9000):
        # for n in range(10):
            success, image = cap.read()
            if not success: continue

            # image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            image.flags.writeable = False
            results = pose.process(image)
            

            if results.pose_landmarks:
                bns = [b for b in results.pose_landmarks.landmark]
                scale = 2
                bones = sorted(body.children, key=lambda b: b.name)
                

                for k in range(33):
                    bones[k].location.y = (bns[k].z)*0.5
                    bones[k].location.x = (0.5-bns[k].x)*scale
                    bones[k].location.z = (0.5-bns[k].y)*scale
                    bones[k].keyframe_insert(data_path="location", frame=n)
                    
                    # Extra Mathmatical Approximations of the 3d pose
                    
                    head_1 = bpy.context.scene.objects["01 left eye (inner)"]
                    head_2 = bpy.context.scene.objects["00 nose"]
                    r_hand_1 = bpy.context.scene.objects["16 right wrist"]
                    r_hand_2 = bpy.context.scene.objects["20 right index"]
                    l_hand_1 = bpy.context.scene.objects["15 left wrist"]
                    l_hand_2 = bpy.context.scene.objects["19 left index"]
                    hip_1 = bpy.context.scene.objects["24 right hip"]
                    hip_2 = bpy.context.scene.objects["23 left hip"]
                    shoulder_1 = bpy.context.scene.objects["12 right shoulder"]
                    shoulder_2 = bpy.context.scene.objects["11 left shoulder"]
                    
                    
                    
                    xl = bpy.data.scenes[0].frame_current
                    l_xl = xl - 1
                    head_rot_initial = 0
                    r_hand_rot_initial = 0
                    l_hand_rot_initial = 0
                    hip_rot_initial = 0
                    
                    if l_xl < xl:
                        head_rot_x = head_1.location.x - head_2.location.x
                        head_rot_z = head_1.location.z - head_2.location.z
                        head_rot = (np.arctan([head_rot_x / head_rot_z])) + 0.15
                        head_rot_final = head_rot - head_rot_initial
                        head_2.rotation_euler = (90, (head_rot_final), 0)
                        head_2.keyframe_insert(data_path="rotation_euler", frame = xl)
                        head_rot_initial = head_rot
                            

                    if l_xl < xl:
                        r_hand_rot_x = r_hand_1.location.x - r_hand_2.location.x
                        r_hand_rot_z = r_hand_1.location.z - r_hand_2.location.z
                        
                        if r_hand_rot_z == 0:
                            r_hand_rot_z = r_hand_rot_z + 0.0001
                            
                        else:
                            r_hand_rot = (np.arctan([r_hand_rot_x / r_hand_rot_z]))
                            r_hand_rot_final = r_hand_rot - r_hand_rot_initial
                            r_hand_2.rotation_euler = (0, -r_hand_rot_final, 180)
                            r_hand_2.keyframe_insert(data_path="rotation_euler", frame = xl)
                            r_hand_rot_initial = r_hand_rot
                            
                    if l_xl < xl:
                        l_hand_rot_x = l_hand_1.location.x - l_hand_2.location.x
                        l_hand_rot_z = l_hand_1.location.z - l_hand_2.location.z
                        
                        if l_hand_rot_z == 0:
                            l_hand_rot_z = l_hand_rot_z + 0.0001
                            
                        else:
                            l_hand_rot = (np.arctan([l_hand_rot_x / l_hand_rot_z]))
                            l_hand_rot_final = l_hand_rot - l_hand_rot_initial
                            l_hand_2.rotation_euler = (0, -l_hand_rot_final, -180)
                            l_hand_2.keyframe_insert(data_path="rotation_euler", frame = xl)
                            l_hand_rot_initial = l_hand_rot
                            
                    if l_xl < xl:
                        hip_rot_z = hip_1.location.x - hip_2.location.x
                        torso_width = hip_rot_z
                        torso_height = shoulder_1.location.z - hip_1.location.z
                        area = ((abs(torso_width * torso_height))*10)
                        
                        if (shoulder_1.location.y - shoulder_2.location.y) == 0:
                            shoulder_1.location.y = shoulder_1.location.y + 0.001
                            
                        torso_slope = -(((shoulder_1.location.z + 10) - shoulder_2.location.z) / (shoulder_1.location.y - shoulder_2.location.y))
                        
                        depth_value_initial = 0
                        
                        if torso_width == 0.00:
                            torso_width = torso_width + 0.001
                        
                        if (torso_width * 1.4) > torso_height:
                            depth_value = torso_width
                            depth = depth_value - depth_value_initial
                            depth_value = depth_value_initial
                            
                        if (torso_width * 1.4) < torso_height:
                            depth_value = torso_height
                            depth = depth_value - depth_value_initial
                            depth_value = depth_value_initial
                            
                        Pose = bpy.data.objects["Pose"]
                        pose_x = Pose.location.x
                        pose_z = Pose.location.z 
                        
                        
                        Pose.location = (pose_x, ((-2 * depth) + 1), pose_z)
                        Pose.keyframe_insert(data_path="location", frame = xl)
                        
                        if hip_rot_z == 0:
                            hip_rot_z = hip_rot_z + 0.0001
                            
                        if torso_slope > 0.0000:
                            hip_rot = (((((np.arcsin(hip_rot_z))))*10) - 1)
                            hip_rot_final = hip_rot - hip_rot_initial
                            hip_2.rotation_euler = (0, 0, hip_rot_final)
                            hip_2.keyframe_insert(data_path="rotation_euler", frame = xl)
                            hip_rot_initial = hip_rot
                        if torso_slope < 0.0000:
                            hip_rot = (((((np.arcsin(hip_rot_z))))*10) - 1)
                            hip_rot_final = hip_rot - hip_rot_initial
                            hip_2.rotation_euler = (0, 0, -hip_rot_final)
                            hip_2.keyframe_insert(data_path="rotation_euler", frame = xl)
                            hip_rot_initial = hip_rot
                        if torso_slope == 0:
                            hip_2.rotation_euler = (0, 0, 0)
                            hip_2.keyframe_insert(data_path="rotation_euler", frame = xl)
                    
                
                    

            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            image = cv2.flip(image, 1)

            cv2.imshow('MediaPipe Pose', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            bpy.context.scene.frame_set(n)

        cap.release()
        cv2.destroyAllWindows()

        

def draw_file_opener(self, context):
    layout = self.layout
    scn = context.scene
    col = layout.column()
    row = col.row(align=True)
    row.prop(scn.settings, 'file_path', text='directory:')
    row.operator("something.identifier_selector", icon="FILE_FOLDER", text="")


class RunFileSelector(bpy.types.Operator, ExportHelper):
    """Import Video"""
    bl_idname = "something.identifier_selector"
    bl_label = "some folder"
    filename_ext = ""

    def execute(self, context):
        fdir = self.properties.filepath
        context.scene.settings.file_path = fdir
        print("Using file: ", context.scene.settings.file_path)
        if context.scene.settings.body_tracking: run_body(context.scene.settings.file_path)
        else: run_full(context.scene.settings.file_path)
        return{'FINISHED'}
    
    




class Settings(PropertyGroup):
    smoothing: bpy.props.FloatProperty(name = "Animation Smoothing",
                            description = "Smoothing between 0 and 1",
                            min = 0.0,
                            max = 1.0,
                            default = 0.1)

    file_path = bpy.props.StringProperty()
    

    # Capture only body pose if True, otherwise capture hands, face and body
    body_tracking = bpy.props.BoolProperty(default=True)
    
    eyedropper : bpy.props.StringProperty(name = "Armature")
    
    smooth_val : bpy.props.FloatProperty(name = "Smooth Value", min = 0, max = 10)

class RunOperator(bpy.types.Operator):
    """Capture Motion"""
    bl_idname = "object.run_body_operator"
    bl_label = "Run Body Operator"

    def execute(self, context):
        if context.scene.settings.body_tracking: run_body("None")
        else: run_full("None")
        return {'FINISHED'}
    
    
class AddArmature(bpy.types.Operator):
    """Add Rig"""
    bl_idname = "object.add_rig"
    bl_label = "Add Rig"
    
    
    def execute(self, context):
        import rigify
        bpy.ops.object.armature_human_metarig_add()
        bpy.ops.object.mode_set(mode='OBJECT')
        for obj in bpy.context.selected_objects:
            rig_name = obj.name
        context = bpy.context
        scene = bpy.context.scene
        mrig = bpy.data.objects[rig_name]
        rigify.generate.generate_rig(context, mrig)
        return {'FINISHED'}
    
    
    
         
    
class MessageBox(bpy.types.Operator):
    bl_idname = "message.messagebox"
    bl_label = ""

    message = bpy.props.StringProperty(
        name = "message",
        description = "message",
        default = 'Installing additional libraries, this may take a moment...'
    )

    def execute(self, context):
        self.report({'INFO'}, self.message)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 400)

    def draw(self, context):
        self.layout.label(text=self.message)


class BlenderMocapPanel(bpy.types.Panel):
    bl_label = "Blender Mocap"
    bl_category = "Blender Mocap"
    bl_idname = "Blender Mocap"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Blender Mocap"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        settings = context.scene.settings
        scene = context.scene
        mytool = scene.settings
        
        row = layout.row()
        row.label(text="Select an Armature")
        
        layout.prop_search(mytool, "eyedropper", context.scene, "objects")
        
        row = layout.row()
        row.label(text="Run Motion Capture")

        row = layout.row()
        row.operator(RunOperator.bl_idname, text="Capture Motion")

        row = layout.row()
        row.operator(RunFileSelector.bl_idname, text="Import Video")
        
        row = layout.row()
        row.operator(AddArmature.bl_idname, text="Add Rig")
        
        row = layout.row()
        row.operator(TransferAnimation.bl_idname, text="Transfer Animation")

        row = layout.row()
        row.label(text="(Press q to stop)")

        row = layout.row()
        row.label(text="Select the rig and drivers")

        row = layout.row()
        row.operator(SelectSystem.bl_idname, text="Select System")
        
        layout.prop(mytool, "smooth_val")
        
        row = layout.row()
        row.operator(Smooth_animation.bl_idname, text = "Smooth Animation")
        

        row = layout.row()
        label = "Body" if settings.body_tracking else "Body, Hands and Face"
        row.prop(settings, 'body_tracking', text=label, toggle=True)
        
        context = bpy.context     
        scene = context.scene
        mytool = scene.settings 
        
     
def smooth_animation(armature):
    
    context = bpy.context
    scene = context.scene
    mytool = scene.settings
    
    armature = scene.objects.get(mytool.eyedropper)
    
    if (mytool.smooth_val > 0.00):
        new_drivers = body_names
                    
        for n in range(31):
            new_drivers = bpy.data.objects[body_names[n]]
            new_drivers.select_set(True)
            fcurves = bpy.context.active_object.animation_data.action.fcurves
            bpy.context.area.type = "GRAPH_EDITOR"
            bpy.ops.graph.gaussian_smooth(factor=((mytool.smooth_val)/10))
            new_drivers.select_set(False)
        
        bpy.context.area.type = "VIEW_3D"
        scene = context.scene
        mytool = scene.settings
                        
        selected_armature = scene.objects.get(mytool.eyedropper)
                        
        selected_armature.select_set(False)
        bpy.data.objects["Body"].select_set(False)
        bpy.data.objects["Pose"].select_set(False)
            
        #fcurves = bpy.context.active_object.animation_data.action.fcurves
        #for curve in fcurves:
            #bpy.ops.graph.gaussian_smooth(factor=((mytool.scale_val)/10))

        
        
def add_constraints(selected_armature):
    
    context = bpy.context
    scene = context.scene
    mytool = scene.settings
    
    selected_armature = scene.objects.get(mytool.eyedropper)
    
    constraint_bones = [
    "hand_ik.R",
    "hand_ik.L",
    "torso",
    "foot_ik.L",
    "foot_ik.R",
    "root",
    ]
    
    constraint_cubes = [
    "15 left wrist",
    "16 right wrist",
    "23 left hip",
    "32 right foot index",
    "31 left foot index",
    "24 right hip",
    ]
    
    
    for k in range(6):
        current_bone = constraint_bones[k]
        new_bone = selected_armature.pose.bones.get(current_bone)
        
        clc = new_bone.constraints.new("COPY_LOCATION")
        constraint_cubes_object = scene.objects.get(constraint_cubes[k])
        clc.target = constraint_cubes_object
        
    face_bone_constraint = selected_armature.pose.bones.get("head")
    crc = face_bone_constraint.constraints.new("COPY_ROTATION")
    constraint_cubes_object = scene.objects.get("00 nose")
    crc.target = constraint_cubes_object
    
    torso_bone_constraint = selected_armature.pose.bones.get("torso")
    crc_1 = torso_bone_constraint.constraints.new("COPY_ROTATION")
    constraint_cubes_object_1 = scene.objects.get("23 left hip")
    crc_1.target = constraint_cubes_object_1
    
    

    
class TransferAnimation(bpy.types.Operator):
    """Transfer Animation"""
    bl_idname = "object.transfer_animation"
    bl_label = "Transfer Animation"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.settings
        add_constraints(mytool.eyedropper)
        delete_stretch()
        return {'FINISHED'}
    
    
    
class SelectSystem(bpy.types.Operator):
    """Select System"""
    bl_idname = "object.select_system"
    bl_label = "Select System"
    
    
    def execute(self, context):
        new_drivers = body_names
        
        for n in range(31):
            new_drivers = bpy.data.objects[body_names[n]]
            new_drivers.select_set(True)
            
        scene = context.scene
        mytool = scene.settings
            
        selected_armature = scene.objects.get(mytool.eyedropper)
            
        selected_armature.select_set(True)
        bpy.data.objects["Body"].select_set(True)
        bpy.data.objects["Pose"].select_set(True)
        return {'FINISHED'}
    
    
class Smooth_animation(bpy.types.Operator):
    """Smooth Animation"""
    bl_idname = "object.smooth_animation"
    bl_label = "Smooth Animation"
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.settings
        smooth_animation(mytool.eyedropper)
        return {'FINISHED'}


_classes = [
    BlenderMocapPanel,
    RunOperator,
    RunFileSelector,
    AddArmature,
    TransferAnimation,
    SelectSystem,
    Smooth_animation,
    Settings,
    MessageBox
]


def register():
    for c in _classes: register_class(c)
    bpy.types.Scene.settings = bpy.props.PointerProperty(type=Settings)
    


def unregister():
    for c in _classes: unregister_class(c)
    del bpy.types.Scene.settings


if __name__ == "__main__":
    register()
