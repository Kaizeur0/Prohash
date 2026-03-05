import sys
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.progress import track
import inquirer
import time

from core.detector import HashDetector
from core.hardware_checker import HardwareChecker
from core.dependency_checker import DependencyChecker
from core.strategy_engine import StrategyEngine
from core.executor import HashcatExecutor
from core.custom_attacks import InjectedSaltAttack
from ui.teaching_module import TeachingModule
from utils.wordlist_manager import WordlistManager
from utils.logger import log_info, log_error

console = Console()

def print_header():
    console.clear()
    console.print(Panel("[bold green]ProHash[/bold green] - L'Assistant Hashcat Intelligent", expand=False))

def interactive_mode():
    """Démarre le mode interactif principal de ProHash."""
    
    # 1. Vérification des dépendances 
    console.print("[yellow][*] Vérification du système...[/yellow]")
    dep_checker = DependencyChecker()
    dep_checker.check_all()
    
    hw_checker = HardwareChecker()
    hw_info = hw_checker.get_hardware_info()
    console.print(f"[green][+] Système prêt. CPU cœurs: {hw_info['cpu_cores']} | RAM: {hw_info['ram_total_gb']} Go[/green]")
    
    # Menu principal
    questions = [
        inquirer.List('action',
                      message="Choisissez votre mode d'utilisation",
                      choices=[
                          'Mode Apprentissage (Facile - avec explications)',
                          'Mode Pro (Expert - direct)',
                          'Quitter'
                      ],
                  ),
    ]
    
    answers = inquirer.prompt(questions)
    
    if not answers or answers['action'] == 'Quitter':
         console.print("Au revoir !")
         sys.exit(0)
         
    is_pro_mode = (answers['action'] == 'Mode Pro (Expert - direct)')
    
    start_hash_analysis(hw_info, is_pro_mode)


def start_hash_analysis(hw_info, is_pro_mode=False):
    """Gère le workflow d'analyse d'un seul hash."""
    
    console.print("\n")
    user_hash = Prompt.ask("[bold blue]Entrez le hash à analyser[/bold blue]")
    
    if not user_hash:
        return
        
    # 2. Détection du Hash
    detector = HashDetector()
    candidates = detector.detect(user_hash)
    
    if not candidates:
        console.print(Panel("[red]Impossible d'identifier l'algorithme ce hash avec nos signatures actuelles.[/red]"))
        return
        
    # Affiche le module pédagogique seulement si on n'est PAS en mode Pro
    if not is_pro_mode:
        teacher = TeachingModule()
        teacher.explain_hash(candidates)
        
    best_candidate = candidates[0]
    
    # 3. Moteur de Stratégie
    strategy_engine = StrategyEngine()
    strategy = strategy_engine.select_strategy(best_candidate, hw_info)
    
    # 4. Choix de la wordlist
    wordlist_mgr = WordlistManager()
    selected_wordlist = wordlist_mgr.select_wordlist()
    
    if not selected_wordlist:
        console.print("[red]Attaque annulée (aucune wordlist sélectionnée).[/red]")
        return
    
    # Mapping des modes supportés par l'injection de sel dynamique
    supported_custom_attacks = {
        '0': 'md5',
        '100': 'sha1',
        '1400': 'sha256',
        '1700': 'sha512'
    }

    attack_type = "Hashcat"
    custom_algo = None
    
    if best_candidate['hashcat_mode'] in supported_custom_attacks:
        custom_algo = supported_custom_attacks[best_candidate['hashcat_mode']]
        console.print(f"\n[bold yellow][i] Info:[/i] Ce hash ({custom_algo.upper()}) est éligible à l'attaque 'Injected Salt Hybrid' 100% CPU de ProHash.[/bold yellow]")
        attack_choice = inquirer.prompt([
            inquirer.List('type',
                message="Quelle méthode d'attaque utiliser ?",
                choices=[
                    "Hashcat (Dictionnaire standard - GPU recommandé)",
                    "Injection de Sel ProHash (Multicore CPU)"
                ]
            )
        ])
        if attack_choice and "Injection de Sel" in attack_choice['type']:
            attack_type = "Injected Salt"

    console.print("\n[bold]Résumé avant exécution:[/bold]")
    console.print(f"- [cyan]Algorithme cible[/cyan] : {best_candidate['name']} (Mode {best_candidate['hashcat_mode']})")
    
    if attack_type == "Hashcat":
        console.print(f"- [cyan]Stratégie[/cyan] : {strategy['description']}")
    else:
        console.print(f"- [cyan]Stratégie[/cyan] : Injected Salt Hybrid Custom Attack")
        
    console.print(f"- [cyan]Wordlist[/cyan] : {selected_wordlist}")
    
    # Confirmation interactive
    confirm = inquirer.prompt([
        inquirer.Confirm('proceed', message="Démarrer l'attaque ?", default=True)
    ])
    
    if confirm and confirm['proceed']:
        
         if attack_type == "Injected Salt":
             console.print("\n[green]Démarrage de l'attaque Injected Salt Custom...[/green]")
             attack = InjectedSaltAttack(target_hash=user_hash, wordlist_path=selected_wordlist, algorithm=custom_algo)
             start_time = time.time()
             result = attack.execute()
             elapsed = time.time() - start_time
             console.print(f"\n[*] Attaque terminée en {elapsed:.2f} secondes.")
             
             if result:
                 console.print(f"\n[bold green][+] SUCCESS: Le mot de passe est -> {result}[/bold green]")
             else:
                 console.print("\n[bold red][-] ECHEC: Mot de passe non trouvé dans la wordlist avec cette méthode.[/bold red]")
             console.print("\n[bold green]FIN DE L'OPÉRATION.[/bold green]")
             return
             
         console.print("\n[green]Démarrage de l'attaque Hashcat...[/green]")
         
         # Si le candidat est un JWT, on extrait le format Hashcat depuis le JWT brut
         attack_hash = user_hash
         if best_candidate['hashcat_mode'] == '16500':
             from core.jwt_extractor import JWTExtractor
             from rich.progress import Progress
             
             with Progress() as progress:
                 task = progress.add_task("[cyan]Extraction de la signature HMAC du JWT...", total=100)
                 time.sleep(0.5) # Effet visuel
                 extractor = JWTExtractor()
                 extracted_data = extractor.extract(user_hash)
                 progress.update(task, completed=100)
                 
             if extracted_data:
                 attack_hash = extracted_data['token']
                 console.print(f"[+] Token extrait avec succès pour Hashcat.")
             else:
                 console.print("[red]Impossible d'extraire les données du JWT. Annulation.[/red]")
                 return

         executor = HashcatExecutor()
         executor.execute_attack(
             target_hash=attack_hash,
             hash_mode=best_candidate['hashcat_mode'],
             wordlist=selected_wordlist,
             strategy=strategy
         )
         console.print("\n[bold green]FIN DE L'OPÉRATION.[/bold green]")





def start_cli():
    """Point d'entrée principal de l'interface."""
    print_header()
    interactive_mode()
