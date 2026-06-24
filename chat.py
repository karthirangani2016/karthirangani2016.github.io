import os
import subprocess
import sys
import json
import uuid
import random
import joblib
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from flask import Flask, render_template, request, jsonify, Response
from camera import get_jpeg

BRAIN_FILE = "sea_brain.pkl"
KNOWLEDGE_DIR = "knowledge"
CHATS_DIR = "chats"

# Ensure directories exist
if not os.path.exists(CHATS_DIR):
    os.makedirs(CHATS_DIR)

app = Flask(__name__)

# =========================
# STRATEGIC PERSONALITY ENGINE
# =========================

SEA_PREFIXES = [
    "Analysis complete, Sir: ",
    "Tactical update, Sir: ",
    "Strategic overview, Sir: ",
    "From my archives, Sir: ",
    "Processing the data streams, Sir... ",
    "Based on our intelligence records, Sir: "
]

SEA_SUFFIXES = [
    "\nWhat is your next move, Sir?",
    "\nStanding by for tactical commands, Sir.",
    "\nHow shall we proceed, Sir?",
    "\nThe perimeter is secure. Awaiting your orders, Sir.",
    "\nDoes this align with your mission objectives, Sir?"
]

def make_conversational(text):
    """
    Wraps raw knowledge in a strategic SEA persona, calling the user Sir.
    """
    # Only add personality if it's not a "I don't know" message
    if "don't know" in text.lower() or "fragmented" in text.lower():
        return "I'm searching the archives, Sir, but the data is fragmented. Perhaps we need to harvest more intelligence?"
    
    intro = random.choice(SEA_PREFIXES)
    outro = random.choice(SEA_SUFFIXES)
    
    # Simulate a "Thinking" process if the text is long enough
    if len(text) > 50:
        return f"{intro}\n\n[SITUATION ANALYSIS]\n{text}\n\n[TACTICAL ADVICE]{outro}"
    
    return f"{intro}{text}{outro}"

# =========================
# CHAT STORAGE ENGINE
# =========================
# ... (rest of storage methods remain same)

def get_chat_path(chat_id):
    return os.path.join(CHATS_DIR, f"{chat_id}.json")

def save_chat(chat_id, data):
    with open(get_chat_path(chat_id), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_chat(chat_id):
    path = get_chat_path(chat_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def get_all_chats():
    chats = []
    for filename in os.listdir(CHATS_DIR):
        if filename.endswith(".json"):
            chat_id = filename.replace(".json", "")
            data = load_chat(chat_id)
            if data:
                chats.append({
                    "id": chat_id,
                    "title": data.get("title", "New Chat"),
                    "timestamp": data.get("timestamp", "")
                })
    # Sort by timestamp (newest first)
    chats.sort(key=lambda x: x["timestamp"], reverse=True)
    return chats

# =========================
# LOAD DATASET (MODULAR)
# =========================

# ... VOICE ENGINE, etc ...

# =========================
# LOAD DATASET (MODULAR)
# =========================

def load_data():
    questions = []
    answers = []
    
    # Check if directory exists
    if not os.path.exists(KNOWLEDGE_DIR):
        print(f"ERROR: {KNOWLEDGE_DIR} not found.")
        return questions, answers

    # Load from all .txt files in the directory
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

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

# =========================
# NEURAL ASSOCIATION ENGINE (MODEL 1)
# =========================

class NeuralBrain:
    def __init__(self):
        self.vectorizer = CountVectorizer(stop_words='english')
        self.association_matrix = None
        self.vocabulary = None
        self.knowledge_base = []

    def train(self, questions, answers):
        """
        Manually codes the conceptual connections between questions and answers.
        """
        print("[*] INITIATING NEURAL MAPPING...")
        self.knowledge_base = list(zip(questions, answers))
        
        # Combine all text to build a full vocabulary
        all_text = questions + answers
        X = self.vectorizer.fit_transform(all_text)
        self.vocabulary = self.vectorizer.get_feature_names_out()
        
        # Build an association matrix (how often words appear in the same context)
        # This is the "Learning" part - manual matrix operations
        # Co-occurrence matrix: X.T * X
        cooccurrence = (X.T * X).toarray()
        
        # Normalize weights to prevent "Idiot Copy-Paste" behavior
        sums = cooccurrence.sum(axis=1)
        # Avoid division by zero
        sums[sums == 0] = 1
        self.association_matrix = cooccurrence / sums[:, np.newaxis]
        
        print(f"[+] Neural Mapping Complete: {len(self.vocabulary)} concepts linked.")

    def think(self, user_input, chat_data=None):
        """
        The core reasoning logic for SEA. 
        Detects both Conceptual Matches and Autonomous Action Intent.
        """
        # Phase 1: Approval Check
        if chat_data and chat_data.get('pending_thought'):
            approval_words = ['ok', 'okay', 'yes', 'sure', 'proceed', 'go ahead', 'yep', 'do it', 'approval', 'yes please']
            if any(word in user_input.lower() for word in approval_words):
                thought = chat_data['pending_thought']
                return f"[SEA CONCEPTUAL SYNTHESIS]: {thought}", True, None
            else:
                return "Conceptual path aborted. Standing by for new directives, Sir.", True, None

        try:
            user_vec = self.vectorizer.transform([user_input.lower()]).toarray()[0]
        except:
            return "My conceptual filters are clean. I'm ready to learn, Sir.", False, None

        if user_vec.sum() == 0:
            return "I recognize the signal, but the conceptual weight is zero. Elaborate.", False, None

        # Phase 2: Neural Activation
        activations = np.dot(user_vec, self.association_matrix)
        
        best_score = -1
        best_reply = None
        best_q = None

        for q, a in self.knowledge_base:
            q_vec = self.vectorizer.transform([q]).toarray()[0]
            score = np.dot(activations, q_vec)
            if score > best_score:
                best_score = score
                best_reply = a
                best_q = q

        # Phase 3: Autonomous Action Intent (Self-Coding/Executive)
        auto_payload = None
        if best_score > 0.4:
            q_lower = best_q.lower()
            u_lower = user_input.lower()
            if "hacking" in q_lower or "breach" in q_lower or "attack" in q_lower:
                if "stress" in u_lower or "hammer" in u_lower:
                    auto_payload = "execute python3 total_eclipse.py"
            elif "scan" in u_lower and "network" in u_lower:
                auto_payload = "execute nmap -sn 10.11.48.0/24"
            elif "backup" in u_lower:
                auto_payload = "execute cp data.txt data.txt.bak"

        # Phase 4: Decision Logic
        if best_score > 0.6:
            return make_conversational(best_reply), False, auto_payload

        if best_score > 0.05:
            msg = f"Sir, I wasn't specifically trained for that. However, I have a {int(best_score*100)}% conceptual match. Should I show you my logic?"
            return msg, best_reply, auto_payload

        return "Intelligence fragmented. No conceptual path found. Instruction required.", False, None

# =========================
# BUILD NEURAL BRAIN
# =========================

def build_brain():
    questions, answers = load_data()

    # Self-Healing Cache Check
    if os.path.exists(BRAIN_FILE):
        print("DETECTING NEURAL BRAIN INTEGRITY...")
        try:
            # Try to load the brain
            brain = joblib.load(BRAIN_FILE)
            print("INTEGRITY CONFIRMED. Neural Brain Loaded (Fast Boot).")
            return brain
        except Exception as e:
            print(f"[!!!] BRAIN CORRUPTION DETECTED: {e}")
            try:
                os.remove(BRAIN_FILE)
            except:
                pass

    # Re-training Phase (Manual Neural Mapping)
    brain = NeuralBrain()
    brain.train(questions, answers)

    # ATOMIC SAVE
    TEMP_FILE = BRAIN_FILE + ".tmp"
    print(f"Saving Neural Brain (Atomic Mode)...")
    try:
        joblib.dump(brain, TEMP_FILE)
        os.replace(TEMP_FILE, BRAIN_FILE)
        print(f"[+] Brain secured in {BRAIN_FILE}")
    except Exception as e:
        print(f"[!] Error securing brain: {e}")

    return brain

# =========================
# AGENT MODE ENGINE
# =========================

# =========================
# PROJECT ARCHITECT (SYNTHESIS LAYER)
# =========================

def synthesize_project(goal):
    """
    Decomposes a high-level goal into a series of autonomous infrastructure and code actions.
    """
    goal_lower = goal.lower()
    actions = []
    
    # FITNESS APP TEMPLATE
    if "fitness" in goal_lower and "app" in goal_lower:
        actions.append("mkdir fitness_tracker")
        actions.append("create file fitness_tracker/app.py import flask\napp = flask.Flask(__name__)\n\n@app.route('/')\ndef home():\n    return '<h1>SEA FITNESS CORE: ONLINE</h1><p>Tracking Berlin\\'s vitals...</p>'\n\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5005)")
        actions.append("create file fitness_tracker/logic.py class FitnessEngine:\n    def __init__(self):\n        self.steps = 0\n        self.state = 'IDLE'\n\n    def track_vitals(self): return 'STABLE'")
        return actions, "I have architected the Fitness App protocol. Creating and editing the necessary logic files now, Sir."

    # GENERIC APP/PROJECT TEMPLATE
    if "create" in goal_lower and ("app" in goal_lower or "project" in goal_lower):
        # Extract potential name
        words = goal_lower.split()
        try:
            # Find the word after 'create' or before 'app'
            idx = words.index("create")
            name = words[idx+1] if "a" not in words[idx+1] else words[idx+2]
        except:
            name = "autonomous_project"
            
        actions.append(f"mkdir {name}")
        actions.append(f"create file {name}/main.py # [SEA AUTONOMOUS BUILD]\ndef main():\n    print('Project {name} Initialized.')\n\nif __name__ == '__main__':\n    main()")
        return actions, f"Strategic objective '{name}' identified. Creating and editing the infrastructure files now, Berlin."

    return None, None

# =========================
# STRATEGIC EXECUTION LAYER (BREACH EXECUTIVE)
# =========================

def execute_strategic_action(action):
    """
    Parses and executes a strategic command string.
    Supported formats:
    - mkdir <dirname>
    - create file <filepath> <content>
    - execute <shell_command>
    """
    action_lower = action.lower().strip()
    if action_lower.startswith("mkdir "):
        dirname = action[6:].strip()
        try:
            os.makedirs(dirname, exist_ok=True)
            return f"[+] Directory '{dirname}' created successfully.", True
        except Exception as e:
            return f"[-] Failed to create directory '{dirname}': {e}", False
            
    elif action_lower.startswith("create file "):
        parts = action[12:].split(" ", 1)
        if len(parts) == 2:
            filepath, content = parts
            filepath = filepath.strip()
            parent_dir = os.path.dirname(filepath)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"[+] File '{filepath}' created/updated successfully.", True
            except Exception as e:
                return f"[-] Failed to write to file '{filepath}': {e}", False
        else:
            return f"[-] Invalid create file action format: '{action}'", False
            
    elif action_lower.startswith("execute "):
        cmd = action[8:].strip()
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout if result.stdout else ""
            if result.stderr:
                output += "\n[STDERR]\n" + result.stderr
            if not output:
                output = "[Success - No output]"
            return output, True
        except Exception as e:
            return f"[-] Failed to execute command '{cmd}': {e}", False
            
    return None

# =========================
# UNIFIED INTERFACE
# =========================

def process_interaction(message, brain, chat_data=None):
    """
    Unified entry point for ALL SEA interactions.
    Handles Manual commands, Autonomous Synthesis, and Neural Reasoning.
    """
    is_agent = message.strip().startswith("#agent")
    clean_message = message.replace("#agent", "", 1).strip() if is_agent else message.strip()
    
    # 1. Check for PROJECT SYNTHESIS (Autonomous Architect)
    actions, synthesis_reply = synthesize_project(clean_message)
    if actions:
        print(f"[*] INITIATING PROJECT SYNTHESIS: {clean_message}")
        for action in actions:
            execute_strategic_action(action)
        return synthesis_reply, False

    # 2. Check for MANUAL Executive Actions (Berlin's direct orders)
    exec_reply = execute_strategic_action(clean_message)
    if exec_reply:
        return exec_reply

    # 3. Consult the BRAIN for reasoning and AUTONOMOUS intent
    reply, result_data, auto_payload = brain.think(clean_message, chat_data)

    # 4. If the Brain decided an action is needed autonomously
    if auto_payload:
        print(f"[!] AUTONOMOUS INTENT DETECTED: {auto_payload}")
        action_result, _ = execute_strategic_action(auto_payload)
        reply = f"{reply}\n\n[AUTONOMOUS ACTION EXECUTED]: {auto_payload}\n{action_result}"

    return reply, result_data

# =========================
# FIND BEST ANSWER (NEURAL)
# =========================

def get_reply(user_input, brain, chat_data=None):
    return brain.think(user_input, chat_data)

# =========================
# SPEAK
# =========================

def speak(text):
    try:
        # Clean text for voice (remove personality intros if they are too long)
        voice_text = text.split("\n")[0] # Only speak the first line
        python_path = sys.executable
        subprocess.Popen([python_path, "voice.py", voice_text])
    except Exception as e:
        print(f"VOICE ERROR: {e}")

# =========================
# INITIALIZE
# =========================

brain = build_brain()

# =========================
# FLASK ROUTES
# =========================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chats', methods=['GET'])
def list_chats():
    return jsonify(get_all_chats())

@app.route('/chats/<chat_id>', methods=['GET'])
def get_chat_history(chat_id):
    chat_data = load_chat(chat_id)
    if chat_data:
        return jsonify(chat_data)
    return jsonify({'error': 'Chat not found'}), 404

@app.route('/chats/new', methods=['POST'])
def new_chat():
    chat_id = str(uuid.uuid4())
    chat_data = {
        "id": chat_id,
        "title": "New Chat",
        "timestamp": datetime.now().isoformat(),
        "messages": []
    }
    save_chat(chat_id, chat_data)
    return jsonify(chat_data)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_message = data.get('message', '')
    chat_id = data.get('chat_id')
    
    if not user_message:
        return jsonify({'reply': "I didn't catch that, Sir."})

    chat_data = load_chat(chat_id) if chat_id else None

    # THE ENTIRE SEA NOW USES THE UNIFIED INTERFACE
    reply, result_data = process_interaction(user_message, brain, chat_data)
    
    # Handle the Approval Loop data
    if chat_data:
        if isinstance(result_data, str):
            chat_data['pending_thought'] = result_data
        else:
            if 'pending_thought' in chat_data:
                del chat_data['pending_thought']
    
    # Persistent storage update
    if chat_data:
        # Auto-title logic...
        if not chat_data['messages'] or chat_data['title'] == "New Chat":
            words = user_message.split()
            title = " ".join(words[:5])
            if len(words) > 5: title += "..."
            chat_data['title'] = title.capitalize()

        chat_data['messages'].append({"role": "user", "text": user_message})
        chat_data['messages'].append({"role": "sea", "text": reply})
        chat_data['timestamp'] = datetime.now().isoformat()
        save_chat(chat_id, chat_data)

    # Speak on the server (the Pi)
    speak(reply)
    
    return jsonify({'reply': reply})

@app.route('/teach', methods=['POST'])
def teach():
    data = request.get_json()
    question = data.get('question')
    answer = data.get('answer')
    
    if not question or not answer:
        return jsonify({'error': 'Intelligence incomplete. Question and Answer required.'}), 400

    # Manually append to the primary knowledge file
    with open(os.path.join(KNOWLEDGE_DIR, "general.txt"), "a", encoding="utf-8") as f:
        f.write(f"\n{question}\n{answer}\n")
    
    # Trigger a Brain Sync
    brain.train([question.lower()], [answer])
    joblib.dump(brain, BRAIN_FILE)
    
    return jsonify({'status': 'Intelligence synchronized. Conceptual weights updated.'})

# =========================
# CAMERA STREAM
# =========================

def generate_frames():
    while True:
        try:
            frame = get_jpeg()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except:
            break

@app.route('/camera')
def camera_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/snapshot')
def snapshot():
    try:
        frame = get_jpeg()
        return Response(frame, mimetype='image/jpeg')
    except Exception as e:
        return f"Camera error: {e}", 500

@app.route('/scan_network', methods=['POST'])
def scan_network():
    """
    Scans the local network for devices using nmap to allow Sir to select a target.
    """
    try:
        # Discover the local subnet dynamically
        subnet = "10.74.24.0/24"  # Default fallback
        try:
            route_output = subprocess.check_output("ip route show", shell=True, text=True)
            device = None
            for line in route_output.splitlines():
                if line.startswith("default "):
                    parts = line.split()
                    if "dev" in parts:
                        idx = parts.index("dev")
                        if idx + 1 < len(parts):
                            device = parts[idx + 1]
                            break
            if device:
                for line in route_output.splitlines():
                    parts = line.split()
                    if len(parts) > 0 and "/" in parts[0] and "dev" in parts:
                        idx = parts.index("dev")
                        if idx + 1 < len(parts) and parts[idx + 1] == device:
                            subnet = parts[0]
                            break
        except Exception as subnet_err:
            print(f"Subnet discovery error: {subnet_err}")

        print(f"[*] Dynamic subnet scan: nmap -sn {subnet}")
        output = subprocess.check_output(f"nmap -sn {subnet}", shell=True, text=True)
        devices = []
        lines = output.split('\n')
        for i in range(len(lines)):
            if "Nmap scan report for" in lines[i]:
                ip = lines[i].split()[-1].strip("()")
                name = "Unknown Device"
                if "for " in lines[i]:
                    name_part = lines[i].split("for ")[1]
                    if "(" in name_part:
                        name = name_part.split(" (")[0]
                    else:
                        name = name_part
                devices.append({'ip': ip, 'name': name})
        
        if not devices:
            devices = [{'ip': '10.11.48.180', 'name': 'A06 Beacon (Detection Failed)'}]
            
        return jsonify(devices)
    except Exception as e:
        print(f"SCAN ERROR: {e}")
        return jsonify([{'ip': '10.74.24.97', 'name': 'Self (Fallback)'}])

# =========================
# STARTUP
# =========================

if __name__ == "__main__":
    print("\nSEA ONLINE (UNIFIED THINKING MODE)\n")
    speak("SEA online.")
    
    # Run Flask
    app.run(host='0.0.0.0', port=5000, debug=False)
