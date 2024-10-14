# VIPER: Video and Image-Based Pose Estimation
A Blender Addon that uses István Sárándi's Metrabs 3D pose estimation model in Blender to capture a person's movements, and apply them to multiple characters.

Here is a demo of what the addon can do:

https://www.loom.com/share/ce14131ef20c4d74ac738ffcb00d0383

The addon extracts 3D joint locations from the image, using the Metrabs model, and marks those locations with empties in the 3D space. The addon then constrains the locations of the hands and feet to the corresponding empties. To calculate rotations of the torso and the root, the addon assumes that the direction of the rig is within 180 degress of the vector orthogonal to the pelvis. To calculate the rotation of the shoulders, the addon assumes that the direction of the shoulders is within 180 degrees of the head vector.

In order for the bone constraints to accurately map the true locations of the bones, the average scale of the empties for each person has to be roughly the same scale as the rigify rig. In order to do this, the addon calculates the length of the shin (since the length of the shin is constant) created by the empties, dividing it by the default length of the shin in the rigify addon, and uses a Procrustes analysis to scale the empties to match the rig.

Since the addon uses bone constraints, a "save animation" feature was necessary to copy the movements directly into keyframes on the rig. This feature merely bakes the action of the rig using visual keying, allowing the transfer of motion across rigs, and easier integration into 3D projects.

The Metrabs model takes around two seconds per frame to estimate static poses on a cpu, meaning that a 60 second video at 24 fps would take over 45 minutes for the motion to be extracted. However, the key step reduces this time complexity significantly. The key step refers to the amount of frames skipped plus one (if the key step is four, it places a keyframe every four frames). This not only reduces the amount of frames that need to be used, but it also inherently smooths the animation. For the same 60 second video, with a key step of four (which is recommended), the addon would only take a little over ten minutes to extract the motion.


# How To Install:

First, download the zip file from github, and then download the metrabs model, and add it to the addon folder within zip file: https://omnomnom.vision.rwth-aachen.de/data/metrabs/metrabs_mob3l_y4t.zip 

Then, open Blender **WITH** **ADMINISTRATOR** **PRIVILEGES**.

https://www.loom.com/share/909dcb9579a74c17aeba4d5d7f071a46


# How to Use:

Click "Add Rig", or import your own rig from the Rigify addon. This must be the rig though, not the actual armature.

![image](https://github.com/Daniel-W-Blender-Python/Blender-Motion-Capture-Addon/assets/142774885/5272a9e2-7486-44bf-bc85-1a613c4f6a13)

Then, you can delete the armature beneath the rig. To show more parts of the rig, click "data", and check all of the layers.

![image](https://github.com/Daniel-W-Blender-Python/Blender-Motion-Capture-Addon/assets/142774885/176ac437-ea9d-45bd-83d1-43d29944b649)

You have to input the rig you want to track the motion to in the "Armature" box.

![image](https://github.com/Daniel-W-Blender-Python/Blender-Motion-Capture-Addon/assets/142774885/2e4ca3ba-2b93-4a6a-9b56-4680209b3643)

Then, you can either capture motion from a webcam, or you could import a file. This may take a while the first time you click it. Then hit "Transfer Animation" to transfer the animation to your rig.

![image](https://github.com/Daniel-W-Blender-Python/Blender-Motion-Capture-Addon/assets/142774885/060a6084-ab0f-4b1b-9baf-acdf279f3516)

To smooth the animation, set the degree to which you want it smoothed in the "Smooth Value" box, then click the "Smooth Animation" button. To save the animation to your rig, click "Save Animation". This ensures that if you want to track motion for a different character in your scene, the motion you tracked for your original character will stay with that rig.

The "Select System" button, selects the rig and the drivers, so that you can move the rig around the scene without your motion being changed.

In Version 3, there is a new Rokoko Retargeting feature. Rokoko is a popular free motion capture resource, but it uses a different rig than the standard one from Rigify. In the addon, you would first import the Rokoko rig (with animation) as an FBX, making sure to click "Automatic Bone Orientation" before importing:

![image](https://github.com/Daniel-W-Blender-Python/Blender-Motion-Capture-Addon/assets/142774885/2e576c2b-e1bf-4bd5-a919-637ba0cbbc0f)

This orients the bones in the standard format, rather than rotating them all vertically in the 3d space. Then, select "Root" as the object under "Source" in the addon. After that, select the Rigify rig you are using as the object under "Target".

![image](https://github.com/Daniel-W-Blender-Python/Blender-Motion-Capture-Addon/assets/142774885/5c8463e5-6b90-4d07-bbc0-8e0d4a338234)

Then, to link the rig to the Rokoko armature's motion, click "Link Armatures". This will add bone constraints to the bones on the rig, so that whatever you change to the Rokoko armature in terms of motion, it will be mimicked by the rig.

![image](https://github.com/Daniel-W-Blender-Python/Blender-Motion-Capture-Addon/assets/142774885/4cbeb298-193e-4599-a666-65aafa7fea1c)

If you want to transfer the Rokoko armature's motion to the rig, click the "Retarget Animation" button.



# TroubleShooting

If you are getting an error when adding a rig, try first enabling the "Rigify" addon.

![image](https://github.com/Daniel-W-Blender-Python/Blender-Motion-Capture-Addon/assets/142774885/749dbf6a-9db2-44e8-8503-23d18329d34a)

If you are getting an error stating that there is no module named cv2, or that there is no module named mediapipe, try opening the scripting tab in blender, adding a new python script, and running this code:

import subprocess

import sys

import os

python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')

py_lib = os.path.join(sys.prefix, 'lib', 'site-packages','pip')

subprocess.check_call([sys.executable, "-m", "ensurepip"])

subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

subprocess.check_call([sys.executable, "-m", "pip", "install", "mediapipe"])

subprocess.check_call([sys.executable, "-m", "pip", "install", "opencv-python"])

![image](https://github.com/Daniel-W-Blender-Python/Blender-Motion-Capture-Addon/assets/142774885/2fbd2085-5228-4b7f-824b-3b57346ffeb4)

This will download the OpenCV and Mediapipe libraries, which are required to run this addon.

If your computer is crashing while checking the addon box, try importing and running both scripts (Blender Mocap V (Latest Version) and the code above), then checking the box:

![image](https://github.com/Daniel-W-Blender-Python/Blender-Motion-Capture-Addon/assets/142774885/664018bc-86be-46b1-9c04-b13cece1b2df)

If you are getting an error when clicking "Smooth Animation", make sure that the drivers aren't hidden in the scene.

If you are getting an error when clicking "Save Animation", or the button simply doesn't work, try showing all the layers of the rig. Then try saving the animation.

![image](https://github.com/Daniel-W-Blender-Python/Blender-Motion-Capture-Addon/assets/142774885/641b108a-2a4e-46a5-b95c-22ee053fee17)

If the "Smooth Animation" button still doesn't work, try selecting all of the drivers, and then clicking the button:

![image](https://github.com/Daniel-W-Blender-Python/Blender-Motion-Capture-Addon/assets/142774885/9774681f-dcc7-41b3-b4a1-7871e22a93f6)











