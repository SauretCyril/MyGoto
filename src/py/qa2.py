from transformers import pipeline
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text













# Charger le modèle et le tokenizer
similarity_pipeline = pipeline("feature-extraction", 
                             model="jjzha/jobbert-base-cased",
                             tokenizer="jjzha/jobbert-base-cased")

# Fonction améliorée pour calculer la similarité cosinus
def cosine_similarity(vec1, vec2):
    # Calculer la moyenne sur l'axe des tokens pour obtenir un vecteur unique par texte
    vec1_mean = np.mean(vec1, axis=0)  # Réduit à (768,)
    vec2_mean = np.mean(vec2, axis=0)  # Réduit à (768,)
    
    # Calculer la similarité cosinus
    similarity = np.dot(vec1_mean, vec2_mean) / (np.linalg.norm(vec1_mean) * np.linalg.norm(vec2_mean))
    return similarity

# Exemple de texte pour l'offre d'emploi et le CV
#job_offer = "Développer les nouvelles fonctionnalités de l'application existante en NextJS..."
#cv_text = "Développement de nouvelles fonctionnalités pour une application web en utilisant React et Next.js..."

job_offer_pdf = "G:\OneDrive\Entreprendre\CV\persona\IngeEtudeDev_Ideal/PRF_Cyril_SAURET_Ingénieur_Développeur_REACT_ideal.pdf"
candidate_profile_pdf = "G:/OneDrive/Entreprendre/Actions-4/M434/M434_annonce_.pdf"
cv_text = extract_text_from_pdf(job_offer_pdf)
job_offer = extract_text_from_pdf(candidate_profile_pdf)

# Extraire les caractéristiques et convertir en tableaux numpy
job_features = np.array(similarity_pipeline(job_offer)[0])  # Ajout de [0] pour obtenir le premier élément
cv_features = np.array(similarity_pipeline(cv_text)[0])     # Ajout de [0] pour obtenir le premier élément

# Calculer la similarité
similarity_score = cosine_similarity(job_features, cv_features)
print(f"Similarity score: {similarity_score}")
