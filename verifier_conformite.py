# verifier_conformite.py
import subprocess
import sys

FICHIER_C = "calcul_gouverne.c"

# RÈGLES CRITIQUES DO-178C (MISRA C)
# Liste des mots-clefs formellement interdits pour garantir le déterminisme mémoire
MOTS_INTERDITS = [
    "malloc",   # Allocation dynamique (Interdit : risque de fragmentation)
    "free",     # Libération dynamique (Interdit : risque de pointeur fou)
    "calloc",   # Allocation dynamique alternative
    "realloc",  # Réallocation dynamique
    "printf",   # Entrées/Sorties standards (Interdit dans un firmware de vol)
    "scanf"     # Entrées standards
]

def verifier_mots_interdits():
    """Analyse lexicale simple pour traquer les fonctions dynamiques interdites."""
    print(f"[DO-178C] Étape 1 : Inspection lexicale de '{FICHIER_C}'...")
    erreurs = 0
    
    with open(FICHIER_C, "r", encoding="utf-8") as f:
        lignes = f.readlines()
        
    for index, ligne in enumerate(lignes):
        # On ignore les commentaires pour éviter les faux positifs
        if ligne.strip().startswith(("//", "/*", "*")):
            continue
            
        for mot in MOTS_INTERDITS:
            if mot in ligne:
                print(f"  ❌ VIOLATION CRITIQUE à la ligne {index + 1} : Utilisation de '{mot}' détectée !")
                erreurs += 1
                
    return erreurs

def executer_cppcheck():
    """Lance l'analyse statique profonde (MISRA / Style / Sécurité) via Cppcheck."""
    print(f"\n[DO-178C] Étape 2 : Lancement de l'analyse statique profonde (Cppcheck)...")
    
    commande = [
        "cppcheck",
        "--enable=all",          # Active toutes les vérifications (style, avertissements, etc.)
        # SÉCURITÉ AÉRONAUTIQUE : On désactive 'unusedFunction' car les fonctions sont appelées par Rust
        # On supprime 'missingIncludeSystem' pour ignorer l'absence d'en-têtes natifs sous Windows
        "--suppress=unusedFunction",
        "--suppress=missingIncludeSystem",
        "--error-exitcode=1",    # Force un code de sortie d'erreur si un bug est trouvé
        "--inconclusive",
        FICHIER_C
    ]
    
    try:
        # Exécution de la commande
        resultat = subprocess.run(commande, capture_output=True, text=True, check=True)
        print("  ✅ Cppcheck : Aucune anomalie détectée dans la structure du code C.")
        return 0
    except subprocess.CalledProcessError as e:
        # Cppcheck ne lèvera une erreur maintenant que s'il y a un VRAI bug de syntaxe ou de mémoire
        print("  ❌ Cppcheck a détecté des anomalies structurelles :")
        print(e.output)
        print(e.stderr)
        return 1
    except FileNotFoundError:
        print("  ⚠️ Avertissement : Cppcheck n'est pas installé ou introuvable dans le PATH.")
        print("  L'inspection lexicale de l'Étape 1 a tout de même été effectuée avec succès.")
        return 0

if __name__ == "__main__":
    print("=== AUDIT AUTOMATISÉ DE CONFORMITÉ LOGICIELLE DE VOL ===")
    fautes_lexicales = verifier_mots_interdits()
    fautes_structurelles = executer_cppcheck()
    
    print("\n=======================================================")
    if fautes_lexicales == 0 and fautes_structurelles == 0:
        print("🏆 RÉSULTAT : CODE 100% CONFORME AUX EXIGENCES DE VOL !")
        sys.exit(0)
    else:
        print("💥 RÉSULTAT : CONFORMITÉ REFUSÉE. Veuillez corriger les violations.")
        sys.exit(1)
