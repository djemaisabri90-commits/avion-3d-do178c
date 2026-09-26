// src/main.rs
use std::fs::File;
use std::io::{Read, Write};
use std::thread::sleep;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

unsafe extern "C" {
    unsafe fn calculer_correction_gouverne(angle_brut: i32) -> f32;
    unsafe fn calculer_portance(vitesse_noeuds: f32, angle_roulis_degres: f32) -> f32;
}

#[repr(C)]
struct PaquetTelemetrie {
    timestamp: u64,
    angle_gouverne: f32,
    angle_roulis: f32,    // Nouvelle donnée
    portance: f32,        // Nouvelle donnée
    checksum: u32,
}

fn main() {
    println!("[RUST-C] Système de vol multi-paramètres actif...");
    let mut ordre_profondeur: f32 = 0.0;
    let mut ordre_roulis: f32 = 0.0;
    let vitesse_croisiere: f32 = 250.0; // Vitesse constante en nœuds

    loop {
        // 1. Lecture des ordres combinés de la station Python (8 octets : 2x f32)
        if let Ok(mut fichier_cmd) = File::open("commande_pilote.bin") {
            let mut tampon = [0u8; 8];
            if fichier_cmd.read_exact(&mut tampon).is_ok() {
                ordre_profondeur = f32::from_le_bytes([tampon[0], tampon[1], tampon[2], tampon[3]]);
                ordre_roulis = f32::from_le_bytes([tampon[4], tampon[5], tampon[6], tampon[7]]);
            }
        }

        // 2. Calculs via les équations du fichier C
        let angle_brut_c = (ordre_profondeur * 10.0) as i32;
        let correction_gouverne = unsafe { calculer_correction_gouverne(angle_brut_c) };
        let angle_final_profondeur = correction_gouverne / 0.05;

        // Calcul de la portance aérodynamique en C
        let portance_calculee = unsafe { calculer_portance(vitesse_croisiere, ordre_roulis) };

        // 3. Construction et envoi de la télémétrie IoT
        let paquet = PaquetTelemetrie {
            timestamp: SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs(),
            angle_gouverne: angle_final_profondeur,
            angle_roulis: ordre_roulis,
            portance: portance_calculee,
            checksum: 0xABCDEF,
        };

        if let Ok(mut fichier_out) = File::create("signal_machine.bin") {
            let octets: &[u8] = unsafe {
                std::slice::from_raw_parts(
                    &paquet as *const PaquetTelemetrie as *const u8,
                    std::mem::size_of::<PaquetTelemetrie>(),
                )
            };
            let _ = fichier_out.write_all(octets);
        }

        sleep(Duration::from_millis(30));
    }
}
