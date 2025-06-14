# Guide d'acquisition IRM

Ce projet Flask propose un guide interactif pour sélectionner un modèle d'IRM adapté aux besoins et contraintes.

## Installation
1. Cloner le dépôt.
2. Créer un environnement virtuel Python 3.8+.
3. Installer les dépendances : `pip install -r requirements.txt`.
4. Initialiser la base SQLite (automatique à la première exécution).
5. Ajouter des fournisseurs, modèles et critères via un shell Python ou interface admin.
6. Lancer l'application : `python app.py`.

## Utilisation
- Accéder à `http://localhost:5000/`.
- Remplir le formulaire des critères et poids, puis soumettre.
- Consulter la recommandation et les scores des modèles.
- Voir les détails d’un modèle.

## Personnalisation
- Adapter les critères dans la table `criteria`.
- Enrichir la table `models` avec les fiches techniques.
- Modifier la logique de scoring dans `app.py` selon besoins réels.
- Remplacer SQLite par PostgreSQL/MySQL pour production.