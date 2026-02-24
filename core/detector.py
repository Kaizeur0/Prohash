import json
import re
import os
from utils.logger import log_info, log_error
from core.hashcat_integration import HashcatIntegration

class HashDetector:
    """Détecte le type d'un hash basé sur la longueur, les caractères, etc."""
    
    def __init__(self, signatures_file="./database/hash_signatures.json"):
        self.signatures_file = signatures_file
        self.signatures = {}
        self.hc_integration = HashcatIntegration()
        self._load_signatures()

    def _load_signatures(self):
        """Charge les signatures (regex) depuis la base de données JSON"""
        if not os.path.exists(self.signatures_file):
            log_error(f"Fichier de signatures introuvable : {self.signatures_file}")
            return
            
        try:
            with open(self.signatures_file, "r") as f:
                 self.signatures = json.load(f)
            log_info(f"{len(self.signatures)} signatures de hash chargées.")
        except json.JSONDecodeError:
             log_error(f"Fichier JSON invalide : {self.signatures_file}")
             
    def detect(self, hash_string):
        """
        Identifie le type probable d'un hash fourni.
        Retourne une liste de candidats potentiels triée par pertinence.
        """
        hash_string = hash_string.strip()
        candidates = []
        
        for name, info in self.signatures.items():
            pattern = info.get("pattern", "")
            
            # Utilisation de booléen: il faut au moins qu'il y ait un pattern et un match
            if pattern and re.match(pattern, hash_string):
                hc_mode = str(info.get("hashcat_mode", ""))
                hc_info = self.hc_integration.get_mode_info(hc_mode)
                
                description = info.get("description", "Pas de description")
                if hc_info:
                    description = f"{hc_info['name']} ({hc_info['category']})"
                
                candidate_info = {
                    "name": name,
                    "hashcat_mode": hc_mode,
                    "description": description
                }
                candidates.append(candidate_info)
                
        if candidates:
            log_info(f"Détection terminée : {len(candidates)} candidat(s) trouvé(s).")
            # Dans un cas réel complexe, on pourrait trier les candidats (ex. probabilité selon un algorithme)
            # Ici on retourne simplement la liste.
            return candidates
        else:
            log_info("Aucun candidat ne correspond à ce format de hash.")
            return []
