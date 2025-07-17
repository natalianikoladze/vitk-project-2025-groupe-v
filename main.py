import itk
import vtk

# =======================
#        CONSTANTES
# =======================
file1_path = "Data/case6_gre1.nrrd"
file2_path = "Data/case6_gre2.nrrd"
seed_coords = (84, 72, 47)
output_dir = "."


# =======================
#       UTILITAIRES
# =======================
def save_image(image, filename):
    itk.imwrite(image, f"{output_dir}/{filename}")


def anisotropic_diffusion(image, iterations=5, timestep=0.05, conductance=3.0):
    gradient = itk.GradientAnisotropicDiffusionImageFilter.New(image)
    gradient.SetNumberOfIterations(iterations)
    gradient.SetTimeStep(timestep)
    gradient.SetConductanceParameter(conductance)
    gradient.Update()
    return gradient.GetOutput()


def region_growing(image, seed_coords, multiplier=2.5, replace_value=1):
    confidence_filter = itk.ConfidenceConnectedImageFilter.New(image)
    confidence_filter.SetInitialNeighborhoodRadius(2)
    confidence_filter.SetMultiplier(multiplier)
    confidence_filter.SetNumberOfIterations(2)
    confidence_filter.SetReplaceValue(replace_value)

    seed = itk.Index[3]()
    seed[0], seed[1], seed[2] = seed_coords
    confidence_filter.AddSeed(seed)

    confidence_filter.Update()
    return confidence_filter.GetOutput()


def rescale_to_8bit(image):
    ImageTypeOut = itk.Image[itk.UC, 3]
    final = itk.RescaleIntensityImageFilter[type(image), ImageTypeOut].New()
    final.SetInput(image)
    final.SetOutputMinimum(0)
    final.SetOutputMaximum(255)
    final.Update()
    return final.GetOutput()


def create_vtk_actor(itk_image, color=(1, 1, 1), opacity=0.5):
    vtk_image = itk.vtk_image_from_image(itk_image)
    reader = vtk.vtkMarchingCubes()
    reader.SetInputData(vtk_image)
    reader.SetValue(0, 0.5)
    reader.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetOpacity(opacity)

    return actor


# =======================
#      CHARGEMENT
# =======================
PixelType = itk.F
fixed_image = itk.imread(file1_path, PixelType)
moving_image = itk.imread(file2_path, PixelType)

save_image(fixed_image, "fixed_image.nii.gz")
save_image(moving_image, "moving_image.nii.gz")

dimension = fixed_image.GetImageDimension()

# =======================
#      RECALAGE
# =======================
TransformType = itk.TranslationTransform[itk.D, dimension]
initial_transform = TransformType.New()
initial_transform.SetIdentity()

optimizer = itk.RegularStepGradientDescentOptimizerv4.New()
optimizer.SetLearningRate(4.0)
optimizer.SetMinimumStepLength(0.001)
optimizer.SetNumberOfIterations(100)

metric = itk.MeanSquaresImageToImageMetricv4[
    type(fixed_image), type(moving_image)
].New()
interpolator = itk.LinearInterpolateImageFunction[type(fixed_image), itk.D].New()
metric.SetFixedInterpolator(interpolator)

registration = itk.ImageRegistrationMethodv4[
    type(fixed_image), type(moving_image)
].New()
registration.SetFixedImage(fixed_image)
registration.SetMovingImage(moving_image)
registration.SetInitialTransform(initial_transform)
registration.SetMetric(metric)
registration.SetOptimizer(optimizer)

registration.Update()
final_translation_transform = registration.GetTransform()

# Recalage BSpline
transform_bspline = itk.BSplineTransform[itk.D, dimension, 3].New()
spacing = fixed_image.GetSpacing()
origin = fixed_image.GetOrigin()
direction = fixed_image.GetDirection()
size = fixed_image.GetLargestPossibleRegion().GetSize()
physical_dimensions = [spacing[i] * size[i] for i in range(dimension)]
mesh_size = [8] * dimension

transform_bspline.SetTransformDomainOrigin(origin)
transform_bspline.SetTransformDomainPhysicalDimensions(physical_dimensions)
transform_bspline.SetTransformDomainMeshSize(mesh_size)
transform_bspline.SetTransformDomainDirection(direction)

parameters = transform_bspline.GetParameters()
for i in range(parameters.size()):
    parameters[i] = 0.0
transform_bspline.SetParameters(parameters)

# Reacalage Composite
composite_transform = itk.CompositeTransform[itk.D, dimension].New()
composite_transform.AddTransform(final_translation_transform)
composite_transform.AddTransform(transform_bspline)

# Resampler
resampler = itk.ResampleImageFilter[type(moving_image), type(fixed_image)].New()
resampler.SetInput(moving_image)
resampler.SetTransform(composite_transform)
resampler.SetUseReferenceImage(True)
resampler.SetReferenceImage(fixed_image)
resampler.SetDefaultPixelValue(0)
resampler.Update()
aligned_image = resampler.GetOutput()

save_image(aligned_image, "aligned_image.nii.gz")

# =======================
#   SEGMENTATION
# =======================
smooth_fixed = anisotropic_diffusion(fixed_image)
segmentation_fixed = region_growing(smooth_fixed, seed_coords, multiplier=2.3)
segmentation_fixed_8bit = rescale_to_8bit(segmentation_fixed)
save_image(segmentation_fixed_8bit, "segmentation_fixed.nii.gz")

smooth_aligned = anisotropic_diffusion(aligned_image)
segmentation_aligned = region_growing(smooth_aligned, seed_coords, multiplier=2.5)
segmentation_aligned_8bit = rescale_to_8bit(segmentation_aligned)
save_image(segmentation_aligned_8bit, "segmentation_aligned.nii.gz")

# smooth_moving = anisotropic_diffusion(moving_image)
# segmentation_moving = region_growing(smooth_moving, seed_coords, multiplier=2.5)
# segmentation_moving_8bit = rescale_to_8bit(segmentation_moving)
# save_image(segmentation_moving_8bit, "moving.nii.gz")

# =======================
#     VISUALISATION
# =======================
print_fixed = True
print_aligned = False
print_brain = False


def callback(obj, event):
    global print_fixed, print_aligned, print_brain
    key = obj.GetKeySym()
    if key == "1":
        print_fixed = not print_fixed
    elif key == "2":
        print_aligned = not print_aligned
    # elif key == "3":
    # print_brain = not print_brain
    show()


# Lecture des résultats
seg_image_fixed = itk.imread("segmentation_fixed.nii.gz")
seg_image_aligned = itk.imread("segmentation_aligned.nii.gz")
# mov_image = itk.imread("moving.nii.gz")

# Création des acteurs
actors = [
    create_vtk_actor(seg_image_fixed, color=(1, 0, 0)),  # Rouge
    create_vtk_actor(seg_image_aligned, color=(0, 1, 0)),  # Vert
    # create_vtk_actor(mov_image, color=(0, 0, 1)),
]

# Renderer / Fenêtre
renderer = vtk.vtkRenderer()
window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)
interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
interactor.AddObserver("KeyPressEvent", callback)


def show():
    renderer.RemoveAllViewProps()
    if print_fixed:
        renderer.AddActor(actors[0])
    if print_aligned:
        renderer.AddActor(actors[1])
    # if print_brain:
    #  renderer.AddActor(actors[2])
    window.Render()


show()
interactor.Initialize()
interactor.Start()
