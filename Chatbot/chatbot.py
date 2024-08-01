from flask import Flask, request, jsonify
import requests
from transformers import MBartTokenizer, MBartForConditionalGeneration
import os
from flask_cors import CORS
import logging
import re

app = Flask(__name__)
CORS(app)

# Configuration de l'API Wit.ai
WIT_API_TOKEN = 'XX'
WIT_API_URL = 'XX'

dialog_model_name = "facebook/mbart-large-cc25"
dialog_tokenizer = MBartTokenizer.from_pretrained(dialog_model_name)
dialog_model = MBartForConditionalGeneration.from_pretrained(dialog_model_name)
dialog_tokenizer.src_lang = "fr_XX"
dialog_tokenizer.tgt_lang = "fr_XX"

# Fonction pour interroger Wit.ai
def query_witai(message):
    headers = {
        'Authorization': f'Bearer {WIT_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    response = requests.get(WIT_API_URL + message, headers=headers)
    return response.json()

# Fonction pour extraire le domaine à partir de la réponse de Wit.ai
def extract_domain(response):
    intents = response.get('intents', [])
    if intents:
        return intents[0].get('name')
    return None

# Fonction pour extraire les questions à partir de la réponse de Wit.ai
def extract_question(response):
    question_array = []
    def extract_values(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'value':
                    question_array.append(value)
                else:
                    extract_values(value)
        elif isinstance(data, list):
            for item in data:
                extract_values(item)
    traits = response.get('traits', {})
    extract_values(traits)
    if question_array:
        return question_array
    else:
        return [
            "Pourriez-vous expliquer comment cela s'applique à notre entreprise ?",
            "Avez-vous des exemples concrets où vous avez utilisé ces compétences dans un contexte professionnel ?"
        ]

# Fonction pour extraire le nom à partir de l'entrée de l'utilisateur
def extract_name(user_input):
    formules = ["je m'appelle", "mon nom est", "moi c'est", "je m'appel", "je suis"]
    invalid_words = ["je suis un"]

    for phrase in formules:
        if phrase in user_input.lower():
            parts = user_input.lower().split(phrase)
            if len(parts) > 1:
                extracted_name = parts[1].strip().split()
                if len(extracted_name) > 1:
                    first_name = extracted_name[0].strip().capitalize()
                    last_name = extracted_name[1].strip().capitalize()
                    if last_name not in invalid_words:
                        return f"{first_name} {last_name}"
    return None

def validate_answer(answer):
    words_check = len(answer.split()) >= 3
    special_chars_check = bool(re.search(r'[^a-zA-Z0-9?!\s]', answer))
    return words_check and special_chars_check

logging.basicConfig(level=logging.DEBUG)

@app.route('/interview', methods=['POST'])
def interview():
    data = request.json
    app.logger.debug(f"Requête reçue avec les données: {data}")

    if not data:
        app.logger.error("Invalid input, JSON payload is required.")
        return jsonify({"error": "Invalid input, JSON payload is required."}), 400

    level = data.get('level')
    sub_level = data.get('sub_level', 0)
    user_input = data.get('user_input')
    filename = data.get('filename')
    question = data.get('question')
    answer = data.get('answer')
    name = data.get('name')
    domain = data.get('domain')
    initial_questions = data.get('initial_questions', [])

    app.logger.debug(f"level: {level}, sub_level: {sub_level}, user_input: {user_input}, filename: {filename}, question: {question}, answer: {answer}, name: {name}, domain: {domain}")

    if level is None:
        app.logger.error("Invalid input, 'level' is required.")
        return jsonify({"error": "Invalid input, 'level' is required."}), 400

    if level == 0:
        if sub_level == 0:
            if not user_input:
                app.logger.error("Invalid input, 'user_input' is required.")
                return jsonify({"error": "Invalid input, 'user_input' is required."}), 400

            if not name:
                name = extract_name(user_input)
                if not name:
                    app.logger.debug("Nom non détecté.")
                    return jsonify({"message": "C'est quoi votre nom déjà ?", "sub_level": 0, "level": 0})

            if not filename:
                filename = f"{name.replace(' ', '_')}.txt"
            
            if not domain:
                domain = extract_domain(query_witai(user_input))
                if not domain:
                    app.logger.debug("Domaine non détecté.")
                    return jsonify({"message": f"J'ai pas bien saisi vos compétences, {name} ?", "filename": filename, "sub_level": 1, "level": 0, "name": name})

            initial_questions = extract_question(query_witai(user_input))
            initial_questions += [
                "Parlez-moi de votre expérience professionnelle.",
                "Quelles compétences clés avez-vous développées dans vos précédentes expériences ?",
                "Quels sont vos principaux objectifs de carrière à long terme ?"
            ]
            question = initial_questions.pop(0)
            with open(filename, "w", encoding="utf-8") as file:
                file.write(f"NOM :: {name}\n")
                file.write(f"DOMAINE :: {domain}\n")
                file.write(f"COMPÉTENCES :: {user_input}\n\n")
            return jsonify({
                "filename": filename,
                "question": question,
                "initial_questions": initial_questions,
                "level": 1
            })

        elif sub_level == 1:
            domain = extract_domain(query_witai(user_input))
            if not domain:
                app.logger.debug("Domaine toujours non détecté.")
                return jsonify({"message": f"J'ai toujours pas bien saisi votre domaine, {name}. Pouvez-vous préciser ?", "filename": filename, "sub_level": 1, "level": 0, "name": name})

            initial_questions = extract_question(query_witai(user_input))
            initial_questions += [
                "Parlez-moi de votre expérience professionnelle.",
                "Quelles compétences clés avez-vous développées dans vos précédentes expériences ?",
                "Quels sont vos principaux objectifs de carrière à long terme ?"
            ]
            question = initial_questions.pop(0)
            with open(filename, "a", encoding="utf-8") as file:
                file.write(f"DOMAINE :: {domain}\n")
                file.write(f"COMPÉTENCES :: {user_input}\n\n")
            return jsonify({
                "filename": filename,
                "question": question,
                "initial_questions": initial_questions,
                "level": 1
            })

    elif level == 1:
        if not filename or not answer:
            app.logger.error("Invalid input, 'filename' and 'answer' are required.")
            return jsonify({"error": "Invalid input, 'filename' and 'answer' are required."}), 400

        if not validate_answer(answer):
            app.logger.debug("Réponse non valide.")
            return jsonify({"question": f"Veuillez répondre correctement à la question : {question}", "level": 1, "initial_questions": initial_questions, "filename": filename})

        with open(filename, "a", encoding="utf-8") as file:
            file.write(f"Question: {question}\n")
            file.write(f"Réponse: {answer}\n\n")

        if initial_questions:
            question = initial_questions.pop(0)
            return jsonify({
                "filename": filename,
                "question": question,
                "initial_questions": initial_questions,
                "level": 1
            })
        else:
            return jsonify({
                "message": "Merci pour vos réponses. L'entretien est terminé.",
                "level": 2
            })

    return jsonify({"error": "Invalid input. Please provide the required data."}), 400

if __name__ == "__main__":
    app.run(port=5000, debug=True)
