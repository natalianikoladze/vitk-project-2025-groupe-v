# Recalage d'images médicales avec ITK

##  Auteurs
Adrien Landreau
Natalia Nikoladze
Kemil Bina
Simon Campredon

---

## 1. Introduction

Ce projet a pour but de réaliser une segmentation d’images médicales (IRM ou autres modalités) en utilisant la librairie `ITK` en Python. La segmentation aide à identifier et isoler des objets spécifiques au sein d'une image, rendant les processus automatisés comme la reconnaissance d'objets plus efficaces.

---

## 2. Objectifs du projet

- Lire deux images médicales au format `.nrrd`
- Aligner la seconde image sur la première
- Appliquer une transformation de translation pour appliquer la segmentation
- Visualiser les résultats

---

## 3. Technologies utilisées

- Python
- ITK (Insight Toolkit) – pour le traitement et recalage d’image
- Format de données : `.nrrd`, `.nii.gz`

---

## 4. ⚙️ Description du traitement
- Chargement des données
- Définition de la transformation (translation)
- Choix de la métrique et de l'optimiseur
- Choix du recalage
- Application de la transformation
- Segmentation des images

---

## 5. Choix techniques et justification

| Élément         | Choix                           | Justification |
|----------------|----------------------------------|---------------|
| **Transformation** | `TranslationTransform`           | Simple, adaptée aux petits décalages |
| **Métrique**       | `MeanSquaresImageToImageMetricv4` | Bonne précision sur images de même modalité |
| **Optimiseur**     | `RegularStepGradientDescent`      | Efficace, contrôlable avec les paramètres |
| **Interpolation**  | Linéaire                        | Bon compromis entre vitesse et qualité |

---

## 6. ⚠️ Problème rencontré
Lors de nos tests, l'ajout d'un optimizer après une transformation bspline normale, a cause d'une fonction interne. Après plusieurs recherches, nous avons trouvé que le problème venait de l'implémentation. Notre implémentation aurait marcher dans une logique C++, mais dans notre cas, nous étions en python. Pour confirmer ceci nous avons essayer d'autres metrics ou optimizer. Puisque ces implémentations ne fonctionnent pas dans notre cas en Python, nous avons une transform composé d'une translation, puis d'un bspline.

## 7. Limites

- Type de transformation limité : seule une transformation de translation est utilisée, ce qui ne permet pas de corriger des déformations plus complexes.

- Paramètres statiques : les paramètres de l’optimiseur (learning rate, nombre d’itérations) sont fixés manuellement et non adaptés dynamiquement selon les cas.


---

## 8. Instructions d'utilisation

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

## 9. ✅ Résultats
- Alignement visuel réussi : les images recalées montrent un bon alignement des structures anatomiques principales après translation.