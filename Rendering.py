import numpy as np
import slicer
import qt
import vtk
import SimpleITK as sitk

l2n = lambda l: np.array(l)
n2l = lambda n: list(n)


def showVolumeRenderingCT(volumeNode):
    volRenLogic = slicer.modules.volumerendering.logic()
    displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
    displayNode.SetVisibility(True)
    displayNode.GetVolumePropertyNode().Copy(volRenLogic.GetPresetByName('CT-Chest-Contrast-Enhanced'))

def showVolumeRenderingColorMap(volumeNode):
    print("this")

    volRenLogic = slicer.modules.volumerendering.logic()
    displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
    propertyNode = displayNode.GetVolumePropertyNode()
    VolumeProperty = propertyNode.GetVolumeProperty()

    VolumeProperty.SetAmbient(0.95)
    VolumeProperty.SetDiffuse(0.15)
    VolumeProperty.SetSpecular(0.0)
    VolumeProperty.SetSpecularPower(1.0)

    array = slicer.util.arrayFromVolume(volumeNode)
    array_max = np.max(array)

    opacityTransfer = vtk.vtkPiecewiseFunction()
    opacityTransfer.AddPoint(0,0)
    opacityTransfer.AddPoint(array_max*0.15, 0)
    opacityTransfer.AddPoint(array_max*0.3,0.08)
    opacityTransfer.AddPoint(array_max*0.5,0.08)
    opacityTransfer.AddPoint(array_max*0.75,0.2)
    opacityTransfer.AddPoint(array_max*0.85,0.5)
    opacityTransfer.AddPoint(array_max*0.99,1)

    ctf = vtk.vtkColorTransferFunction()
    ctf.AddRGBPoint(array_max*0.25, 0.1,0.1,1.0)
    ctf.AddRGBPoint(array_max*0.5, 0.2,1.0,0.2)
    ctf.AddRGBPoint(array_max*0.75, 1.0,0.5,0.0)
    ctf.AddRGBPoint(array_max*0.9, 1.0,0.0,0.0)

    propertyNode.SetColor(ctf)
    propertyNode.SetScalarOpacity(opacityTransfer)
    slicer.mrmlScene.AddNode(propertyNode)
    displayNode.UnRegister(volRenLogic)


