# test_fighter.py
from ursina import *
from ursina.shaders import lit_with_shadows_shader
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import loadPrcFileData
from ursina import application
# --- Optimisations AVANT Ursina ---
loadPrcFileData("", "sync-video 0")
loadPrcFileData("", "framebuffer-multisample 1")
loadPrcFileData("", "multisamples 4")

app = Ursina()

# ✅ Récupération de 'base' APRÈS la création de l'app
base = application.base
# ============================================================
# LUMIÈRES (avec bloom, elles vont briller)
# ============================================================
DirectionalLight().look_at(Vec3(1, -1, -1))
AmbientLight(color=color.rgba(150, 150, 170, 255))

window.color = color.rgb(135, 206, 235)   # bleu ciel clair
Sky()                                     # ciel dégradé

# Petit soleil visible pour déclencher le bloom
"""
soleil = Entity(
    model='sphere',
    scale=15,
    position=(-100, 200, 200), # ✅ devant l'avion (Z positif)
    color=color.rgb(255, 240, 180),
    unlit=True,       # émissif → va briller avec le bloom
)
"""

# ============================================================
# SOLEIL
# ============================================================
# Halo externe (orange transparent)
Entity(
    model='sphere',
    scale=35,
    position=(-100, 300, 300),
    color=color.rgba(255, 100, 30, 40),
    unlit=True,
)

# Halo intermédiaire (jaune-orange)
Entity(
    model='sphere',
    scale=25,
    position=(-100, 300, 300),
    color=color.rgba(255, 180, 60, 120),
    unlit=True,
)

# Cœur du soleil (jaune pâle, PAS blanc)
Entity(
    model='sphere',
    scale=18,
    position=(-100, 300, 300),
    color=color.rgb(255, 230, 140),       # ✅ jaune, pas blanc
    unlit=True,
)


# ============================================================
# AVION
# ============================================================
avion = Entity(
    model='./assets/fighterjet.obj',
    texture='./assets/diffuse.png',
    scale=1,
    shader=lit_with_shadows_shader,
)

# ============================================================
# POST-PROCESSING : BLOOM
# ============================================================
filters = CommonFilters(base.win, base.cam)
filters.setBloom(
    blend=(0.9, 0.6, 0.3, 0.0),    # R, G, B, seuil
    mintrigger=0.6,                 # seuil de luminosité déclenchant le bloom
    maxtrigger=1.0,                 # saturation max
    desat=0.2,                      # désaturation du halo
    intensity=1.5,                  # intensité globale
    size="large",                  # small / medium / large
)

# Anti-aliasing FXAA (bords lisses sans coût GPU énorme)
filters.setCartoonInk(separation=0)   # désactivé, on garde juste FXAA
# filters.setFxaa()                    # décommentez si vous voulez FXAA

# ============================================================
# CAMÉRA
# ============================================================
EditorCamera()

Text('Clic droit = tourner | Molette = zoom | Echap = quitter',
     position=window.bottom, origin=(0, 0), background=True)

def input(key):
    if key == 'escape':
        application.quit()

app.run()