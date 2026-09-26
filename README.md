# ✈️ Simulateur Avionique 3D Connecté - Spécification DO-178C

Prototype de système avionique et cyber-résistant pour drone agricole multi-langages, développé selon les principes de cloisonnement de la norme **DO-178C**.

## 📊 Architecture Polyglotte & Cloisonnement
L'application est divisée en 3 couches indépendantes et étanches :
1. **Calculateur Critique (Langage C) :** Lois de contrôle, butées aérodynamiques physiques (écrêtage à ±30°) et calcul de portance.
2. **Gestionnaire IoT & Cyber (Langage Rust) :** Lecture sécurisée des commandes USB/Radio et apposition d'une signature d'intégrité (*Checksum* `0xABCDEF`).
3. **IHM & Boîte Noire (Langage Python) :** Rendu de jeu vidéo 3D en temps réel via le moteur *Ursina Engine* et enregistrement continu des données de vol (*Flight Data Recorder*).

## 🛡️ Pipeline de Certification de Vol
* **Analyse Statique Automatique :** Intégration de `Cppcheck` dans le script de build Cargo (`build.rs`). La compilation s'interrompt si une fonction interdite (ex: `malloc`) est détectée.
* **Matrice de Traçabilité :** Liste des exigences de vol (HLR/LLR) documentée en interne.

## 🚀 Lancement du projet
1. Lancez l'électronique de bord : `cargo run`
2. Lancez le simulateur 3D au sol : `python station_terrestre.py`
3. Analysez les données de la boîte noire après le vol : `python analyser_boite_noire.py`
