from rich.console import Console
from rich.panel import Panel

class TeachingModule:
    """Affiche des explications pédagogiques à l'utilisateur."""
    
    def __init__(self):
        self.console = Console()

    def explain_hash(self, candidates):
        """
        Donne un contexte éducatif sur le type de hash détecté.
        candidates est une liste de dict (les retours de HashDetector).
        """
        if not candidates:
            return
            
        best_match = candidates[0]
        name = best_match.get("name", "Inconnu")
        mode = best_match.get("hashcat_mode", "?")
        desc = best_match.get("description", "Pas de description")
        
        text = (
            f"[bold cyan]Le Hash : qu'est-ce que c'est ?[/bold cyan]\n"
            f"Un hash n'est pas un texte chiffré qu'on peut déchiffrer. C'est le résultat d'un calcul "
            f"mathématique à sens unique. Pour le « casser », nous devons deviner différents "
            f"mots de passe jusqu'à ce que l'un d'eux donne le même résultat.\n\n"
            f"[bold underline]Déduction pour ce hash :[/bold underline]\n"
            f"L'algorithme identifié par sa structure semble être le [bold yellow]{name}[/bold yellow] "
            f"(Mode Hashcat: {mode}).\n\n"
            f"[italic]{desc}[/italic]"
        )
        
        panel = Panel(text, title="👨‍🏫 Leçon ProHash", border_style="cyan", padding=(1, 2))
        self.console.print(panel)
