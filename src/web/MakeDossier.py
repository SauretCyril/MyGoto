import os
import json
import shutil
import sys
from pathlib import Path
from tkinter import Tk, filedialog
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent))
current_dir = os.getcwd()
print("Dossier courant:", current_dir)
from py.function3 import read_annonces_json
exit()

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()
# Récupérer le répertoire parent à partir du fichier .env
parent_dir = os.getenv('ANNONCES_FILE_DIR')
print ("parent_dir",parent_dir)

# Si le répertoire parent n'est pas défini dans le fichier .env, demander la sélection du répertoire parent
""" if not parent_dir:
    parent_dir = filedialog.askdirectory(title="Sélectionnez le répertoire parent") """
# Charger les annonces
annonces = read_annonces_json()
# Récupérer le nombre d'annonces
nombre_annonces = len(annonces)
print(f"Nombre d'annonces: {nombre_annonces}")

# Créer un nom de répertoire par défaut
default_dir_name = f"M{nombre_annonces:03d}"
print( "default_dir_name",default_dir_name)

# Demander le nom du nouveau répertoire avec une boîte de dialogue
#dir_name = simpledialog.askstring("Nom du répertoire", f"Entrez le nom du nouveau répertoire (par défaut: {default_dir_name}): ", initialvalue=default_dir_name)

# Créer le chemin complet du nouveau répertoire
new_dir_path = os.path.join(parent_dir, default_dir_name)
print("Creating new directory at",new_dir_path)

# Créer le nouveau répertoire
#os.makedirs(new_dir_path, exist_ok=True)
""" 
# Créer un fichier JSON dans le nouveau répertoire
json_file_path = os.path.join(new_dir_path, 'data.json')
with open(json_file_path, 'w') as json_file:
    json.dump({}, json_file)

# Demander la sélection du fichier à copier
file_to_copy = filedialog.askopenfilename(title="Sélectionnez le fichier à copier")

# Copier le fichier dans le nouveau répertoire
shutil.copy(file_to_copy, new_dir_path)

print(f"Répertoire '{new_dir_path}' créé avec succès, fichier JSON créé et fichier '{file_to_copy}' copié.") """
