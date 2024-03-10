# TextureExtractor
Blender Add-on which bakes the texture for a selected mesh and outputs it to a file. Useful for exporting only the parts of the mesh that relate to selected vertices. 
This can assist with getting the related textures output 

-------------------------------------------------------------------------------------------
A youtube video will be uploaded to the ClassOutside channel with a step by step walkthrough.

Description:
1. Install the add-on
2. Save the Blender file
  - An output folder named "Texture Output" will be made in the same folder as your .Blend file.
  - Without saving the Blender file first, the texture output may not appear in the right place.
3. Select the mesh you want the image texture for.
4. Copy the mesh
5. In Object mode, select the copied mesh and right click
6. Select the option labelled "Start Texture Bake Process"
7. Afterwards an image file with the same name as the mesh should be available in the "Texture Output" folder.

(Optional) Steps to use the exported image texture on the original object
1. Select the original mesh
2. Open the Shader Editor
3. Navigate to the object's material with the image texture you want to replace.
4. Change the image texture node to use the exported image texture.
5. With the mesh selected, go into Edit mode.
6. Select all vertices.
7. Click the UV option, and select "Unwrap" and then "Smart UV Project"
8. The exported image should now be aligned with the original mesh. 
