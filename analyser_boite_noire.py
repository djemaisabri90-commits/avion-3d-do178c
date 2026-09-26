# analyser_boite_noire.py
import struct
import os

FORMAT_BOITE_NOIRE = "QfffB"
TAILLE_LIGNE = struct.calcsize(FORMAT_BOITE_NOIRE)

def depouiller_boite_noire():
    if not os.path.exists("boite_noire.bin"):
        print("❌ Erreur : Aucun fichier 'boite_noire.bin' détecté. Lancez le simulateur d'abord.")
        return

    print("=== DÉPOUILLEMENT ANALYTIQUE DE LA BOÎTE NOIRE ===")
    taille_totale = os.path.getsize("boite_noire.bin")
    nombre_echantillons = taille_totale // TAILLE_LIGNE
    
    print(f"Fichier d'archive détecté : {taille_totale} octets ({nombre_echantillons} points de vol enregistrés)\n")
    
    compteur_alertes = 0
    
    with open("boite_noire.bin", "rb") as f:
        for i in range(nombre_echantillons):
            octets = f.read(TAILLE_LIGNE)
            if not octets:
                break
                
            timestamp, tangage, roulis, portance, code_cyber = struct.unpack(FORMAT_BOITE_NOIRE, octets)
            
            status_texte = "NOMINAL" if code_cyber == 0 else "🚨 CORROMPU (CYBER-ATTACK)"
            if code_cyber == 1:
                compteur_alertes += 1
                
            # On affiche un échantillon sur 10 pour ne pas surcharger la console, ou toutes les alertes
            if i % 10 == 0 or code_cyber == 1:
                print(f"[Point {i:04d}] Time: {timestamp} | Tangage: {tangage:5.1f}° | Roulis: {roulis:5.1f}° | Portance: {portance:5.1f} N | Statut: {status_texte}")

    print("\n=== BILAN DU RAPPORT D'ENQUÊTE DE VOL ===")
    if compteur_alertes == 0:
        print("✅ Aucun incident détecté. Intégrité des enveloppes et du flux radio : 100%.")
    else:
        print(f"⚠️ ATTENTION : {compteur_alertes} violations d'intégrité cyber ont été mémorisées dans la boîte noire !")

if __name__ == "__main__":
    depouiller_boite_noire()
