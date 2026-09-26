// build.rs
use std::process::Command;

fn main() {
    println!("cargo:rerun-if-changed=calcul_gouverne.c");

    // Lancement automatique du script d'analyse statique Python avant la compilation
    let statut_audit = Command::new("cmd")
        .arg("verifier_conformite.py")
        .status()
        .expect("Impossible de lancer le script d'audit de conformité.");

    // Si l'audit échoue, on stoppe immédiatement la chaîne de compilation
    if !statut_audit.success() {
        panic!("❌ Arrêt de la compilation : Le code C a échoué à l'audit de conformité DO-178C !");
    }

    // Si l'audit est un succès, on compile le fichier C normalement
    cc::Build::new()
        .file("calcul_gouverne.c")
        .compile("calcul_gouverne");
}
