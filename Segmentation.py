import os
import glob
import sys
import slicer
import sitkUtils

from niiCook2 import niiCook

root_dir = "E:\\Train_data_set"
sub_path_list = sorted(glob.glob(os.path.join(root_dir, 'S*')))

for sub_path in sub_path_list:

    sub_name = sub_path.split("\\")[-1].split("_")[0]
    if sub_name =="S08" or sub_name =="S14":
        T1_path = glob.glob(os.path.join(sub_path, "*crop_CT.nii"))[0]

        # Compute
        skullcook = niiCook()
        skullcook.readSavedFile(T1_path)
        masterVolumeNode = sitkUtils.PushVolumeToSlicer(skullcook.itkImage, None)
        masterVolumeNode.SetName(sub_name)

        # masterVolumeNode = slicer.util.getNode("S"+str(i)+"_rigid_CT")
        # slicer.util.saveNode(masterVolumeNode, path +'\\CT'+str(i)+'.nii')

        # Create segmentation
        segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
        segmentationNode.SetName('Segmentation_'+sub_name)
        #segmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
        #segmentationNode = slicer.util.getNode('Segmentation_1')
        segmentationNode.CreateDefaultDisplayNodes() # only needed for display
        segmentationNode.SetReferenceImageGeometryParameterFromVolumeNode(masterVolumeNode)

        # Create temporary segment editor to get access to effects
        segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
        segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
        segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")

        # Do masking
        addedSegmentID = segmentationNode.GetSegmentation().AddEmptySegment("brain")
        segmentEditorNode.SetMaskSegmentID(addedSegmentID)
        segmentEditorNode.SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteAllSegments)
        segmentEditorNode.SetMaskMode(slicer.vtkMRMLSegmentEditorNode.PaintAllowedInsideSingleSegment)

        segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
        segmentEditorWidget.setSegmentationNode(segmentationNode)
        segmentEditorWidget.setMasterVolumeNode(masterVolumeNode)
        segmentationDisplayNode=segmentationNode.GetDisplayNode()
        segmentation=segmentationNode.GetSegmentation()

        slicer.app.processEvents()
        segmentEditorWidget.setActiveEffectByName("Threshold")
        effect = segmentEditorWidget.activeEffect()
        effect.setParameter("MinimumThreshold", 250)
        effect.setParameter("MaximumThreshold", 3000)
        effect.self().onApply()

        slicer.app.processEvents()
        segmentEditorWidget.setActiveEffectByName("Islands")
        effect = segmentEditorWidget.activeEffect()
        effect.setParameter("Operation", "KEEP_LARGEST_ISLAND")
        effect.self().onApply()

        slicer.app.processEvents()
        segmentEditorWidget.setActiveEffectByName("Wrap Solidify")
        effect = segmentEditorWidget.activeEffect()
        effect.setParameter("region", "largestCavity")
        effect.setParameter("carveHolesInOuterSurface", True)
        effect.setParameter("carveHolesInOuterSurfaceDiameter", 80)
        effect.setParameter("outputType", "segment")
        #effect.setParameter("remeshOversampling", 0.3)
        effect.self().onApply()

        seg = slicer.util.getNode('Segmentation_'+sub_name)
        lmVN = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode')
        lmVN.SetName('brain')
        slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(seg, lmVN)
        slicer.util.saveNode(lmVN, sub_path +'\\'+sub_name+'_brain.nii')


# # Do masking
# addedSegmentID = segmentationNode.GetSegmentation().AddEmptySegment("skull")
# segmentEditorNode.SetMaskSegmentID(addedSegmentID)
# segmentEditorNode.SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteAllSegments)
# segmentEditorNode.SetMaskMode(slicer.vtkMRMLSegmentEditorNode.PaintAllowedInsideSingleSegment)
#
# segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
# segmentEditorWidget.setSegmentationNode(segmentationNode)
# segmentEditorWidget.setMasterVolumeNode(masterVolumeNode)
# segmentationDisplayNode=segmentationNode.GetDisplayNode()
# segmentation=segmentationNode.GetSegmentation()
#
# slicer.app.processEvents()
# segmentEditorWidget.setActiveEffectByName("Threshold")
# effect = segmentEditorWidget.activeEffect()
# effect.setParameter("MinimumThreshold", 250)
# effect.setParameter("MaximumThreshold", 3000)
# effect.self().onApply()
#
#


# # Create segments by thresholding
# segmentsFromHounsfieldUnits = [
#     ["Emphysema right", -1000, -900,0.0,0.0,0.0],
#     ["Ventilated right", -900, -600,0,0.5,1.0],
#     ["Infiltration right", -600, -50,1.0,0.5,0],
#     ["Collapsed right", -50, 3000,1.0,0,1.0] ]
# for segmentName, thresholdMin, thresholdMax, r, g, b in segmentsFromHounsfieldUnits:
#     # Create segment
#     logging.info('Creating segment.')
#     addedSegmentID = segmentationNode.GetSegmentation().AddEmptySegment(segmentName)
#     segmentEditorNode.SetSelectedSegmentID(addedSegmentID)
#     # Set color
#     logging.info('Setting segment color.')
#     segmentId = segmentation.GetSegmentIdBySegmentName(segmentName)
#     segmentationDisplayNode.SetSegmentOpacity3D(segmentId,0.2)
#     segmentation.GetSegment(segmentId).SetColor(r,g,b)  # color should be set in segmentation node
#     # Fill by thresholding
#     logging.info('Thresholding.')
#     segmentEditorWidget.setActiveEffectByName("Threshold")
#     effect = segmentEditorWidget.activeEffect()
#     effect.setParameter("MinimumThreshold",str(thresholdMin))
#     effect.setParameter("MaximumThreshold",str(thresholdMax))
#     effect.self().onApply()
#
#
#
# # Change overall segmentation display properties
# # segmentationDisplayNode.SetOpacity3D(0.5)
#
#
# # Delete temporary segment editor
# segmentEditorWidget = None
# slicer.mrmlScene.RemoveNode(segmentEditorNode)
#
# logging.info('Creating statistics.')
# # Compute segment volumes
# resultsTableNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTableNode')
# import SegmentStatistics
# segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
# segStatLogic.getParameterNode().SetParameter("Segmentation", segmentationNode.GetID())
# segStatLogic.getParameterNode().SetParameter("ScalarVolume", masterVolumeNode.GetID())
# segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.enabled","True")
# segStatLogic.getParameterNode().SetParameter("ScalarVolumeSegmentStatisticsPlugin.voxel_count.enabled","False")
# segStatLogic.getParameterNode().SetParameter("ScalarVolumeSegmentStatisticsPlugin.volume_mm3.enabled","False")
# segStatLogic.computeStatistics()
# segStatLogic.exportToTable(resultsTableNode)
# segStatLogic.showTable(resultsTableNode)
#
# # Export segmentation to a labelmap
# #labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode')
# #slicer.modules.segmentations.logic().ExportVisibleSegmentsToLabelmapNode(segmentationNode, labelmapVolumeNode, masterVolumeNode)
# #slicer.util.saveNode(labelmapVolumeNode, "c:/tmp/BodyComposition-label.nrrd")
# stopTime = time.time()
# logging.info('Processing completed in {0:.2f} seconds'.format(stopTime-startTime))