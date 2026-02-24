import os
import shutil
import json
from utils.logger import log_info, log_error

class DependencyChecker:
    """Vérifie que tous les outils requis existent."""
    
    def __init__(self):
        self.status = {
            "hashcat": False,
            "wordlists": False,
            "config_files": False
        }

    def _check_hashcat(self):
        """Vérifie si hashcat est installé dans le PATH système."""
        # On lit la variable d'environnement ou 'hashcat' par défaut
        hc_path = os.getenv("HASHCAT_PATH", "hashcat")
        if shutil.which(hc_path):
            self.status["hashcat"] = True
            log_info("Hashcat a été trouvé sur le système.")
        else:
            log_error(f"Hashcat est INTROUVABLE. Chemin testé : {hc_path}")

    def _check_wordlists(self):
        """Vérifie qu'au moins une wordlist est configurée et accessible."""
        config_path = "./database/wordlists_config.json"
        
        if not os.path.exists(config_path):
            log_error("Fichier de configuration des wordlists manquant.")
            return

        self.status["config_files"] = True
            
        try:
            with open(config_path, "r") as f:
                wordlists = json.load(f)
                
            for name, config in wordlists.items():
                 path = config.get("path", "")
                 if os.path.exists(path):
                     # Au moins une wordlist existe, c'est bon
                     self.status["wordlists"] = True
                     log_info(f"Wordlist trouvée : {name} ({path})")
                     return
                     
            log_error("Aucune wordlist valide n'a été trouvée sur le disque. Veuillez en télécharger une (ex: rockyou.txt).")
        except json.JSONDecodeError:
            log_error(f"Fichier de configuration des wordlists invalide ({config_path}).")
        except Exception as e:
            log_error(f"Erreur inattendue : {e}")

    def check_all(self):
        """Lance l'ensemble des vérifications logicielles."""
        log_info("Démarrage de la vérification des dépendances...")
        self._check_hashcat()
        self._check_wordlists()
        
        all_ok = all(self.status.values() if self.status["config_files"] else [self.status["hashcat"]])
        if all_ok:
             log_info("Toutes les dépendances critiques sont satisfaites.")
        else:
             log_error("Des dépendances sont manquantes. ProHash ne pourra pas fonctionner correctement.")
             
        return all_ok
