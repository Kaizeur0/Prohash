import os
import time
from datetime import datetime

class ReportGenerator:
    """Génère un rapport texte après une attaque Hashcat réussie."""
    
    def __init__(self, reports_dir="./reports"):
        self.reports_dir = reports_dir
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def generate_success_report(self, target_hash, password, duration_seconds):
        """Crée un fichier Markdown résumant l'attaque."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"success_report_{timestamp}.md"
        filepath = os.path.join(self.reports_dir, filename)
        
        formatted_duration = time.strftime('%H:%M:%S', time.gmtime(duration_seconds))
        
        content = f"""# ✅ Rapport de Crack ProHash

## 📋 Informations du Hash
- **Hash Original** : `{target_hash}`
- **Mot de Passe en clair** : `{password}`

## ⏱️ Statistiques
- **Date de fin** : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Temps total d'exécution** : {formatted_duration}

---
*Généré automatiquement par ProHash - L'Assistant Hashcat Intelligent*
"""
        
        with open(filepath, "w") as f:
            f.write(content)
            
        return filepath
