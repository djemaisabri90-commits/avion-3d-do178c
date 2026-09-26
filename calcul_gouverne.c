// calcul_gouverne.c
#include <stdint.h>

#define ANGLE_MAX_CONFORME 30.0f
#define ANGLE_MIN_CONFORME -30.0f

// Version blindée contre les anomalies physiques ou cyber
float calculer_correction_gouverne(int32_t angle_brut) {
    float angle_degres = (float)angle_brut * 0.1f; 
    
    // BUTÉE DE SÉCURITÉ (Écrêtage aérodynamique)
    // Si le signal commande un angle fou, le C force le maximum tolérable
    if (angle_degres > ANGLE_MAX_CONFORME) {
        angle_degres = ANGLE_MAX_CONFORME;
    } else if (angle_degres < ANGLE_MIN_CONFORME) {
        angle_degres = ANGLE_MIN_CONFORME;
    } else {
        // Valeur nominale : aucun ajustement nécessaire
    }
    
    // Application de la loi de contrôle proportionnelle
    float correction = angle_degres * 0.05f; 
    
    return correction;
}

// 2. DEUXIÈME ÉQUATION : Calcul de la Portance aérodynamique (Simulée)
// Formule simplifiée : Portance = Coefficient * Vitesse^2 * cos(Angle_Roulis)
float calculer_portance(float vitesse_noeuds, float angle_roulis_degres) {
    // Conversion de l'angle en approximation de cosinus pour rester déterministe et rapide
    float angle_rad = angle_roulis_degres * 0.0174533f; // deg to rad
    float cos_approx = 1.0f - (angle_rad * angle_rad * 0.5f); // Développement limité de cos(x)
    
    // Coefficient aérodynamique global de l'aile
    float cz = 0.0002f; 
    float portance = cz * (vitesse_noeuds * vitesse_noeuds) * cos_approx;
    
    if (portance < 0.0f) {
        portance = 0.0f;
    }
    return portance;
}

//void fonction_interdite() {
    //int *ptr = (int*)malloc(sizeof(int)); // Volontairement interdit
//}