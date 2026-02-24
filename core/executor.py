import os
import subprocess
import tempfile
import time
from utils.logger import log_info, log_error
from reports.generator import ReportGenerator

class HashcatExecutor:
    """Gère l'exécution réelle de Hashcat en ligne de commande."""
    
    def __init__(self):
        self.session_name = f"prohash_session_{int(time.time())}"
        self.report_gen = ReportGenerator()

    def execute_attack(self, target_hash, hash_mode, wordlist, strategy):
        """Lance l'attaque Hashcat avec la configuration donnée."""
        
        # 1. Création d'un fichier temporaire pour stocker le hash
        fd, temp_hash_path = tempfile.mkstemp(prefix="prohash_", suffix=".txt")
        try:
            with os.fdopen(fd, 'w') as tmp:
                tmp.write(target_hash)
                
            log_info(f"Fichier hash temporaire créé : {temp_hash_path}")
            
            # 2. Construction de la commande Hashcat
            # Format: hashcat -m <mode> -a 0 <hashfile> <wordlist> --session <name>
            
            command = [
                "hashcat",
                "-m", str(hash_mode),
                "-a", "0", # Attack mode 0 = Straight (Wordlist)
                temp_hash_path,
                wordlist,
                "--session", self.session_name,
                "--status-timer", "10", # Mise à jour auto de l'affichage
                "--status"
            ]
            
            # Ajout du fichier de règles si spécifié par la stratégie
            rule_file = strategy.get("rule_file")
            if rule_file and os.path.exists(rule_file):
                log_info(f"Attachement de la règle Hashcat: {rule_file}")
                command.extend(["-r", rule_file])
                
            print(f"\n[+] Commande générée : {' '.join(command)}")
            print("[!] Exécution de Hashcat en cours. Appuyez sur 'q' pour quitter, 's' pour le statut.\n")
            
            start_time = time.time()
            
            # 3. Exécution avec interaction dans le terminal
            process = subprocess.Popen(command)
            process.wait() # Attend la fin du processus Hashcat
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 4. Vérification des résultats (Récupération du mot de passe)
            if process.returncode in [0, 1]:  # Hashcat retourne 0 (succès) ou 1 (épuisé)
                self._check_result(target_hash, hash_mode, duration)
            elif process.returncode == -2:
                print("\n[!] Attaque mise en pause par l'utilisateur.")
                print(f"[i] Pour reprendre plus tard, utilisez : hashcat --session {self.session_name} --restore")
            else:
                log_error(f"Hashcat s'est terminé avec le code d'erreur: {process.returncode}")
                
        finally:
            # 5. Nettoyage sécurisé du fichier hash
            if os.path.exists(temp_hash_path):
                os.remove(temp_hash_path)
                log_info("Fichier hash temporaire nettoyé.")

    def _check_result(self, target_hash, hash_mode, duration):
        """Utilise 'hashcat --show' pour vérifier si le hash a été cracké et générer le rapport."""
        try:
            show_command = ["hashcat", "-m", str(hash_mode), "--show", target_hash]
            result = subprocess.run(show_command, capture_output=True, text=True)
            output = result.stdout.strip()
            
            if output:
                # Le format de --show est généralement "hash:password"
                parts = output.split(":")
                if len(parts) >= 2:
                    cracked_password = parts[-1]
                    print("\n" + "="*50)
                    print("🎉 [SUCCÈS] HASH CRACKÉ ! 🎉")
                    print(f"Mot de passe trouvé : \033[92m{cracked_password}\033[0m")
                    print("="*50 + "\n")
                    
                    # Génération du rapport
                    report_path = self.report_gen.generate_success_report(target_hash, cracked_password, duration)
                    print(f"[i] Rapport d'attaque sauvegardé : {report_path}")
                else:
                    print(output)
            else:
                print("\n[-] Échec : Le mot de passe n'a pas été trouvé dans ce dictionnaire.")
                
        except Exception as e:
            log_error(f"Erreur lors de la vérification du résultat : {e}")
