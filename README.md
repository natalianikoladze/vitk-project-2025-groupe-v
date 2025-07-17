# Recalage d'images médicales avec ITK

##  Auteurs
Adrien Landreau
Natalia Nikoladze
Kemil Bina
Simon Campredon

---

## 1. Introduction

Ce projet a pour but de réaliser un recalage d’images médicales (IRM ou autres modalités) en utilisant la librairie `ITK` en Python. Le recalage permet d’aligner deux images issues d’une même région anatomique mais prises à des temps ou conditions différentes.

---

## 2. Objectifs du projet

- Lire deux images médicales au format `.nrrd`
- Aligner la seconde image sur la première
- Appliquer une transformation de **translation** pour corriger le décalage
- Visualiser les résultats

---

## 3. Technologies utilisées

- Python
- ITK (Insight Toolkit) – pour le traitement et recalage d’image
- Format de données : `.nrrd`, `.nii.gz`

---

## 4. ⚙️ Description du traitement

### Étape 1 – Chargement des données
```python
file1_path = "Data/case6_gre1.nrrd"
file2_path = "Data/case6_gre2.nrrd"

PixelType = itk.F
fixed_image = itk.imread(file1_path, PixelType)
moving_image = itk.imread(file2_path, PixelType)
```


### Étape 2 – Définition de la transformation (Translation uniquement)
```python
TransformType = itk.TranslationTransform[itk.D, dimension]
initial_transform = TransformType.New()
initial_transform.SetIdentity()
```

### Étape 3 – Choix de la métrique et de l'optimiseur
```python
optimizer = itk.RegularStepGradientDescentOptimizerv4.New()
optimizer.SetLearningRate(4.0)
optimizer.SetMinimumStepLength(0.001)
optimizer.SetNumberOfIterations(100)

metric = itk.MeanSquaresImageToImageMetricv4[FixedImageType, MovingImageType].New()
interpolator = itk.LinearInterpolateImageFunction[FixedImageType, itk.D].New()
metric.SetFixedInterpolator(interpolator)
```

### Étape 4 – Méthode de recalage
```python
registration = itk.ImageRegistrationMethodv4[FixedImageType, MovingImageType].New()
registration.SetFixedImage(fixed_image)
registration.SetMovingImage(moving_image)
registration.SetInitialTransform(initial_transform)
registration.SetMetric(metric)
registration.SetOptimizer(optimizer)

registration.Update()
```

### Étape 5 – Application de la transformation et sauvegarde
```python
resampler = itk.ResampleImageFilter[MovingImageType, FixedImageType].New()
resampler.SetInput(moving_image)
resampler.SetTransform(final_transform)
resampler.SetUseReferenceImage(True)
resampler.SetReferenceImage(fixed_image)
resampler.SetDefaultPixelValue(0)
resampler.Update()

aligned_image = resampler.GetOutput()
```

### Étape 6 - Segmentation des images
```
smooth_fixed = anisotropic_diffusion(fixed_image)
segmentation_fixed = region_growing(smooth_fixed, seed_coords, multiplier=2.3)
segmentation_fixed_8bit = rescale_to_8bit(segmentation_fixed)
save_image(segmentation_fixed_8bit, "segmentation_fixed.nii.gz")

smooth_aligned = anisotropic_diffusion(aligned_image)
segmentation_aligned = region_growing(smooth_aligned, seed_coords, multiplier=2.5)
segmentation_aligned_8bit = rescale_to_8bit(segmentation_aligned)
save_image(segmentation_aligned_8bit, "segmentation_aligned.nii.gz")
```


---

## 6. Choix techniques et justification

| Élément         | Choix                           | Justification |
|----------------|----------------------------------|---------------|
| **Transformation** | `TranslationTransform`           | Simple, adaptée aux petits décalages |
| **Métrique**       | `MeanSquaresImageToImageMetricv4` | Bonne précision sur images de même modalité |
| **Optimiseur**     | `RegularStepGradientDescent`      | Efficace, contrôlable avec les paramètres |
| **Interpolation**  | Linéaire                        | Bon compromis entre vitesse et qualité |

---

## 7. ⚠️ Problème rencontré
Lors de nos tests, l'ajout d'un optimizer après une transformation bspline normale, a cause d'une fonction interne. Après plusieurs recherches, nous avons trouvé que le problème venait de l'implémentation. Notre implémentation aurait marcher dans une logique C++, mais dans notre cas, nous étions en python. Pour confirmer ceci nous avons essayer d'autres metrics ou optimizer. Puisque ces implémentations ne fonctionnent pas dans notre cas en Python, nous avons une transform composé d'une translation, puis d'un bspline.

## 8. Limites

- Type de transformation limité : seule une transformation de translation est utilisée, ce qui ne permet pas de corriger des déformations plus complexes.

- Paramètres statiques : les paramètres de l’optimiseur (learning rate, nombre d’itérations) sont fixés manuellement et non adaptés dynamiquement selon les cas.


---

## 9. Instructions d'utilisation

1. Placer les fichiers `.nrrd` dans un dossier `Data/`
2. Installer les dépendances :
```bash
pip install itk
```
3. Lancer le programme :
```
python main.py
```
4. Outil de visualisation
- Appuyer sur les touches 1, 2, ou 3

---

## 10. ✅ Résultats
- Alignement visuel réussi : les images recalées montrent un bon alignement des structures anatomiques principales après translation.