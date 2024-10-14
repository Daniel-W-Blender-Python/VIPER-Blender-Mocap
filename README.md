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











