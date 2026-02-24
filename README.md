# ProHash - L'Assistant Hashcat Intelligent 🚀

**ProHash** est un outil interactif en ligne de commande (CLI) développé en Python. Il agit comme une surcouche intelligente pour le célèbre outil de récupération de mots de passe **Hashcat**.

Son objectif est de démocratiser l'utilisation de Hashcat en gommant la complexité de ses lignes de commande, tout en offrant une expérience d'apprentissage pour les débutants en cybersécurité, et un workflow tactique ultra-rapide pour les professionnels.

## ✨ Fonctionnalités Clés

- **🎓 Modes d'utilisation adaptables** : Mode "Apprentissage" avec des explications ludiques sur chaque concept, ou Mode "Pro" pour un résultat direct sans friction.
- **🔍 Détection Automatique** : Collez un hash, ProHash devinera son algorithme et l'associera automatiquement au mode Hashcat.
- **📚 Gestion des Wordlists** : ProHash détecte instantanément vos dictionnaires système (ex: `rockyou.txt`) et vous propose de les utiliser en un clic.
- **🧠 Moteur de Stratégie & Règles** : Le bot analyse votre matériel (CPU/GPU) et la complexité du hash pour optimiser l'attaque (ex: ajout automatique de règles pour les cibles compliquées).
- **📊 Auto-Reporting** : Une fois le mot de passe cassé, un rapport formaté est automatiquement sauvegardé.

## 📁 Structure du projet

- **core/**: Le moteur principal avec la logique métier (détection, exécution de Hashcat, vérifications matérielles).
- **database/**: Fichiers de configuration, signatures de hash et profils d'attaques.
- **ui/**: Interface en ligne de commande (CLI) et module pédagogique complet.
- **utils/**: Fonctions utilitaires, journalisation (logs) et gestionnaire de dictionnaires.
- **reports/**: Rapports générés automatiquement après une attaque réussie.

## 🛠️ Prérequis

- Python 3.8+
- [Hashcat](https://hashcat.net/hashcat/) installé et accessible nativement sur le système
- (Optionnel) Drivers OpenCL / CUDA pour l'accélération matérielle GPU

## Installation

```bash
git clone https://github.com/votre_profil/ProHash.git
cd ProHash
pip install -r requirements.txt
```

## Utilisation Rapide

```bash
python main.py
```
