import streamlit as st
import hashlib
import json
import os

for key, default in [
    ("page","home"),("name",""),("subject",""),
    ("score",0),("answers",{}),("logged_in",False),("username",""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

st.set_page_config(page_title="Quizify", layout="wide", page_icon="⚡")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800;900&family=Exo+2:wght@300;400;500;600;700;800&display=swap');

/* ══════════════════════════════════════
   BASE
══════════════════════════════════════ */
html, body, [class*="css"] { font-family:'Exo 2', sans-serif; }

.stApp {
    background: #020b18 !important;
    min-height: 100vh;
}

/* Animated grid */
.stApp::before {
    content:'';
    position:fixed; inset:0;
    background-image:
        linear-gradient(rgba(0,210,255,0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,210,255,0.045) 1px, transparent 1px);
    background-size:55px 55px;
    animation:gridMove 20s linear infinite;
    z-index:0; pointer-events:none;
}
@keyframes gridMove {
    from { background-position:0 0; }
    to   { background-position:0 55px; }
}

/* Ambient glows */
.stApp::after {
    content:'';
    position:fixed; inset:0;
    background:
        radial-gradient(ellipse 55% 45% at 8% 15%, rgba(0,180,255,0.10) 0%, transparent 65%),
        radial-gradient(ellipse 45% 40% at 92% 75%, rgba(0,80,200,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 35% 30% at 50% 5%,  rgba(0,255,200,0.06) 0%, transparent 55%);
    z-index:0; pointer-events:none;
    animation:glowPulse 8s ease-in-out infinite alternate;
}
@keyframes glowPulse {
    0%   { opacity:0.7; }
    100% { opacity:1.0; }
}

.block-container {
    position:relative; z-index:2;
    padding:0 52px 80px !important;
    max-width:1060px !important;
    margin:0 auto !important;
}

/* ══════════════════════════════════════
   FLOATING PARTICLES
══════════════════════════════════════ */
.particles { position:fixed; inset:0; pointer-events:none; z-index:1; overflow:hidden; }
.p { position:absolute; border-radius:50%; animation:floatUp linear infinite; opacity:0; }
.p1  {width:3px;height:3px;background:#00d2ff;left:8%;  animation-duration:9s; animation-delay:0s;}
.p2  {width:2px;height:2px;background:#0080ff;left:22%; animation-duration:13s;animation-delay:2s;}
.p3  {width:4px;height:4px;background:#00ffcc;left:38%; animation-duration:10s;animation-delay:4s;}
.p4  {width:2px;height:2px;background:#ffffff;left:52%; animation-duration:15s;animation-delay:1s;}
.p5  {width:3px;height:3px;background:#0080ff;left:68%; animation-duration:11s;animation-delay:3s;}
.p6  {width:2px;height:2px;background:#00d2ff;left:82%; animation-duration:13s;animation-delay:5s;}
.p7  {width:3px;height:3px;background:#ffffff;left:18%; animation-duration:16s;animation-delay:7s;}
.p8  {width:4px;height:4px;background:#00d2ff;left:58%; animation-duration:8s; animation-delay:2.5s;}
.p9  {width:2px;height:2px;background:#0080ff;left:91%; animation-duration:10s;animation-delay:6s;}
.p10 {width:3px;height:3px;background:#00ffcc;left:4%;  animation-duration:14s;animation-delay:4s;}
@keyframes floatUp {
    0%   {transform:translateY(105vh) scale(0); opacity:0;}
    8%   {opacity:0.9;}
    92%  {opacity:0.5;}
    100% {transform:translateY(-5vh) scale(1.2); opacity:0;}
}

/* ══════════════════════════════════════
   LOGO
══════════════════════════════════════ */
.logo-area { text-align:center; padding:38px 0 10px; }
.logo-main {
    font-family:'Orbitron', monospace;
    font-size:3.5rem; font-weight:900;
    letter-spacing:8px; text-transform:uppercase;
    background:linear-gradient(90deg, #00d2ff 0%, #00ffcc 40%, #0080ff 70%, #00d2ff 100%);
    background-size:250% auto;
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
    animation:logoShimmer 4s linear infinite;
    filter:drop-shadow(0 0 24px rgba(0,210,255,0.55));
}
@keyframes logoShimmer {
    0%   { background-position:250% center; }
    100% { background-position:-250% center; }
}
.logo-tagline {
    font-family:'Exo 2', sans-serif;
    font-size:0.72rem; letter-spacing:5px; text-transform:uppercase;
    color:rgba(0,210,255,0.45); margin-top:6px;
}
.logo-rule {
    width:130px; height:1px; margin:12px auto 0;
    background:linear-gradient(90deg, transparent, #00d2ff, transparent);
    box-shadow:0 0 10px #00d2ff;
    animation:ruleBlink 2.5s ease-in-out infinite alternate;
}
@keyframes ruleBlink { 0%{opacity:0.4;} 100%{opacity:1;} }

/* ══════════════════════════════════════
   PAGE TITLES
══════════════════════════════════════ */
.pg-title {
    font-family:'Orbitron', monospace;
    font-size:1.9rem; font-weight:700;
    color:#ffffff; text-align:center;
    margin:22px 0 6px; letter-spacing:4px;
    text-transform:uppercase;
    text-shadow:0 0 25px rgba(0,210,255,0.7), 0 0 50px rgba(0,210,255,0.3);
}
.pg-sub {
    font-size:0.85rem; text-align:center;
    color:rgba(0,210,255,0.5);
    letter-spacing:3px; text-transform:uppercase;
    margin-bottom:34px; font-weight:500;
}

/* ══════════════════════════════════════
   SUBJECT CHIPS
══════════════════════════════════════ */
.chip-row {
    display:flex; flex-wrap:wrap; gap:10px;
    justify-content:center; margin-bottom:34px;
}
.chip {
    background:rgba(0,210,255,0.06);
    border:1px solid rgba(0,210,255,0.22);
    border-radius:3px;
    padding:7px 17px;
    font-size:0.75rem; font-weight:600;
    color:rgba(0,210,255,0.75);
    letter-spacing:2px; text-transform:uppercase;
    transition:all 0.2s;
}
.chip:hover {
    background:rgba(0,210,255,0.14);
    border-color:#00d2ff; color:#00d2ff;
    box-shadow:0 0 14px rgba(0,210,255,0.25);
}

/* ══════════════════════════════════════
   HERO CARDS
══════════════════════════════════════ */
.hero-grid {
    display:grid; grid-template-columns:1fr 1fr;
    gap:22px; max-width:880px; margin:0 auto 44px;
}
.hero-cell {
    background:rgba(0,18,38,0.9);
    border:1px solid rgba(0,210,255,0.18);
    border-radius:4px; padding:46px 32px; text-align:center;
    position:relative; overflow:hidden;
    transition:all 0.3s; cursor:default;
    box-shadow:0 8px 32px rgba(0,0,0,0.4);
}
.hero-cell:hover {
    border-color:rgba(0,210,255,0.55);
    box-shadow:0 0 40px rgba(0,210,255,0.1), 0 8px 32px rgba(0,0,0,0.5);
    transform:translateY(-5px);
}
/* corner brackets */
.hero-cell::before, .hero-cell::after {
    content:''; position:absolute; width:14px; height:14px;
    border-color:rgba(0,210,255,0.6); border-style:solid;
}
.hero-cell::before { top:-1px; left:-1px; border-width:2px 0 0 2px; }
.hero-cell::after  { bottom:-1px; right:-1px; border-width:0 2px 2px 0; }
/* scan sweep */
.scan {
    position:absolute; top:0; left:-80%; width:50%; height:100%;
    background:linear-gradient(90deg, transparent, rgba(0,210,255,0.05), transparent);
    animation:sweep 4s ease-in-out infinite;
}
.hero-cell:nth-child(2) .scan { animation-delay:2s; }
@keyframes sweep { 0%{left:-80%;} 100%{left:160%;} }
.hero-icon { font-size:3rem; display:block; margin-bottom:14px; filter:drop-shadow(0 0 12px rgba(0,210,255,0.5)); }
.hero-h {
    font-family:'Orbitron',monospace; font-size:1rem; font-weight:700;
    letter-spacing:3px; text-transform:uppercase;
    color:#00d2ff; margin-bottom:10px;
    text-shadow:0 0 15px rgba(0,210,255,0.6);
}
.hero-p { font-size:0.88rem; color:rgba(255,255,255,0.45); line-height:1.65; }

/* ══════════════════════════════════════
   GLASS PANEL (login/signup forms)
══════════════════════════════════════ */
.glass-panel {
    background:rgba(0,18,38,0.85);
    border:1px solid rgba(0,210,255,0.22);
    border-radius:4px; padding:48px 44px;
    margin:0 auto 40px; max-width:480px;
    position:relative; overflow:hidden;
    box-shadow:0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(0,210,255,0.04);
    animation:panelIn 0.45s ease;
}
/* corner brackets */
.glass-panel::before, .glass-panel::after {
    content:''; position:absolute; width:16px; height:16px;
    border-color:#00d2ff; border-style:solid;
}
.glass-panel::before { top:-1px; left:-1px; border-width:2px 0 0 2px; box-shadow:-4px -4px 12px rgba(0,210,255,0.2); }
.glass-panel::after  { bottom:-1px; right:-1px; border-width:0 2px 2px 0; box-shadow:4px 4px 12px rgba(0,210,255,0.2); }
@keyframes panelIn { from{opacity:0;transform:translateY(20px);} to{opacity:1;transform:none;} }
.panel-title {
    font-family:'Orbitron',monospace; font-size:1.2rem; font-weight:700;
    color:#00d2ff; text-align:center; margin-bottom:30px;
    letter-spacing:4px; text-transform:uppercase;
    text-shadow:0 0 20px rgba(0,210,255,0.6);
}

/* ══════════════════════════════════════
   BUTTONS
══════════════════════════════════════ */
.stButton > button {
    font-family:'Orbitron', monospace !important;
    font-size:0.78rem !important; font-weight:700 !important;
    letter-spacing:3px !important; text-transform:uppercase !important;
    padding:15px 24px !important; border-radius:3px !important;
    border:1px solid rgba(0,210,255,0.7) !important;
    background:rgba(0,210,255,0.06) !important;
    color:#00d2ff !important; width:100% !important;
    transition:all 0.22s ease !important; cursor:pointer !important;
    text-shadow:0 0 10px rgba(0,210,255,0.5) !important;
    box-shadow:0 0 18px rgba(0,210,255,0.08), inset 0 0 18px rgba(0,210,255,0.03) !important;
}
.stButton > button:hover {
    background:rgba(0,210,255,0.14) !important;
    border-color:#00d2ff !important;
    box-shadow:0 0 30px rgba(0,210,255,0.3), inset 0 0 20px rgba(0,210,255,0.06) !important;
    color:#ffffff !important;
    text-shadow:0 0 16px #00d2ff !important;
    transform:translateY(-2px) !important;
}
.stButton > button:active { transform:translateY(1px) !important; }

/* ══════════════════════════════════════
   FORM INPUTS
══════════════════════════════════════ */
.stTextInput label, .stSelectbox label {
    font-family:'Orbitron', monospace !important;
    font-size:0.65rem !important; font-weight:600 !important;
    color:rgba(0,210,255,0.55) !important;
    text-transform:uppercase !important; letter-spacing:2.5px !important;
}
.stTextInput > div > div > input {
    background:rgba(0,210,255,0.04) !important;
    border:1px solid rgba(0,210,255,0.25) !important;
    border-radius:3px !important;
    font-size:0.98rem !important; padding:14px 18px !important;
    color:#00d2ff !important; font-weight:600 !important;
    font-family:'Exo 2', sans-serif !important;
    transition:all 0.22s !important; letter-spacing:0.5px !important;
}
.stTextInput > div > div > input::placeholder { color:rgba(0,210,255,0.25) !important; }
/* Force input typed text to be visible — NOT black */
.stTextInput input, .stTextInput > div > div > input, input[type="text"], input[type="password"] {
    color:#00d2ff !important;
    -webkit-text-fill-color:#00d2ff !important;
    caret-color:#00d2ff !important;
}
.stTextInput > div > div > input:focus {
    border-color:#00d2ff !important;
    box-shadow:0 0 22px rgba(0,210,255,0.18), inset 0 0 12px rgba(0,210,255,0.04) !important;
    background:rgba(0,210,255,0.07) !important; outline:none !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background:rgba(0,210,255,0.04) !important;
    border:1px solid rgba(0,210,255,0.25) !important;
    border-radius:3px !important;
    color:#00d2ff !important; font-family:'Exo 2',sans-serif !important;
    transition:all 0.22s !important;
}
.stSelectbox > div > div:focus-within,
.stSelectbox > div > div:hover {
    border-color:#00d2ff !important;
    box-shadow:0 0 18px rgba(0,210,255,0.18) !important;
}
.stSelectbox span { color:#00d2ff !important; }

/* ══════════════════════════════════════
   RADIO OPTIONS  ← FULLY FIXED
══════════════════════════════════════ */

/* Hide ONLY the widget-level label (the blank "" box), not the option labels */
div[data-testid="stRadio"] > div > label:first-child { display:none !important; }
[data-testid="stWidgetLabel"] { display:none !important; }

/* Style the radio option container rows */
div[data-testid="stRadio"] > div { gap:12px !important; display:flex !important; flex-direction:column !important; }

/* Each option wrapper */
div[data-testid="stRadio"] > div > div {
    background:rgba(255,255,255,0.04) !important;
    border:1.5px solid rgba(0,210,255,0.25) !important;
    border-radius:8px !important;
    transition:all 0.22s ease !important;
    position:relative !important;
    overflow:hidden !important;
}
div[data-testid="stRadio"] > div > div:hover {
    background:rgba(0,210,255,0.1) !important;
    border-color:#00d2ff !important;
    box-shadow:0 0 20px rgba(0,210,255,0.15), inset 0 0 20px rgba(0,210,255,0.04) !important;
    transform:translateX(6px) !important;
}

/* Option text — fully visible with #015c77 color */
div[data-testid="stRadio"] > div > div label {
    display:flex !important;
    align-items:center !important;
    padding:16px 22px !important;
    cursor:pointer !important;
    width:100% !important;
    color:#015c77 !important;
    font-size:1rem !important;
    font-weight:700 !important;
    font-family:'Exo 2', sans-serif !important;
    letter-spacing:0.4px !important;
    line-height:1.4 !important;
    background:transparent !important;
    border:none !important;
    border-radius:0 !important;
}

/* Target every possible inner element Streamlit uses for radio text */
div[data-testid="stRadio"] > div > div label p,
div[data-testid="stRadio"] > div > div label div,
div[data-testid="stRadio"] > div > div label span:last-child,
div[data-testid="stRadio"] > div > div label span:not(:first-child),
div[data-testid="stRadio"] p,
div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
    color:#015c77 !important;
    font-size:1rem !important;
    font-weight:700 !important;
}

/* Radio circle dot styling */
div[data-testid="stRadio"] > div > div label span:first-child {
    border-color:rgba(0,210,255,0.5) !important;
    width:18px !important; height:18px !important;
    min-width:18px !important; margin-right:14px !important;
    flex-shrink:0 !important;
}

/* ══════════════════════════════════════
   QUESTION CARD
══════════════════════════════════════ */
.qcard {
    background:rgba(0,15,32,0.92);
    border:1px solid rgba(0,210,255,0.18);
    border-radius:10px; padding:28px 32px 22px;
    margin-bottom:6px; position:relative; overflow:hidden;
    box-shadow:0 4px 24px rgba(0,0,0,0.35);
    animation:panelIn 0.4s ease;
}
.qcard::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg, transparent 0%, #00d2ff 50%, transparent 100%);
    box-shadow:0 0 12px #00d2ff;
}
.qcard:hover { border-color:rgba(0,210,255,0.38); }
.qbadge {
    display:inline-flex; align-items:center; gap:6px;
    background:rgba(0,210,255,0.1); border:1px solid rgba(0,210,255,0.4);
    color:#00d2ff; font-family:'Orbitron',monospace;
    font-size:0.62rem; font-weight:700; padding:5px 14px;
    border-radius:3px; letter-spacing:2.5px; text-transform:uppercase;
    margin-bottom:14px; text-shadow:0 0 10px rgba(0,210,255,0.5);
}
.qtext {
    font-size:1.15rem; font-weight:700; color:#ffffff;
    line-height:1.5; font-family:'Exo 2',sans-serif; letter-spacing:0.2px;
}

/* ══════════════════════════════════════
   PROGRESS BAR
══════════════════════════════════════ */
.prog-wrap {
    background:rgba(0,210,255,0.08);
    border:1px solid rgba(0,210,255,0.2);
    border-radius:3px; height:8px;
    max-width:900px; margin:0 auto 30px; overflow:hidden;
}
.prog-fill {
    height:100%; border-radius:3px;
    background:linear-gradient(90deg, #0050c8, #00d2ff, #00ffcc);
    box-shadow:0 0 16px rgba(0,210,255,0.7);
    transition:width 0.5s ease;
    animation:glowBar 2s ease-in-out infinite alternate;
}
@keyframes glowBar { 0%{box-shadow:0 0 8px #00d2ff;} 100%{box-shadow:0 0 24px #00d2ff, 0 0 40px rgba(0,210,255,0.4);} }

/* ══════════════════════════════════════
   STATS ROW
══════════════════════════════════════ */
.stats-row { display:flex; justify-content:center; gap:14px; flex-wrap:wrap; margin-bottom:26px; }
.stat {
    background:rgba(0,210,255,0.06);
    border:1px solid rgba(0,210,255,0.22);
    border-radius:3px; padding:8px 20px;
    font-family:'Orbitron',monospace; font-size:0.65rem;
    color:rgba(0,210,255,0.6); letter-spacing:2px; text-transform:uppercase;
}
.stat b { color:#00d2ff; font-weight:800; text-shadow:0 0 8px rgba(0,210,255,0.7); }

/* ══════════════════════════════════════
   RESULT
══════════════════════════════════════ */
.result-wrap { max-width:640px; margin:0 auto 40px; animation:panelIn 0.6s ease; }
.result-hero {
    background:rgba(0,12,28,0.97);
    border:1px solid rgba(0,210,255,0.35);
    border-radius:10px 10px 0 0;
    padding:60px 44px 50px; text-align:center;
    position:relative; overflow:hidden;
}
.result-hero::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    background:linear-gradient(90deg, #0050c8, #00d2ff, #00ffcc, #00d2ff, #0050c8);
    background-size:200% auto; animation:shimmerLine 3s linear infinite;
    box-shadow:0 0 20px #00d2ff;
}
@keyframes shimmerLine { 0%{background-position:200%;} 100%{background-position:-200%;} }
.result-grid {
    position:absolute; inset:0; pointer-events:none;
    background-image:
        linear-gradient(rgba(0,210,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,210,255,0.025) 1px, transparent 1px);
    background-size:28px 28px;
}
.result-emoji { font-size:4.5rem; display:block; margin-bottom:12px; filter:drop-shadow(0 0 18px rgba(0,210,255,0.6)); }
.result-status {
    font-family:'Orbitron',monospace; font-size:0.7rem; letter-spacing:6px;
    color:rgba(0,210,255,0.6); text-transform:uppercase; margin-bottom:18px;
}
.result-num {
    font-family:'Orbitron',monospace; font-size:7rem; font-weight:900;
    color:#00d2ff; line-height:1;
    text-shadow:0 0 40px rgba(0,210,255,0.9), 0 0 80px rgba(0,210,255,0.4);
    animation:numGlow 2.5s ease-in-out infinite alternate;
}
@keyframes numGlow { 0%{text-shadow:0 0 30px rgba(0,210,255,0.8);} 100%{text-shadow:0 0 60px #00d2ff, 0 0 100px rgba(0,150,255,0.5);} }
.result-denom { font-family:'Exo 2',sans-serif; font-size:1.05rem; color:rgba(255,255,255,0.38); margin-top:6px; letter-spacing:2px; }
.result-footer {
    background:rgba(0,6,18,0.97);
    border:1px solid rgba(0,210,255,0.2); border-top:none;
    border-radius:0 0 10px 10px;
    padding:22px 36px; text-align:center;
}
.result-label { font-family:'Orbitron',monospace; font-size:0.7rem; letter-spacing:3px; color:rgba(0,210,255,0.45); text-transform:uppercase; }
.result-label span { color:#00d2ff; font-weight:700; }

/* ══════════════════════════════════════
   MISC
══════════════════════════════════════ */
.ndiv { border:none; border-top:1px solid rgba(0,210,255,0.12); margin:24px 0; }

/* Scanlines */
.scanlines {
    position:fixed; inset:0; pointer-events:none; z-index:9999;
    background:repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,0,0,0.025) 3px, rgba(0,0,0,0.025) 4px);
}

#MainMenu, footer, header { visibility:hidden; }
.stDeployButton { display:none !important; }
</style>

<div class="scanlines"></div>
<div class="particles">
  <div class="p p1"></div><div class="p p2"></div><div class="p p3"></div>
  <div class="p p4"></div><div class="p p5"></div><div class="p p6"></div>
  <div class="p p7"></div><div class="p p8"></div><div class="p p9"></div>
  <div class="p p10"></div>
</div>
""", unsafe_allow_html=True)

# ── User Store ─────────────────────────────────
USERS_FILE = "quizify_users.json"
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f: return json.load(f)
    return {}
def save_users(u):
    with open(USERS_FILE,"w") as f: json.dump(u,f)
def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()

# ── Questions ───────────────────────────────────
questions = {
    "Java": [
        ("What is the default value of an int in Java?",["null","0","1","-1"],"0"),
        ("Which keyword is used to inherit a class?",["implements","extends","inherits","super"],"extends"),
        ("What does JVM stand for?",["Java Virtual Machine","Java Variable Method","Java Verified Module","Java Version Manager"],"Java Virtual Machine"),
        ("Entry point method of a Java program?",["start()","run()","main()","init()"],"main()"),
        ("Which is NOT a Java primitive type?",["int","boolean","String","char"],"String"),
        ("Size of an int in Java?",["2 bytes","4 bytes","8 bytes","16 bytes"],"4 bytes"),
        ("Keyword that prevents method overriding?",["static","final","abstract","private"],"final"),
        ("What does OOP stand for?",["Object Oriented Programming","Out Of Place","Open Online Platform","Optional Object Parameter"],"Object Oriented Programming"),
        ("Which collection allows duplicates?",["Set","Map","List","HashSet"],"List"),
        ("Parent class of all Java classes?",["Base","Root","Object","Super"],"Object"),
    ],
    "C++": [
        ("What does 'cout' do in C++?",["Reads input","Prints output","Declares variable","Loops"],"Prints output"),
        ("Pointer member access operator?",[".","::", "->","*"],"->"),
        ("C++ source file extension?",  [".c",".java",".cpp",".py"],".cpp"),
        ("Which is NOT an OOP concept?",["Encapsulation","Polymorphism","Compilation","Inheritance"],"Compilation"),
        ("What is a destructor?",["Allocates memory","Deletes a class","Cleans up object on destroy","Creates a copy"],"Cleans up object on destroy"),
        ("Dynamic memory allocation keyword?",["malloc","new","alloc","create"],"new"),
        ("What does 'cin' stand for?",["Console In","Character Input","Code In","Class Input"],"Console In"),
        ("C++ reference declaration?",["int* x","int& x","int[] x","int@ x"],"int& x"),
        ("What is a template in C++?",["Design pattern","Class blueprint","Generic programming feature","Header file"],"Generic programming feature"),
        ("What is 'std' in 'std::cout'?",["Standard library namespace","String data","Static declaration","Structured type"],"Standard library namespace"),
    ],
    "Python": [
        ("Output of print(2 ** 3)?",["6","8","9","5"],"8"),
        ("Keyword to define a function?",["func","define","def","fun"],"def"),
        ("What data type is []?",["tuple","dict","set","list"],"list"),
        ("Result of len('hello')?",["4","5","6","hello"],"5"),
        ("Single-line comment symbol?",["//","#","--","/*"],"#"),
        ("Output of type(3.14)?",["<class 'int'>","<class 'str'>","<class 'float'>","<class 'num'>"],"<class 'float'>"),
        ("Keyword for loops?",["repeat","loop","for","iterate"],"for"),
        ("Create a dictionary in Python?",["[]","()","{}","<>"],"{}"),
        ("What does 'None' represent?",["0","False","Empty string","Null/no value"],"Null/no value"),
        ("What is a lambda?",["A loop","An anonymous function","A class","A module"],"An anonymous function"),
    ],
    "JavaScript": [
        ("Declare a constant in JS?",["var","let","const","static"],"const"),
        ("DOM stands for?",["Document Object Model","Data Object Method","Dynamic Output Mode","Display Object Map"],"Document Object Model"),
        ("typeof null returns?",["'null'","'undefined'","'object'","'boolean'"],"'object'"),
        ("Add element to END of array?",["push()","pop()","shift()","unshift()"],"push()"),
        ("What does === check?",["Value only","Type only","Value and type","Reference"],"Value and type"),
        ("Who created JavaScript?",["Microsoft","Google","Netscape","Apple"],"Netscape"),
        ("What is a closure?",["A loop construct","Close browser","Function with outer scope access","Error handler"],"Function with outer scope access"),
        ("JS comment syntax?",["# comment","<!-- -->","// comment","** comment"],"// comment"),
        ("JSON stands for?",["Java Syntax Object Notation","JavaScript Object Notation","Java Standard Output Name","JSON Script Object Node"],"JavaScript Object Notation"),
        ("Remove LAST array element?",["shift()","pop()","splice()","remove()"],"pop()"),
    ],
    "CSS": [
        ("CSS stands for?",["Creative Style Sheets","Cascading Style Sheets","Computer Style System","Colorful Style Syntax"],"Cascading Style Sheets"),
        ("Property to change text color?",["font-color","text-color","color","foreground"],"color"),
        ("Select element with id='box'?",[".box","#box","*box","box"],"#box"),
        ("Invisible but still in flow?",["display:none","visibility:hidden","opacity:1","hidden:true"],"visibility:hidden"),
        ("Flexbox helps with?",["Animations","Responsive layout","Colors","Typography"],"Responsive layout"),
        ("Spacing INSIDE an element?",["margin","border","padding","spacing"],"padding"),
        ("Style ALL paragraphs?",["#p",".p","p","*p"],"p"),
        ("Correct CSS syntax?",["p {color; red}","p: color=red","p {color: red;}","{p color: red}"],"p {color: red;}"),
        ("Set background color?",["bg-color","background-color","bgcolor","color-bg"],"background-color"),
        ("z-index controls?",["Zoom level","Stacking order","Font size","Border width"],"Stacking order"),
    ],
    "HTML": [
        ("HTML stands for?",["Hyper Text Makeup Language","Hyper Text Markup Language","High Text Modern Language","Home Tool Markup Language"],"Hyper Text Markup Language"),
        ("Tag for hyperlinks?",["<link>","<a>","<href>","<url>"],"<a>"),
        ("Largest heading tag?",["<h6>","<head>","<h1>","<title>"],"<h1>"),
        ("Ordered list tag?",["<ul>","<li>","<ol>","<list>"],"<ol>"),
        ("HTML line break?",["<break>","<lb>","<newline>","<br>"],"<br>"),
        ("Image source attribute?",["href","src","url","link"],"src"),
        ("Body of webpage tag?",["<main>","<section>","<body>","<content>"],"<body>"),
        ("Paragraph tag?",["<para>","<txt>","<p>","<text>"],"<p>"),
        ("Embed JavaScript file?",["<js>","<javascript>","<script>","<code>"],"<script>"),
        ("Link external CSS?",["<style>","<css>","<link>","<stylesheet>"],"<link>"),
    ],
    "Next.js": [
        ("Next.js is built on top of?",["Angular","Vue","React","Svelte"],"React"),
        ("Pages folder (Pages Router)?",["/src","/components","/pages","/views"],"/pages"),
        ("SSR stands for?",["Static Site Rendering","Server Side Rendering","Simple Script Runner","Style Sheet Rendering"],"Server Side Rendering"),
        ("Next.js config file?",["package.json","next.config.js","app.config.js","server.js"],"next.config.js"),
        ("getStaticProps is used for?",["Client-side fetching","Fetch data at build time","API routing","Middleware"],"Fetch data at build time"),
        ("ISR stands for?",["Instant Script Refresh","Incremental Static Regeneration","Internal Server Response","Initial State Render"],"Incremental Static Regeneration"),
        ("Newer router in Next.js?",["Pages Router","App Router","File Router","Link Router"],"App Router"),
        ("Purpose of _app.js?",["API route handler","Global layout wrapper","Static config","Middleware"],"Global layout wrapper"),
        ("Create an API route in Next.js?",["In /services","In /pages/api","In /routes","In /controllers"],"In /pages/api"),
        ("Who created Next.js?",["Meta","Google","Microsoft","Vercel"],"Vercel"),
    ],
}

ICONS = {"Java":"☕","C++":"⚙️","Python":"🐍","JavaScript":"⚡","CSS":"🎨","HTML":"🌐","Next.js":"▲"}

def logo():
    st.markdown("""
    <div class="logo-area">
      <div class="logo-main">QUIZIFY</div>
      <div class="logo-tagline">Neural Knowledge Assessment System</div>
      <div class="logo-rule"></div>
    </div>""", unsafe_allow_html=True)

def chips():
    st.markdown("""
    <div class="chip-row">
      <span class="chip">☕ Java</span><span class="chip">⚙️ C++</span>
      <span class="chip">🐍 Python</span><span class="chip">⚡ JavaScript</span>
      <span class="chip">🎨 CSS</span><span class="chip">🌐 HTML</span>
      <span class="chip">▲ Next.js</span>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════ HOME ═══════════════════════
if st.session_state.page == "home":
    logo()
    chips()
    st.markdown("""
    <div class="hero-grid">
      <div class="hero-cell">
        <div class="scan"></div>
        <span class="hero-icon">🧠</span>
        <div class="hero-h">Neural Quiz</div>
        <div class="hero-p">Test your programming knowledge across 7 languages with 10 expert-crafted questions each</div>
      </div>
      <div class="hero-cell">
        <div class="scan"></div>
        <span class="hero-icon">🏆</span>
        <div class="hero-h">Rank Up</div>
        <div class="hero-p">Score 9/10 to achieve SUPERSTAR status. Conquer every subject and level up your skills</div>
      </div>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("[ LOGIN ]", use_container_width=True):
            st.session_state.page = "login"; st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("[ SIGN UP ]", use_container_width=True):
            st.session_state.page = "signup"; st.rerun()

# ═══════════════════════════ SIGNUP ═════════════════════
elif st.session_state.page == "signup":
    logo()
    st.markdown('<div class="pg-title">Initialize Account</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Create your neural profile</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        n  = st.text_input("Full Name",        placeholder="Your full name",    key="sn")
        u  = st.text_input("Username",         placeholder="Choose username",    key="su")
        p  = st.text_input("Password",         placeholder="Create password",    type="password", key="sp")
        cp = st.text_input("Confirm Password", placeholder="Confirm password",   type="password", key="scp")
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("[ BACK ]", use_container_width=True, key="sbk"):
                st.session_state.page = "home"; st.rerun()
        with c2:
            if st.button("[ REGISTER ]", use_container_width=True, key="srg"):
                users = load_users()
                if not all([n, u, p]):   st.warning("⚠ All fields required")
                elif p != cp:            st.warning("⚠ Passwords do not match")
                elif u in users:         st.warning("⚠ Username already taken")
                else:
                    users[u] = {"name": n, "password": hash_pw(p)}
                    save_users(users)
                    st.success("✓ Profile created. Proceed to login.")
                    st.session_state.page = "login"; st.rerun()
        st.markdown("<hr class='ndiv'>", unsafe_allow_html=True)
        st.markdown("<center style='color:rgba(0,210,255,0.35);font-size:0.72rem;letter-spacing:2px;font-family:Orbitron,monospace;'>EXISTING PROFILE?</center>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("[ LOGIN INSTEAD ]", use_container_width=True, key="sli"):
            st.session_state.page = "login"; st.rerun()

# ═══════════════════════════ LOGIN ══════════════════════
elif st.session_state.page == "login":
    logo()
    st.markdown('<div class="pg-title">Access Terminal</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Authenticate to enter</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        u = st.text_input("Username", placeholder="Enter username", key="lu")
        p = st.text_input("Password", placeholder="Enter password", type="password", key="lp")
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("[ BACK ]", use_container_width=True, key="lbk"):
                st.session_state.page = "home"; st.rerun()
        with c2:
            if st.button("[ ACCESS ]", use_container_width=True, key="lac"):
                users = load_users()
                if u in users and users[u]["password"] == hash_pw(p):
                    st.session_state.logged_in = True
                    st.session_state.username  = u
                    st.session_state.name      = users[u]["name"]
                    st.session_state.page      = "info"; st.rerun()
                else:
                    st.warning("⚠ Access denied — invalid credentials")
        st.markdown("<hr class='ndiv'>", unsafe_allow_html=True)
        st.markdown("<center style='color:rgba(0,210,255,0.35);font-size:0.72rem;letter-spacing:2px;font-family:Orbitron,monospace;'>NO PROFILE YET?</center>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("[ CREATE ACCOUNT ]", use_container_width=True, key="lca"):
            st.session_state.page = "signup"; st.rerun()

# ═══════════════════════════ INFO ═══════════════════════
elif st.session_state.page == "info":
    if not st.session_state.logged_in:
        st.session_state.page = "home"; st.rerun()
    logo()
    chips()
    st.markdown(f'<div class="pg-title">WELCOME, {st.session_state.name.upper()}</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Select subject module to begin</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        subj = st.selectbox("Select Module", list(ICONS.keys()),
                            format_func=lambda x: f"{ICONS[x]}  {x}", key="ss")
        st.session_state.subject = subj
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("[ LOGOUT ]", use_container_width=True):
                for k in ["logged_in","username","name","subject","score","answers"]:
                    st.session_state[k] = "" if k in ["username","name","subject"] else (False if k=="logged_in" else (0 if k=="score" else {}))
                st.session_state.page = "home"; st.rerun()
        with c2:
            if st.button("[ LAUNCH QUIZ ]", use_container_width=True):
                st.session_state.page = "quiz"
                st.session_state.score = 0
                st.session_state.answers = {}; st.rerun()

# ═══════════════════════════ QUIZ ═══════════════════════
elif st.session_state.page == "quiz":
    if not st.session_state.logged_in:
        st.session_state.page = "home"; st.rerun()
    logo()
    subj = st.session_state.subject
    icon = ICONS.get(subj, "📚")
    cqs  = questions[subj]
    answered = sum(1 for i in range(len(cqs)) if f"q_{i}" in st.session_state.answers)
    pct = int((answered / len(cqs)) * 100)

    st.markdown(f'<div class="pg-title">{icon} {subj.upper()} MODULE</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="stats-row">
      <div class="stat">Operator: <b>{st.session_state.name}</b></div>
      <div class="stat">Questions: <b>{len(cqs)}</b></div>
      <div class="stat">Answered: <b>{answered}</b></div>
      <div class="stat">Progress: <b>{pct}%</b></div>
    </div>
    <div class="prog-wrap"><div class="prog-fill" style="width:{pct}%"></div></div>
    """, unsafe_allow_html=True)

    for i, (q, options, correct) in enumerate(cqs):
        st.markdown(f"""
        <div class="qcard">
          <div class="qbadge">// QUERY_{i+1:02d} &nbsp;·&nbsp; {subj.upper()}</div>
          <div class="qtext">{q}</div>
        </div>""", unsafe_allow_html=True)
        saved = options.index(st.session_state.answers[f"q_{i}"]) if f"q_{i}" in st.session_state.answers else None
        ans = st.radio("", options, key=f"q_{i}", index=saved, label_visibility="collapsed")
        if ans:
            st.session_state.answers[f"q_{i}"] = ans
        st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("[ ABORT ]", use_container_width=True):
            st.session_state.page = "info"; st.rerun()
    with c2:
        if st.button("[ SUBMIT ANSWERS ]", use_container_width=True):
            score = sum(1 for i in range(len(cqs))
                        if f"q_{i}" in st.session_state.answers
                        and st.session_state.answers[f"q_{i}"] == cqs[i][2])
            st.session_state.score = score
            st.session_state.page  = "result"; st.rerun()

# ═══════════════════════════ RESULT ═════════════════════
elif st.session_state.page == "result":
    logo()
    score = st.session_state.score
    total = len(questions[st.session_state.subject])
    icon  = ICONS.get(st.session_state.subject, "📚")
    p     = score / total

    if p >= 0.9:   emoji, msg = "🌟", "SUPERSTAR"
    elif p >= 0.7: emoji, msg = "🎯", "EXCELLENT"
    elif p >= 0.5: emoji, msg = "👍", "PASS"
    else:          emoji, msg = "⚡", "RETRY"

    st.markdown(f"""
    <div class="result-wrap">
      <div class="result-hero">
        <div class="result-grid"></div>
        <span class="result-emoji">{emoji}</span>
        <div class="result-status">// STATUS: {msg}</div>
        <div class="result-num">{score}</div>
        <div class="result-denom">OUT OF {total} &nbsp;·&nbsp; {icon} {st.session_state.subject.upper()}</div>
      </div>
      <div class="result-footer">
        <div class="result-label">Operator: <span>{st.session_state.name}</span></div>
      </div>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("[ HOME ]", use_container_width=True):
            st.session_state.score=0; st.session_state.answers={}
            st.session_state.page="info"; st.rerun()
    with col2:
        if st.button("[ RETRY ]", use_container_width=True):
            st.session_state.score=0; st.session_state.answers={}
            st.session_state.page="quiz"; st.rerun()
    with col3:
        if st.button("[ NEW MODULE ]", use_container_width=True):
            st.session_state.score=0; st.session_state.answers={}
            st.session_state.page="info"; st.rerun()