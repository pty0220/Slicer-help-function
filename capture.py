import slicer
import ScreenCapture

import vtk
import datetime



# Caputer 3D rendering window with transparent background
def c(path = 0):
    renderWindow = slicer.app.layoutManager().threeDWidget(0).threeDView().renderWindow()
    renderWindow.SetAlphaBitPlanes(1)
    wti = vtk.vtkWindowToImageFilter()
    wti.SetInput(renderWindow)
    wti.SetInputBufferTypeToRGBA()
    writer = vtk.vtkPNGWriter()
    now = datetime.datetime.now()
    if path == 0:
        nowDatetime = now.strftime('%Y-%m-%d-%H-%M-%S')
        writer.SetFileName("D:\\capture"+nowDatetime+".png")
    else:
        writer.SetFileName(path)

    writer.SetInputConnection(wti.GetOutputPort())
    writer.Write()


def d():
    viewNodeID = "vtkMRMLViewNode1"
    cap = ScreenCapture.ScreenCaptureLogic()
    view = cap.viewFromNode(slicer.mrmlScene.GetNodeByID(viewNodeID))
    now = datetime.datetime.now()
    nowDatetime = now.strftime('%Y-%m-%d-%H-%M-%S')
    cap.captureImageFromView(view, "D:\\capture"+nowDatetime+".png")


