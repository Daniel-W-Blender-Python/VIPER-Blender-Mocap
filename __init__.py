bl_info = {
    "name": "VIPER Blender Full Mocap",
    "author": "Daniel W",
    "version": (0, 2),
    "blender": (4, 0, 0),
    "location": "3D View > Sidebar > VIPER Blender Full Mocap",
    "description": "Full Motion Capture",
    "category": "3D View"
}

import bpy
from bpy.types import Panel, Operator, PropertyGroup, FloatProperty, PointerProperty, StringProperty
from bpy.utils import register_class, unregister_class
from bpy_extras.io_utils import ImportHelper
import bpy_extras
import rigify
import subprocess
import sys
import os
import tensorflow as tf
import cv2
import numpy as np
import math
from mathutils import Quaternion
import sys
import time


def install_dependencies():
    python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
    py_lib = os.path.join(sys.prefix, 'lib', 'site-packages','pip')
    subprocess.check_call([sys.executable, "-m", "ensurepip"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tensorflow"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "jaxlib"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "jax"])
    
    
def draw_file_opener(self, context):
    layout = self.layout
    scn = context.scene
    col = layout.column()
    row = col.row(align=True)
    row.prop(scn.settings, 'file_path', text='directory:')
    row.operator("something.identifier_selector", icon="FILE_FOLDER", text="")
    
    
def extract_images(pathIn, pathOut):
    vidcap = cv2.VideoCapture(pathIn)
    success,image = vidcap.read()
    count = 0

    for sequence in range(1):
        try:
            os.makedirs(os.path.join(pathOut, 'Imgs'))
        except:
            pass
    while success:
        if (count % 2)==0:
            cv2.imwrite(pathOut + '/Imgs/' + "Img%d.jpg" % (count/2), image)
            success,image =  vidcap.read()
        count += 1

    return pathOut
    
    
class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @property
    def in_first_quadrant(self):
        return self.x > 0 and self.y > 0

    @property
    def in_second_quadrant(self):
        return self.x < 0 and self.y > 0
    
    @property
    def in_third_quadrant(self):
        return self.x < 0 and self.y < 0
    
    @property
    def in_fourth_quadrant(self):
        return self.x > 0 and self.y < 0
    
    @property
    def length(self):
        return math.sqrt(((self.x) ** 2) + ((self.y) ** 2) + ((self.z) ** 2))
    
    @property
    def euler_to_quaternion(self):
        
        roll = self.x
        yaw = self.z
        pitch = self.y
        
        qw = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
        qx = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
        qy = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
        qz = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)

        return [qw, qx, qy, qz]
    
    
def delete_constraints(num):
    
    context = bpy.context     
    scene = context.scene
    mytool = scene.settings
    
    if num == 0:
        target = scene.objects.get(mytool.eyedropper1)
    if num == 1:
        target = scene.objects.get(mytool.eyedropper2)
    if num == 2:
        target = scene.objects.get(mytool.eyedropper3)
    if num == 3:
        target = scene.objects.get(mytool.eyedropper4)
    
    constraint_bones = [
    "head",
    "neck", "tweak_spine.004",
    "tweak_spine.003",
    "tweak_spine.002",
    "tweak_spine.001",
    "torso",
    "shoulder.L",
    "shoulder.R",
    "upper_arm_tweak.L",
    "upper_arm_tweak.R",
    "forearm_tweak.L",
    "forearm_tweak.R",
    "hand_ik.L",
    "hand_ik.R",
    "shin_tweak.L",
    "shin_tweak.R",
    "foot_ik.L",
    "foot_ik.R",
    "root",
    "thigh_ik.R",
    "thigh_ik.L",
    "upper_arm_ik.R",
    "upper_arm_ik.L",
    "chest",
    "spine_fk.002"
    ]
    
    for k in range(5):
        for n in range(26):
            if target.pose.bones[constraint_bones[n]].constraints:
                target.pose.bones[constraint_bones[n]].constraints.remove(target.pose.bones[constraint_bones[n]].constraints[0])
    
    
stretch_bones_influence = [
"DEF-shin.L.001",
"DEF-shin.R.001",
"DEF-thigh.L.001",
"DEF-thigh.R.001",
"DEF-upper_arm.L.001",
"DEF-upper_arm.R.001",
"DEF-forearm.L.001",
"DEF-forearm.R.001"
]

stretch_bones_ik = [
"MCH-shin_ik.L",
"MCH-shin_ik.R",
"MCH-forearm_ik.L",
"MCH-forearm_ik.R"

]
    
def delete_stretch(num):
    context = bpy.context
    scene = context.scene  
    mytool = scene.settings
    
    if num == 0:
        current_armature = (mytool.eyedropper1)
    if num == 1:
        current_armature = (mytool.eyedropper2)
    if num == 2:
        current_armature = (mytool.eyedropper3)
    if num == 3:
        current_armature = (mytool.eyedropper4)
        
    new_armature = bpy.data.objects[current_armature]
    for n in range(len(stretch_bones_influence)):
        new_armature.pose.bones[stretch_bones_influence[n]].constraints["Stretch To"].influence = 0
    for k in range(4):
        new_armature.pose.bones[stretch_bones_ik[k]].constraints["IK"].use_stretch = False
        new_armature.pose.bones[stretch_bones_ik[k]].constraints["IK.001"].use_stretch = False
        
        
def add_constraints(n):
    
    context = bpy.context     
    scene = context.scene
    mytool = scene.settings
                            
    constraint_bones = [
    "hand_ik.L",
    "hand_ik.R",
    "foot_ik.L",
    "foot_ik.R",
    "forearm_tweak.R",
    "forearm_tweak.L",
    "shin_tweak.R",
    "shin_tweak.L"
    ]
        
        
    constraint_cubes = [
    ["Pose_0_22",
    "Pose_0_23",
    "Pose_0_7",
    "Pose_0_8",
    "Pose_0_19",
    "Pose_0_18",
    "Pose_0_5",
    "Pose_0_4"],
    ["Pose_1_22",
    "Pose_1_23",
    "Pose_1_7",
    "Pose_1_8",
    "Pose_1_19",
    "Pose_1_18",
    "Pose_1_5",
    "Pose_1_4"],
    ["Pose_2_22",
    "Pose_2_23",
    "Pose_2_7",
    "Pose_2_8",
    "Pose_2_19",
    "Pose_2_18",
    "Pose_2_5",
    "Pose_2_4"],
    ["Pose_3_22",
    "Pose_3_23",
    "Pose_3_7",
    "Pose_3_8",
    "Pose_3_19",
    "Pose_3_18",
    "Pose_3_5",
    "Pose_3_4"]        
    ]
        
        
        
    for k in range(8):
        current_bone = constraint_bones[k]
        if n == 0:
            new_bone = bpy.data.objects[mytool.eyedropper1].pose.bones.get(current_bone)
        if n == 1:
            new_bone = bpy.data.objects[mytool.eyedropper2].pose.bones.get(current_bone)
        if n == 2:
            new_bone = bpy.data.objects[mytool.eyedropper3].pose.bones.get(current_bone)
        if n == 3:
            new_bone = bpy.data.objects[mytool.eyedropper4].pose.bones.get(current_bone)
            
        clc = new_bone.constraints.new("COPY_LOCATION")
        constraint_cubes_object = scene.objects.get(constraint_cubes[n][k])
        clc.target = constraint_cubes_object
            
    if n == 0:
        constraint_face_object = scene.objects.get("Pose_0_15")
        selected_armature = bpy.data.objects[mytool.eyedropper1]
    if n == 1:
        constraint_face_object = scene.objects.get("Pose_1_15")
        selected_armature = bpy.data.objects[mytool.eyedropper2]
    if n == 2:
        constraint_face_object = scene.objects.get("Pose_2_15")
        selected_armature = bpy.data.objects[mytool.eyedropper3]
    if n == 3:
        constraint_face_object = scene.objects.get("Pose_3_15")   
        selected_armature = bpy.data.objects[mytool.eyedropper4] 
            
    if n == 0:
        constraint_hip_object = scene.objects.get("Pose_0_3")
    if n == 1:
        constraint_hip_object = scene.objects.get("Pose_1_3")
    if n == 2:
        constraint_hip_object = scene.objects.get("Pose_2_3")
    if n == 3:
        constraint_hip_object = scene.objects.get("Pose_3_3")      
            
    face_bone_constraint = selected_armature.pose.bones.get("head")
    crc = face_bone_constraint.constraints.new("COPY_ROTATION")
    crc.target = constraint_face_object
    
    torso_bone_constraint = selected_armature.pose.bones.get("torso")
    crc_1 = torso_bone_constraint.constraints.new("COPY_ROTATION")
    crc_1.target = constraint_hip_object
    
    r_hand_bone_constraint = selected_armature.pose.bones.get("hand_ik.R")
    crc_2 = r_hand_bone_constraint.constraints.new("COPY_ROTATION")
    crc_2.target = selected_armature
    crc_2.subtarget = "ORG-forearm.R"
        
    l_hand_bone_constraint = selected_armature.pose.bones.get("hand_ik.L")
    crc_3 = l_hand_bone_constraint.constraints.new("COPY_ROTATION")
    crc_3.target = selected_armature
    crc_3.subtarget = "ORG-forearm.L"
    
    
def get_frame_count(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return frame_count


def save_animation():
    
    collection = [
    "Face",
    "Face (Primary)",
    "Face (Secondary)",
    "Torso",
    "Torso (Tweak)",
    "Fingers",
    "Fingers (Detail)",
    "Arm.L (IK)",
    "Arm.L (FK)",
    "Arm.L (Tweak)",
    "Arm.R (IK)",
    "Arm.R (FK)",
    "Arm.R (Tweak)",    
    "Leg.L (IK)",
    "Leg.L (FK)",
    "Leg.L (Tweak)",
    "Leg.R (IK)",
    "Leg.R (FK)",
    "Leg.R (Tweak)",  
    "Root"
    ]  
    
    context = bpy.context
    scene = context.scene
    mytool = scene.settings
    
    num_poses = mytool.num_people
    
    for k in range(num_poses):
        if k == 0:
            armature = scene.objects.get(mytool.eyedropper1)
        if k == 1:
            armature = scene.objects.get(mytool.eyedropper2)
        if k == 2:
            armature = scene.objects.get(mytool.eyedropper3)
        if k == 3:
            armature = scene.objects.get(mytool.eyedropper4)
        
        armature.select_set(True)
        
        for u in range(len(collection)):
            armature.data.collections[collection[u]].is_visible = True

        
        bpy.context.view_layer.objects.active = armature
        
        bpy.ops.nla.bake(frame_start=bpy.data.scenes[0].frame_start, frame_end=bpy.data.scenes[0].frame_end, visual_keying=True, bake_types={'OBJECT'})
        
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.nla.bake(frame_start=bpy.data.scenes[0].frame_start, frame_end=bpy.data.scenes[0].frame_end, visual_keying=True, bake_types={'POSE'})
        bpy.ops.object.mode_set(mode='OBJECT')
        
        armature.select_set(False)

    
    
def extract_motion(file, context):
    
    settings = context.scene.settings
    scene = context.scene
    mytool = scene.settings
  
    addon_dir = os.path.dirname(os.path.realpath(__file__))
    model_asset_path = os.path.join(addon_dir, "metrabs_mob3l_y4t")
    
    model = tf.saved_model.load(model_asset_path)
    
    scene_objects = [n for n in bpy.context.scene.objects.keys()]
    
    num_poses = mytool.num_people
    
    for n in range(num_poses):
        if ("Pose_"+str(n)) not in scene_objects:
            bpy.ops.object.add(radius=1.0, type='EMPTY')
            pose = bpy.context.active_object
            pose.name = "Pose_"+str(n)
        for i in range(29):
            if ("Pose_"+str(n)+"_"+str(i)) not in scene_objects:
                bpy.ops.object.add(radius=0.05, type='EMPTY')
                pose = bpy.context.active_object
                pose.name = "Pose_"+str(n)+"_"+str(i)
                pose.parent = scene.objects.get("Pose_"+str(n))
                
    for q in range(num_poses):
        delete_stretch(q)
        delete_constraints(q)
        add_constraints(q)
        
    frames_path = os.path.join(addon_dir, "Video Frames")
                
    extract_images(mytool.file_name, frames_path)
    
    frame_count = get_frame_count(mytool.file_name)
    
    bpy.data.scenes[0].frame_start = 0
    bpy.data.scenes[0].frame_end = frame_count
    
    for t in range(frame_count):
        if t %mytool.key_step == 0:
            
            bpy.data.scenes[0].frame_set(t)
            image_path = os.path.join(frames_path, ("Imgs/Img" + str(t) + ".jpg"))
            img = tf.image.decode_image(tf.io.read_file(image_path))
            pred = model.detect_poses(img, skeleton='smpl+head_30')
            pred['poses3d'].shape
            
            joint_names = model.per_skeleton_joint_names['smpl+head_30'].numpy().astype(str)
            joint_edges = model.per_skeleton_joint_edges['smpl+head_30'].numpy()
            
            poses3d = pred['poses3d'].numpy()
            poses3d[..., 1], poses3d[..., 2] = poses3d[..., 2], -poses3d[..., 1]
            num = 0
            for pose3d, pose2d in zip(poses3d, pred['poses2d'].numpy()):
                print("Person")
                
                sumx = 0
                sumy = 0
                sumz = 0
                
                for i in range(29):
                    sumx += (pose3d[i][0] / 750)
                    sumy += (pose3d[i][1] / 750)
                    sumz += (pose3d[i][2] / 750)
                    
                avgx = sumx / 29
                avgy = sumy / 29
                avgz = sumz / 29
                
                shin = Vector((pose3d[5][0]-pose3d[8][0]) / 750, (pose3d[5][1]-pose3d[8][1]) / 750, (pose3d[5][2]-pose3d[8][2]) / 750)
                scale = 0.4542 / shin.length
                
                    
                for k in range(29):
                    joint = scene.objects.get("Pose_"+str(num)+"_"+str(k))
                    try:
                        joint.location.x = avgx + ((((pose3d[k][0]) / 750) - avgx) * scale)
                        joint.location.y = avgy + ((((pose3d[k][1]) / 750) - avgy) * scale)
                        joint.location.z = avgz + ((((pose3d[k][2]) / 750) - avgz) * scale)
                        joint.keyframe_insert(data_path="location", frame=t)
                    except:
                        joint_location = False
                if num == 0:
                    try:
                        rig = scene.objects.get(mytool.eyedropper1)
                        rig.location = scene.objects.get("Pose_"+str(num)+"_"+str(6)).location
                        rig.location.z = rig.location.z - 1.35
                        rig.keyframe_insert(data_path="location", frame=t)
                    except:
                        rig_location = False
                if num == 1:
                    try:
                        rig = scene.objects.get(mytool.eyedropper2)
                        rig.location = scene.objects.get("Pose_"+str(num)+"_"+str(6)).location
                        rig.location.z = rig.location.z - 1.35
                        rig.keyframe_insert(data_path="location", frame=t)
                    except:
                        rig_location = False
                if num == 2:
                    try:
                        rig = scene.objects.get(mytool.eyedropper3)
                        rig.location = scene.objects.get("Pose_"+str(num)+"_"+str(6)).location
                        rig.location.z = rig.location.z - 1.35
                        rig.keyframe_insert(data_path="location", frame=t)
                    except:
                        rig_location = False
                if num == 3:
                    try:
                        rig = scene.objects.get(mytool.eyedropper4)
                        rig.location = scene.objects.get("Pose_"+str(num)+"_"+str(6)).location
                        rig.location.z = rig.location.z - 1.35
                        rig.keyframe_insert(data_path="location", frame=t)
                    except:
                        rig_location = False
                    
                num += 1
                
            empty_list = [
            ["Pose_0_17", "Pose_1_17", "Pose_2_17", "Pose_3_17"],
            ["Pose_0_19", "Pose_1_19", "Pose_2_19", "Pose_3_19"],
            ["Pose_0_23", "Pose_1_23", "Pose_2_23", "Pose_3_23"],
            ["Pose_0_2", "Pose_1_2", "Pose_2_2", "Pose_3_2"],
            ["Pose_0_1", "Pose_1_1", "Pose_2_1", "Pose_3_1"],
            ["Pose_0_28", "Pose_1_28", "Pose_2_28", "Pose_3_28"],
            ["Pose_0_25", "Pose_1_25", "Pose_2_25", "Pose_3_25"],
            ["Pose_0_27", "Pose_1_27", "Pose_2_27", "Pose_3_27"],
            ["Pose_0_9", "Pose_1_9", "Pose_2_9", "Pose_3_9"],
            ["Pose_0_0", "Pose_1_0", "Pose_2_0", "Pose_3_0"],
            ["Pose_0_11", "Pose_1_11", "Pose_2_11", "Pose_3_11"],
            ["Pose_0_8", "Pose_1_8", "Pose_2_8", "Pose_3_8"],
            ["Pose_0_14", "Pose_1_14", "Pose_2_14", "Pose_3_14"],
            ["Pose_0_13", "Pose_1_13", "Pose_2_13", "Pose_3_13"],
            ["Pose_0_6", "Pose_1_6", "Pose_2_6", "Pose_3_6"],
            ["Pose_0_3", "Pose_1_3", "Pose_2_3", "Pose_3_3"]
            ]
                
            for n in range(num_poses):
                shoulder = scene.objects.get(empty_list[0][n])
                elbow = scene.objects.get(empty_list[1][n])
                hand = scene.objects.get(empty_list[2][n])
                right_pelvis = scene.objects.get(empty_list[3][n])
                left_pelvis = scene.objects.get(empty_list[4][n])
                right_ear = scene.objects.get(empty_list[5][n])
                left_ear = scene.objects.get(empty_list[6][n])
                nose = scene.objects.get(empty_list[7][n])
                spine = scene.objects.get(empty_list[8][n])
                pelvis = scene.objects.get(empty_list[9][n])
                right_toe = scene.objects.get(empty_list[10][n])
                right_foot = scene.objects.get(empty_list[11][n])
                right_shoulder = scene.objects.get(empty_list[12][n])
                left_shoulder = scene.objects.get(empty_list[13][n])
                chest = scene.objects.get(empty_list[14][n])
                lower_spine = scene.objects.get(empty_list[15][n])
            
                mid_head = (right_ear.location + left_ear.location) / 2
                head_vector = nose.location - mid_head
                head_vector_array = np.array([head_vector.x, head_vector.y, head_vector.z])
                len_head_vector = Vector(head_vector.x, head_vector.y, head_vector.z).length
                    
                    
                foot_vector = right_toe.location - right_foot.location
                foot_vector_array = np.array([foot_vector[0], foot_vector[1], foot_vector[2]])
                len_foot_vector = Vector(foot_vector.x, foot_vector.y, foot_vector.z).length
                    
                
                pelvis_vector = right_pelvis.location - left_pelvis.location
                spine_vector = spine.location - chest.location
                
                pelvis_vector_array = np.array([pelvis_vector.x, pelvis_vector.y, pelvis_vector.z])
                spine_vector_array = np.array([spine_vector.x, spine_vector.y, spine_vector.z])
                
                pelvis_direction_vector_1 = np.cross(pelvis_vector_array, spine_vector_array)
                pelvis_direction_vector_2 = np.cross(spine_vector_array, pelvis_vector_array)
                
                len_pelvis_direction_vector_1 = Vector(pelvis_direction_vector_1[0], pelvis_direction_vector_1[1], pelvis_direction_vector_1[2]).length
                len_pelvis_direction_vector_2 = Vector(pelvis_direction_vector_2[0], pelvis_direction_vector_2[1], pelvis_direction_vector_2[2]).length
                
                angle_1 = np.arccos(np.dot(pelvis_direction_vector_1, foot_vector_array) / (len_pelvis_direction_vector_1 * len_foot_vector))
                angle_2 = np.arccos(np.dot(pelvis_direction_vector_2, foot_vector_array) / (len_pelvis_direction_vector_2 * len_foot_vector))
                
                if angle_1 <= (math.pi / 2):
                    dir_vector = pelvis_direction_vector_1
                if angle_2 < (math.pi / 2):
                    dir_vector = pelvis_direction_vector_2
                    
                if dir_vector[1] == 0:
                    dir_vector[1] = 0.0001
                if pelvis_vector.x == 0:
                    pelvis_vector.x = 0.0001
                angle_xy = np.arctan(dir_vector[0] / dir_vector[1])
                angle_xz = np.arctan(pelvis_vector.z / pelvis_vector.x) / 2
                angle_zy = np.arctan(dir_vector[2] / dir_vector[1])
                
                angle_xz = 0
                angle_zy = 0
                
                if Vector(dir_vector[0], dir_vector[1], 0).in_fourth_quadrant:
                    angle_xy = -angle_xy
                if Vector(dir_vector[0], dir_vector[1], 0).in_second_quadrant:
                    angle_xy = -((math.pi / 2) + angle_xy) - (math.pi / 2)
                if Vector(dir_vector[0], dir_vector[1], 0).in_third_quadrant:
                    angle_xy = -angle_xy
                if Vector(dir_vector[0], dir_vector[1], 0).in_first_quadrant:
                    angle_xy = ((math.pi / 2) - angle_xy) + (math.pi / 2)

                if n == 0:
                    bpy.data.objects[mytool.eyedropper1].rotation_euler = (0, (0), angle_xy)
                    bpy.data.objects[mytool.eyedropper1].keyframe_insert(data_path="rotation_euler", frame=t)
                if n == 1:
                    bpy.data.objects[mytool.eyedropper2].rotation_euler = (0, (0), angle_xy)
                    bpy.data.objects[mytool.eyedropper2].keyframe_insert(data_path="rotation_euler", frame=t)
                if n == 2:
                    bpy.data.objects[mytool.eyedropper3].rotation_euler = (0, (0), angle_xy)
                    bpy.data.objects[mytool.eyedropper3].keyframe_insert(data_path="rotation_euler", frame=t)
                if n == 3:
                    bpy.data.objects[mytool.eyedropper4].rotation_euler = (0, (0), angle_xy)
                    bpy.data.objects[mytool.eyedropper4].keyframe_insert(data_path="rotation_euler", frame=t)
                    
                    
                    
                shoulder_vector = right_shoulder.location - left_shoulder.location
                spine_vector = spine.location - pelvis.location
                
                shoulder_vector_array = np.array([shoulder_vector.x, shoulder_vector.y, shoulder_vector.z])
                spine_vector_array = np.array([spine_vector.x, spine_vector.y, spine_vector.z])
                
                shoulder_direction_vector_1 = np.cross(shoulder_vector_array, spine_vector_array)
                shoulder_direction_vector_2 = np.cross(spine_vector_array, shoulder_vector_array)
                
                len_shoulder_direction_vector_1 = Vector(shoulder_direction_vector_1[0], shoulder_direction_vector_1[1], shoulder_direction_vector_1[2]).length
                len_shoulder_direction_vector_2 = Vector(shoulder_direction_vector_2[0], shoulder_direction_vector_2[1], shoulder_direction_vector_2[2]).length
                
                shoulder_angle_1 = np.arccos(np.dot(shoulder_direction_vector_1, head_vector_array) / (len_shoulder_direction_vector_1 * len_head_vector))
                shoulder_angle_2 = np.arccos(np.dot(shoulder_direction_vector_2, head_vector_array) / (len_shoulder_direction_vector_2 * len_head_vector))
                
                if shoulder_angle_1 < (math.pi / 2):
                    shoulder_dir_vector = shoulder_direction_vector_1
                if shoulder_angle_2 < (math.pi / 2):
                    shoulder_dir_vector = shoulder_direction_vector_2
                    
                shoulder_angle_xy = np.arctan((shoulder_dir_vector[1] - dir_vector[1]) / (shoulder_dir_vector[0] - dir_vector[0]))
                
                shoulder_rot = Vector(0, 0, shoulder_angle_xy).euler_to_quaternion
                    
                if n == 0:
                    bpy.data.objects[mytool.eyedropper1].pose.bones["chest"].rotation_quaternion = (5, shoulder_rot[1], shoulder_rot[2], shoulder_rot[3])
                    bpy.data.objects[mytool.eyedropper1].pose.bones["chest"].keyframe_insert(data_path="rotation_quaternion", frame=t)
                if n == 1:
                    bpy.data.objects[mytool.eyedropper2].pose.bones["chest"].rotation_quaternion = (5, shoulder_rot[1], shoulder_rot[2], shoulder_rot[3])
                    bpy.data.objects[mytool.eyedropper2].pose.bones["chest"].keyframe_insert(data_path="rotation_quaternion", frame=t)
                if n == 2:
                    bpy.data.objects[mytool.eyedropper3].pose.bones["chest"].rotation_quaternion = (5, shoulder_rot[1], shoulder_rot[2], shoulder_rot[3])
                    bpy.data.objects[mytool.eyedropper3].pose.bones["chest"].keyframe_insert(data_path="rotation_quaternion", frame=t)
                if n == 3:
                    bpy.data.objects[mytool.eyedropper4].pose.bones["chest"].rotation_quaternion = (5, shoulder_rot[1], shoulder_rot[2], shoulder_rot[3])
                    bpy.data.objects[mytool.eyedropper4].pose.bones["chest"].keyframe_insert(data_path="rotation_quaternion", frame=t)
                    
                    
                head_vector_array = np.array([head_vector.x, head_vector.y, head_vector.z])
                len_dir_vector = Vector(dir_vector[0], dir_vector[1], dir_vector[2]).length
                
                head_tilt_vector = np.array([(left_ear.location.x - right_ear.location.x), (left_ear.location.y - right_ear.location.y), (left_ear.location.z - right_ear.location.z)])
                len_head_tilt_vector = Vector(head_tilt_vector[0], head_tilt_vector[1], head_tilt_vector[2]).length
                
                if head_vector.y == 0:
                    head_vector.y = 0.0001
                if len_head_tilt_vector == 0:
                    len_head_tilt_vector = 0.0001
                if len_head_vector == 0:
                    len_head_vector = 0.0001
                head_angle_xy = np.arctan(head_vector.x / head_vector.y)
                head_angle_xz = np.arcsin((left_ear.location.z - right_ear.location.z) / len_head_tilt_vector)
                head_angle_zy = np.arcsin(head_vector.z / len_head_vector)
                head_vector_zy = np.array([(left_ear.location.y - right_ear.location.y), (left_ear.location.z - right_ear.location.z)])
         
         
                if Vector(head_vector.x, head_vector.y, 0).in_fourth_quadrant:
                    head_angle_xy = -head_angle_xy
                if Vector(head_vector.x, head_vector.y, 0).in_second_quadrant:
                    head_angle_xy = -((math.pi / 2) + head_angle_xy) - (math.pi / 2)
                if Vector(head_vector.x, head_vector.y, 0).in_third_quadrant:
                    head_angle_xy = -head_angle_xy
                if Vector(head_vector.x, head_vector.y, 0).in_first_quadrant:
                    head_angle_xy = ((math.pi / 2) - head_angle_xy) + (math.pi / 2)
                
                if head_vector.z < 0:    
                    head_angle_zy = (-head_angle_zy) + (math.pi / 2)
                if head_vector.z >= 0:    
                    head_angle_zy = (head_angle_zy) + (math.pi / 2)

                
                if n == 0:
                    bpy.data.objects["Pose_0_15"].rotation_euler = (head_angle_zy, head_angle_xz, head_angle_xy)
                    bpy.data.objects["Pose_0_15"].keyframe_insert(data_path="rotation_euler", frame=t)
                if n == 1:
                    bpy.data.objects["Pose_1_15"].rotation_euler = (head_angle_zy, head_angle_xz, head_angle_xy)
                    bpy.data.objects["Pose_1_15"].keyframe_insert(data_path="rotation_euler", frame=t)
                if n == 2:
                    bpy.data.objects["Pose_2_15"].rotation_euler = (head_angle_zy, head_angle_xz, head_angle_xy)
                    bpy.data.objects["Pose_2_15"].keyframe_insert(data_path="rotation_euler", frame=t)
                if n == 3:
                    bpy.data.objects["Pose_3_15"].rotation_euler = (head_angle_zy, head_angle_xz, head_angle_xy)
                    bpy.data.objects["Pose_3_15"].keyframe_insert(data_path="rotation_euler", frame=t)
                    
        #        spine_vector = spine.location - lower_spine.location
                len_spine_vector = Vector(spine_vector.x, spine_vector.y, spine_vector.z).length
                
                if len_spine_vector == 0:
                    len_spine_vector = 0.0001
                
                spine_angle_yz = (math.pi /2) - np.arcsin((spine.location.z - pelvis.location.z) / len_spine_vector)
                
                if n == 0:
                    bpy.data.objects["Pose_0_3"].rotation_euler = (spine_angle_yz, 0, angle_xy)
                    bpy.data.objects["Pose_0_3"].keyframe_insert(data_path="rotation_euler", frame=t)
                if n == 1:
                    bpy.data.objects["Pose_1_3"].rotation_euler = (spine_angle_yz, 0, angle_xy)
                    bpy.data.objects["Pose_1_3"].keyframe_insert(data_path="rotation_euler", frame=t)
                if n == 2:
                    bpy.data.objects["Pose_2_3"].rotation_euler = (spine_angle_yz, 0, angle_xy)
                    bpy.data.objects["Pose_2_3"].keyframe_insert(data_path="rotation_euler", frame=t)
                if n == 3:
                    bpy.data.objects["Pose_3_3"].rotation_euler = (spine_angle_yz, 0, angle_xy)
                    bpy.data.objects["Pose_3_3"].keyframe_insert(data_path="rotation_euler", frame=t)
                                  
        
    
class Settings(PropertyGroup):
    smoothing: bpy.props.FloatProperty(name = "Animation Smoothing",
                            description = "Smoothing between 0 and 1",
                            min = 0.0,
                            max = 1.0,
                            default = 0.1)

    file_path = bpy.props.StringProperty()
    
    file_name : bpy.props.StringProperty(name = "File Path")
    
    body_tracking = bpy.props.BoolProperty(default=True)
    
    num_people : bpy.props.IntProperty(name = "Poses", default = 1, min = 1, max = 4)
    
    smooth_val : bpy.props.FloatProperty(name = "Smooth Value", min = 0, max = 10)
    
    eyedropper1 : bpy.props.StringProperty(name = "Armature 1")
    eyedropper2 : bpy.props.StringProperty(name = "Armature 2")
    eyedropper3 : bpy.props.StringProperty(name = "Armature 3")
    eyedropper4 : bpy.props.StringProperty(name = "Armature 4")

    key_step : bpy.props.IntProperty(name = "Key Step", default = 4, min = 1, max = 8)
    
    est_time : bpy.props.IntProperty(name = "Estimated Time (Minutes)", default = 0, min = 0, max = 120)

#    cam_index : bpy.props.IntProperty(name = "Camera Index", default = 0, min = 0, max = 5)


class RunFileSelector_Face(bpy.types.Operator, ImportHelper):
    """Import Video (Face)"""
    bl_idname = "something.identifier_selector_face"
    bl_label = "some folder"
    filename_ext = ""

    def execute(self, context):
        settings = context.scene.settings
        scene = context.scene
        mytool = scene.settings
        filename = self.properties.filepath
        mytool.file_name = filename
        return{'FINISHED'} 
    

class ExtractMotion(bpy.types.Operator):
    """Extract Motion"""
    bl_idname = "py.extract_motion"
    bl_label = "Extract Motion"

    def execute(self, context):
        settings = context.scene.settings
        scene = context.scene
        mytool = scene.settings
        extract_motion(mytool.file_name, context)
        return{'FINISHED'} 
    
    
class Save_Animation(bpy.types.Operator):
    """Save Animation"""
    bl_idname = "object.save_animation"
    bl_label = "Save Animation"
    
    def execute(self, context):
        save_animation()
        return {'FINISHED'}
    
    
class InstallDependencies(bpy.types.Operator):
    """Install Dependencies"""
    bl_idname = "object.install_dependencies"
    bl_label = "Install Dependencies"
    
    
    def execute(self, context):
        install_dependencies()
        return {'FINISHED'} 
    
class AddArmature(bpy.types.Operator):
    """Add Rig"""
    bl_idname = "object.add_rig"
    bl_label = "Add Rig"
    
    
    def execute(self, context):
        bpy.ops.object.armature_human_metarig_add()
        bpy.ops.object.mode_set(mode='OBJECT')
        for obj in bpy.context.selected_objects:
            rig_name = obj.name
        context = bpy.context
        scene = bpy.context.scene
        mrig = bpy.data.objects[rig_name]
        rigify.operators.upgrade_face.update_face_rig(mrig)
        rigify.generate.generate_rig(context, mrig)
        context = bpy.context
        scene = bpy.context.scene
        #context = scene.get_context()
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
    bl_label = "VIPER Blender Full Mocap"
    bl_category = "VIPER Blender Full Mocap"
    bl_idname = "VIPER Blender Full Mocap"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "VIPER Blender Full Mocap"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        settings = context.scene.settings
        scene = context.scene
        mytool = scene.settings    
        
        row = layout.row()
        row.label(text="Number of People")
        
        layout.prop(mytool, "num_people")
        
        if mytool.num_people == 1:
            
            layout.prop_search(mytool, "eyedropper1", context.scene, "objects")
            
        if mytool.num_people == 2:
            
            layout.prop_search(mytool, "eyedropper1", context.scene, "objects")
            layout.prop_search(mytool, "eyedropper2", context.scene, "objects")
            
        if mytool.num_people == 3:
            
            layout.prop_search(mytool, "eyedropper1", context.scene, "objects")
            layout.prop_search(mytool, "eyedropper2", context.scene, "objects")
            layout.prop_search(mytool, "eyedropper3", context.scene, "objects")
            
        if mytool.num_people == 4:
            
            layout.prop_search(mytool, "eyedropper1", context.scene, "objects")
            layout.prop_search(mytool, "eyedropper2", context.scene, "objects")
            layout.prop_search(mytool, "eyedropper3", context.scene, "objects")
            layout.prop_search(mytool, "eyedropper4", context.scene, "objects")

        layout.prop(mytool, "key_step")
#        layout.prop(mytool, "cam_index")
        
        row = layout.row()
        row.label(text="Import Video")
 
        row = layout.row()
        row.operator(RunFileSelector_Face.bl_idname, text="Import Video", icon="SEQUENCE")
        
        layout.prop(mytool, "file_name")
        
        row = layout.row()
        row.label(text="Extract Motion")
        
        row = layout.row()
        row.operator(ExtractMotion.bl_idname, text="Extract Motion", icon="INDIRECT_ONLY_OFF")
        
        row = layout.row()
        row.label(text="Save Animation to Armatures")
        
        row = layout.row()
        row.operator(Save_Animation.bl_idname, text="Save Animation", icon="DECORATE_DRIVER")
        
        row = layout.row()
        row.operator(AddArmature.bl_idname, text="Add Rig", icon="OUTLINER_OB_ARMATURE")

        row = layout.row()
        row.label(text="Install Tensorflow and OpenCV")

        row = layout.row()
        row.operator(InstallDependencies.bl_idname, text="Install Dependencies", icon="IMPORT")

        row = layout.row()
        label = "Body" if settings.body_tracking else "Body, Hands and Face"
        row.prop(settings, 'body_tracking', text=label, toggle=True)
        
        context = bpy.context     
        scene = context.scene
        mytool = scene.settings
        


_classes = [
    BlenderMocapPanel,
    RunFileSelector_Face,
    AddArmature,
    ExtractMotion,
    Save_Animation,
    InstallDependencies,
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
    install_dependencies()
    register()

