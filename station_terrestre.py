# station_terrestre.py
from ursina import *
from ursina.shaders import lit_with_shadows_shader
from ursina import application
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import loadPrcFileData
import struct
import random

# --- Optimisations Panda3D ---
loadPrcFileData("", "notify-level-pnmimage error")
loadPrcFileData("", "notify-level-display error")
loadPrcFileData("", "sync-video 0")
loadPrcFileData("", "framebuffer-multisample 1")
loadPrcFileData("", "multisamples 4")
loadPrcFileData("", "texture-anisotropic-degree 8")

# À insérer au début du fichier avec les autres formats struct
# Format de la boîte noire : Q (Timestamp), f (Tangage), f (Roulis), f (Portance), B (Statut Cyber : 0 ou 1)
FORMAT_BOITE_NOIRE = "QfffB"
PKT_BOITE_NOIRE = struct.Struct(FORMAT_BOITE_NOIRE)

# --- Format binaire précompilé ---
PKT = struct.Struct("QfffI")
TAILLE_PAQUET = PKT.size

app = Ursina(title="SIMULATEUR AVANCÉ 3D", borderless=False)
base = application.base

def enregistrer_dans_boite_noire(timestamp, tangage, roulis, portance, sain):
    """Écrit chaque échantillon de vol de manière brute et compacte (Mode Boîte Noire)."""
    code_cyber = 0 if sain else 1 # 0 = OK, 1 = Alerte Cyber
    
    try:
        # Ouverture en mode 'ab' (Append Binary) pour ajouter les données à la suite sans effacer
        with open("boite_noire.bin", "ab") as f_blackbox:
            donnees_paquet = PKT_BOITE_NOIRE.pack(timestamp, tangage, roulis, portance, code_cyber)
            f_blackbox.write(donnees_paquet)
    except IOError:
        pass # En DO-178C, un échec d'écriture de log sol ne doit jamais bloquer l'IHM

# ============================================================
# 1. CIEL & LUMIÈRES
# ============================================================
Sky(texture='sky_default')
window.color = color.rgb(135, 206, 235)


sun = DirectionalLight(shadows=True)
sun.look_at(Vec3(1, -2, -1))
AmbientLight(color=color.rgba(150, 150, 170, 255))

# ============================================================
# 2. SOLEIL VISIBLE (attaché à la caméra)
# ============================================================
# Soleil fixe dans le monde (pas attaché à la caméra)
soleil_pos = (-150, 120, -200)   # ✅ position fixe, en haut à droite
# Halo externe
Entity(
    model='sphere', scale=40,
    position=soleil_pos,
    color=color.rgba(255, 100, 30, 40),
    unlit=True,
)
# Halo intermédiaire
Entity(
    model='sphere', scale=25,
    position=soleil_pos,
    color=color.rgba(255, 180, 60, 120),
    unlit=True,
)
# Cœur
Entity(
    model='sphere', scale=15,
    position=soleil_pos,
    color=color.rgb(255, 230, 140),
    unlit=True,
)

# ============================================================
# 3. AVION (.obj du fighter jet)
# ============================================================
def creer_avion():
    """Charge le fighter jet et recentre son pivot décalé."""
    root = Entity(name="Avion")
    
    scale = 0.05
    
    modele = Entity(
        parent=root,
        model='./assets/fighterjet.obj',
        texture='./assets/diffuse.png',
        scale=scale,
        shader=lit_with_shadows_shader,
    )
    
    # ✅ CORRIGÉ : on multiplie par le scale pour convertir en unités monde
    modele.x -= modele.bounds.center.x * scale
    modele.y -= modele.bounds.center.y * scale
    modele.z -= modele.bounds.center.z * scale
    
    print(f"Offset appliqué (monde) : "
          f"x={-modele.bounds.center.x * scale:.3f}, "
          f"y={-modele.bounds.center.y * scale:.3f}, "
          f"z={-modele.bounds.center.z * scale:.3f}")
    
    return root

avion = creer_avion()
avion.position = (0, 20, 0)


print(f"Taille avion : {avion.scale}")
print(f"Bounds : {avion.bounds}")
print(f"Position : {avion.position}")

# ============================================================
# 4. TERRAIN DÉFILANT (pooling)
# ============================================================
TAILLE_SOL = 400
NB_SOLS = 3

sols = []
for i in range(NB_SOLS):
    s = Entity(
        model='cube',
        scale=(TAILLE_SOL, 1, TAILLE_SOL),
        position=(0, -10, -i * TAILLE_SOL),
        color=color.rgb(80, 140, 80),
        shader=lit_with_shadows_shader,
    )
    sols.append(s)

# ============================================================
# 5. NUAGES (pooling)
# ============================================================
NUAGES = []
for _ in range(40):
    n = Entity(
        model='sphere',
        scale=(random.uniform(15, 30),
               random.uniform(4, 8),
               random.uniform(15, 30)),
        position=(random.uniform(-200, 200),
                  random.uniform(30, 70),
                  random.uniform(-600, 50)),
        color=color.rgba(255, 255, 255, 180),
        unlit=True,
    )
    NUAGES.append(n)

# ============================================================
# 6. CAMÉRA
# ============================================================
camera.parent = avion
camera.position = (0, 2, -50)
camera.rotation = (0, 0, 0)
#camera.fov = 90

# Remplacez le bloc caméra par :
#EditorCamera()
#print(f"Cam pos: {camera.position}")
print(f"Cam world: {camera.world_position}")
print(f"Cam rot: {camera.rotation}")

# ============================================================
# 7. POST-PROCESSING (BLOOM)
# ============================================================
filters = CommonFilters(base.win, base.cam)
filters.setBloom(
    blend=(0.9, 0.6, 0.3, 0.0),
    mintrigger=0.9,
    maxtrigger=1.0,
    desat=0.2,
    intensity=0.5,
    size="small",
)

# ============================================================
# 8. PARAMÈTRES DE VOL
# ============================================================
vitesse        = 0.0
VITESSE_MAX    = 60
VITESSE_MIN    = 0
ACCEL          = 30
LACET          = 40
TANGAGE        = 45
_frame_counter = 0

# ============================================================
# 9. HUD
# ============================================================
hud = Text(
    text='',
    position=window.top_left,
    background=True,
    scale=1.1,
)

# ============================================================
# 10. BOUCLE PRINCIPALE CONNECTÉE C/RUST (DO-178C)
# ============================================================
# Variables de consignes envoyées par le pilote au sol
cmd_tangage = 0.0
cmd_roulis = 0.0

def update():
    global vitesse, _frame_counter, cmd_tangage, cmd_roulis
    dt = time.dt
    if dt <= 0:
        return

    # --- 1. ACCÉLÉRATION / FREIN (Gestion locale) ---
    if held_keys['w']:
        vitesse = min(vitesse + ACCEL * dt, VITESSE_MAX)
    elif held_keys['s']:
        vitesse = max(vitesse - ACCEL * dt, VITESSE_MIN)
    else:
        vitesse *= (1 - 0.3 * dt)

    # --- 2. TRAITEMENT DES CONSIGNES CLAVIER (Pour envoi au C/Rust) ---
    if held_keys['a']:
        cmd_roulis = lerp(cmd_roulis, -25.0, 0.1) # Demande roulis gauche
    elif held_keys['d']:
        cmd_roulis = lerp(cmd_roulis, 25.0, 0.1)  # Demande roulis droit
    else:
        cmd_roulis = lerp(cmd_roulis, 0.0, 0.1)

    if held_keys['up arrow']:
        cmd_tangage = lerp(cmd_tangage, -20.0, 0.1) # Demande piquer
    elif held_keys['down arrow']:
        cmd_tangage = lerp(cmd_tangage, 20.0, 0.1)  # Demande cabrer
    else:
        cmd_tangage = lerp(cmd_tangage, 0.0, 0.1)

    # --- 3. EXPORTATION DES ORDRES VERS L'EMBARQUÉ (Écriture binaire) ---
    try:
        with open("commande_pilote.bin", "wb") as f_out:
            # Envoi des consignes (tangage et roulis réclamés par le pilote)
            f_out.write(struct.pack("ff", cmd_tangage, cmd_roulis))
    except IOError:
        pass

    # --- 4. IMPORTATION DE LA TÉLÉMÉTRIE SÉCURISÉE (Lecture C/Rust) ---
    angle_reel_tangage = 0.0
    angle_reel_roulis = 0.0
    portance_aerodynamique = 0.0
    status_cyber_sain = True

    if os.path.exists("signal_machine.bin"):
        try:
            with open("signal_machine.bin", "rb") as f:
                donnees_brutes = f.read(TAILLE_PAQUET)
            if len(donnees_brutes) == TAILLE_PAQUET:
                # Dépaquetage via le format précompilé struct.Struct("QfffI")
                timestamp, angle_reel_tangage, angle_reel_roulis, portance_aerodynamique, checksum = PKT.unpack(donnees_brutes)
                status_cyber_sain = (checksum == 0xabcdef)

                # ✅ L'ASTUICE : On enregistre immédiatement l'instant de vol dans la Boîte Noire
                
                enregistrer_dans_boite_noire(
                    timestamp, 
                    angle_reel_tangage, 
                    angle_reel_roulis, 
                    portance_aerodynamique, 
                    status_cyber_sain
                )
        except IOError:
            pass

    # --- 5. APPLICATION DES DEPLACEMENTS ET ROTATIONS VALIDÉS ---
    if status_cyber_sain:
        # L'avion s'oriente selon les valeurs calculées et validées par le code C
        avion.rotation_x = angle_reel_tangage
        avion.rotation_z = angle_reel_roulis
        
        # En fonction du lacet aérodynamique induit par le roulis
        if held_keys['a']: avion.rotation_y -= LACET * dt
        if held_keys['d']: avion.rotation_y += LACET * dt
        
        # Alerte si le calcul C s'écrête en butée
        hud_status_msg = "[OK] SYSTEM STATUS: NOMINAL (DO-178C VALIDATED)"
    else:
        # Failsafe Cyber-Alerte : On fige l'attitude de l'appareil en vol stabilisé
        avion.rotation_x = 0
        avion.rotation_z = 0
        hud_status_msg = "[ALERT] ALERTE CRITIQUE : CALCULATEUR BORD COMPROMIS !"

    # Déplacement de l'avion vers l'avant selon sa cinématique
    avion.position += avion.forward * vitesse * dt
    
    # Simulation de l'effet de la portance (C) sur l'altitude (Axe Y)
    # Si la portance calculée en C chute, l'avion descend doucement
    if vitesse > 5:
        avion.y += (portance_aerodynamique - 12.0) * dt # 12.0 simule le poids de l'appareil

    # --- 6. RECYCLAGE DES ÉLÉMENTS (POOLING) ---
    for s in sols:
        if s.z - avion.world_z > TAILLE_SOL:
            s.z -= TAILLE_SOL * NB_SOLS
        elif avion.world_z - s.z > TAILLE_SOL * (NB_SOLS - 1):
            s.z += TAILLE_SOL * NB_SOLS

    for n in NUAGES:
        if n.z - camera.world_z > 200:
            n.z -= 800
            n.x = random.uniform(-200, 200)
            n.y = random.uniform(30, 70)

    # --- 7. FLUX DU TABLEAU DE BORD (HUD) ---
    _frame_counter += 1
    if _frame_counter % 5 == 0:
        fps = int(1 / max(dt, 1e-4))
        hud.text = (
            f'{hud_status_msg}\n'
            f'VITESSE  : {vitesse:5.1f} kts\n'
            f'ALTITUDE : {avion.y:5.1f} ft\n'
            f'PORTANCE : {portance_aerodynamique:5.2f} N (Calcul C)\n'
            f'FPS      : {fps}\n'
            f'[W/S] Gaz  [A/D] Roulis  [Up/Down] Tangage  [C] Vue Caméra'
        )

# ============================================================
# 11. ENTRÉES CLAVIER & ENGINES
# ============================================================
def input(key):
    if key == 'escape':
        application.quit()
    elif key == 'c':
        if camera.z < -1:
            # Vue cockpit rapprochée
            camera.position = (0, 1.2, 3)
            camera.rotation = (0, 0, 0)
        else:
            # Vue poursuite standard arrière
            camera.position = (0, 4, -40)
            camera.rotation = (0, 0, 0)

# ============================================================
# 12. LANCEMENT INDUSTRIEL
# ============================================================
app.run()
