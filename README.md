# Blender-Motion-Capture-Addon
A Blender Addon that uses Mediapipe in Blender to capture a person's movements, and apply them to a character in real time.

The initial code was taken from the "BlendyPose" python script by ZonkSoft, and adapted to apply the motion onto a character in Blender. Mediapipe is a pose-estimation library authored by Google, that estimates the pose of a person in an image (using open-cv in Python), and predicts the 3d coordinates of each landmark. In Blender, the addon applies the location of each landmark onto plain axes in the 3d space, and adds bone constraints to some of the bones in the Blender Rigify Addon (only with the rig, not the armature), so that the bone follows the axes in the space.

The drivers (plain axes) are the objects that move the bones, meaning that the keyframes are not actually applied to the rig. This is important to know when using this addon for more advanced scenes in Blender. In order to move the rig around after the drivers are connected (after "Transfer Animation" is clicked), the "Select System" button must be pressed, so that the drivers move with the rig, and the motion is properly conserved. However, if you are going to re-capture the motion after moving the rig to a different location/rotation, this button does not need to be pressed.

The motion capture in the addon will not run if there is no armature chosen in the "Select an Armature" dropdown. If it is not chosen, Blender will present an error, and you must then choose an armature before proceeding.

Another thing to note is to not change the name/designation of the drivers, as the addon relies on that information.

If an error appears, stating that mediapipe isn't defined, try installing the addon on elevated privelages for Blender.

And for the final part of this addon, the smooth animation button smooths the animation to make it look more realistic. Above this button is a section where you can decide the degree to how much you want the animation smoothed. For example, setting this value to "10" would smooth the animation the most.

In future versions, this addon will hopefully run more on deep learning algorithms, which will allow things like multi-person motion capture, as well as more accurate motion capture in general.
