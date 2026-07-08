import streamlit as st
import sqlite3
import plotly.graph_objects as go
import hashlib
from datetime import date, datetime, timedelta
from search import search_food
from portions import scale_nutrition, PORTION_PRESETS
from tracking import log_entry, get_daily_summary, add_favourite, get_favourites, delete_entry, get_history
from barcode import lookup_barcode
from photo_estimation import estimate_from_photo
from geometry import (estimate_cylinder, estimate_cuboid, estimate_sphere,
                      estimate_ellipsoid, diameter_to_radius, DENSITY_TABLE)
from nutrition import estimate_nutrition_from_mass
from moroccan_foods import populate_moroccan_database
from database import init_db
import tempfile, os

st.set_page_config(page_title="Velora", layout="wide",
                   initial_sidebar_state="expanded")
init_db()
populate_moroccan_database()

# ── Icons ─────────────────────────────────────────────────────
def ic(name, sz=16, col="#8C8678"):
    S = f'width="{sz}" height="{sz}" viewBox="0 0 24 24" fill="none" stroke="{col}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
    icons = {
        "grid":    f'<svg {S}><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/></svg>',
        "history": f'<svg {S}><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
        "star":    f'<svg {S}><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
        "gear":    f'<svg {S}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
        "user":    f'<svg {S}><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
        "trash":   f'<svg {S}><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>',
        "plus":    f'<svg {S}><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
        "moon":    f'<svg {S}><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
        "target":  f'<svg {S}><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
        "globe":   f'<svg {S}><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
        "scale":   f'<svg {S}><path d="M12 3v18M3 9l9-6 9 6M5 21h14"/></svg>',
        "trend":   f'<svg {S}><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
        "lock":    f'<svg {S}><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
        "mail":    f'<svg {S}><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>',
        "check":   f'<svg {S}><polyline points="20 6 9 17 4 12"/></svg>',
        "crown":   f'<svg {S}><path d="M2 20h20M5 20L3 8l5 4 4-6 4 6 5-4-2 12"/></svg>',
        "camera":  f'<svg {S}><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>',
        "logout":  f'<svg {S}><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>',
        "back":    f'<svg {S}><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>',
        "barcode": f'<svg {S}><path d="M4 6v12M8 6v12M12 6v12M16 6v12M20 6v12M2 8h2M2 16h2M20 8h2M20 16h2"/></svg>',
    }
    return icons.get(name, "")

# ── Translations ──────────────────────────────────────────────
LANG = {
    "en": {
        "daily_log":"Daily Log","daily_sub":"Today's nutrition",
        "history":"History","history_sub":"Past meals & trends",
        "favourites":"Favourites","fav_sub":"Your saved foods",
        "settings":"Settings","settings_sub":"Preferences & profile",
        "breakfast":"Breakfast","lunch":"Lunch","dinner":"Dinner","snack":"Snack",
        "calories":"Calories","protein":"Protein","carbs":"Carbs","fat":"Fat",
        "nothing_logged":"Nothing logged yet","tap_plus":"Tap + to add",
        "log_meal":"Log meal","save_fav":"Save","clear":"Clear","use_this":"Use",
        "per_100g":"Per 100g","portion":"Portion","meal":"Meal",
        "remaining":"remaining","goal_reached":"Goal reached",
        "daily_goal":"Daily goal","macro_split":"Macro split",
        "text_ai":"Text / AI","photo":"Photo","barcode":"Barcode","geometric":"Geometric",
        "sign_in":"Sign in","register":"Create account",
        "email":"Email","password":"Password",
        "username":"Username","confirm_pw":"Confirm password",
        "no_account":"New here?","have_account":"Have an account?",
        "wrong_creds":"Incorrect email or password.",
        "user_exists":"Email or username already registered.",
        "pw_no_match":"Passwords do not match.",
        "sign_out":"Sign out","language":"Language",
        "goal_label":"Goal","calorie_target":"Daily calorie target",
        "halal_active":"Halal scanner active",
        "weight_label":"Weight (kg)","height_label":"Height (cm)","age_label":"Age",
        "weight_log":"Weight history","log_weight":"Log weight","no_weights":"No entries yet.",
        "profile":"Profile","physical":"Physical stats",
        "food_name":"Food name","shape":"Shape","food_type":"Food type",
        "diameter":"Diameter (cm)","height_dim":"Height (cm)",
        "calc_mass":"Calculate","est_mass":"Estimated mass","est_nutrition":"Estimate nutrition",
        "not_found":"Product not found.",
        "no_favs":"No favourites yet.","save_hint":"Search a food and save it.",
        "searching":"Searching...","analysing":"Analysing...","looking_up":"Looking up...",
        "save_changes":"Save","saved_ok":"Saved.",
        "halal_scanner":"Halal Scanner",
        "halal_explain":"Automatically checks all ingredients for haram and doubtful additives on every barcode scan.",
        "enable_halal":"Enable halal scanner",
        "morning":"Good morning","afternoon":"Good afternoon","evening":"Good evening",
        "log_food":"Log food","back":"Back",
        "delete_entry":"Remove",
        "no_history":"No history yet.",
        "premium":"Premium",
        "premium_feature":"Premium feature",
        "premium_desc":"Upgrade to Velora Premium to unlock this feature.",
        "upgrade":"Upgrade to Premium",
        "7day_limit":"Showing last 7 days. Upgrade for full history.",
        "weekly_trend":"Weekly calorie trend",
        "advice":"Nutrition Advice",
        "advice_sub":"Personalised tips based on your logs",
        "get_advice":"Get personalised advice",
        "advice_premium":"AI-powered nutrition advice is a Premium feature.",
    },
    "fr": {
        "daily_log":"Journal du jour","daily_sub":"Votre nutrition aujourd'hui",
        "history":"Historique","history_sub":"Repas passés & tendances",
        "favourites":"Favoris","fav_sub":"Vos aliments sauvegardés",
        "settings":"Paramètres","settings_sub":"Préférences & profil",
        "breakfast":"Petit-déjeuner","lunch":"Déjeuner","dinner":"Dîner","snack":"Collation",
        "calories":"Calories","protein":"Protéines","carbs":"Glucides","fat":"Lipides",
        "nothing_logged":"Rien enregistré","tap_plus":"Appuyez sur + pour ajouter",
        "log_meal":"Enregistrer","save_fav":"Sauvegarder","clear":"Effacer","use_this":"Utiliser",
        "per_100g":"Pour 100g","portion":"Portion","meal":"Repas",
        "remaining":"restants","goal_reached":"Objectif atteint",
        "daily_goal":"Objectif","macro_split":"Répartition macros",
        "text_ai":"Texte / IA","photo":"Photo","barcode":"Code-barres","geometric":"Géométrique",
        "sign_in":"Se connecter","register":"Créer un compte",
        "email":"E-mail","password":"Mot de passe",
        "username":"Nom d'utilisateur","confirm_pw":"Confirmer le mot de passe",
        "no_account":"Nouveau ?","have_account":"Déjà un compte ?",
        "wrong_creds":"E-mail ou mot de passe incorrect.",
        "user_exists":"E-mail ou nom déjà utilisé.",
        "pw_no_match":"Les mots de passe ne correspondent pas.",
        "sign_out":"Se déconnecter","language":"Langue",
        "goal_label":"Objectif","calorie_target":"Objectif calorique",
        "halal_active":"Scanner halal actif",
        "weight_label":"Poids (kg)","height_label":"Taille (cm)","age_label":"Âge",
        "weight_log":"Historique poids","log_weight":"Enregistrer","no_weights":"Aucune entrée.",
        "profile":"Profil","physical":"Données physiques",
        "food_name":"Aliment","shape":"Forme","food_type":"Type",
        "diameter":"Diamètre (cm)","height_dim":"Hauteur (cm)",
        "calc_mass":"Calculer","est_mass":"Masse estimée","est_nutrition":"Estimer",
        "not_found":"Produit introuvable.",
        "no_favs":"Aucun favori.","save_hint":"Recherchez et sauvegardez un aliment.",
        "searching":"Recherche...","analysing":"Analyse...","looking_up":"Recherche...",
        "save_changes":"Enregistrer","saved_ok":"Enregistré.",
        "halal_scanner":"Scanner Halal",
        "halal_explain":"Vérifie automatiquement les ingrédients à chaque scan.",
        "enable_halal":"Activer le scanner halal",
        "morning":"Bonjour","afternoon":"Bon après-midi","evening":"Bonsoir",
        "log_food":"Enregistrer","back":"Retour",
        "delete_entry":"Supprimer",
        "no_history":"Aucun historique.",
        "premium":"Premium",
        "premium_feature":"Fonctionnalité Premium",
        "premium_desc":"Passez à Velora Premium pour débloquer cette fonctionnalité.",
        "upgrade":"Passer à Premium",
        "7day_limit":"7 derniers jours affichés. Premium pour l'historique complet.",
        "weekly_trend":"Tendance calorique hebdomadaire",
        "advice":"Conseils Nutritionnels",
        "advice_sub":"Conseils personnalisés basés sur vos repas",
        "get_advice":"Obtenir des conseils",
        "advice_premium":"Les conseils IA sont une fonctionnalité Premium.",
    }
}

def T(key):
    lang = st.session_state.get("language","en")
    return LANG.get(lang, LANG["en"]).get(key, key)

def greeting():
    h = datetime.now().hour
    if h < 12: return T("morning")
    elif h < 18: return T("afternoon")
    return T("evening")

# ── Auth helpers ──────────────────────────────────────────────
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def get_user_by_email(email):
    conn = sqlite3.connect("calorie_app.db")
    c = conn.cursor()
    c.execute("SELECT id,username,password_hash,is_muslim,language,daily_calorie_goal,is_premium FROM users WHERE email=?", (email,))
    r = c.fetchone(); conn.close(); return r

def register_user(username, email, pw_hash):
    conn = sqlite3.connect("calorie_app.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username,email,password_hash) VALUES (?,?,?)", (username,email,pw_hash))
        conn.commit()
        c.execute("SELECT id FROM users WHERE email=?", (email,))
        uid = c.fetchone()[0]; conn.close(); return uid, None
    except sqlite3.IntegrityError:
        conn.close(); return None, "exists"

def update_user_prefs(user_id, **kw):
    if not kw: return
    conn = sqlite3.connect("calorie_app.db")
    c = conn.cursor()
    cols = ", ".join(f"{k}=?" for k in kw)
    c.execute(f"UPDATE users SET {cols} WHERE id=?", list(kw.values())+[user_id])
    conn.commit(); conn.close()

def log_weight_entry(user_id, weight_kg):
    conn = sqlite3.connect("calorie_app.db")
    c = conn.cursor()
    c.execute("INSERT INTO weight_log (user_id,weight_kg,date) VALUES (?,?,?)",
              (user_id, weight_kg, date.today().isoformat()))
    conn.commit(); conn.close()

def get_weight_history(user_id):
    conn = sqlite3.connect("calorie_app.db")
    c = conn.cursor()
    c.execute("SELECT date,weight_kg FROM weight_log WHERE user_id=? ORDER BY date", (user_id,))
    r = c.fetchall(); conn.close(); return r

def get_user_profile(user_id):
    conn = sqlite3.connect("calorie_app.db")
    c = conn.cursor()
    c.execute("SELECT username,email,age,height_cm,weight_kg,goal,daily_calorie_goal,is_premium FROM users WHERE id=?", (user_id,))
    r = c.fetchone(); conn.close(); return r

def ensure_premium_column():
    conn = sqlite3.connect("calorie_app.db")
    c = conn.cursor()
    try: c.execute("ALTER TABLE users ADD COLUMN is_premium INTEGER DEFAULT 0")
    except: pass
    conn.commit(); conn.close()

ensure_premium_column()

# ── Charts ────────────────────────────────────────────────────
def calorie_ring(consumed, goal):
    rem = max(goal-consumed, 0.01)
    fig = go.Figure()
    fig.add_trace(go.Pie(
        values=[max(consumed,0.01), rem], hole=0.72,
        marker=dict(colors=["#B0822A","#1E2124"]),
        textinfo="none", hoverinfo="skip", sort=False
    ))
    for txt, y, fam, sz, col in [
        (f"<b>{int(consumed)}</b>", 0.55, "Fraunces, serif", 24, "#F4F0E6"),
        ("kcal", 0.38, "JetBrains Mono, monospace", 10, "#B0822A"),
        (f"of {int(goal)}", 0.22, "JetBrains Mono, monospace", 8, "#6A6A5A"),
    ]:
        fig.add_annotation(text=txt, x=0.5, y=y, showarrow=False,
            font=dict(family=fam, size=sz, color=col))
    fig.update_layout(showlegend=False, margin=dict(t=6,b=6,l=6,r=6),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=170, width=170)
    return fig

def macro_donut(protein, carbs, fat):
    total = protein+carbs+fat
    if total==0: protein=carbs=fat=1
    lang = st.session_state.get("language","en")
    labels = {"en":["Protein","Carbs","Fat"],"fr":["Protéines","Glucides","Lipides"]}.get(lang,["Protein","Carbs","Fat"])
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=labels, values=[protein,carbs,fat], hole=0.62,
        marker=dict(colors=["#C4622D","#2A7A7A","#A878E0"]),
        textinfo="none",
        hovertemplate="%{label}: %{value}g (%{percent})<extra></extra>"))
    fig.update_layout(showlegend=True,
        legend=dict(font=dict(family="JetBrains Mono, monospace",size=9,color="#6A6A5A"),
            bgcolor="rgba(0,0,0,0)",orientation="h",yanchor="bottom",y=-0.2,xanchor="center",x=0.5),
        margin=dict(t=6,b=28,l=6,r=6),
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=185)
    return fig

def history_chart(history_data, goal):
    dates = list(history_data.keys())[-14:]
    cals = [history_data[d]["totals"]["calories"] for d in dates]
    fig = go.Figure()
    fig.add_hline(y=goal, line_dash="dot", line_color="#B0822A",
                  annotation_text="goal", annotation_position="right",
                  annotation_font=dict(family="JetBrains Mono, monospace",size=9,color="#B0822A"))
    fig.add_trace(go.Bar(x=dates, y=cals,
        marker=dict(color=["#3E6A48" if c<=goal else "#C4622D" for c in cals],
                    cornerradius=6),
        text=[f"{c:.0f}" for c in cals], textposition="outside",
        textfont=dict(family="JetBrains Mono, monospace",size=9,color="#6A6A5A"),
        hovertemplate="%{x}: %{y:.0f} kcal<extra></extra>"))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20,b=10,l=10,r=10),height=200,bargap=0.35,
        xaxis=dict(showgrid=False,tickfont=dict(family="JetBrains Mono, monospace",size=8,color="#6A6A5A")),
        yaxis=dict(showgrid=False,visible=False))
    return fig

def weight_chart(history):
    if not history: return None
    dates=[r[0] for r in history]; weights=[r[1] for r in history]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates,y=weights,mode="lines+markers",
        line=dict(color="#B0822A",width=2),marker=dict(color="#C4622D",size=6),
        hovertemplate="%{x}: %{y} kg<extra></extra>"))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10,b=10,l=10,r=10),height=180,
        xaxis=dict(showgrid=False,tickfont=dict(family="JetBrains Mono, monospace",size=9,color="#6A6A5A")),
        yaxis=dict(showgrid=True,gridcolor="#1A1D20",tickfont=dict(family="JetBrains Mono, monospace",size=9,color="#6A6A5A")))
    return fig

# ── UI helpers ────────────────────────────────────────────────
def chips(cal, prot, carb, fat):
    lang = st.session_state.get("language","en")
    labels = {"en":("Cal","Prot","Carbs","Fat"),"fr":("Cal","Prot","Gluc","Lip")}.get(lang,("Cal","Prot","Carbs","Fat"))
    colors = ("#D9B86A","#E09070","#5AACAC","#A878E0")
    borders = ("#B0822A35","#C4622D35","#2A7A7A35","#A878E035")
    vals = (f"{cal} kcal",f"{prot}g",f"{carb}g",f"{fat}g")
    html = '<div style="display:flex;gap:6px;margin-top:10px;flex-wrap:wrap;">'
    for label,color,border,val in zip(labels,colors,borders,vals):
        html += f'<div style="flex:1;min-width:58px;background:#0D0E10;border:1px solid {border};border-radius:9px;padding:8px 6px;text-align:center;"><div style="font-family:JetBrains Mono,monospace;font-size:0.5rem;color:{color};letter-spacing:0.1em;text-transform:uppercase;margin-bottom:3px;">{label}</div><div style="font-family:Fraunces,serif;font-size:1rem;font-weight:300;color:#F4F0E6;">{val}</div></div>'
    html += "</div>"
    return html

def badge_html(input_method, verified=False):
    if verified or "database" in str(input_method):
        return '<span style="font-family:JetBrains Mono,monospace;font-size:0.5rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;padding:3px 8px;border-radius:20px;margin-bottom:8px;display:inline-block;background:#1A2A1E;color:#5A9E6A;border:1px solid #3E6A48;">Verified</span>'
    m=str(input_method)
    if "ai" in m: c,bg,b,l="#D9B86A","#1E1A0E","#B0822A30","AI"
    elif "barcode" in m: c,bg,b,l="#5AACAC","#0E1E1E","#2A7A7A30","Barcode"
    elif "photo" in m: c,bg,b,l="#C07AE0","#180E20","#7A46B030","Photo"
    elif "geometric" in m: c,bg,b,l="#5AB8B8","#0E1E1E","#2E6A6A30","Geometric"
    else: c,bg,b,l="#D9B86A","#1E1A0E","#B0822A30","AI"
    return f'<span style="font-family:JetBrains Mono,monospace;font-size:0.5rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;padding:3px 8px;border-radius:20px;margin-bottom:8px;display:inline-block;background:{bg};color:{c};border:1px solid {b};">{l}</span>'

def halal_html(halal):
    s=halal.get("status",""); m=halal.get("message","")
    styles={"halal":"background:#1A2A1E;border:1px solid #3E6A48;color:#7DC48A;",
            "doubtful":"background:#2A2218;border:1px solid #B0822A;color:#D9B86A;",
            "haram":"background:#2A1818;border:1px solid #8B2E2E;color:#E07878;"}
    style=styles.get(s,"background:#1A1B1E;border:1px solid #252830;color:#6A6A5A;")
    return f'<div style="{style}border-radius:9px;padding:10px 14px;margin:10px 0;font-family:Inter,sans-serif;font-size:0.8rem;font-weight:500;">{m}</div>'

def premium_gate(feature_key):
    """Shows a premium upgrade prompt instead of the feature."""
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1A1810 0%,#1A1420 100%);
        border:1px solid #B0822A40;border-radius:14px;padding:24px 26px;
        text-align:center;margin:16px 0;">
        <div style="margin-bottom:10px;">{ic("crown",28,"#D9B86A")}</div>
        <div style="font-family:Fraunces,serif;font-size:1.2rem;font-weight:300;
            color:#F4F0E6;margin-bottom:6px;">{T("premium_feature")}</div>
        <div style="font-family:Inter,sans-serif;font-size:0.8rem;color:#6A6A5A;
            margin-bottom:16px;line-height:1.5;">{T("premium_desc")}</div>
    </div>
    """, unsafe_allow_html=True)
    st.button(f"{T('upgrade')} →", key=f"upgrade_{feature_key}",
              use_container_width=True)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,600&family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.main .block-container{padding:2rem 2.5rem 3rem;max-width:1100px;}

section[data-testid="stSidebar"]{
    background:
        radial-gradient(ellipse at 20% 0%, rgba(196,98,45,0.07) 0%, transparent 55%),
        radial-gradient(ellipse at 80% 100%, rgba(42,122,122,0.05) 0%, transparent 55%),
        #0A0B0D !important;
    border-right:1px solid #141618;
}
section[data-testid="stSidebar"] .block-container{padding:1.6rem 1rem;}

/* zellige header */
.zh{border-radius:14px;padding:24px 26px;margin-bottom:18px;position:relative;
    overflow:hidden;background:#111318;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Cpath d='M24 4L44 24L24 44L4 24Z' fill='none' stroke='%23B0822A' stroke-opacity='0.06' stroke-width='1'/%3E%3Cpath d='M24 12L36 24L24 36L12 24Z' fill='none' stroke='%23C4622D' stroke-opacity='0.04' stroke-width='1'/%3E%3Ccircle cx='24' cy='24' r='3' fill='none' stroke='%23B0822A' stroke-opacity='0.07' stroke-width='1'/%3E%3C/svg%3E");
    background-size:48px 48px;border:1px solid #1E2124;border-left:2px solid #B0822A;}
.zh::before{content:'';position:absolute;top:-25px;right:-25px;width:120px;height:120px;
    background:radial-gradient(circle,rgba(196,98,45,0.09) 0%,transparent 65%);border-radius:50%;}
.pt{font-family:'Fraunces',serif;font-size:1.8rem;font-weight:300;color:#F4F0E6;margin:0 0 3px;line-height:1.1;position:relative;}
.ps{font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#C4622D;letter-spacing:0.18em;text-transform:uppercase;position:relative;}

/* auth */
.auth-card{background:#0E0F12;border:1px solid #1E2124;border-radius:16px;padding:30px 32px;}
.auth-title{font-family:'Fraunces',serif;font-size:1.6rem;font-weight:300;color:#F4F0E6;margin-bottom:3px;}
.auth-sub{font-family:'Inter',sans-serif;font-size:0.78rem;color:#6A6A5A;margin-bottom:20px;line-height:1.5;}
.field-label{font-family:'JetBrains Mono',monospace;font-size:0.54rem;color:#6A6A5A;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:4px;margin-top:10px;display:flex;align-items:center;gap:5px;}

/* sidebar */
.sb{font-family:'Fraunces',serif;font-size:1.3rem;font-weight:300;color:#E8E0D0;margin-bottom:1px;}
.st2{font-family:'JetBrains Mono',monospace;font-size:0.52rem;color:#C4622D;letter-spacing:0.16em;text-transform:uppercase;margin-bottom:1.1rem;}
.su{font-family:'JetBrains Mono',monospace;font-size:0.52rem;color:#4A4A3A;letter-spacing:0.06em;margin-bottom:1px;}
.sn{font-family:'Fraunces',serif;font-size:0.95rem;font-weight:300;color:#D8D0C0;margin-bottom:0.8rem;}

/* macro cards */
.mc{background:#0E0F12;border:1px solid #1A1D20;border-radius:12px;padding:15px 12px;text-align:center;transition:transform 0.2s;}
.mc:hover{transform:translateY(-2px);}
.mc-lbl{font-family:'JetBrains Mono',monospace;font-size:0.52rem;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px;display:block;}
.mc-val{font-family:'Fraunces',serif;font-size:1.6rem;font-weight:300;color:#F4F0E6;line-height:1;display:block;}
.mc-unit{font-family:'JetBrains Mono',monospace;font-size:0.56rem;color:#4A4A3A;}
.mc-cal{border-top:2px solid #B0822A;}.mc-cal .mc-lbl{color:#C4622D;}
.mc-pro{border-top:2px solid #C4622D;}.mc-pro .mc-lbl{color:#E09070;}
.mc-crb{border-top:2px solid #2A7A7A;}.mc-crb .mc-lbl{color:#5AACAC;}
.mc-fat{border-top:2px solid #7A46B0;}.mc-fat .mc-lbl{color:#A878E0;}

/* meals */
.meal-wrap{background:#0E0F12;border:1px solid #1A1D20;border-radius:11px;padding:12px 14px;margin-bottom:6px;}
.meal-lbl{font-family:'JetBrains Mono',monospace;font-size:0.55rem;letter-spacing:0.13em;text-transform:uppercase;color:#B0822A;}
.food-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #111318;}
.food-row:last-child{border-bottom:none;}
.fn{font-family:'Inter',sans-serif;font-size:0.83rem;color:#D8D0C0;font-weight:400;}
.fm{font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:#4A4A3A;margin-top:2px;}
.fc{font-family:'Fraunces',serif;font-size:0.95rem;font-weight:300;color:#B0822A;white-space:nowrap;margin-right:6px;}

/* history card */
.hc{background:#0E0F12;border:1px solid #1A1D20;border-radius:11px;padding:14px 16px;margin-bottom:8px;}
.hc-date{font-family:'JetBrains Mono',monospace;font-size:0.56rem;letter-spacing:0.1em;text-transform:uppercase;color:#C4622D;margin-bottom:8px;}
.hc-total{font-family:'Fraunces',serif;font-size:1.1rem;font-weight:300;color:#F4F0E6;}

/* result card */
.rc{background:#0E0F12;border:1px solid #B0822A40;border-radius:14px;padding:18px 20px;margin:8px 0;position:relative;overflow:hidden;}
.rc::before{content:'';position:absolute;top:0;right:0;width:70px;height:70px;background:radial-gradient(circle,rgba(176,130,42,0.05) 0%,transparent 70%);border-radius:50%;}
.rn{font-family:'Fraunces',serif;font-size:1.25rem;font-weight:300;color:#F4F0E6;margin-bottom:2px;}
.rd{font-family:'Inter',sans-serif;font-size:0.7rem;color:#4A4A3A;font-style:italic;margin-bottom:10px;}

/* log panel */
.lp{background:linear-gradient(135deg,#0E1810 0%,#0E0F12 100%);border:1px solid #2E5A3230;border-radius:12px;padding:18px 20px;margin-top:12px;}
.lp-title{font-family:'JetBrains Mono',monospace;font-size:0.54rem;letter-spacing:0.14em;text-transform:uppercase;color:#5A9E6A;margin-bottom:8px;}
.lp-food{font-family:'Fraunces',serif;font-size:1.1rem;font-weight:300;color:#F4F0E6;margin-bottom:10px;}

/* settings */
.ss{background:#0E0F12;border:1px solid #1A1D20;border-radius:12px;padding:16px 18px;margin-bottom:10px;}
.ss-title{font-family:'JetBrains Mono',monospace;font-size:0.54rem;letter-spacing:0.13em;text-transform:uppercase;color:#C4622D;margin-bottom:11px;display:flex;align-items:center;gap:6px;}
.halal-feat{background:linear-gradient(135deg,#0C1810 0%,#0E1210 100%);border:1px solid #2E5A3230;border-radius:12px;padding:16px 18px;margin-bottom:10px;}
.halal-feat-title{font-family:'Fraunces',serif;font-size:1rem;font-weight:300;color:#F4F0E6;margin-bottom:4px;}
.halal-feat-desc{font-family:'Inter',sans-serif;font-size:0.76rem;color:#4A4A3A;line-height:1.55;margin-bottom:10px;}

/* empty */
.empty{text-align:center;padding:2.5rem 0;color:#2A2D32;font-family:'Inter',sans-serif;font-size:0.82rem;}
.empty .big{margin-bottom:10px;display:block;opacity:0.25;}

/* buttons */
.stButton>button{background:linear-gradient(135deg,#B0822A 0%,#C4622D 100%) !important;color:#F4F0E6 !important;border:none !important;border-radius:9px !important;font-family:'Inter',sans-serif !important;font-weight:600 !important;font-size:0.8rem !important;padding:0.46rem 0.9rem !important;transition:all 0.2s !important;box-shadow:0 2px 8px rgba(176,130,42,0.16) !important;}
.stButton>button:hover{transform:translateY(-1px) !important;box-shadow:0 4px 16px rgba(196,98,45,0.28) !important;}

/* tabs */
.stTabs [data-baseweb="tab-list"]{background:#0E0F12;border-radius:10px;padding:3px;gap:3px;border:1px solid #1A1D20;}
.stTabs [data-baseweb="tab"]{background:transparent;color:#4A4A3A;border-radius:7px;font-family:'Inter',sans-serif;font-size:0.78rem;font-weight:500;padding:7px 13px;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#B0822A 0%,#C4622D 100%) !important;color:#F4F0E6 !important;}

/* inputs */
.stTextInput input,.stNumberInput input{background:#0A0B0D !important;border:1px solid #1E2124 !important;color:#F4F0E6 !important;border-radius:9px !important;}
.stTextInput input:focus{border-color:#B0822A !important;box-shadow:0 0 0 2px rgba(176,130,42,0.09) !important;}
.stSelectbox>div>div{background:#0A0B0D !important;border-radius:9px !important;}
.stProgress>div>div{background:linear-gradient(90deg,#B0822A,#C4622D) !important;border-radius:4px !important;}
hr{border-color:#141618 !important;margin:1.2rem 0 !important;}
.streamlit-expanderHeader{background:#0E0F12 !important;border-radius:9px !important;border:1px solid #1A1D20 !important;color:#D8D0C0 !important;}
[data-testid="column"]:empty{display:none;}
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-track{background:#0A0B0D;}
::-webkit-scrollbar-thumb{background:#1E2124;border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:#B0822A;}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
for k,v in [
    ("user_id",None),("username",None),("is_muslim",False),("is_premium",False),
    ("language","en"),("daily_goal",2000),("auth_mode","login"),
    ("onboarding_done",False),("onboarding_step",1),
    ("result",None),("active_meal","breakfast"),("page","daily_log"),
]:
    if k not in st.session_state: st.session_state[k]=v

def velora_logo(sz="md"):
    fsz = "1.7rem" if sz=="md" else "1.3rem"
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:22px;">
        <div style="width:46px;height:46px;
            background:linear-gradient(135deg,#B0822A,#C4622D);border-radius:12px;
            margin:0 auto 10px;display:flex;align-items:center;justify-content:center;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
                stroke="#F4F0E6" stroke-width="1.5" stroke-linecap="round">
                <path d="M12 3L4 7.5V12c0 4.5 3.5 8.5 8 9.5 4.5-1 8-5 8-9.5V7.5L12 3z"/>
                <path d="M9 12l2 2 4-4"/>
            </svg>
        </div>
        <div style="font-family:Fraunces,serif;font-size:{fsz};font-weight:300;color:#F4F0E6;letter-spacing:-0.01em;">Velora</div>
        <div style="font-family:JetBrains Mono,monospace;font-size:0.54rem;color:#C4622D;letter-spacing:0.18em;text-transform:uppercase;margin-top:3px;">Nutrition Intelligence</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════
if not st.session_state.user_id and not st.session_state.onboarding_done:
    _,col,_ = st.columns([1,1.2,1])
    with col:
        velora_logo()
        if st.session_state.auth_mode == "login":
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="auth-title">{T("sign_in")}</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-sub">Track your nutrition with AI precision.</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="field-label">{ic("mail",12,"#4A4A3A")} {T("email")}</div>', unsafe_allow_html=True)
            email_in = st.text_input("",placeholder="you@example.com",key="li_em",label_visibility="collapsed")
            st.markdown(f'<div class="field-label">{ic("lock",12,"#4A4A3A")} {T("password")}</div>', unsafe_allow_html=True)
            pw_in = st.text_input("",type="password",key="li_pw",label_visibility="collapsed")
            if st.button(T("sign_in"),use_container_width=True,key="do_login"):
                if email_in and pw_in:
                    row = get_user_by_email(email_in.lower().strip())
                    if row and row[2]==hash_pw(pw_in):
                        uid,uname,_,is_m,lang,dgoal = row[0],row[1],row[2],row[3],row[4],row[5]
                        is_prem = row[6] if len(row)>6 else 0
                        st.session_state.user_id=uid
                        st.session_state.username=uname.capitalize()
                        st.session_state.is_muslim=bool(is_m)
                        st.session_state.is_premium=bool(is_prem)
                        st.session_state.language=lang or "en"
                        st.session_state.daily_goal=dgoal or 2000
                        st.session_state.onboarding_done=True
                        st.rerun()
                    else: st.error(T("wrong_creds"))
            st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
            if st.button(f'{T("no_account")} {T("register")} →',use_container_width=True,key="goto_reg"):
                st.session_state.auth_mode="register"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="auth-title">{T("register")}</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-sub">Join Velora and start tracking today.</div>', unsafe_allow_html=True)
            for label,icon,key,ph,typ in [
                (T("username"),"user","r_un","yourname","text"),
                (T("email"),"mail","r_em","you@example.com","text"),
                (T("password"),"lock","r_pw","","password"),
                (T("confirm_pw"),"lock","r_pw2","","password"),
            ]:
                st.markdown(f'<div class="field-label">{ic(icon,12,"#4A4A3A")} {label}</div>', unsafe_allow_html=True)
                if typ=="password": st.text_input("",type="password",key=key,label_visibility="collapsed")
                else: st.text_input("",placeholder=ph,key=key,label_visibility="collapsed")
            if st.button(T("register"),use_container_width=True,key="do_reg"):
                un=st.session_state.r_un; em=st.session_state.r_em
                pw=st.session_state.r_pw; pw2=st.session_state.r_pw2
                if not all([un,em,pw,pw2]): st.error("Please fill in all fields.")
                elif pw!=pw2: st.error(T("pw_no_match"))
                else:
                    uid,err=register_user(un.lower().strip(),em.lower().strip(),hash_pw(pw))
                    if err: st.error(T("user_exists"))
                    else:
                        st.session_state.user_id=uid
                        st.session_state.username=un.capitalize()
                        st.session_state.onboarding_done=False
                        st.session_state.onboarding_step=1
                        st.rerun()
            if st.button(f'{T("have_account")} {T("sign_in")} →',use_container_width=True,key="goto_login"):
                st.session_state.auth_mode="login"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════
# ONBOARDING
# ══════════════════════════════════════════════════════════════
if st.session_state.user_id and not st.session_state.onboarding_done:
    _,col,_=st.columns([1,1.4,1])
    with col:
        velora_logo()
        step=st.session_state.onboarding_step
        if step==1:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:0.54rem;color:#C4622D;letter-spacing:0.14em;text-transform:uppercase;margin-bottom:6px;">1 / 2 — Preferences</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-title">Personalise Velora</div>', unsafe_allow_html=True)
            goal=st.selectbox("",["Lose weight","Build muscle","Maintain weight","General health","Track what I eat"],label_visibility="collapsed",key="ob_goal")
            lang=st.radio("Language / Langue",["en","fr"],format_func=lambda x:"English" if x=="en" else "Français",horizontal=True)
            st.markdown(f"""
            <div class="halal-feat" style="margin-top:14px;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
                    {ic("moon",17,"#7DC48A")}
                    <div class="halal-feat-title">{T("halal_scanner")}</div>
                </div>
                <div class="halal-feat-desc">{T("halal_explain")}</div>
            </div>
            """, unsafe_allow_html=True)
            enable_halal=st.checkbox(T("enable_halal"),key="ob_halal")
            if st.button("Continue →",use_container_width=True):
                st.session_state.language=lang; st.session_state.is_muslim=enable_halal
                update_user_prefs(st.session_state.user_id,goal=goal.lower(),language=lang,is_muslim=int(enable_halal))
                st.session_state.onboarding_step=2; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        elif step==2:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:0.54rem;color:#C4622D;letter-spacing:0.14em;text-transform:uppercase;margin-bottom:6px;">2 / 2 — Calorie Target</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-title">Set your daily target</div>', unsafe_allow_html=True)
            mode=st.radio("",["Set manually","Calculate from stats"],horizontal=True,label_visibility="collapsed")
            daily_goal=1800; age_v=weight_v=height_v=None
            if mode=="Set manually":
                daily_goal=st.number_input("kcal / day",min_value=800,max_value=5000,value=1800,step=50)
            else:
                c1,c2,c3=st.columns(3)
                with c1: age_v=st.number_input("Age",10,100,20)
                with c2: weight_v=st.number_input("Weight kg",30.0,200.0,60.0)
                with c3: height_v=st.number_input("Height cm",140.0,220.0,165.0)
                sex=st.radio("",["Female","Male"],horizontal=True,label_visibility="collapsed")
                if sex=="Female": bmr=10*weight_v+6.25*height_v-5*age_v-161
                else: bmr=10*weight_v+6.25*height_v-5*age_v+5
                act=st.selectbox("Activity",["Sedentary","Lightly active","Moderately active","Very active"])
                factor={"Sedentary":1.2,"Lightly active":1.375,"Moderately active":1.55,"Very active":1.725}[act]
                daily_goal=int(bmr*factor)
                st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.74rem;color:#B0822A;padding:4px 0;">Recommended: {daily_goal} kcal / day</div>', unsafe_allow_html=True)
            if st.button("Get started →",use_container_width=True):
                kw=dict(daily_calorie_goal=daily_goal)
                if age_v: kw["age"]=int(age_v)
                if weight_v: kw["weight_kg"]=float(weight_v)
                if height_v: kw["height_cm"]=float(height_v)
                update_user_prefs(st.session_state.user_id,**kw)
                st.session_state.daily_goal=daily_goal; st.session_state.onboarding_done=True; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════
user_id=st.session_state.user_id
is_premium=st.session_state.is_premium

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div class="sb">Velora</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="st2">Nutrition Intelligence</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="su">{greeting()},</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sn">{st.session_state.username}{"&nbsp;&nbsp;" + ic("crown",12,"#D9B86A") if is_premium else ""}</div>', unsafe_allow_html=True)

    if st.session_state.is_muslim:
        st.markdown(f'<div style="display:flex;align-items:center;gap:4px;font-family:JetBrains Mono,monospace;font-size:0.5rem;color:#5A9E6A;letter-spacing:0.06em;margin-bottom:6px;">{ic("moon",11,"#5A9E6A")} {T("halal_active")}</div>', unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.page == "search_log":
        if st.button(f"← {T('back')}", key="nav_back", use_container_width=True):
            st.session_state.page="daily_log"; st.session_state.result=None; st.rerun()
    else:
        nav_items = [
            ("daily_log", "grid", T("daily_log")),
            ("history", "history", T("history")),
            ("favourites", "star", T("favourites")),
            ("settings", "gear", T("settings")),
        ]
        for page_key, icon_name, label in nav_items:
            is_active = st.session_state.page == page_key
            if st.button(
                label,
                key=f"nav_{page_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.page=page_key; st.session_state.result=None; st.rerun()

    summary = get_daily_summary(user_id)
    st.markdown("---")
    st.plotly_chart(
        calorie_ring(summary["totals"]["calories"],
                     summary.get("daily_goal",st.session_state.daily_goal)),
        use_container_width=True, config={"displayModeBar":False}
    )
    rem=summary["remaining_calories"]
    msg=f"{rem:.0f} {T('remaining')}" if rem>0 else T("goal_reached")
    color="#4A4A3A" if rem>0 else "#5A9E6A"
    st.markdown(f'<div style="text-align:center;font-family:JetBrains Mono,monospace;font-size:0.58rem;color:{color};margin-top:-5px;">{msg}</div>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button(T("sign_out"),use_container_width=True,key="signout"):
        for k in ["user_id","username","is_muslim","is_premium","language","daily_goal","result","onboarding_done","page","auth_mode"]:
            st.session_state[k]=None if k!="onboarding_done" else False
        st.session_state.auth_mode="login"; st.rerun()

page=st.session_state.page


# ══════════════════════════════════════════════════════════════
# DAILY LOG
# ══════════════════════════════════════════════════════════════
if page=="daily_log":
    st.markdown(f'<div class="zh"><div class="pt">{T("daily_log")}</div><div class="ps">{T("daily_sub")}</div></div>', unsafe_allow_html=True)
    t_=summary["totals"]
    c1,c2,c3,c4=st.columns(4)
    for col,css,lbl,val,unit in [
        (c1,"mc-cal",T("calories"),t_["calories"],"kcal"),
        (c2,"mc-pro",T("protein"),t_["protein_g"],"g"),
        (c3,"mc-crb",T("carbs"),t_["carbs_g"],"g"),
        (c4,"mc-fat",T("fat"),t_["fat_g"],"g"),
    ]:
        with col:
            st.markdown(f'<div class="mc {css}"><span class="mc-lbl">{lbl}</span><span class="mc-val">{val}</span><span class="mc-unit"> {unit}</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_d,_=st.columns([1,2])
    with col_d:
        st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.54rem;color:#C4622D;letter-spacing:0.14em;text-transform:uppercase;margin-bottom:5px;">{T("macro_split")}</div>', unsafe_allow_html=True)
        st.plotly_chart(macro_donut(t_["protein_g"],t_["carbs_g"],t_["fat_g"]),use_container_width=True,config={"displayModeBar":False})

    st.markdown("---")

    meal_types=["breakfast","lunch","dinner","snack"]
    any_logged=any(summary["meals"].get(m) for m in meal_types)
    if not any_logged:
        st.markdown(f'<div class="empty"><span class="big">{ic("grid",30,"#2A2D32")}</span>{T("nothing_logged")}<br><span style="font-size:0.72rem;">{T("tap_plus")}</span></div>', unsafe_allow_html=True)

    for meal_type in meal_types:
        entries=summary["meals"].get(meal_type,[])
        meal_cal=sum(e["calories"] for e in entries)
        col_h,col_btn=st.columns([6,1])
        with col_h:
            cal_txt=f'&nbsp;<span style="color:#4A4A3A;font-size:0.9rem;">{meal_cal:.0f} kcal</span>' if entries else ""
            st.markdown(f'<div class="meal-lbl" style="padding:8px 0 4px;">{T(meal_type)}{cal_txt}</div>', unsafe_allow_html=True)
        with col_btn:
            if st.button("+",key=f"add_{meal_type}"):
                st.session_state.active_meal=meal_type; st.session_state.page="search_log"; st.rerun()
        if entries:
            st.markdown('<div class="meal-wrap">', unsafe_allow_html=True)
            for e in entries:
                dc,ic2,cc=st.columns([0.35,4.5,1.2])
                with dc:
                    if st.button("×",key=f"del_{e['entry_id']}"):
                        delete_entry(e["entry_id"],user_id); st.rerun()
                with ic2:
                    st.markdown(f'<div style="padding:4px 0;"><div class="fn">{e["food"]}</div><div class="fm">{e["quantity_g"]}g · P {e["protein_g"]}g · C {e["carbs_g"]}g · F {e["fat_g"]}g</div></div>', unsafe_allow_html=True)
                with cc:
                    st.markdown(f'<div class="fc" style="text-align:right;padding-top:5px;">{e["calories"]} kcal</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="font-family:Inter,sans-serif;font-size:0.72rem;color:#1E2124;padding:4px 0 8px;font-style:italic;">{T("tap_plus")}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# HISTORY
# ══════════════════════════════════════════════════════════════
elif page=="history":
    st.markdown(f'<div class="zh"><div class="pt">{T("history")}</div><div class="ps">{T("history_sub")}</div></div>', unsafe_allow_html=True)

    history_data=get_history(user_id)

    if not history_data:
        st.markdown(f'<div class="empty"><span class="big">{ic("history",30,"#2A2D32")}</span>{T("no_history")}</div>', unsafe_allow_html=True)
    else:
        goal=summary.get("daily_goal",st.session_state.daily_goal)

        # Chart — premium gate for full, free gets 7 days
        if is_premium:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.54rem;color:#C4622D;letter-spacing:0.14em;text-transform:uppercase;margin-bottom:6px;">{T("weekly_trend")}</div>', unsafe_allow_html=True)
            st.plotly_chart(history_chart(history_data,goal),use_container_width=True,config={"displayModeBar":False})
        else:
            limited={k:v for i,(k,v) in enumerate(history_data.items()) if i<7}
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.54rem;color:#C4622D;letter-spacing:0.14em;text-transform:uppercase;margin-bottom:6px;">{T("weekly_trend")}</div>', unsafe_allow_html=True)
            st.plotly_chart(history_chart(limited,goal),use_container_width=True,config={"displayModeBar":False})
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.58rem;color:#4A4A3A;text-align:center;padding:4px 0 10px;">{T("7day_limit")}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Day-by-day list
        display_data=history_data if is_premium else dict(list(history_data.items())[:7])
        for day_str, day_data in display_data.items():
            totals=day_data["totals"]
            pct=min(totals["calories"]/goal*100,100) if goal>0 else 0
            bar_color="#3E6A48" if totals["calories"]<=goal else "#C4622D"
            with st.expander(f"{day_str}  ·  {totals['calories']} kcal", expanded=False):
                st.markdown(
                    f'<div style="background:#0D0E10;border-radius:6px;height:4px;margin-bottom:12px;overflow:hidden;">'
                    f'<div style="width:{pct:.0f}%;height:100%;background:{bar_color};border-radius:6px;"></div></div>'
                    f'<div style="display:flex;gap:16px;font-family:JetBrains Mono,monospace;font-size:0.58rem;color:#4A4A3A;margin-bottom:10px;">'
                    f'<span>P <b style="color:#E09070;">{totals["protein_g"]}g</b></span>'
                    f'<span>C <b style="color:#5AACAC;">{totals["carbs_g"]}g</b></span>'
                    f'<span>F <b style="color:#A878E0;">{totals["fat_g"]}g</b></span></div>',
                    unsafe_allow_html=True
                )
                for e in day_data["entries"]:
                    st.markdown(
                        f'<div class="food-row"><div>'
                        f'<div class="fn">{e["food"]}</div>'
                        f'<div class="fm">{e["meal_type"]} · {e["quantity_g"]}g</div>'
                        f'</div><div class="fc">{e["calories"]} kcal</div></div>',
                        unsafe_allow_html=True
                    )

        # AI advice — premium only
        st.markdown("---")
        st.markdown(f'<div class="zh" style="margin-top:10px;"><div class="pt" style="font-size:1.4rem;">{T("advice")}</div><div class="ps">{T("advice_sub")}</div></div>', unsafe_allow_html=True)
        if is_premium:
            if st.button(T("get_advice"),use_container_width=True):
                recent=list(history_data.values())[:3]
                avg_cal=sum(d["totals"]["calories"] for d in recent)/max(len(recent),1)
                avg_prot=sum(d["totals"]["protein_g"] for d in recent)/max(len(recent),1)
                from ai_text_estimation import estimate_from_text
                from mistralai.client import Mistral
                import os; from dotenv import load_dotenv; load_dotenv()
                client=Mistral(api_key=os.environ["MISTRAL_API_KEY"])
                with st.spinner(T("analysing")):
                    resp=client.chat.complete(
                        model="mistral-small-latest",
                        messages=[
                            {"role":"system","content":"You are a friendly, concise nutrition coach. Give 3 practical, specific tips based on the user's recent eating data. Be warm but direct. No bullet formatting — write in short paragraphs. Max 150 words total."},
                            {"role":"user","content":f"My recent averages: {avg_cal:.0f} kcal/day, {avg_prot:.0f}g protein/day. My goal is {goal} kcal. Give me 3 personalised nutrition tips."}
                        ]
                    )
                st.markdown(
                    f'<div style="background:#0E0F12;border:1px solid #1A1D20;border-radius:12px;padding:18px 20px;font-family:Inter,sans-serif;font-size:0.84rem;color:#D8D0C0;line-height:1.6;">{resp.choices[0].message.content}</div>',
                    unsafe_allow_html=True
                )
        else:
            premium_gate("advice")


# ══════════════════════════════════════════════════════════════
# SEARCH & LOG
# ══════════════════════════════════════════════════════════════
elif page=="search_log":
    active_meal=st.session_state.active_meal
    st.markdown(f'<div class="zh"><div class="pt">{T("log_food")} — {T(active_meal)}</div><div class="ps">{T("search_sub") if "search_sub" in LANG["en"] else "Find your food"}</div></div>', unsafe_allow_html=True)

    tab1,tab2,tab3,tab4=st.tabs([T("text_ai"),T("photo"),T("barcode"),T("geometric")])

    with tab1:
        query=st.text_input("",placeholder="harira · msemen · 2 oeufs · تفاحة · chicken",label_visibility="collapsed")
        if query:
            with st.spinner(T("searching")):
                results=search_food(query)
            if results and "error" not in results[0]:
                for r in results:
                    st.markdown(f'<div class="rc">{badge_html(r.get("input_method","ai_text"),r.get("verified",False))}<div class="rn">{r["food"]}</div><div class="rd">{T("per_100g")}</div>'+chips(r["calories"],r["protein_g"],r["carbs_g"],r["fat_g"])+'</div>',unsafe_allow_html=True)
                    if st.button(T("use_this"),key=f"use_{r['food']}"):
                        st.session_state.result=r; st.rerun()

    with tab2:
        # Photo — 3 free per day, unlimited premium
        if not is_premium:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.56rem;color:#D9B86A;letter-spacing:0.08em;padding:6px 0;">{ic("crown",12,"#D9B86A")} Premium: unlimited · Free: 3/day</div>', unsafe_allow_html=True)
        up=st.file_uploader("",type=["jpg","jpeg","png"],label_visibility="collapsed")
        if up:
            cl,cr=st.columns([1,1.4])
            with cl: st.image(up,use_container_width=True)
            with cr:
                with st.spinner(T("analysing")):
                    with tempfile.NamedTemporaryFile(delete=False,suffix=".jpg") as tmp:
                        tmp.write(up.read()); tp=tmp.name
                    result=estimate_from_photo(tp); os.unlink(tp)
                if "error" not in result:
                    st.markdown(f'<div class="rc">{badge_html("photo")}<div class="rn">{result["food"]}</div><div class="rd">{result.get("portion_description","")}</div>'+chips(result["calories"],result["protein_g"],result["carbs_g"],result["fat_g"])+'</div>',unsafe_allow_html=True)
                    if st.button(T("use_this"),key="use_photo"):
                        result["input_method"]="photo"; st.session_state.result=result; st.rerun()
                else: st.error(result["error"])

    with tab3:
        st.markdown(f'<div style="font-family:Inter,sans-serif;font-size:0.78rem;color:#4A4A3A;margin-bottom:10px;">{T("barcode")}'+(" — "+T("halal_active") if st.session_state.is_muslim else "")+'</div>', unsafe_allow_html=True)
        bc=st.text_input("",placeholder="e.g. 3017620422003",label_visibility="collapsed")
        if bc:
            with st.spinner(T("looking_up")):
                result=lookup_barcode(bc)
            if result.get("found") and result.get("valid"):
                h=result.get("halal",{})
                show_h=st.session_state.is_muslim and h
                h_html=halal_html(h) if show_h else ""
                st.markdown(f'<div class="rc">{badge_html("barcode")}<div class="rn">{result["food"]}</div><div class="rd">{T("per_100g")} — verified label</div>'+chips(result["calories"],result["protein_g"],result["carbs_g"],result["fat_g"])+h_html+'</div>',unsafe_allow_html=True)
                if show_h and h.get("flags"):
                    with st.expander("Ingredient details"):
                        for flag in h["flags"]: st.markdown(f"- {flag}")
                        st.caption(h.get("disclaimer",""))
                if st.button(T("use_this"),key="use_barcode"):
                    result["input_method"]="barcode"; st.session_state.result=result; st.rerun()
            else: st.warning(result.get("message",T("not_found")))

    with tab4:
        fname=st.text_input(T("food_name"),placeholder="khobz, apple, egg")
        d1,d2=st.columns(2)
        with d1: shape=st.selectbox(T("shape"),["Cylinder","Cuboid","Sphere","Ellipsoid"])
        with d2: dk=st.selectbox(T("food_type"),list(DENSITY_TABLE.keys()))
        mass_g=None; g1,g2=st.columns(2)
        if shape=="Cylinder":
            with g1: diam=st.number_input(T("diameter"),min_value=1.0,value=15.0)
            with g2: ht=st.number_input(T("height_dim"),min_value=0.5,value=3.0)
            if st.button(T("calc_mass")): mass_g=estimate_cylinder(diameter_to_radius(diam),ht,DENSITY_TABLE[dk])
        elif shape=="Cuboid":
            with g1:
                ln=st.number_input("Length (cm)",min_value=1.0,value=10.0)
                wd=st.number_input("Width (cm)",min_value=1.0,value=10.0)
            with g2: ht=st.number_input(T("height_dim"),min_value=0.1,value=1.5)
            if st.button(T("calc_mass")): mass_g=estimate_cuboid(ln,wd,ht,DENSITY_TABLE[dk])
        elif shape=="Sphere":
            with g1: diam=st.number_input(T("diameter"),min_value=1.0,value=8.0)
            if st.button(T("calc_mass")): mass_g=estimate_sphere(diameter_to_radius(diam),DENSITY_TABLE[dk])
        elif shape=="Ellipsoid":
            with g1:
                a=st.number_input("Semi-axis a (cm)",min_value=0.5,value=3.0)
                b=st.number_input("Semi-axis b (cm)",min_value=0.5,value=2.2)
            with g2: c_ax=st.number_input("Semi-axis c (cm)",min_value=0.5,value=2.2)
            if st.button(T("calc_mass")): mass_g=estimate_ellipsoid(a,b,c_ax,DENSITY_TABLE[dk])
        if mass_g:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.74rem;color:#2A7A7A;padding:6px 0;">{T("est_mass")}: {mass_g}g</div>',unsafe_allow_html=True)
            if fname and st.button(T("est_nutrition")):
                with st.spinner(""):
                    result=estimate_nutrition_from_mass(fname,mass_g)
                if "error" not in result:
                    st.markdown(f'<div class="rc">{badge_html("standard_geometric")}<div class="rn">{result["food"]}</div><div class="rd">{mass_g}g from dimensions</div>'+chips(result["calories"],result["protein_g"],result["carbs_g"],result["fat_g"])+'</div>',unsafe_allow_html=True)
                    if st.button(T("use_this"),key="use_geo"):
                        result["input_method"]="standard_geometric"; st.session_state.result=result; st.rerun()

    if st.session_state.result:
        r=st.session_state.result
        st.markdown(f'<div class="lp"><div class="lp-title">{T("log_meal")}</div><div class="lp-food">{r.get("food","")}</div>',unsafe_allow_html=True)
        lc1,lc2,lc3=st.columns(3)
        with lc1:
            p_opts=["Custom (grams)"]+list(PORTION_PRESETS.keys())
            p_ch=st.selectbox(T("portion"),p_opts)
        with lc2:
            if p_ch=="Custom (grams)": qty=st.number_input("g",min_value=1.0,value=100.0)
            else:
                qty=p_ch
                st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.7rem;color:#4A4A3A;padding-top:26px;">≈ {PORTION_PRESETS[p_ch]}g</div>',unsafe_allow_html=True)
        with lc3:
            meal_opts=["breakfast","lunch","dinner","snack"]
            meal_lbls=[T(m) for m in meal_opts]
            def_idx=meal_opts.index(st.session_state.active_meal) if st.session_state.active_meal in meal_opts else 0
            meal_sel=st.selectbox(T("meal"),meal_lbls,index=def_idx)
            meal_type=meal_opts[meal_lbls.index(meal_sel)]; st.session_state.active_meal=meal_type
        scaled=scale_nutrition(r,qty)
        st.markdown(chips(scaled["calories"],scaled["protein_g"],scaled["carbs_g"],scaled["fat_g"]),unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
        bl,bf,bc_=st.columns(3)
        with bl:
            if st.button(T("log_meal"),use_container_width=True):
                log_entry(user_id,r.get("food","Unknown"),r.get("calories",0),r.get("protein_g",0),r.get("carbs_g",0),r.get("fat_g",0),scaled["quantity_g"],meal_type,r.get("input_method","unknown"),r.get("source","unknown"))
                st.session_state.result=None; st.session_state.page="daily_log"; st.rerun()
        with bf:
            if st.button(T("save_fav"),use_container_width=True):
                add_favourite(user_id,r.get("food","")); st.success(T("saved_ok"))
        with bc_:
            if st.button(T("clear"),use_container_width=True):
                st.session_state.result=None; st.rerun()


# ══════════════════════════════════════════════════════════════
# FAVOURITES
# ══════════════════════════════════════════════════════════════
elif page=="favourites":
    st.markdown(f'<div class="zh"><div class="pt">{T("favourites")}</div><div class="ps">{T("fav_sub")}</div></div>',unsafe_allow_html=True)
    favs=get_favourites(user_id)
    if not favs:
        st.markdown(f'<div class="empty"><span class="big">{ic("star",28,"#2A2D32")}</span>{T("no_favs")}<br><span style="font-size:0.7rem;">{T("save_hint")}</span></div>',unsafe_allow_html=True)
    else:
        max_favs=None if is_premium else 10
        if not is_premium and len(favs)>=10:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.56rem;color:#D9B86A;padding:4px 0 10px;">{ic("crown",12,"#D9B86A")} Premium: unlimited favourites · Free: 10 max</div>',unsafe_allow_html=True)
        for f in favs[:max_favs]:
            c1,c2=st.columns([4,1])
            with c1:
                st.markdown(f'<div class="rc" style="padding:14px 16px;"><div class="rn" style="font-size:0.95rem;">{f["food"]}</div>'+chips(f["calories"],f["protein_g"],f["carbs_g"],f["fat_g"])+'</div>',unsafe_allow_html=True)
            with c2:
                st.markdown("<div style='padding-top:14px;'>",unsafe_allow_html=True)
                if st.button(T("use_this"),key=f"fav_{f['food']}"):
                    fav_r=dict(f); fav_r["input_method"]=f.get("source","database")
                    st.session_state.result=fav_r; st.session_state.page="search_log"; st.rerun()
                st.markdown("</div>",unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════
elif page=="settings":
    st.markdown(f'<div class="zh"><div class="pt">{T("settings")}</div><div class="ps">{T("settings_sub")}</div></div>',unsafe_allow_html=True)
    urow=get_user_profile(user_id)
    if urow: uname,uemail,uage,uheight,uweight,ugoal,ucal,uprem=urow
    else: uname=uemail=uage=uheight=uweight=ugoal=ucal=uprem=None

    # Profile
    premium_badge = f'<div style="font-family:JetBrains Mono,monospace;font-size:0.54rem;color:#D9B86A;margin-top:5px;">Premium member</div>' if uprem else ""
    st.markdown(f'<div class="ss"><div class="ss-title">{T("profile")}</div><div style="font-family:Inter,sans-serif;font-size:0.8rem;color:#4A4A3A;"><b style="color:#D8D0C0;">{uname}</b> · {uemail}</div>{premium_badge}</div>', unsafe_allow_html=True)

    # Language
    st.markdown(f'<div class="ss"><div class="ss-title">{ic("globe",13,"#C4622D")} {T("language")}</div>',unsafe_allow_html=True)
    lang_sel=st.radio("",["en","fr"],format_func=lambda x:"English" if x=="en" else "Français",horizontal=True,index=0 if st.session_state.language=="en" else 1,label_visibility="collapsed")
    if lang_sel!=st.session_state.language:
        st.session_state.language=lang_sel; update_user_prefs(user_id,language=lang_sel); st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)

    # Goal
    st.markdown(f'<div class="ss"><div class="ss-title">{ic("target",13,"#C4622D")} {T("goal_label")} & {T("calorie_target")}</div>',unsafe_allow_html=True)
    goal_opts=["Lose weight","Build muscle","Maintain weight","General health","Track what I eat"]
    curr_g=ugoal or "general"
    matched=next((g for g in goal_opts if g.lower().startswith(curr_g.split()[0].lower())),goal_opts[3])
    new_goal=st.selectbox(T("goal_label"),goal_opts,index=goal_opts.index(matched) if matched in goal_opts else 3)
    new_cal=st.number_input(T("calorie_target"),min_value=800,max_value=5000,value=int(ucal or 2000),step=50)
    if st.button(T("save_changes"),key="save_goal"):
        update_user_prefs(user_id,goal=new_goal.lower(),daily_calorie_goal=new_cal); st.session_state.daily_goal=new_cal; st.success(T("saved_ok"))
    st.markdown('</div>',unsafe_allow_html=True)

    # Halal
    st.markdown(f'<div class="halal-feat"><div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">{ic("moon",17,"#7DC48A")}<div class="halal-feat-title">{T("halal_scanner")}</div></div><div class="halal-feat-desc">{T("halal_explain")}</div>',unsafe_allow_html=True)
    halal_on=st.checkbox(T("enable_halal"),value=st.session_state.is_muslim)
    if halal_on!=st.session_state.is_muslim:
        st.session_state.is_muslim=halal_on; update_user_prefs(user_id,is_muslim=int(halal_on)); st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)

    # Physical
    st.markdown(f'<div class="ss"><div class="ss-title">{ic("scale",13,"#C4622D")} {T("physical")}</div>',unsafe_allow_html=True)
    pc1,pc2,pc3=st.columns(3)
    with pc1: s_age=st.number_input(T("age_label"),min_value=10,max_value=100,value=int(uage or 20))
    with pc2: s_ht=st.number_input(T("height_label"),min_value=100.0,max_value=220.0,value=float(uheight or 165))
    with pc3: s_wt=st.number_input(T("weight_label"),min_value=20.0,max_value=250.0,value=float(uweight or 65))
    if st.button(T("save_changes"),key="save_phys"):
        update_user_prefs(user_id,age=int(s_age),height_cm=float(s_ht),weight_kg=float(s_wt)); st.success(T("saved_ok"))
    st.markdown('</div>',unsafe_allow_html=True)

    # Weight log
    st.markdown(f'<div class="ss"><div class="ss-title">{ic("trend",13,"#C4622D")} {T("weight_log")}</div>',unsafe_allow_html=True)
    wh=get_weight_history(user_id)
    if wh:
        fig_w=weight_chart(wh)
        if fig_w: st.plotly_chart(fig_w,use_container_width=True,config={"displayModeBar":False})
        st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.66rem;color:#4A4A3A;margin-bottom:6px;">Last: <span style="color:#D8D0C0;">{wh[-1][1]} kg</span> — {wh[-1][0]}</div>',unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="font-family:Inter,sans-serif;font-size:0.78rem;color:#4A4A3A;margin-bottom:6px;">{T("no_weights")}</div>',unsafe_allow_html=True)
    new_w=st.number_input(T("weight_label"),min_value=20.0,max_value=250.0,value=float(uweight or 65),key="new_w")
    if st.button(T("log_weight"),key="log_w"):
        log_weight_entry(user_id,new_w); update_user_prefs(user_id,weight_kg=new_w); st.success(T("saved_ok")); st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)

    # Premium upgrade section
    if not is_premium:
        st.markdown("---")
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1A1810 0%,#1A1420 100%);
            border:1px solid #B0822A40;border-radius:14px;padding:22px 24px;text-align:center;">
            <div style="margin-bottom:10px;">{ic("crown",28,"#D9B86A")}</div>
            <div style="font-family:Fraunces,serif;font-size:1.3rem;font-weight:300;color:#F4F0E6;margin-bottom:6px;">Velora Premium</div>
            <div style="font-family:Inter,sans-serif;font-size:0.78rem;color:#6A6A5A;line-height:1.6;margin-bottom:16px;">
                Unlimited photo estimation · Full meal history · AI nutrition advice ·
                Unlimited favourites · Weekly trend charts · PDF export (coming soon)
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"{T('upgrade')} →", use_container_width=True, key="upgrade_main"):
            st.info("Payment integration coming soon. Contact us to activate Premium manually.")