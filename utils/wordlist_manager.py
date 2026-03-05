"""Module pour la gestion et la sélection des wordlists système et custom."""
import os
import inquirer
from utils.logger import log_info

class WordlistManager:
    """Gère la détection et la sélection des wordlists."""
    
    DEFAULT_WORDLISTS = [
        "/usr/share/wordlists/rockyou.txt",
        "/usr/share/wordlists/rockyou.txt.gz",
        "/usr/share/dict/words",
        "/usr/share/wordlists/dirb/common.txt",
        "/usr/share/wordlists/dirbuster/directory-list-2.3-small.txt"
    ]
    
    def __init__(self):
        self.system_wordlists = self._detect_wordlists()

    def _detect_wordlists(self):
        """Cherche les wordlists communes sur le système."""
        found = []
        for path in self.DEFAULT_WORDLISTS:
            if os.path.exists(path):
                found.append(path)
        return found

    def select_wordlist(self):
        """Interface interactive pour la sélection de wordlist."""
        if not self.system_wordlists:
            log_info("Aucune wordlist par défaut trouvée sur ce système.")
            return self._prompt_custom_wordlist()
            
        print("\n[+] Wordlists par défaut trouvées sur votre système :")
        for wl in self.system_wordlists:
            print(f"    - {wl}")
            
        choices = self.system_wordlists + ["[+] Spécifier un autre chemin personnalisé", "[-] Quitter"]
        
        questions = [
            inquirer.List(
                'wordlist',
                message="Sélectionnez une wordlist à utiliser",
                choices=choices
            )
        ]
        
        answers = inquirer.prompt(questions)
        
        if not answers or answers['wordlist'] == "[-] Quitter":
            return None
            
        if answers['wordlist'] == "[+] Spécifier un autre chemin personnalisé":
            return self._prompt_custom_wordlist()
            
        return answers['wordlist']

    def _prompt_custom_wordlist(self):
        """Demande manuellement un chemin vers une wordlist."""
        questions = [
            inquirer.Text('path', message="Entrez le chemin absolu vers votre wordlist")
        ]
        
        while True:
            answers = inquirer.prompt(questions)
            if not answers or not answers['path']:
                print("\n[-] Opération annulée.")
                return None
                
            path = answers['path'].strip()
            if os.path.exists(path) and os.path.isfile(path):
                return path
            
            print(f"\n[!] Le fichier '{path}' n'existe pas ou n'est pas un fichier valide. Veuillez réessayer.")
