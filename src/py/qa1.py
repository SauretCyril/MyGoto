import eel
from PyPDF2 import PdfReader
from transformers import pipeline
import numpy as np
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def split_text(text, max_length=512):
    # Diviser le texte en morceaux de longueur maximale
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

def preprocess_text(text):
    # Nettoyage basique
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    
    # Utilisation de spaCy pour le traitement linguistique
    nlp = spacy.load('fr_core_news_md')
    doc = nlp(text)
    
    # Extraction des lemmes et suppression des stop words
    processed_text = ' '.join([token.lemma_ for token in doc if not token.is_stop])
    return processed_text

def check_text_validity(text):
    """Vérifie si le texte est valide et retourne des statistiques"""
    if not text or len(text) < 10:
        return False, "Texte trop court ou vide"
    
    words = text.split()
    if len(words) < 5:
        return False, "Trop peu de mots"
    
    return True, f"OK ({len(words)} mots)"

def compute_similarity(text1, text2, max_length=512):
    print("\n=== DÉBUT DU TRAITEMENT ===")
    
    # Vérification des textes en entrée
    print("\n0. Vérification des textes...")
    for idx, text in enumerate([text1, text2]):
        is_valid, msg = check_text_validity(text)
        print(f"Texte {idx+1}: {msg}")
        if not is_valid:
            print(f"ATTENTION: Texte {idx+1} potentiellement invalide!")
            return 0
    
    print("\n1. Prétraitement des textes...")
    text1 = preprocess_text(text1)
    text2 = preprocess_text(text2)
    
    print("\n2. Chargement du modèle de similarité spécialisé...")
    # Utilisation d'un modèle spécialisé pour l'analyse de CV et offres d'emploi
    similarity_pipeline = pipeline("feature-extraction", 
                                model="jjzha/jobbert-base-cased",
                                tokenizer="jjzha/jobbert-base-cased")
    
    print("\n3. Calcul des poids TF-IDF...")
    try:
        vectorizer = TfidfVectorizer(min_df=1, max_df=0.9)  # Ajustement des paramètres
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        feature_weights = dict(zip(vectorizer.get_feature_names_out(), 
                                 tfidf_matrix.toarray()[0]))
        print(f"Termes les plus importants:")
        for term, weight in sorted(feature_weights.items(), 
                                 key=lambda x: x[1], 
                                 reverse=True)[:5]:
            print(f"  - {term}: {weight:.3f}")
    except Exception as e:
        print(f"Erreur TF-IDF: {str(e)}")
        return 0
    
    print("\n4. Découpage des textes en chunks...")
    text1_chunks = split_text(text1, max_length)
    text2_chunks = split_text(text2, max_length)
    print(f"Nombre de chunks: {len(text1_chunks)} et {len(text2_chunks)}")
    
    # Amélioration de la gestion des scores
    weighted_scores = []
    chunk_details = []  # Pour le debugging
    
    for i, chunk1 in enumerate(text1_chunks):
        chunk_scores = []
        print(f"\nTraitement du chunk {i+1}/{len(text1_chunks)}...")
        
        for j, chunk2 in enumerate(text2_chunks):
            try:
                features1 = similarity_pipeline(chunk1)[0]
                features2 = similarity_pipeline(chunk2)[0]
                
                if len(features1) == len(features2):
                    base_score = cosine_similarity(features1, features2)
                    weight = np.mean([feature_weights.get(word, 1.0) 
                                   for word in chunk1.split()])
                    score = base_score * (1 + np.log1p(weight))
                    
                    # Vérification des scores aberrants
                    if 0 <= score <= 10:  # Plage attendue
                        chunk_scores.append(score)
                        chunk_details.append({
                            'chunk1_id': i,
                            'chunk2_id': j,
                            'score': score,
                            'base_score': base_score,
                            'weight': weight
                        })
                    else:
                        print(f"Score ignoré car hors limites: {score}")
                        
            except Exception as e:
                print(f"Erreur lors de la comparaison: {str(e)}")
                continue
    
    if not weighted_scores and not chunk_details:
        print("ATTENTION: Aucun score valide calculé!")
        return 0
    
    print("\nDétails des meilleurs scores par chunk:")
    for detail in sorted(chunk_details, key=lambda x: x['score'], reverse=True)[:3]:
        print(f"Chunk {detail['chunk1_id']} vs {detail['chunk2_id']}: "
              f"Score={detail['score']:.3f} (base={detail['base_score']:.3f}, "
              f"weight={detail['weight']:.3f})")
    
    print("\n6. Calcul du score final...")
    final_score = (np.mean(weighted_scores) if weighted_scores else 0) * 100
    adjusted_score = min(final_score / 0.6, 100.0)
    print(f"Score brut: {final_score:.1f}%")
    print(f"Score ajusté: {adjusted_score:.1f}%")
    
    print("\n=== FIN DU TRAITEMENT ===")
    return adjusted_score

def cosine_similarity(features1, features2):
    features1 = np.array(features1).flatten()
    features2 = np.array(features2).flatten()
    return np.dot(features1, features2) / (np.linalg.norm(features1) * np.linalg.norm(features2))

def analyze_differences(job_text, profile_text):
    """Analyse les termes importants présents dans l'offre mais absents du profil"""
    print("\n=== ANALYSE DES DIFFÉRENCES ===")
    
    # Prétraitement des textes
    job_text = preprocess_text(job_text)
    profile_text = preprocess_text(profile_text)
    
    # Extraction des termes importants avec TF-IDF
    vectorizer = TfidfVectorizer(max_features=50)
    tfidf_matrix = vectorizer.fit_transform([job_text, profile_text])
    
    # Récupération des termes et scores pour l'offre d'emploi
    job_terms = dict(zip(vectorizer.get_feature_names_out(), 
                        tfidf_matrix.toarray()[0]))
    
    # Création d'un set des termes du profil
    profile_terms = set(word for word in profile_text.split())
    
    # Identification des termes manquants importants
    missing_terms = []
    for term, importance in sorted(job_terms.items(), key=lambda x: x[1], reverse=True):
        if term not in profile_text and importance > 0.1:  # Seuil d'importance
            missing_terms.append((term, importance))
    
    # Affichage des résultats
    print("\nCompétences/termes requis manquants (par importance) :")
    for term, importance in missing_terms:
        print(f"- {term} (importance: {importance:.2f})")
    
    return missing_terms

@eel.expose
def validate_job_offer_and_candidate(job_offer_pdf, candidate_profile_pdf):
    print(f"\nAnalyse des fichiers :")
    print(f"- Offre d'emploi : {os.path.basename(job_offer_pdf)}")
    print(f"- Profil candidat : {os.path.basename(candidate_profile_pdf)}")
    
    job_offer_text = extract_text_from_pdf(job_offer_pdf)
    candidate_profile_text = extract_text_from_pdf(candidate_profile_pdf)
    
    if not job_offer_text or not candidate_profile_text:
        return "Le texte extrait de l'offre d'emploi ou du profil candidat est vide. Veuillez vérifier les fichiers PDF."
    
    print(f"\nLongueur des textes extraits :")
    print(f"- Offre d'emploi : {len(job_offer_text)} caractères")
    print(f"- Profil candidat : {len(candidate_profile_text)} caractères")
    
    similarity_score = compute_similarity(job_offer_text, candidate_profile_text)
    
    # Analyse des différences
    missing_skills = analyze_differences(job_offer_text, candidate_profile_text)
    
    # Interprétation du score
    interpretation = ""
    if similarity_score >= 75:
        interpretation = "Excellente correspondance"
    elif similarity_score >= 60:
        interpretation = "Bonne correspondance"
    elif similarity_score >= 40:
        interpretation = "Correspondance moyenne"
    else:
        interpretation = "Faible correspondance"
    
    # Formatage du résultat
    result = f"Score de correspondance : {similarity_score:.1f}% - {interpretation}\n\n"
    if missing_skills:
        result += "Compétences manquantes principales :\n"
        result += "\n".join([f"- {term}" for term, _ in missing_skills[:5]])
    
    return result


if __name__ == "__main__":
    job_offer_pdf = "G:\OneDrive\Entreprendre\CV\persona\IngeEtudeDev_Ideal/PRF_Cyril_SAURET_Ingénieur_Développeur_REACT_ideal.pdf"
    candidate_profile_pdf = "G:/OneDrive/Entreprendre/Actions-4/M434/M434_annonce_.pdf"
    print(validate_job_offer_and_candidate(job_offer_pdf, candidate_profile_pdf))

