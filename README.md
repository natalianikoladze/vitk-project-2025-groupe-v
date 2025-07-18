# Recalage d'images médicales avec ITK

##  Auteurs
Adrien Landreau
Natalia Nikoladze
Kemil Bina
Simon Campredon

---

## 1. Introduction

Ce projet a pour but de réaliser une segmentation d’images médicales (IRM ou autres\
modalités) en utilisant la librairie `ITK` en Python, et de visualiser le rendu en\
utilisant la librairie `VTK` en Python.
La segmentation aide à identifier et isoler des objets spécifiques au sein d'une\
image, rendant les processus automatisés comme la reconnaissance d'objets plus efficaces.

---

## 2. Objectifs du projet

- Lire deux images médicales au format `.nrrd`
- Aligner la seconde image sur la première
- Appliquer une transformation composite de **translation** et **b-spline** pour corriger le décalage
- Appliquer une segmentation afin d'isoler la tumeur
- Visualiser les résultats

---

## 3. Technologies utilisées

- Python
- ITK (Insight Toolkit)
- VTK (Visualization Toolkit)
- Format de données : `.nrrd`, `.nii.gz`

---

## 4. Description du traitement

- Chargement des données
Récupération des .nrrd dans le dossier Data.
\
- Définition de la transformation (Translation).
Permet de repositionner l'image entre deux scans au cas où le cerveau serait légèrement décalé.
\
- Choix de la métrique et de l'optimiseur.
\
– Définition de la transformation (B-spline)
Adapté aux changement locaux, comme le changement de taille d'une tumeur.
\
- Choix du recalage
\
– Application de la transformation composite (Translation/B-spline) et sauvegarde\
de l'image "aligned_image.nii.gz".
\
– Segmentation des images
Segmentation de la tumeur sur les images "fixed_image.nii.gz" et "aligned_image.nii.gz".
Sauvegarde des images "segmentation_fixed.nii.gz" et "segmentation_aligned.nii.gz"

## 5.  Problème rencontré
Lors de l'ajout de la transformation b-spline, nous avons essayé d'ajouter un optimizer, comme pour\
la translation. Cependant, nous avons reçu une erreur qui indiquait qu'une fonction utilsiée en\
interne par la fonction d'optimisation n'était pas implémentée pour la classe BSpline.\
Pourtant, la fonction était utilisée dans un exemple de la documentation d'ITK sans encombre.\
Il semblerait donc qu'elle soit implémentée en C++ mais pas en Python.\
Nous avons testé plusieurs optimiseurs et metrics pour BSpline, mais tous renvoyaient la même erreur.\
ITK étant malheureusement très mal documenté, nous n'avons pas pu trouver de fonction d'optimisation\
qui fonctionne. Nous avons donc dû laisser BSpline sans optimizer.

## 6. Instructions d'utilisation
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

## 7. Résultats
- Alignement visuel réussi : les images recalées montrent un bon alignement des structures\
anatomiques segmentées après translation.
