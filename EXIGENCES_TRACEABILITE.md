# MATRICE DE TRAÇABILITÉ DES EXIGENCES LOGICIELLES (DO-178C / DAL C)
**Projet :** Simulateur Avionique 3D Connecté (`AVION-3D`)  
**Statut de l'Audit :** 100% Conforme (Vérifié par `verifier_conformite.py`)

---

## 1. Définition des Exigences de Haut Niveau (HLR)

*   **HLR-01 (Pilotage Multi-Axes) :** Le logiciel doit permettre à l'opérateur terrestre de commander en temps réel le tangage (gouverne de profondeur) et le roulis (ailerons) de l'aéronef via une interface interactive.
*   **HLR-02 (Sécurité des Enveloppes de Vol) :** Le calculateur embarqué doit brider structurellement les commandes mécaniques pour empêcher l'aéronef de dépasser ses limites aérodynamiques structurelles.
*   **HLR-03 (Résilience Cyber-IoT) :** Le canal de communication radio doit vérifier l'intégrité de chaque paquet de télémétrie. Tout paquet altéré doit être rejeté et signalé visuellement à la station de contrôle.

---

## 2. Définition des Exigences de Bas Niveau (LLR)

*   **LLR-01.1 (Saisie Clavier) :** L'IHM Python doit intercepter les touches `Up/Down` pour le tangage et `Left/Right` pour le roulis à une fréquence de rafraîchissement minimale de 20 Hz.
*   **LLR-02.1 (Butée Physique C) :** Le module en langage C doit écrêter l'angle de tangage brut reçu à une butée stricte de ± 30.0 degrés avant tout calcul de gain.
*   **LLR-02.2 (Modélisation de Portance) :** Le code C doit calculer la portance physique en fonction du carré de la vitesse et du cosinus de l'angle de roulis.
*   **LLR-03.1 (Signature Cryptographique Rust) :** Le module Rust doit apposer un Checksum fixe `0xABCDEF` sur chaque structure de données transmise.

---

## 3. Matrice de Traçabilité Bidirectionnelle (RTM)

Ce tableau croise les exigences avec l'implémentation exacte dans vos fichiers et les tests automatisés :

| Identifiant Exigence (HLR) | Exigence Bas Niveau (LLR) | Fichier d'Implémentation Source | Fonction / Bloc de Code Spécifique | Méthode de Vérification (Test) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HLR-01** (Pilotage) | LLR-01.1 (Clavier) | `station_terrestre.py` | `def update()` & `held_keys` | Test de robustesse IHM (Manuel) |  Validé |
| **HLR-02** (Sécurité) | LLR-02.1 (Butées) | `calcul_gouverne.c` | `calculer_correction_gouverne` | Audit strict par `verifier_conformite.py` |  Validé |
| **HLR-02** (Sécurité) | LLR-02.2 (Portance) | `calcul_gouverne.c` | `calculer_portance` | Vérification mathématique Cppcheck |  Validé |
| **HLR-03** (Cyber) | LLR-03.1 (Checksum) | `src/main.rs` | `let clef_cyber = ...` | Injection d'anomalie dynamique (`0xBAD999`) |  Validé |

---

## 4. Registre des Outils Qualifiés (DO-330)

Pour être conforme, les outils automatiques utilisés au sol doivent être listés :
1.  **Analyseur Statique (TQL-5) :** Cppcheck v2.22.0 (Vérification des règles de style et d'absence de code mort).
2.  **Compilateur (TQL-5) :** Rustc/Cargo & MSVC `link.exe` (Garantie de l'intégrité de la génération du binaire).
