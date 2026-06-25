import os, sys, json, uuid, random, hashlib
from datetime import datetime
from flask import Flask, request, jsonify
from functools import wraps

BRAIN_FILE = "sea_brain.pkl"
KNOWLEDGE_DIR = "knowledge"
CHATS_DIR = "chats"
USERS_FILE = "users.json"

if not os.path.exists(CHATS_DIR):
    os.makedirs(CHATS_DIR)

app = Flask(__name__)

@app.after_request
def add_cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = '*'
    return resp

SEA_PREFIXES = [
    "Analysis complete: ", "Tactical update: ",
    "Strategic assessment: ", "SEA reports: ",
    "Confirmed. ", "Affirmative. ",
]

def make_conversational(text):
    return random.choice(SEA_PREFIXES) + text

# =========================
# USER AUTH
# =========================

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256((password + "sea_2026").encode()).hexdigest()

def create_user(username, password):
    users = load_users()
    if username in users:
        return None
    token = str(uuid.uuid4())
    users[username] = {"password": hash_password(password), "token": token, "created": datetime.now().isoformat()}
    save_users(users)
    return token

def login_user(username, password):
    users = load_users()
    if username not in users or users[username]["password"] != hash_password(password):
        return None
    token = str(uuid.uuid4())
    users[username]["token"] = token
    save_users(users)
    return token

def get_user_by_token(token):
    for u, d in load_users().items():
        if d["token"] == token:
            return u
    return None

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "")
        username = get_user_by_token(token)
        if not username:
            return jsonify({"error": "Unauthorized"}), 401
        return f(username, *args, **kwargs)
    return decorated

# =========================
# BRAIN (NO SKLEARN)
# =========================

class LiteBrain:
    def __init__(self):
        self.knowledge_base = []

    def train(self):
        if not os.path.exists(KNOWLEDGE_DIR):
            return
        files = [f for f in os.listdir(KNOWLEDGE_DIR) if f.endswith('.txt')]
        for filename in files:
            with open(os.path.join(KNOWLEDGE_DIR, filename), "r", encoding="utf-8") as f:
                lines = [x.strip() for x in f.readlines() if x.strip()]
            for i in range(0, len(lines) - 1, 2):
                self.knowledge_base.append((lines[i].lower(), lines[i + 1]))

    def think(self, user_input):
        input_lower = user_input.lower()
        input_words = set(input_lower.split())
        best_score, best_answer = 0, "I don't have data on that yet, Sir."
        for question, answer in self.knowledge_base:
            q_words = set(question.split())
            if len(q_words) > 0 and len(input_words) > 0:
                overlap = len(q_words & input_words)
                score = overlap / max(len(q_words), len(input_words))
                if score > best_score:
                    best_score = score
                    best_answer = answer
        min_score = 0.3 if len(input_words) <= 2 else 0.15
        if best_score < min_score:
            return "I don't have data on that yet, Sir."
        return make_conversational(best_answer)

brain = LiteBrain()

# =========================
# CHAT STORAGE
# =========================

def chats_dir(username):
    p = os.path.join(CHATS_DIR, username)
    os.makedirs(p, exist_ok=True)
    return p

def chat_path(username, chat_id):
    return os.path.join(chats_dir(username), f"{chat_id}.json")

def save_chat(username, chat_id, data):
    with open(chat_path(username, chat_id), "w") as f:
        json.dump(data, f)

def load_chat(username, chat_id):
    p = chat_path(username, chat_id)
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return {"id": chat_id, "title": "New Session", "messages": []}

def all_chats(username):
    chats = []
    d = chats_dir(username)
    for f in os.listdir(d):
        if f.endswith(".json"):
            with open(os.path.join(d, f)) as fh:
                data = json.load(fh)
                chats.append({"id": data["id"], "title": data["title"]})
    chats.sort(key=lambda x: x["id"])
    return chats

# =========================
# ROUTES
# =========================

@app.route('/')
def index():
    return jsonify({"status": "SEA ONLINE", "version": "Pi Lite"})

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    user = data.get("username", "").strip().lower()
    pw = data.get("password", "").strip()
    if not user or not pw:
        return jsonify({"error": "Username and password required"}), 400
    token = create_user(user, pw)
    if not token:
        return jsonify({"error": "Username exists"}), 409
    return jsonify({"token": token, "username": user}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = data.get("username", "").strip().lower()
    pw = data.get("password", "").strip()
    token = login_user(user, pw)
    if not token:
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify({"token": token, "username": user})

@app.route('/auth/verify', methods=['GET'])
@require_auth
def verify(username):
    return jsonify({"valid": True, "username": username})

@app.route('/chats', methods=['GET'])
@require_auth
def list_chats(username):
    return jsonify(all_chats(username))

@app.route('/chats/<chat_id>', methods=['GET'])
@require_auth
def get_chat(username, chat_id):
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
    chat_id = data.get('chat_id')
    reply = brain.think(message)
    if chat_id:
        chat_data = load_chat(username, chat_id)
        chat_data['messages'].append({"role": "user", "text": message})
        chat_data['messages'].append({"role": "sea", "text": reply})
        if len(chat_data['messages']) < 6:
            chat_data['title'] = message[:40]
        save_chat(username, chat_id, chat_data)
    return jsonify({"reply": reply})

@app.route('/teach', methods=['POST'])
@require_auth
def teach(username):
    data = request.get_json()
    question = data.get('question', '').strip()
    answer = data.get('answer', '').strip()
    if not question or not answer:
        return jsonify({"error": "Need both question and answer"}), 400
    with open(os.path.join(KNOWLEDGE_DIR, "custom_taught.txt"), "a", encoding="utf-8") as f:
        f.write(f"{question}\n{answer}\n")
    brain.knowledge_base.append((question.lower(), answer))
    return jsonify({"status": "learned", "question": question, "answer": answer})

if __name__ == "__main__":
    brain.train()
    print("SEA ONLINE (PI LITE MODE)")
    app.run(host='0.0.0.0', port=5000, debug=False)
