# TC Insight – Spec Generator (Python)

Générateur officiel de spécifications TC Insight  
**Excel machine-first ➜ Spec JSON validé (Schema V2)**

---

## 🎯 Objectif du projet

Ce projet permet de générer automatiquement des fichiers de spécification TC Insight (JSON) à partir d'un fichier Excel machine-first standardisé.

Il remplace le processus manuel actuel où un humain :
- lit un Excel
- interprète les règles
- modifie un spec existant à la main

**👉 Ici, aucune interprétation humaine.**  
**👉 Le générateur applique des règles déterministes et validées.**

---

## 🧠 Philosophie

- **Fail fast** : toute erreur est bloquante
- **Zéro ambiguïté** : si ce n'est pas dans l'Excel, ça n'existe pas
- **Validation béton** : Excel ➜ Modèle interne ➜ JSON Schema
- **Architecture type compilateur**

### Flux de génération
```
Excel machine-first
        ↓
Validation Excel
        ↓
Modèle interne (AST)
        ↓
Validation JSON Schema
        ↓
Spec JSON final
```

---

## 📁 Structure du projet
```
tc_insight_spec_generator/
├── schemas/              # JSON Schema officiels
├── src/tc_spec/
│   ├── cli.py           # CLI (tc-spec)
│   ├── main.py          # Orchestration principale
│   ├── excel/           # Lecture & validation Excel
│   ├── model/           # Modèle interne (AST)
│   ├── builder/         # Excel → modèle
│   ├── exporter/        # Modèle → JSON
│   ├── validation/      # Validations
│   └── utils/           # Helpers & erreurs
└── tests/               # Tests unitaires
```

👉 Chaque dossier a une seule responsabilité.

---

## 📊 Excel machine-first (prérequis)

Le générateur n'accepte que des Excels conformes au format **machine-first** officiel.

### Principes clés

- **Une ligne = une entité**
- **Une colonne = un champ JSON**
- **Aucune logique implicite**
- **Aucune cellule "interprétable"**

⚠️ **Un Excel invalide ➜ génération bloquée.**

---

## 🚀 Installation

### Prérequis

- Python ≥ 3.10
- pip

### Installation locale
```bash
pip install -e .
```

---

## ▶️ Utilisation

### Générer un spec JSON
```bash
tc-spec generate spec.xlsx --out spec.json
```

### Valider uniquement l'Excel
```bash
tc-spec validate spec.xlsx
```

### Valider un spec JSON via le schema
```bash
tc-spec validate-json spec.json
```

---

## ✅ Validations effectuées

### Validation Excel (amont)

- Feuilles obligatoires présentes
- Colonnes obligatoires présentes
- Types, opérateurs et enums valides
- Références cohérentes (questions, listes, sections)

### Validation JSON (aval)

- Conformité stricte au JSON Schema V2
- Typage strict des questions
- Règles formelles valides
- Anomalies cohérentes

---

## 🧪 Tests

Lancer les tests :
```bash
pytest
```

Les tests couvrent :

- validation Excel
- builders
- validation JSON Schema

---

## 🧱 Évolutivité

Ce projet est conçu pour :

- supporter plusieurs marchés
- intégrer de nouveaux types de questions
- faire évoluer le schema (V3, V4…)

### Toute évolution doit passer par :

1. Mise à jour du JSON Schema
2. Adaptation du générateur
3. Ajout de tests

---

## 🛑 Règles de contribution

- Pas de logique métier dans la CLI
- Pas de JSON généré avant la phase finale
- Toute nouvelle règle = test obligatoire
- Pas de "quick fix" silencieux

---

## 📌 Statut du projet

- 🟡 En cours de construction
- 🟢 Architecture validée
- 🔜 Générateur complet + CI

---

## 👤 Auteur / Équipe

Projet conçu pour industrialiser la génération de specs TC Insight  
en éliminant toute ambiguïté humaine.