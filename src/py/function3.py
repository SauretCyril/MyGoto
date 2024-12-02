import eel
import json
import os
from dotenv import load_dotenv
#import asyncio  # Add this import
import platform
import subprocess
import shutil  # Add this import

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
            #print (parent_dir)
            for filename in files:
                file_path = os.path.join(root, filename)
                file_path = file_path.replace('\\', '/')  # Normalize path
                #filename.endswith(".json")  and 
                if  filename==".data.json":
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)
                            if not data['etat']=="DELETED":
                                data["dossier"] = parent_dir  # Add parent directory name to data
                                #if not data['etat']=="DELETED":
                                jData={ file_path: data}
                                #print(f"fichier {file_path}")
                                annonces_list.append(jData)

                    except json.JSONDecodeError:
                        errordata={"id":parent_dir,"description":"?","etat":"invalid JSON"}
                        #jData={ file_path: errordata}
                        #annonces_list.append(jData)
                        print(f"Error: The file {file_path} contains invalid JSON.")
                        #print(f"row {jData}")
                
                """  else:
                    print(f"{file_path} n'est pas un fichier d'annonce")   """                  
        #annonces_list = update_annonces_with_qa( annonces_list)
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
                #print(f"file saved {file}")
    except Exception as e:
        print(f"An unexpected error occurred while saving data: {e}")

@eel.expose
def openUrl(url):
    import webbrowser
    webbrowser.open(url)
    
def dirExits(dir):
    directory_path = f'G:/OneDrive/Entreprendre/Actions/{dir}'

    # Vérifier si le répertoire existe
    if not os.path.exists(directory_path):
        """ # Créer le répertoire
        os.makedirs(directory_path)
        print(f'Répertoire {directory_path} créé.') """
        return False;
    else:
        return True;

""" def isWordExist(file):
     """
     
     
     
@eel.expose
def save_filters_json(filters,tabactiv):
    #file_path = os.getenv("ANNONCES_FILE_FILTER")
    file_path = os.path.join(os.getenv("ANNONCES_DIR_FILTER"),tabactiv+"_filter")+".json"
    file_path = file_path.replace('\\', '/')  # Normalize path
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(filters, file, ensure_ascii=False, indent=4)
            #print(f"Filter values successfully saved to {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred while saving filter values: {e}")

@eel.expose
def read_filters_json(tabactiv):
    try:
        file_path = os.path.join(os.getenv("ANNONCES_DIR_FILTER"),tabactiv+"_filter")+".json"
        #print(f"Reading filter values from {file_path}")
        file_path = file_path.replace('\\', '/')  # Normalize path
        if not os.path.exists(file_path):
            return {}
        with open(file_path, 'r', encoding='utf-8') as file:
            filters = json.load(file)
            return filters  # Return dictionary directly
    except Exception as e:
        print(f"An unexpected error occurred while reading filter values: {e}")
        return {}
    
"""   
tmp=read_annonces_json()g
print(tmp) """

@eel.expose
def get_status_qualif(annonce, rowId):  # Make the function asynchronous
    result = []
   
    annonce_dict = json.loads(annonce)  # Convert JSON string to dictionary
    id = annonce_dict.get('id')
    # vérifier que le num id du fichier est bien le même que le le début du nom du répertoire
    
    parent_directory = os.path.dirname(rowId)  # Get the parent directory of rowId
    
    if os.path.exists(rowId) and os.path.basename(rowId).startswith(id):
        result.append({"nom_fichier": True})
    else:
        result.append({"nom_fichier": False}) 
    
    #il doit y avoir un fichier docx dans le répertoire 
    docx_files = [f for f in os.listdir(parent_directory) if f.endswith('.docx') and id in f]
    if os.path.exists(rowId) and docx_files:
        result.append({"fichier_docx": True})
    else:
        result.append({"fichier_docx": False})
    
    #il y a un fichier pdf dans le répertoire 
    pdf_files = [f for f in os.listdir(parent_directory) if f.endswith('.pdf') and id in f]
    if os.path.exists(rowId) and pdf_files:
        result.append({"fichier_pdf": True})
    else:
        result.append({"fichier_pdf": False})
                
    return json.dumps(result) 

""" @eel.expose
def update_annonces_with_qa(annonces_list):
    #annonces_list = read_annonces_json()
    for annonce in annonces_list:
        for file_path, data in annonce.items():
            annonce_json = json.dumps(data)
            row_id = file_path  # Assuming rowId is the file path
            qa_status = get_status_qualif(annonce_json, row_id)
            data['status'] = json.loads(qa_status)
    
#save_annonces_json(annonces_list)
    return annonces_list """

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

""" 
@eel.expose
def openFile(file_path):
    try:
        file_path = file_path.replace('\\', '/')  # Normalize path
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', file_path])
        else:  # Linux
            subprocess.run(['xdg-open', file_path])
        return True
    except Exception as e:
        print(f"Error opening file: {e}")
        return False """
        
        
@eel.expose        
def save_config_col(cols,tabactiv):
   
    file_path = os.path.join(os.getenv("ANNONCES_DIR_FILTER"),tabactiv+"_colums")+".json"
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
    """
    Check if a file exists at the given path.
    
    Args:
        file_path (str): Path to the file to check
        
    Returns:
        bool: True if file exists, False otherwise
    """
    return os.path.isfile(file_path)