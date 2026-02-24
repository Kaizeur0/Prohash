import subprocess
import re
from utils.logger import log_info, log_error

class HashcatIntegration:
    """Gère l'intégration avec Hashcat, y compris la récupération dynamique des modes."""
    
    def __init__(self):
        self.hash_modes = {}
        self._load_hash_modes()

    def _load_hash_modes(self):
        """Exécute hashcat -hh et extrait les modes supportés."""
        try:
            result = subprocess.run(["hashcat", "-hh"], capture_output=True, text=True, check=True)
            output = result.stdout
            
            # Analyse l'affichage de hashcat pour extraire les modes
            # Le format général est: "  900 | MD4                                                      | Raw Hash"
            mode_pattern = re.compile(r"^\s*(\d+)\s*\|\s*([^|]+)\s*\|\s*(.*)$")
            
            in_hash_modes = False
            for line in output.split('\n'):
                if "- [ Hash Modes ] -" in line or "- [ Hash modes ] -" in line:
                    in_hash_modes = True
                    continue
                
                if in_hash_modes:
                    if line.startswith("- ["):
                        break # Fin de la section des modes hash
                    
                    match = mode_pattern.match(line)
                    if match:
                        mode_id = match.group(1).strip()
                        mode_name = match.group(2).strip()
                        category = match.group(3).strip()
                        self.hash_modes[mode_id] = {
                            "name": mode_name,
                            "category": category
                        }
            log_info(f"{len(self.hash_modes)} modes Hashcat chargés dynamiquement.")
        except FileNotFoundError:
            log_error("Hashcat n'est pas installé ou n'est pas dans le PATH.")
        except subprocess.CalledProcessError as e:
            log_error(f"Erreur lors de l'exécution de Hashcat: {e}")
        except Exception as e:
            log_error(f"Erreur inattendue lors du chargement des modes Hashcat: {e}")

    def get_mode_info(self, mode_id):
        """Retourne les informations sur un mode spécifique."""
        return self.hash_modes.get(str(mode_id))
        
    def get_all_modes(self):
        return self.hash_modes
