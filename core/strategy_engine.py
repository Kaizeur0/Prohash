import json
import os
from utils.logger import log_info, log_error

class StrategyEngine:
    """Sélectionne le meilleur profil d'attaque en fonction d'un hash et du matériel."""
    
    def __init__(self, profiles_file="./database/attack_profiles.json"):
        self.profiles_file = profiles_file
        self.profiles = {}
        self._load_profiles()

    def _load_profiles(self):
        """Charge les profils d'attaque depuis la base de données JSON"""
        if not os.path.exists(self.profiles_file):
            log_error(f"Fichier de profils d'attque introuvable : {self.profiles_file}")
            return
            
        try:
            with open(self.profiles_file, "r") as f:
                 self.profiles = json.load(f)
            log_info(f"{len(self.profiles)} profils d'attaque chargés.")
        except json.JSONDecodeError:
             log_error(f"Fichier JSON invalide : {self.profiles_file}")

    def select_strategy(self, hash_type_info, hw_info):
        """
        Analyse l'environnement et sélectionne une stratégie.
        hash_type_info: Dictionnaire avec name, hashcat_mode
        hw_info: Dictionnaire avec le checking hardware
        """
        # Ex: si un hash a besoin de beaucoup de puissance (comme bcrypt) 
        # on orientera vers un profil différent si pas de GPU.
        
        try:
            mode = int(hash_type_info.get("hashcat_mode", 0))
        except ValueError:
            mode = 0
            
        has_gpu = hw_info.get("gpu_acceleration", False)
        
        log_info(f"Analyse de la stratégie pour le mode {mode} (GPU: {has_gpu})")
        
        # Logique simplifiée : si c'est un format lourd (mode >= 1000) et qu'on a un GPU
        # On peut tenter des règles complexes. Sinon on reste sur du rapide.
        
        if mode >= 1000 and has_gpu:
             # Profil orienté puissance de calcul
             strategy = self.profiles.get("complex", {"description": "Complexe"})
        else:
             # Profil de base
             strategy = self.profiles.get("rapid", {"description": "Rapide (Dictionnaire simple)"})
             
        # Recherche d'une règle commune (standard Kali/Parrot)
        rule_path = "/usr/share/hashcat/rules/best64.rule"
        if os.path.exists(rule_path) and mode >= 100: # On n'utilise pas de règles pour des choses trop simples comme MD5 pur
             strategy["rule_file"] = rule_path
             strategy["description"] += " + Règle best64"
             
        if not strategy:
            # Fallback en cas de corruption de JSON
            strategy = {"method": "wordlist", "rules": [], "description": "Stratégie par défaut (rabback)"}
            
        log_info(f"Stratégie sélectionnée : {strategy.get('description', 'Par défaut')}")
        return strategy
