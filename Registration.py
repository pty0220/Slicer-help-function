import slicer
import Elastix
import SimpleITK as sitk
import sitkUtils


# Elastix registration function
def registration_elastix(fixedVolumeNode, movingVolumeNode):

    """Rigid registration Elastix"""

    # MR is fixed volume and CT is moving volume
    elastixLogic = Elastix.ElastixLogic()
    parameterFilenames = elastixLogic.getRegistrationPresets()[1][Elastix.RegistrationPresets_ParameterFilenames]

    outputVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
    outputTransformNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTransformNode")

    regi = elastixLogic.registerVolumes(fixedVolumeNode, movingVolumeNode, parameterFilenames=parameterFilenames,
                                        outputVolumeNode=outputVolumeNode, outputTransformNode=outputTransformNode)

    return outputVolumeNode, outputTransformNode


# Run function
def run(CT_path ="", MR_path =""):

    # Read medical image using sitk
    ctItk = readSavedFile(CT_path)
    mrItk = readSavedFile(MR_path)

    # push itk image to slicer
    ctNode = sitkUtils.PushVolumeToSlicer(ctItk)
    ctNode.SetName("CT")

    mrNode = sitkUtils.PushVolumeToSlicer(mrItk)
    mrNode.SetName("MR")

    # Registration
    regiCtNode, _ = registration_elastix(mrNode, ctNode)
    regiCtNode.SetName('CT_registration')


# Read medical image
def readSavedFile(filePath):

    # read various type of medical image
    if filePath[-2:] == "gz":
        reader = sitk.ImageFileReader()
        reader.SetImageIO("NiftiImageIO")
        reader.SetFileName(filePath)

    elif filePath[-3:] == "nii":
        reader = sitk.ImageFileReader()
        reader.SetImageIO("NiftiImageIO")
        reader.SetFileName(filePath)

    elif filePath[-4:] == "nrrd":
        reader = sitk.ImageFileReader()
        reader.SetImageIO("NrrdImageIO")
        reader.SetFileName(filePath)

    # For DICOM folder
    else:
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(filePath)
        reader.SetFileNames(dicom_names)

    # medical image Simple ITK from
    image = reader.Execute()

    return image