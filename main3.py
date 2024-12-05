import eel
import sys
from pathlib import Path
import src.py.function3 as functions3  # Import the function3 module


# Add the parent directory of the current file to the Python path
sys.path.append(str(Path(__file__).parent))

@eel.expose
def handle_question(question):
    try:
        from src.py.qa import get_answer
        return get_answer(question)
    except Exception as e:
        return f"Erreur: {str(e)}"

eel.init("src/web")  # EEL initialization
eel.start("main3.html", size=(1000, 800), port=8080)  # Starting the App on a different port
# eel.start("qa.html", size=(1000, 800))