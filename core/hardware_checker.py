import psutil
import subprocess
import os
from utils.logger import log_info, log_error

class HardwareChecker:
    """Examine les composants matériels (CPU, RAM, GPU/OpenCL)."""
    
    def __init__(self):
        self.hardware_info = {
            "cpu_cores": 0,
            "cpu_freq": 0.0,
            "ram_total_gb": 0.0,
            "ram_available_gb": 0.0,
            "gpu_acceleration": False,
            "gpu_details": []
        }

    def _check_cpu(self):
        """Récupère les informations CPU."""
        try:
            self.hardware_info["cpu_cores"] = psutil.cpu_count(logical=True)
            freq = psutil.cpu_freq()
            if freq:
                self.hardware_info["cpu_freq"] = round(freq.max / 1000, 2)  # en GHz
            log_info(f"CPU détecté : {self.hardware_info['cpu_cores']} coeurs.")
        except Exception as e:
            log_error(f"Erreur lors de la détection CPU : {e}")

    def _check_ram(self):
        """Récupère les informations de la mémoire vive (RAM)."""
        try:
            mem = psutil.virtual_memory()
            self.hardware_info["ram_total_gb"] = round(mem.total / (1024 ** 3), 2)
            self.hardware_info["ram_available_gb"] = round(mem.available / (1024 ** 3), 2)
            log_info(f"RAM détectée : {self.hardware_info['ram_total_gb']} Go au total.")
        except Exception as e:
             log_error(f"Erreur lors de la détection RAM : {e}")

    def _check_gpu_hashcat(self):
        """Utilise Hashcat pour détecter les GPUs compatibles (OpenCL/CUDA)."""
        hashcat_path = os.getenv("HASHCAT_PATH", "hashcat")
        try:
            # On lance hashcat -I pour lister les devices
            result = subprocess.run(
                [hashcat_path, "-I"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Device" in line and "Type" in line and "GPU" in line:
                        self.hardware_info["gpu_acceleration"] = True
                        self.hardware_info["gpu_details"].append(line.strip())
            
            if self.hardware_info["gpu_acceleration"]:
                log_info(f"Accélération matérielle GPU détectée.")
            else:
                 log_info(f"Aucune accélération matérielle GPU détectée par Hashcat. Utilisation du CPU.")
                 
        except FileNotFoundError:
            log_error("Hashcat n'est pas installé ou introuvable dans le PATH.")
        except subprocess.TimeoutExpired:
            log_error("La détection GPU avec Hashcat a expiré.")
        except Exception as e:
            log_error(f"Erreur inattendue lors de la vérification GPU: {e}")

    def get_hardware_info(self):
        """Lance l'ensemble des vérifications et retourne le dictionnaire."""
        log_info("Démarrage de l'analyse matérielle...")
        self._check_cpu()
        self._check_ram()
        self._check_gpu_hashcat()
        return self.hardware_info
