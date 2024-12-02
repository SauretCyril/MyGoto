import json
import os
from dotenv import load_dotenv
from py.function3 import read_annonces_json
from glob import glob
import shutil

def get_new_name(num):
    #Charger les variables d'environnement à partir du fichier .env
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
    nombre_annonces = len(annonces)+1
    print(f"Nombre d'annonces: {nombre_annonces}")

    # Créer un nom de répertoire par défaut
    default_dir_name = f"M4{nombre_annonces:2d}"
    print( "default_dir_name",default_dir_name)

    # Demander le nom du nouveau répertoire avec une boîte de dialogue
    #dir_name = simpledialog.askstring("Nom du répertoire", f"Entrez le nom du nouveau répertoire (par défaut: {default_dir_name}): ", initialvalue=default_dir_name)

    # Créer le chemin complet du nouveau répertoire
    new_dir_path = os.path.join(parent_dir, num)
    print("Creating new directory at",new_dir_path)
    return new_dir_path
    
def find_annonce_by_id(annonces, id):
    """
    Find an annonce by its ID and return the key and description in the required format.
    
    :param annonces: List of annonces
    :param id: ID of the annonce to find
    :return: Tuple of (key, description) of the found annonce or (None, None) if not found
    """
    for annonce in annonces:
        for key, value in annonce.items():
            if value.get('id') == id:
                print("Found annonce with ID", key)
                parent_directory = os.path.dirname(key)
                description = value.get('description', 'No description available')
                return parent_directory, description

    return None, None

def get_new_dir(annonces):
    load_dotenv()
    parent_dir = os.getenv('ANNONCES_FILE_DIR')
    print ("parent_dir",parent_dir)
    
    nombre_annonces = len(annonces)+1
    print(f"Nombre d'annonces: {nombre_annonces}")

    # Créer un nom de répertoire par défaut
    default_dir_name = f"M4{nombre_annonces:2d}"
    new_dir_path = os.path.join(parent_dir, default_dir_name)
   
    return new_dir_path, default_dir_name

# Example usage
# make_dossier("M404")
annonces = read_annonces_json()
newdir, default_dir_name = get_new_dir(annonces)
print("default_dir_name", default_dir_name)

if not os.path.exists(newdir):
    os.makedirs(newdir, exist_ok=True)

dir, description = find_annonce_by_id(annonces, "M404")
print("dir", dir)
if dir:
    print("Directory found")
    print("Description:", description)
    # Retrieve .docx files in the directory
    docx_files = glob(os.path.join(dir, "*.docx"))
    if docx_files:
        # Find the most recent .docx file
        most_recent_docx = max(docx_files, key=os.path.getmtime)
        print("Most recent .docx file:", most_recent_docx)
        
        # Duplicate the file into the new directory and rename it
        new_file_name = f"{default_dir_name}_{description}.docx"
        new_file_path = os.path.join(newdir, new_file_name)
        #shutil.copy2(most_recent_docx, new_file_path)
        print("Duplicated and renamed file:", new_file_path)
    else:
        print("No .docx files found in the directory")
else :
    print("Directory not found")
    

# directory = find_annonce_directory(annonces, 123)
# print(directory)