import sys, os
import qt, ctk, vtk
import time, datetime
import SimpleITK as sitk
import slicer, logging, sitkUtils
import numpy as np

current_path = os.path.dirname(__file__)
sys.path.append(current_path+'/help_function')

from slicer.ScriptedLoadableModule import *


l2n = lambda l: np.array(l)
n2l = lambda n: list(n)


# Rendering on and off function depending on Node
def dispOnOff(node, OnOff):
    try:
        volRenLogic = slicer.modules.volumerendering.logic()
        DisplayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(node)
        DisplayNode.SetVisibility3D(OnOff)

    except:
        modelDisplayNode = node.GetDisplayNode()
        modelDisplayNode.SetVisibility3D(OnOff)