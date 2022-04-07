# %%

import glob
import os
import time
import numpy as np

import cv2
from scipy import ndimage

import slicer
import Elastix
import JupyterNotebooksLib as slicernb

import sitkUtils as su
import SimpleITK as sitk

# %%

root_dir = 'E:\\Test_data_set'
mni_path = 'C:\\Users\\User\\AppData\\Local\\NA-MIC\\Slicer 4.11.20200930\\mni_icbm152_t1_tal_nlin_asym_09a.nii'

# %%

sub_path_list = sorted(glob.glob(root_dir))

# %%

sub_path_list


# %%

def load_nii(path):
    """Load dicom files to sitk image"""
    reader = sitk.ImageFileReader()
    reader.SetImageIO("NiftiImageIO")
    reader.SetFileName(path)
    image = reader.Execute()

    return image


# %%

def registration_elastix(fixedVolumeNode, movingVolumeNode):
    """Ridgid registration Elastix"""

    # Set Parmeter
    elastixLogic = Elastix.ElastixLogic()
    parameterFilenames = elastixLogic.getRegistrationPresets()[0][Elastix.RegistrationPresets_ParameterFilenames]

    outputVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
    outputTransformNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")

    regi = elastixLogic.registerVolumes(fixedVolumeNode, movingVolumeNode, parameterFilenames=parameterFilenames,
                                        outputVolumeNode=outputVolumeNode, outputTransformNode=outputTransformNode)
    return outputVolumeNode, outputTransformNode


#     if (slicer.util.getNode("register_tmp") == None):
#         outputVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode").SetName("register_tmp")
#     else:5 -
#          outputVolumeNode = slicer.util.getNode("register_tmp")

# Execute


# %%

def write_nii(image, path):
    """Write medical image to nii"""
    sitk.WriteImage(image, path)


# %%

def rescaleIntentsity(image, min_intensity, max_intensity):
    """Rescale Image intensity range of [min , max]"""
    return sitk.RescaleIntensity(image, min_intensity, max_intensity)


# %%

def TransformMarkups(transformNode):
    #     originalFidNode=slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode")

    markupsNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode')
    #     markupsNode.AddControlPoint(vtk.vtkVector3d(0, -1, -1)) #AC
    #     markupsNode.AddControlPoint(vtk.vtkVector3d(0, -23, 0 )) #PC
    markupsNode.AddControlPoint(vtk.vtkVector3d(8, -73.0, 19.0))  # V1
    markupsNode.AddControlPoint(vtk.vtkVector3d(37, -13.0, 51.0))  # M1
    #  markupsNode.AddControlPoint(vtk.vtkVector3d(42, -20.0, 48.0 )) #S1
    markupsNode.AddControlPoint(vtk.vtkVector3d(5.0, 14.0, 47))  # Dosal_ACC +  up5
    markupsNode.AddControlPoint(vtk.vtkVector3d(12, -15, 18.0))  # Thalamus
    #     markupsNode.AddControlPoint(vtk.vtkVect|or3d(5.0, 14.0, 57.0))  #Dorsal_ACC +  up15
    #     markupsNode.AddControlPoint(vtk.vtkVector3d(5.0, -10.0, 51.0)) #Caudal_ACC
    #     markupsNode.AddControlPoint(vtk.vtkVector3d(5.0, -10.0, 56.0)) #Caudal_ACC + up5
    #     markupsNode.AddControlPoint(vtk.vtkVector3d(5.0, -10.0, 61.0)) #Caudal_ACC + up15

    #     markupsNode.AddControlPoint(vtk.vtkVector3d(8, -73.0 - 5, 19.0)) #V1 _5
    #     markupsNode.AddControlPoint(vtk.vtkVector3d(37, -13.0, 51.0 + 5)) #M1 _ 5
    #     markupsNode.AddControlPoint(vtk.vtkVector3d(42, -20.0, 48.0 + 5)) #S1 _ 5

    markupsNode.SetAndObserveTransformNodeID(transformNode.GetID())
    #    slicer.modules.transforms.logic().CreateDisplacementVolumeFromTransform(transformNode, markupsNode, False)
    narray = slicer.util.arrayFromMarkupsControlPoints(markupsNode, world=True)

    print(narray)
    slicer.mrmlScene.RemoveNode(markupsNode)
    return narray


# %%

scene = slicer.mrmlScene
sub_path_list = sorted(glob.glob(os.path.join(root_dir, 'S*')))
print(len(sub_path_list))
i = 0

# %%

sub_path_list

# %%

scene = slicer.mrmlScene
sub_path_list = sorted(glob.glob(os.path.join(root_dir, 'S*')))
print(len(sub_path_list))
i = 0

mni_image = load_nii(mni_path)
MNI_node = su.PushVolumeToSlicer(mni_image)

for sub_path in sub_path_list:
    try:
        sub_name = sub_path.split("\\")[-1].split("_")[0]

        print(i)
        i += 1

        T1_path = glob.glob(os.path.join(sub_path, '*crop_T1.nii'))[0]
        T1_image = load_nii(T1_path)
        print('load dicom', T1_path)

        # sitk image to VolumeNode
        T1_node = su.PushVolumeToSlicer(T1_image)
        print('push image to volumenode')

        MNI_registeredNode, MNI_transformNode = registration_elastix(T1_node, MNI_node)
        print('mni-registration')

        target_np = TransformMarkups(MNI_transformNode)

        sub_name = sub_path.split("\\")[-1].split("_")[0]
        save_path = os.path.join(sub_path)

        if not os.path.exists(save_path):
            os.makedirs(save_path)
            print(save_path)

        V1 = str(
            '{:.3f}'.format(target_np[0][0]) + ' {:.3f}'.format(target_np[0][1]) + ' {:.3f}'.format(target_np[0][2]))
        f = open(os.path.join(save_path, 'target_V1_MNI.txt'), 'w')
        f.write(V1)
        f.close()

        M1 = str(
            '{:.3f}'.format(target_np[1][0]) + ' {:.3f}'.format(target_np[1][1]) + ' {:.3f}'.format(target_np[1][2]))
        f = open(os.path.join(save_path, 'target_M1_MNI.txt'), 'w')
        f.write(M1)

        Dorsal_ACC = str(
            '{:.3f}'.format(target_np[2][0]) + ' {:.3f}'.format(target_np[2][1]) + ' {:.3f}'.format(target_np[2][2]))
        f = open(os.path.join(save_path, 'target_DorsalACCUp5.txt'), 'w')
        f.write(Dorsal_ACC)
        f.close()

        Thalamus = str(
            '{:.3f}'.format(target_np[3][0]) + ' {:.3f}'.format(target_np[3][1]) + ' {:.3f}'.format(target_np[3][2]))
        f = open(os.path.join(save_path, 'target_Thalamus.txt'), 'w')
        f.write(Thalamus)
        f.close()

        print('save target mni to native space')

        # clear

        slicer.mrmlScene.RemoveNode(T1_node)
        slicer.mrmlScene.RemoveNode(MNI_transformNode)
        slicer.mrmlScene.RemoveNode(MNI_registeredNode)


    except Exception as e:
        print(e)
        print(sub_path, 'wrong')
        continue

# %%

scene = slicer.mrmlScene
sub_path_list = sorted(glob.glob(os.path.join(root_dir, 'S*')))
print(len(sub_path_list))
i = 0

mni_image = load_nii(mni_path)
MNI_node = su.PushVolumeToSlicer(mni_image)

for sub_path in sub_path_list:
    try:
        sub_name = sub_path.split("\\")[-1].split("_")[0]

        print(i)
        i += 1

        T1_path = glob.glob(os.path.join(sub_path, '*crop_T1.nii'))[0]
        T1_image = load_nii(T1_path)
        print('load dicom', T1_path)

        # sitk image to VolumeNode
        T1_node = su.PushVolumeToSlicer(T1_image)
        print('push image to volumenode')

        MNI_registeredNode, MNI_transformNode = registration_elastix(T1_node, MNI_node)
        print('mni-registration')

        target_np = TransformMarkups(MNI_transformNode)

        sub_name = sub_path.split("\\")[-1].split("_")[0]
        save_path = os.path.join(sub_path)

        if not os.path.exists(save_path):
            os.makedirs(save_path)
            print(save_path)

        V1 = str(
            '{:.3f}'.format(target_np[0][0]) + ' {:.3f}'.format(target_np[0][1]) + ' {:.3f}'.format(target_np[0][2]))
        f = open(os.path.join(save_path, 'target_V1_MNI.txt'), 'w')
        f.write(V1)
        f.close()

        M1 = str(
            '{:.3f}'.format(target_np[1][0]) + ' {:.3f}'.format(target_np[1][1]) + ' {:.3f}'.format(target_np[1][2]))
        f = open(os.path.join(save_path, 'target_M1_MNI.txt'), 'w')
        f.write(M1)

        Dorsal_ACC = str(
            '{:.3f}'.format(target_np[2][0]) + ' {:.3f}'.format(target_np[2][1]) + ' {:.3f}'.format(target_np[2][2]))
        f = open(os.path.join(save_path, 'target_DorsalACCUp5.txt'), 'w')
        f.write(Dorsal_ACC)
        f.close()

        print('save target mni to native space')

        # clear

        slicer.mrmlScene.RemoveNode(T1_node)
        slicer.mrmlScene.RemoveNode(MNI_transformNode)
        slicer.mrmlScene.RemoveNode(MNI_registeredNode)


    except Exception as e:
        print(e)
        print(sub_path, 'wrong')
        continue

