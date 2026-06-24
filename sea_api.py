import os
import sys
import json
import uuid
import random
import hashlib
import joblib
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.neural_network import MLPClassifier
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps

BRAIN_FILE = "sea_brain.pkl"
KNOWLEDGE_DIR = "knowledge"
CHATS_DIR = "chats"
USERS_FILE = "users.json"

if not os.path.exists(CHATS_DIR):
    os.makedirs(CHATS_DIR)

app = Flask(__name__)
CORS(app)

SEA_PREFIXES = [
    "Analysis complete, Sir: ",
    "Tactical update, Sir: ",
    "Strategic assessment: ",
    "Sir, here's the intel: ",
    "SEA reports: ",
    "Confirmed, Sir. ",
    "Affirmative. ",
    "Processing complete. ",
]

def make_conversational(text):
    return random.choice(SEA_PREFIXES) + text

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    salt = "sea_salt_2026"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def create_user(username, password):
    users = load_users()
    if username in users:
        return None
    token = str(uuid.uuid4())
    users[username] = {
        "password": hash_password(password),
        "token": token,
        "created": datetime.now().isoformat()
    }
    save_users(users)
    return token

def login_user(username, password):
    users = load_users()
    if username not in users:
        return None
    if users[username]["password"] != hash_password(password):
        return None
    token = str(uuid.uuid4())
    users[username]["token"] = token
    save_users(users)
    return token

def get_user_by_token(token):
    users = load_users()
    for username, data in users.items():
        if data["token"] == token:
            return username
    return None

def get_user_chats_dir(username):
    path = os.path.join(CHATS_DIR, username)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_chat_path(username, chat_id):
    return os.path.join(get_user_chats_dir(username), f"{chat_id}.json")

def save_chat(username, chat_id, data):
    path = get_chat_path(username, chat_id)
    with open(path, "w") as f:
        json.dump(data, f)

def load_chat(username, chat_id):
    path = get_chat_path(username, chat_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"id": chat_id, "title": "New Session", "messages": []}

def get_all_chats(username):
    chats = []
    dir_path = get_user_chats_dir(username)
    if not os.path.exists(dir_path):
        return chats
    for f in os.listdir(dir_path):
        if f.endswith(".json"):
            path = os.path.join(dir_path, f)
            with open(path, "r") as fh:
                data = json.load(fh)
                chats.append({"id": data["id"], "title": data["title"]})
    chats.sort(key=lambda x: x["id"])
    return chats

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "") if auth.startswith("Bearer ") else auth
        username = get_user_by_token(token)
        if not username:
            return jsonify({"error": "Unauthorized"}), 401
        return f(username, *args, **kwargs)
    return decorated

# =========================
# AUTH ROUTES
# =========================

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    if len(username) < 3 or len(password) < 3:
        return jsonify({"error": "Username and password must be at least 3 characters"}), 400
    token = create_user(username, password)
    if not token:
        return jsonify({"error": "Username already exists"}), 409
    return jsonify({"token": token, "username": username}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username", "").strip().lower()
    password = data.get("password", "").strip()
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    token = login_user(username, password)
    if not token:
        return jsonify({"error": "Invalid username or password"}), 401
    return jsonify({"token": token, "username": username})

@app.route('/auth/verify', methods=['GET'])
@require_auth
def verify(username):
    return jsonify({"valid": True, "username": username})

# =========================
# CHAT ROUTES (AUTH'D)
# =========================

@app.route('/')
def index():
    return jsonify({"status": "SEA ONLINE", "message": "API is running."})

@app.route('/chats', methods=['GET'])
@require_auth
def list_chats(username):
    return jsonify(get_all_chats(username))

@app.route('/chats/<chat_id>', methods=['GET'])
@require_auth
def get_chat_history(username, chat_id):
    return jsonify(load_chat(username, chat_id))

@app.route('/chats/new', methods=['POST'])
@require_auth
def new_chat(username):
    chat_id = str(uuid.uuid4())
    data = {"id": chat_id, "title": "New Session", "messages": []}
    save_chat(username, chat_id, data)
    return jsonify(data), 201

@app.route('/ask', methods=['POST'])
@require_auth
def ask(username):
    data = request.get_json()
    message = data.get('message', '')
    chat_id = data.get('chat_id', None)

    chat_data = load_chat(username, chat_id) if chat_id else None
    reply, result_data = process_interaction(message, brain, chat_data)

    if chat_data:
        chat_data['messages'].append({"role": "user", "text": message})
        chat_data['messages'].append({"role": "sea", "text": reply})
        if len(chat_data['messages']) < 6:
            chat_data['title'] = message[:40]
        if result_data:
            chat_data.update(result_data)
        save_chat(username, chat_id, chat_data)

    return jsonify({"reply": reply})

# =========================
# KNOWLEDGE / BRAIN
# =========================

def load_data():
    questions = []
    answers = []
    if not os.path.exists(KNOWLEDGE_DIR):
        print(f"ERROR: {KNOWLEDGE_DIR} not found.")
        return questions, answers
    files = [f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith('.txt')]
    print(f"Loading knowledge from: {files}")
    for filename in files:
        file_path = os.path.join(KNOWLEDGE_DIR, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [x.strip() for x in f.readlines() if x.strip()]
        for i in range(0, len(lines) - 1, 2):
            questions.append(lines[i].lower())
            answers.append(lines[i + 1])
    return questions, answers

class NeuralBrain:
    def __init__(self):
        self.vectorizer = CountVectorizer(stop_words='english')
        self.association_matrix = None
        self.vocabulary = None
        self.knowledge_base = []

    def train(self, questions, answers):
        print("[*] INITIATING NEURAL MAPPING...")
        self.knowledge_base = list(zip(questions, answers))
        all_text = questions + answers
        X = self.vectorizer.fit_transform(all_text)
        self.vocabulary = self.vectorizer.get_feature_names_out()
        cooccurrence = (X.T * X).toarray()
        sums = cooccurrence.sum(axis=1)
        sums[sums == 0] = 1
        self.association_matrix = cooccurrence / sums[:, np.newaxis]
        print(f"[+] Neural Mapping Complete: {len(self.vocabulary)} concepts linked.")

    def think(self, user_input, chat_data=None):
        if chat_data and chat_data.get('pending_thought'):
            approval_words = ['ok', 'okay', 'yes', 'sure', 'proceed', 'go ahead', 'yep', 'do it', 'approval', 'yes please']
            if any(word in user_input.lower() for word in approval_words):
                thought = chat_data['pending_thought']
                return f"Executing approved thought: {thought}", {'pending_thought': None}, None
            else:
                return "Awaiting approval, Sir.", chat_data, None

        input_lower = user_input.lower()
        intent_keywords = {
            'create': 'autonomous_architect', 'make': 'autonomous_architect',
            'build': 'autonomous_architect', 'generate': 'autonomous_architect',
            'develop': 'autonomous_architect', 'status': 'system_status',
            'report': 'system_status', 'scan': 'network_scan',
            'agent': 'agent_mode', 'code': 'agent_mode', 'project': 'agent_mode',
        }
        detected_intent = 'reasoning'
        for word, intent in intent_keywords.items():
            if word in input_lower:
                detected_intent = intent
                break
        if detected_intent == 'network_scan':
            return "Network scan unavailable in cloud deployment.", {}, None
        best_score = 0
        best_answer = "I don't have enough data to answer that, Sir. Try teaching me with: #teach question :: answer"
        for question, answer in self.knowledge_base:
            q_words = set(question.lower().split())
            i_words = set(input_lower.split())
            if len(q_words) > 0 and len(i_words) > 0:
                overlap = len(q_words & i_words)
                score = overlap / max(len(q_words), len(i_words))
                if score > best_score:
                    best_score = score
                    best_answer = answer
        if best_score < 0.15 and detected_intent != 'reasoning':
            return self._handle_intent(detected_intent, user_input), {}, None
        return make_conversational(best_answer), {}, None

    def _handle_intent(self, intent, user_input):
        responses = {
            'system_status': "All systems nominal, Sir. SEA core online. Memory stable. No anomalies detected.",
            'agent_mode': f"Agent Mode Active. Strategic analysis for '{user_input}' in progress. Define parameters for deployment.",
            'autonomous_architect': f"Autonomous Architect engaged. Analyzing request: '{user_input}'. Stand by for synthesis.",
        }
        return responses.get(intent, f"Command received: {user_input}. Processing...")

def build_brain():
    print("[*] BUILDING SEA BRAIN...")
    if os.path.exists(BRAIN_FILE) and os.path.getsize(BRAIN_FILE) > 1000:
        try:
            brain = joblib.load(BRAIN_FILE)
            print(f"[+] Brain loaded from {BRAIN_FILE}")
            return brain
        except Exception as e:
            print(f"[-] Failed to load brain: {e}")
    print("[*] Training brain from knowledge base...")
    questions, answers = load_data()
    if not questions:
        print("[!] No training data found. Using fallback responses.")
        brain = NeuralBrain()
        brain.knowledge_base = [("hello", "Hello Sir. SEA standing by."), ("hi", "Greetings, Sir. Awaiting your command.")]
        return brain
    brain = NeuralBrain()
    brain.train(questions, answers)
    try:
        joblib.dump(brain, BRAIN_FILE)
        print(f"[+] Brain saved to {BRAIN_FILE}")
    except Exception as e:
        print(f"[-] Could not save brain: {e}")
    return brain

def process_interaction(message, brain, chat_data=None):
    is_agent = message.strip().startswith("#agent")
    clean_message = message.replace("#agent", "", 1).strip() if is_agent else message.strip()
    reply, result_data, auto_payload = brain.think(clean_message, chat_data)
    if auto_payload:
        reply = f"{reply}\n\n[AUTONOMOUS ACTION]: {auto_payload}"
    return reply, result_data

brain = build_brain()

if __name__ == "__main__":
    print("\nSEA ONLINE (CLOUD MODE)\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
