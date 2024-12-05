import eel
import json
import os
from dotenv import load_dotenv
#import asyncio  # Add this import
import platform
import subprocess
import shutil  # Add this import

from .qa import  get_info  # Use absolute imports
# Define the path to the JSON file

load_dotenv()
@eel.expose
def read_annonces_json():
    try:
        directory_path = os.getenv("ANNONCES_FILE_DIR")
        if not os.path.exists(directory_path):
            return []

        annonces_list = []
       
        for root, _, files in os.walk(directory_path):
            parent_dir = os.path.basename(root)
            file_annonce = parent_dir + "_annonce_.pdf"
            record_added = False
            data = {}
            for filename in files:
                file_path = os.path.join(root, filename)
                file_path = file_path.replace('\\', '/')  # Normalize path
               
                if filename == ".data.json":
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            if not data['etat'] == "DELETED":
                                data["dossier"] = parent_dir  # Add parent directory name to data
                                jData = {file_path: data}
                                annonces_list.append(jData)
                            record_added = True

                    except json.JSONDecodeError:
                        errordata = {"id": parent_dir, "description": "?", "etat": "invalid JSON"}
                        print(f"Error: The file {file_path} contains invalid JSON.")
            
            if not record_added:
                for filename in files:
                    file_path = os.path.join(root, filename)
                    file_path = file_path.replace('\\', '/')  # Normalize path
                    file_annonce = parent_dir + "_annonce_.pdf"
                    file_annonce_path = os.path.join(root, ".data.json")
                    if filename == file_annonce:
                        Data = define_default_data()     
                        Data["dossier"] = parent_dir
                        Data["etat"] = "gpt"
                        
                        try: 
                            infos = get_info(file_path, "peux tu me trouver l'url de l'annonce ( elle se trouve entre <- et ->)  [url], l'entreprise [entreprise], le titre du poste [poste] (ce titre ne doit pas dépasser 20 caractère)")
                            infos = json.loads(infos)  # Parse the JSON response
                            if infos:
                                Data["url"] = infos["url"]
                                Data["entreprise"] = infos["entreprise"]
                                Data["description"] = infos["poste"]
                                record_added = True  
                                Data["etat"] = "New"
                                jData = {file_annonce_path: Data}   
                                annonces_list.append(jData)
                            else:
                                record_added = True  
                                Data["etat"] = "Vide"
                                jData = {file_annonce_path: Data}   
                                annonces_list.append(jData)
                               
                        except Exception as e:
                            print(f"An unexpected error occurred get infos with gpt: {e}")
                            record_added = True  
                            Data["etat"] = "Error"
                            jData = {file_annonce_path: Data}   
                            annonces_list.append(jData)
                    if record_added: break
                                
        return annonces_list 
    except Exception as e:
        print(f"An unexpected error occurred while reading annonces: {e}")
        return []

@eel.expose
def save_annonces_json(data):
    try:
        for item in data:
            for file_path, content in item.items():
                file_path = file_path.replace('\\', '/')  # Normalize path
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(content, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"An unexpected error occurred while saving data: {e}")

@eel.expose
def openUrl(url):
    import webbrowser
    webbrowser.open(url)
    
def dirExits(dir):
    directory_path = f'G:/OneDrive/Entreprendre/Actions/{dir}'

    if not os.path.exists(directory_path):
        return False
    else:
        return True

@eel.expose
def save_filters_json(filters, tabactiv):
    file_path = os.path.join(os.getenv("ANNONCES_DIR_FILTER"), tabactiv + "_filter") + ".json"
    file_path = file_path.replace('\\', '/')  # Normalize path
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(filters, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"An unexpected error occurred while saving filter values: {e}")

@eel.expose
def read_filters_json(tabactiv):
    try:
        file_path = os.path.join(os.getenv("ANNONCES_DIR_FILTER"), tabactiv + "_filter") + ".json"
        file_path = file_path.replace('\\', '/')  # Normalize path
        if not os.path.exists(file_path):
            return {}
        with open(file_path, 'r', encoding='utf-8') as file:
            filters = json.load(file)
            return filters  # Return dictionary directly
    except Exception as e:
        print(f"An unexpected error occurred while reading filter values: {e}")
        return {}

@eel.expose
def get_status_qualif(annonce, rowId):
    result = []
   
    annonce_dict = json.loads(annonce)  # Convert JSON string to dictionary
    id = annonce_dict.get('id')
    
    parent_directory = os.path.dirname(rowId)  # Get the parent directory of rowId
    
    if os.path.exists(rowId) and os.path.basename(rowId).startswith(id):
        result.append({"nom_fichier": True})
    else:
        result.append({"nom_fichier": False}) 
    
    docx_files = [f for f in os.listdir(parent_directory) if f.endswith('.docx') and id in f]
    if os.path.exists(rowId) and docx_files:
        result.append({"fichier_docx": True})
    else:
        result.append({"fichier_docx": False})
    
    pdf_files = [f for f in os.listdir(parent_directory) if f.endswith('.pdf') and id in f]
    if os.path.exists(rowId) and pdf_files:
        result.append({"fichier_pdf": True})
    else:
        result.append({"fichier_pdf": False})
                
    return json.dumps(result)

@eel.expose
def open_parent_directory(file_path):
    try:
        parent_directory = os.path.dirname(file_path)
        parent_directory = parent_directory.replace('\\', '/')  # Normalize path
        if platform.system() == 'Windows':
            os.startfile(parent_directory)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', parent_directory])
        else:  # Linux
            subprocess.run(['xdg-open', parent_directory])
        return True
    except Exception as e:
        print(f"Error opening parent directory: {e}")
        return False

@eel.expose        
def save_config_col(cols, tabactiv):
    file_path = os.path.join(os.getenv("ANNONCES_DIR_FILTER"), tabactiv + "_colums") + ".json"
    file_path = file_path.replace('\\', '/')  # Normalize path
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(cols, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"An unexpected error occurred while saving colums config: {e}")

@eel.expose
def load_config_col(tabactiv):
    try:
        file_path = os.path.join(os.getenv("ANNONCES_DIR_FILTER"), tabactiv + "_colums") + ".json"
        file_path = file_path.replace('\\', '/')  # Normalize path
        if not os.path.exists(file_path):
            return json.dumps([])  # Return empty list if file does not exist
        with open(file_path, 'r', encoding='utf-8') as file:
            conf = json.load(file)
            return json.dumps(conf)  # Return JSON string
    except Exception as e:
        print(f"An unexpected error occurred while reading columns config: {e}")
        return json.dumps([])

@eel.expose
def file_exists(file_path):
    return os.path.isfile(file_path)

def define_default_data():
    return {
        "id": "",
        "description": "?",
        "etat": "Auto",
        "entreprise": "?",
        "categorie": "",
        "Date": "",
        "todo": "?",
        "todoList": "",
        "action": "",
        "tel": "",
        "contact": "",
        "url": "",
        "Commentaire": "",
        "type": "AN",
        "type_question": "pdf"
    }