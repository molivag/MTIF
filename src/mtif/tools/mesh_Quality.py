# trace generated using paraview version 5.11.1
#import paraview
#paraview.compatibility.major = 5
#paraview.compatibility.minor = 11

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'Legacy VTK Reader'
output6femticvtk = LegacyVTKReader(registrationName='output.6.femtic.vtk', FileNames=['/home/marcusfinix/dev/meshTran/computing/output.6.femtic.vtk'])

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# show data in view
output6femticvtkDisplay = Show(output6femticvtk, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
output6femticvtkDisplay.Representation = 'Surface'

# reset view to fit data
renderView1.ResetCamera(False)

# show color bar/color legend
output6femticvtkDisplay.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [0.0, 0.0, 313888.74035208457]
renderView1.CameraParallelScale = 81240.3840463596

# get 2D transfer function for 'NodeSerial'
nodeSerialTF2D = GetTransferFunction2D('NodeSerial')

# get color transfer function/color map for 'NodeSerial'
nodeSerialLUT = GetColorTransferFunction('NodeSerial')
nodeSerialLUT.TransferFunction2D = nodeSerialTF2D
nodeSerialLUT.RGBPoints = [0.0, 0.231373, 0.298039, 0.752941, 14530.0, 0.865003, 0.865003, 0.865003, 29060.0, 0.705882, 0.0156863, 0.14902]
nodeSerialLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'NodeSerial'
nodeSerialPWF = GetOpacityTransferFunction('NodeSerial')
nodeSerialPWF.Points = [0.0, 0.0, 0.5, 0.0, 29060.0, 1.0, 0.5, 0.0]
nodeSerialPWF.ScalarRangeInitialized = 1
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [0.0, 0.0, 313888.74035208457]
renderView1.CameraParallelScale = 81240.3840463596

# create a new 'Clip'
clip1 = Clip(registrationName='Clip1', Input=output6femticvtk)
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [0.0, 0.0, 313888.74035208457]
renderView1.CameraParallelScale = 81240.3840463596
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [0.0, 0.0, 313888.74035208457]
renderView1.CameraParallelScale = 81240.3840463596

# Properties modified on clip1
clip1.Invert = 0
clip1.Crinkleclip = 1

# show data in view
clip1Display = Show(clip1, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
clip1Display.Representation = 'Surface'

# hide data in view
Hide(output6femticvtk, renderView1)

# show color bar/color legend
clip1Display.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [0.0, 0.0, 313888.74035208457]
renderView1.CameraParallelScale = 81240.3840463596
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [0.0, 0.0, 313888.74035208457]
renderView1.CameraParallelScale = 81240.3840463596

renderView1.ResetActiveCameraToPositiveZ()

# reset view to fit data
renderView1.ResetCamera(False)
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [0.0, 0.0, -376666.4884225015]
renderView1.CameraFocalPoint = [0.0, 0.0, 1e-20]
renderView1.CameraParallelScale = 97488.46085563152

renderView1.AdjustRoll(-90.0)
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [0.0, 0.0, -376666.4884225015]
renderView1.CameraFocalPoint = [0.0, 0.0, 1e-20]
renderView1.CameraViewUp = [1.0, 2.220446049250313e-16, 0.0]
renderView1.CameraParallelScale = 97488.46085563152

renderView1.AdjustRoll(-90.0)
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [0.0, 0.0, -376666.4884225015]
renderView1.CameraFocalPoint = [0.0, 0.0, 1e-20]
renderView1.CameraViewUp = [4.440892098500626e-16, -1.0, 0.0]
renderView1.CameraParallelScale = 97488.46085563152
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [0.0, 0.0, -376666.4884225015]
renderView1.CameraFocalPoint = [0.0, 0.0, 1e-20]
renderView1.CameraViewUp = [4.440892098500626e-16, -1.0, 0.0]
renderView1.CameraParallelScale = 97488.46085563152

renderView1.AdjustRoll(90.0)
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [0.0, 0.0, -376666.4884225015]
renderView1.CameraFocalPoint = [0.0, 0.0, 1e-20]
renderView1.CameraViewUp = [1.0, 2.220446049250313e-16, 0.0]
renderView1.CameraParallelScale = 97488.46085563152
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [0.0, 0.0, -376666.4884225015]
renderView1.CameraFocalPoint = [0.0, 0.0, 1e-20]
renderView1.CameraViewUp = [1.0, 2.220446049250313e-16, 0.0]
renderView1.CameraParallelScale = 97488.46085563152
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [0.0, 0.0, -376666.4884225015]
renderView1.CameraFocalPoint = [0.0, 0.0, 1e-20]
renderView1.CameraViewUp = [1.0, 2.220446049250313e-16, 0.0]
renderView1.CameraParallelScale = 97488.46085563152
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [-374701.6439581108, -10027.320484514517, -37091.432427564294]
renderView1.CameraFocalPoint = [-5.877827705043118e-36, -2.3567259970382117e-37, 9.99999999999999e-21]
renderView1.CameraViewUp = [0.09830877487451663, 0.007407550298681625, -0.9951283901995984]
renderView1.CameraParallelScale = 97488.46085563152
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [-374701.6439581108, -10027.320484514517, -37091.432427564294]
renderView1.CameraFocalPoint = [-5.877827705043118e-36, -2.3567259970382117e-37, 9.99999999999999e-21]
renderView1.CameraViewUp = [0.09830877487451663, 0.007407550298681625, -0.9951283901995984]
renderView1.CameraParallelScale = 97488.46085563152
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [-374701.6439581108, -10027.320484514517, -37091.432427564294]
renderView1.CameraFocalPoint = [-5.877827705043118e-36, -2.3567259970382117e-37, 9.99999999999999e-21]
renderView1.CameraViewUp = [0.09830877487451663, 0.007407550298681625, -0.9951283901995984]
renderView1.CameraParallelScale = 97488.46085563152
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [-374701.6439581108, -10027.320484514517, -37091.432427564294]
renderView1.CameraFocalPoint = [-5.877827705043118e-36, -2.3567259970382117e-37, 9.99999999999999e-21]
renderView1.CameraViewUp = [0.09830877487451663, 0.007407550298681625, -0.9951283901995984]
renderView1.CameraParallelScale = 97488.46085563152

# set scalar coloring
ColorBy(clip1Display, ('CELLS', 'Resistivity[Ohm-m]'))

# Hide the scalar bar for this color map if no visible data is colored by it.
HideScalarBarIfNotNeeded(nodeSerialLUT, renderView1)

# rescale color and/or opacity maps used to include current data range
clip1Display.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
clip1Display.SetScalarBarVisibility(renderView1, True)

# get 2D transfer function for 'ResistivityOhmm'
resistivityOhmmTF2D = GetTransferFunction2D('ResistivityOhmm')

# get color transfer function/color map for 'ResistivityOhmm'
resistivityOhmmLUT = GetColorTransferFunction('ResistivityOhmm')
resistivityOhmmLUT.TransferFunction2D = resistivityOhmmTF2D
resistivityOhmmLUT.RGBPoints = [100.0, 0.231373, 0.298039, 0.752941, 500000050.0, 0.865003, 0.865003, 0.865003, 1000000000.0, 0.705882, 0.0156863, 0.14902]
resistivityOhmmLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'ResistivityOhmm'
resistivityOhmmPWF = GetOpacityTransferFunction('ResistivityOhmm')
resistivityOhmmPWF.Points = [100.0, 0.0, 0.5, 0.0, 1000000000.0, 1.0, 0.5, 0.0]
resistivityOhmmPWF.ScalarRangeInitialized = 1
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [-374701.6439581108, -10027.320484514517, -37091.432427564294]
renderView1.CameraFocalPoint = [-5.877827705043118e-36, -2.3567259970382117e-37, 9.99999999999999e-21]
renderView1.CameraViewUp = [0.09830877487451663, 0.007407550298681625, -0.9951283901995984]
renderView1.CameraParallelScale = 97488.46085563152

# change representation type
clip1Display.SetRepresentationType('Surface With Edges')
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [-374701.6439581108, -10027.320484514517, -37091.432427564294]
renderView1.CameraFocalPoint = [-5.877827705043118e-36, -2.3567259970382117e-37, 9.99999999999999e-21]
renderView1.CameraViewUp = [0.09830877487451663, 0.007407550298681625, -0.9951283901995984]
renderView1.CameraParallelScale = 97488.46085563152
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [-374701.6439581108, -10027.320484514517, -37091.432427564294]
renderView1.CameraFocalPoint = [-5.877827705043118e-36, -2.3567259970382117e-37, 9.99999999999999e-21]
renderView1.CameraViewUp = [0.09830877487451663, 0.007407550298681625, -0.9951283901995984]
renderView1.CameraParallelScale = 97488.46085563152
# Adjust camera

# current camera placement for renderView1
renderView1.CameraPosition = [-374701.6439581108, -10027.320484514517, -37091.432427564294]
renderView1.CameraFocalPoint = [-5.877827705043118e-36, -2.3567259970382117e-37, 9.99999999999999e-21]
renderView1.CameraViewUp = [0.09830877487451663, 0.007407550298681625, -0.9951283901995984]
renderView1.CameraParallelScale = 97488.46085563152

#================================================================
# addendum: following script captures some of the application
# state to faithfully reproduce the visualization during playback
#================================================================

# get layout
layout1 = GetLayout()

#--------------------------------
# saving layout sizes for layouts

# layout/tab size in pixels
layout1.SetSize(2075, 1135)

#-----------------------------------
# saving camera placements for views

# current camera placement for renderView1
renderView1.CameraPosition = [-374701.6439581108, -10027.320484514517, -37091.432427564294]
renderView1.CameraFocalPoint = [-5.877827705043118e-36, -2.3567259970382117e-37, 9.99999999999999e-21]
renderView1.CameraViewUp = [0.09830877487451663, 0.007407550298681625, -0.9951283901995984]
renderView1.CameraParallelScale = 97488.46085563152

#--------------------------------------------
# uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).