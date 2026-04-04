"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              ATLAS v20                                        ║
║          Autonomous Terrestrial Life Analysis System                          ║
║                                                                               ║
║  Дипломный проект: Платформа исследования экзопланет                         ║
║                                                                               ║
║  Features:                                                                    ║
║  - NASA Exoplanet Archive integration                                         ║
║  - 3D stellar neighborhood map                                                ║
║  - Smart AI analysis & hypothesis generation                                  ║
║  - Presentation mode                                                          ║
║  - Multilingual (RU/EN/KZ)                                                    ║
║  - Dark/Light adaptive themes                                                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import math
import numpy as np
import requests
import time
import random
import json
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# ML CHATBOT (optional)
# ═══════════════════════════════════════════════════════════════════════════════
try:
    import joblib
    chatbot_model = joblib.load('exo_chatbot_model.pkl')
    with open('exo_chatbot_responses.json', 'r', encoding='utf-8') as f:
        chatbot_responses = json.load(f)
    CHATBOT_AVAILABLE = True
except:
    chatbot_model = None
    chatbot_responses = {}
    CHATBOT_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ATLAS — Exoplanet Research Platform",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
DEFAULTS = {
    'lang': 'ru',
    'theme': 'dark',
    'scan_count': 0,
    'habitable_count': 0,
    'selected_idx': 0,
    'compare': [],
    'chat_history': [],
    'custom_planets': {},
    'atlas_results': [],
    'saved_systems': {},
    'scanned_stars': set(),
    'current_system': None,
    'selected_catalog': 'nearby',
    'presentation_mode': False,
    'hypotheses': [],
    'recommendations': [],
    # LM Studio settings
    'lm_studio_enabled': False,
    'lm_studio_ip': 'localhost',
    'lm_studio_port': '1234',
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

if isinstance(st.session_state.scanned_stars, list):
    st.session_state.scanned_stars = set(st.session_state.scanned_stars)

# ═══════════════════════════════════════════════════════════════════════════════
# TRANSLATIONS (100+ keys, 3 languages)
# ═══════════════════════════════════════════════════════════════════════════════
TR = {
    'app_title': {'ru': '🛰️ ATLAS', 'en': '🛰️ ATLAS', 'kz': '🛰️ ATLAS'},
    'app_subtitle': {'ru': 'Autonomous Terrestrial Life Analysis System', 'en': 'Autonomous Terrestrial Life Analysis System', 'kz': 'Жерлік өмірді автономды талдау жүйесі'},
    'tab_missions': {'ru': '🚀 Миссии', 'en': '🚀 Missions', 'kz': '🚀 Миссиялар'},
    'tab_system': {'ru': '🪐 Система', 'en': '🪐 System', 'kz': '🪐 Жүйе'},
    'tab_starmap': {'ru': '🗺️ Карта', 'en': '🗺️ Map', 'kz': '🗺️ Карта'},
    'tab_analysis': {'ru': '🧠 Анализ', 'en': '🧠 Analysis', 'kz': '🧠 Талдау'},
    'tab_compare': {'ru': '📊 Сравнение', 'en': '📊 Compare', 'kz': '📊 Салыстыру'},
    'tab_encyclopedia': {'ru': '📚 Справка', 'en': '📚 Reference', 'kz': '📚 Анықтама'},
    'tab_history': {'ru': '📜 История', 'en': '📜 History', 'kz': '📜 Тарих'},
    'tab_travel': {'ru': '🚀 Полёт', 'en': '🚀 Travel', 'kz': '🚀 Ұшу'},
    'tab_presentation': {'ru': '🎬 Презентация', 'en': '🎬 Presentation', 'kz': '🎬 Презентация'},
    'sidebar_lang': {'ru': '🌐 Язык', 'en': '🌐 Language', 'kz': '🌐 Тіл'},
    'sidebar_theme': {'ru': '🎨 Тема', 'en': '🎨 Theme', 'kz': '🎨 Тақырып'},
    'sidebar_stats': {'ru': '📊 Статистика', 'en': '📊 Statistics', 'kz': '📊 Статистика'},
    'sidebar_search': {'ru': '⚡ Поиск', 'en': '⚡ Search', 'kz': '⚡ Іздеу'},
    'theme_dark': {'ru': '🌙 Тёмная', 'en': '🌙 Dark', 'kz': '🌙 Қараңғы'},
    'theme_light': {'ru': '☀️ Светлая', 'en': '☀️ Light', 'kz': '☀️ Жарық'},
    'stat_systems': {'ru': 'Систем', 'en': 'Systems', 'kz': 'Жүйелер'},
    'stat_habitable': {'ru': 'Обитаемых', 'en': 'Habitable', 'kz': 'Мекендеуге жарамды'},
    'stat_skipped': {'ru': 'Пропущено', 'en': 'Skipped', 'kz': 'Өткізілді'},
    'mission_control': {'ru': '🤖 Центр управления миссиями', 'en': '🤖 Mission Control', 'kz': '🤖 Миссия басқару орталығы'},
    'select_catalog': {'ru': '🗂️ Каталог', 'en': '🗂️ Catalog', 'kz': '🗂️ Каталог'},
    'stars_available': {'ru': 'звёзд доступно', 'en': 'stars available', 'kz': 'жұлдыз қолжетімді'},
    'skip_scanned': {'ru': 'Пропускать изученные', 'en': 'Skip scanned', 'kz': 'Зерттелгенді өткізу'},
    'targets': {'ru': '🎯 Целей', 'en': '🎯 Targets', 'kz': '🎯 Мақсаттар'},
    'start_mission': {'ru': '🚀 Запустить', 'en': '🚀 Start', 'kz': '🚀 Бастау'},
    'clear_scanned': {'ru': '🔄 Сбросить', 'en': '🔄 Reset', 'kz': '🔄 Қалпына келтіру'},
    'mission_complete': {'ru': '✅ Миссия завершена', 'en': '✅ Mission complete', 'kz': '✅ Миссия аяқталды'},
    'candidates_found': {'ru': 'кандидатов', 'en': 'candidates', 'kz': 'үміткер'},
    'load_best': {'ru': '📂 Загрузить лучшую', 'en': '📂 Load best', 'kz': '📂 Үздікті жүктеу'},
    'system_view': {'ru': '🌟 Звёздная система', 'en': '🌟 Star System', 'kz': '🌟 Жұлдыз жүйесі'},
    'select_planet': {'ru': '🪐 Выберите планету', 'en': '🪐 Select planet', 'kz': '🪐 Планета таңдаңыз'},
    'detailed_analysis': {'ru': '🔬 Детальный анализ', 'en': '🔬 Detailed Analysis', 'kz': '🔬 Толық талдау'},
    'physical': {'ru': '⚙️ Физические', 'en': '⚙️ Physical', 'kz': '⚙️ Физикалық'},
    'orbital': {'ru': '🌀 Орбитальные', 'en': '🌀 Orbital', 'kz': '🌀 Орбиталық'},
    'habitability': {'ru': '🌱 Обитаемость', 'en': '🌱 Habitability', 'kz': '🌱 Мекендеуге жарамдылық'},
    'star_params': {'ru': '⭐ Звезда', 'en': '⭐ Star', 'kz': '⭐ Жұлдыз'},
    'atmosphere': {'ru': '🌫️ Атмосфера', 'en': '🌫️ Atmosphere', 'kz': '🌫️ Атмосфера'},
    'hazards': {'ru': '⚠️ Угрозы', 'en': '⚠️ Hazards', 'kz': '⚠️ Қауіптер'},
    'biosignatures': {'ru': '🧬 Биосигнатуры', 'en': '🧬 Biosignatures', 'kz': '🧬 Биосигнатуралар'},
    'add_compare': {'ru': '➕ В сравнение', 'en': '➕ Add to compare', 'kz': '➕ Салыстыруға'},
    'no_system': {'ru': '🔭 Нет данных. Запустите миссию!', 'en': '🔭 No data. Run a mission!', 'kz': '🔭 Деректер жоқ. Миссия іске қосыңыз!'},
    'starmap_title': {'ru': '🗺️ Карта звёздного окружения', 'en': '🗺️ Stellar Neighborhood Map', 'kz': '🗺️ Жұлдыздық аймақ картасы'},
    'starmap_desc': {'ru': '3D карта исследованных систем относительно Солнца', 'en': '3D map of explored systems relative to the Sun', 'kz': 'Күнге қатысты зерттелген жүйелердің 3D картасы'},
    'starmap_empty': {'ru': 'Карта пуста. Исследуйте системы!', 'en': 'Map empty. Explore systems!', 'kz': 'Карта бос. Жүйелерді зерттеңіз!'},
    'analysis_title': {'ru': '🧠 Интеллектуальный анализ ATLAS', 'en': '🧠 ATLAS Intelligent Analysis', 'kz': '🧠 ATLAS интеллектуалды талдау'},
    'recommendations': {'ru': '💡 Рекомендации', 'en': '💡 Recommendations', 'kz': '💡 Ұсыныстар'},
    'hypotheses': {'ru': '🔬 Научные гипотезы', 'en': '🔬 Scientific Hypotheses', 'kz': '🔬 Ғылыми болжамдар'},
    'generate_analysis': {'ru': '🧠 Сгенерировать анализ', 'en': '🧠 Generate analysis', 'kz': '🧠 Талдау жасау'},
    'no_data_analysis': {'ru': 'Мало данных. Исследуйте больше систем.', 'en': 'Not enough data. Explore more.', 'kz': 'Деректер аз. Көбірек зерттеңіз.'},
    'compare_title': {'ru': '📊 Сравнение планет', 'en': '📊 Planet Comparison', 'kz': '📊 Планеталарды салыстыру'},
    'select_planets': {'ru': 'Выберите планеты:', 'en': 'Select planets:', 'kz': 'Планеталарды таңдаңыз:'},
    'radar_chart': {'ru': '🕸️ Радар', 'en': '🕸️ Radar', 'kz': '🕸️ Радар'},
    'bar_chart': {'ru': '📊 Гистограмма', 'en': '📊 Bar Chart', 'kz': '📊 Гистограмма'},
    'comparison_table': {'ru': '📋 Таблица', 'en': '📋 Table', 'kz': '📋 Кесте'},
    'clear_selection': {'ru': '🗑️ Очистить', 'en': '🗑️ Clear', 'kz': '🗑️ Тазалау'},
    'encyclopedia_title': {'ru': '📚 Справочник', 'en': '📚 Reference Guide', 'kz': '📚 Анықтамалық'},
    'history_title': {'ru': '📜 История исследований', 'en': '📜 Research History', 'kz': '📜 Зерттеу тарихы'},
    'saved_systems': {'ru': '📂 Сохранённые системы', 'en': '📂 Saved Systems', 'kz': '📂 Сақталған жүйелер'},
    'load_system': {'ru': 'Загрузить', 'en': 'Load', 'kz': 'Жүктеу'},
    'clear_history': {'ru': '🗑️ Очистить', 'en': '🗑️ Clear', 'kz': '🗑️ Тазалау'},
    'history_empty': {'ru': '📭 История пуста', 'en': '📭 History empty', 'kz': '📭 Тарих бос'},
    'travel_title': {'ru': '🚀 Межзвёздный калькулятор', 'en': '🚀 Interstellar Calculator', 'kz': '🚀 Жұлдызаралық калькулятор'},
    'destination': {'ru': '📍 Цель', 'en': '📍 Destination', 'kz': '📍 Мақсат'},
    'distance_ly': {'ru': 'Расстояние (св.лет)', 'en': 'Distance (ly)', 'kz': 'Қашықтық (ж.ж.)'},
    'velocity': {'ru': '⚡ Скорость', 'en': '⚡ Velocity', 'kz': '⚡ Жылдамдық'},
    'earth_time': {'ru': '⏱️ Время Земли', 'en': '⏱️ Earth Time', 'kz': '⏱️ Жер уақыты'},
    'ship_time': {'ru': '🧑‍🚀 Время корабля', 'en': '🧑‍🚀 Ship Time', 'kz': '🧑‍🚀 Кеме уақыты'},
    'lorentz': {'ru': '⚡ Фактор Лоренца', 'en': '⚡ Lorentz Factor', 'kz': '⚡ Лоренц факторы'},
    'fuel': {'ru': '⚛️ Антиматерия', 'en': '⚛️ Antimatter', 'kz': '⚛️ Антиматерия'},
    'journey_preview': {'ru': '🎬 Превью', 'en': '🎬 Preview', 'kz': '🎬 Алдын ала көру'},
    'phases': {'ru': '📅 Фазы', 'en': '📅 Phases', 'kz': '📅 Фазалар'},
    'presentation_title': {'ru': '🎬 Режим презентации', 'en': '🎬 Presentation Mode', 'kz': '🎬 Презентация режимі'},
    'start_presentation': {'ru': '▶️ Начать', 'en': '▶️ Start', 'kz': '▶️ Бастау'},
    'stop_presentation': {'ru': '⏹️ Завершить', 'en': '⏹️ End', 'kz': '⏹️ Аяқтау'},
    'slide_overview': {'ru': '📊 Обзор', 'en': '📊 Overview', 'kz': '📊 Шолу'},
    'slide_top': {'ru': '🏆 Лучшие', 'en': '🏆 Top', 'kz': '🏆 Үздік'},
    'slide_conclusions': {'ru': '📝 Выводы', 'en': '📝 Conclusions', 'kz': '📝 Қорытынды'},
    'loading': {'ru': 'Загрузка...', 'en': 'Loading...', 'kz': 'Жүктелуде...'},
    'found': {'ru': '✅ Найдено', 'en': '✅ Found', 'kz': '✅ Табылды'},
    'not_found': {'ru': '❌ Не найдено', 'en': '❌ Not found', 'kz': '❌ Табылмады'},
    'planets': {'ru': 'планет', 'en': 'planets', 'kz': 'планета'},
    'best': {'ru': 'Лучший', 'en': 'Best', 'kz': 'Үздік'},
    'unknown': {'ru': 'Неизв.', 'en': 'Unknown', 'kz': 'Белгісіз'},
    'yes': {'ru': 'Да', 'en': 'Yes', 'kz': 'Иә'},
    'no': {'ru': 'Нет', 'en': 'No', 'kz': 'Жоқ'},
    'radius': {'ru': 'Радиус', 'en': 'Radius', 'kz': 'Радиус'},
    'mass': {'ru': 'Масса', 'en': 'Mass', 'kz': 'Масса'},
    'temp': {'ru': 'Температура', 'en': 'Temperature', 'kz': 'Температура'},
    'density': {'ru': 'Плотность', 'en': 'Density', 'kz': 'Тығыздық'},
    'gravity': {'ru': 'Гравитация', 'en': 'Gravity', 'kz': 'Гравитация'},
    'orbit': {'ru': 'Орбита', 'en': 'Orbit', 'kz': 'Орбита'},
    'period': {'ru': 'Период', 'en': 'Period', 'kz': 'Кезең'},
    'distance': {'ru': 'Расстояние', 'en': 'Distance', 'kz': 'Қашықтық'},
    'score': {'ru': 'Оценка', 'en': 'Score', 'kz': 'Баға'},
    'esi': {'ru': 'ESI', 'en': 'ESI', 'kz': 'ESI'},
    'in_hz': {'ru': 'В зоне HZ', 'en': 'In HZ', 'kz': 'HZ аймағында'},
    'escape_v': {'ru': 'Убегания', 'en': 'Escape', 'kz': 'Қашу'},
    'pressure': {'ru': 'Давление', 'en': 'Pressure', 'kz': 'Қысым'},
    'year_len': {'ru': 'Год', 'en': 'Year', 'kz': 'Жыл'},
    'mag_field': {'ru': 'Магн.поле', 'en': 'Mag.Field', 'kz': 'Магн.өріс'},
    'moons': {'ru': 'Спутники', 'en': 'Moons', 'kz': 'Серіктер'},
}

def t(key):
    """Get translation for current language"""
    lang = st.session_state.get('lang', 'ru')
    return TR.get(key, {}).get(lang, key)

# ═══════════════════════════════════════════════════════════════════════════════
# CATALOGS
# ═══════════════════════════════════════════════════════════════════════════════
CATALOGS = {
    'nearby': {
        'name': {'ru': '🌟 Ближайшие (<50 св.лет)', 'en': '🌟 Nearby (<50 ly)', 'kz': '🌟 Жақын (<50 ж.ж.)'},
        'stars': ["Proxima", "TRAPPIST-1", "Ross-128", "Luyten", "Wolf-1061", "GJ-1061", "Teegarden", "YZ-Ceti", "GJ-273", "Kapteyn"]
    },
    'kepler': {
        'name': {'ru': '🔭 Kepler', 'en': '🔭 Kepler', 'kz': '🔭 Kepler'},
        'stars': ["Kepler-442", "Kepler-62", "Kepler-186", "Kepler-452", "Kepler-22", "Kepler-69", "Kepler-438", "Kepler-296", "Kepler-1649", "Kepler-1652"]
    },
    'tess': {
        'name': {'ru': '🛰️ TESS', 'en': '🛰️ TESS', 'kz': '🛰️ TESS'},
        'stars': ["TOI-700", "TOI-1452", "TOI-715", "LHS-1140", "LP-890-9", "TOI-1235", "TOI-270", "TOI-540", "K2-18", "GJ-357"]
    },
    'habitable': {
        'name': {'ru': '🌱 Обитаемые', 'en': '🌱 Habitable', 'kz': '🌱 Мекендеуге жарамды'},
        'stars': ["TRAPPIST-1", "Proxima", "TOI-700", "Kepler-442", "Kepler-62", "LHS-1140", "K2-18", "Kepler-186", "GJ-667C", "HD-40307"]
    },
    'giants': {
        'name': {'ru': '🪐 Гиганты', 'en': '🪐 Giants', 'kz': '🪐 Алыптар'},
        'stars': ["HD-209458", "51-Peg", "HD-189733", "WASP-12", "WASP-17", "HAT-P-7", "TrES-2", "HD-149026", "WASP-79", "KELT-9"]
    },
    'multiplanet': {
        'name': {'ru': '🌐 Многопланетные', 'en': '🌐 Multi-planet', 'kz': '🌐 Көппланеталы'},
        'stars': ["TRAPPIST-1", "Kepler-90", "HD-10180", "Kepler-11", "HR-8799", "55-Cnc", "GJ-876", "Kepler-80", "TOI-178", "HD-219134"]
    }
}

KNOWN_PLANETS = {
    "Earth": {"radius": 1.0, "mass": 1.0, "temp": 288, "distance": 0, "esi": 1.0, "emoji": "🌍", "gravity": 1.0},
    "TRAPPIST-1e": {"radius": 0.92, "mass": 0.77, "temp": 251, "distance": 40.7, "esi": 0.85, "emoji": "🔵", "gravity": 0.93},
    "Proxima b": {"radius": 1.08, "mass": 1.27, "temp": 234, "distance": 4.24, "esi": 0.87, "emoji": "🔴", "gravity": 1.08},
    "Kepler-442b": {"radius": 1.34, "mass": 2.34, "temp": 233, "distance": 1206, "esi": 0.84, "emoji": "🟢", "gravity": 1.3},
    "TOI-700 d": {"radius": 1.19, "mass": 1.72, "temp": 268, "distance": 101.4, "esi": 0.93, "emoji": "🌎", "gravity": 1.21},
}
# ═══════════════════════════════════════════════════════════════════════════════
# CSS THEMES
# ═══════════════════════════════════════════════════════════════════════════════

def get_css():
    """Generate CSS based on current theme"""
    theme = st.session_state.get('theme', 'dark')
    
    if theme == 'dark':
        return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg-primary: #0a0a1a;
    --bg-secondary: #0f0f2a;
    --bg-card: rgba(255,255,255,0.03);
    --bg-card-hover: rgba(255,255,255,0.06);
    --border: rgba(255,255,255,0.08);
    --border-accent: rgba(0,212,255,0.3);
    --text-primary: rgba(255,255,255,0.95);
    --text-secondary: rgba(255,255,255,0.7);
    --text-dim: rgba(255,255,255,0.5);
    --accent: #00d4ff;
    --accent2: #00ff88;
    --accent3: #bf00ff;
    --danger: #ff6b6b;
    --warning: #ffd93d;
    --success: #00ff88;
}

/* Main background */
.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #1a0a2e 50%, #0a1a2a 100%) !important;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Orbitron', monospace !important;
    color: var(--accent) !important;
    letter-spacing: 0.5px;
}

p, span, div, label, td, th, li {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(10,10,30,0.98) 0%, rgba(15,10,35,0.98) 100%) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: var(--accent) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card);
    padding: 12px;
    border-radius: 16px;
    gap: 8px !important;
    border: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    color: var(--text-dim) !important;
    font-weight: 500 !important;
    padding: 12px 20px !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(0,212,255,0.1) !important;
    color: var(--text-primary) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(0,255,136,0.1)) !important;
    color: white !important;
    border: 1px solid var(--border-accent) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(0,255,136,0.1)) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,212,255,0.3), rgba(0,255,136,0.2)) !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,212,255,0.2) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00d4ff, #00ff88) !important;
    color: #000 !important;
    font-weight: 600 !important;
}

/* Metrics */
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    color: var(--accent) !important;
    font-size: 1.8rem !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: rgba(0,20,40,0.5) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: white !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 10px rgba(0,212,255,0.3) !important;
}

.stSelectbox > div > div {
    background: rgba(0,20,40,0.5) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* DataFrames & Tables - DARK THEME */
.stDataFrame, [data-testid="stDataFrame"] {
    background: rgba(0,20,40,0.4) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}

.stDataFrame td, .stDataFrame th,
[data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
    color: white !important;
    background: transparent !important;
    border-color: var(--border) !important;
}

.stTable td, .stTable th {
    color: white !important;
    border: 1px solid var(--border) !important;
    padding: 12px !important;
}

/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
    border-radius: 10px !important;
}

.stProgress > div {
    background: rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
}

/* Alerts & Info boxes */
.stAlert {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}

/* Code blocks */
.stCodeBlock {
    background: rgba(0,10,20,0.8) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

.stCodeBlock code {
    color: var(--accent) !important;
}

/* Custom cards */
.info-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0;
    transition: all 0.3s ease;
}

.info-card:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-accent);
}

.stat-badge {
    display: inline-block;
    background: rgba(0,212,255,0.15);
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 20px;
    padding: 6px 14px;
    margin: 4px;
    font-size: 0.9rem;
    color: white !important;
}

.score-high { color: #00ff88 !important; }
.score-med { color: #00d4ff !important; }
.score-low { color: #ffd93d !important; }
.score-bad { color: #ff6b6b !important; }

/* Hide Streamlit branding */
#MainMenu, footer { visibility: hidden; }

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-accent); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* Animations */
@keyframes glow {
    0%, 100% { box-shadow: 0 0 20px rgba(0,212,255,0.3); }
    50% { box-shadow: 0 0 40px rgba(0,212,255,0.6); }
}

.glow-effect { animation: glow 2s ease-in-out infinite; }
</style>
"""
    else:  # LIGHT THEME - COMPLETELY FIXED
        return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg-primary: #f8fafc;
    --bg-secondary: #f1f5f9;
    --bg-card: #ffffff;
    --bg-card-hover: #f8fafc;
    --border: #cbd5e1;
    --border-accent: #0284c7;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-dim: #64748b;
    --accent: #0284c7;
    --accent2: #059669;
    --accent3: #7c3aed;
    --danger: #dc2626;
    --warning: #d97706;
    --success: #059669;
}

/* Main background */
.stApp {
    background: linear-gradient(135deg, #f0f9ff 0%, #ecfdf5 50%, #faf5ff 100%) !important;
}

/* Typography - DARK TEXT FOR LIGHT THEME */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Orbitron', monospace !important;
    color: var(--accent) !important;
    letter-spacing: 0.5px;
}

p, span, div, label, li {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
    border-right: 2px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: var(--accent) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card);
    padding: 12px;
    border-radius: 16px;
    gap: 8px !important;
    border: 2px solid var(--border);
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.stTabs [data-baseweb="tab"] {
    color: var(--text-dim) !important;
    font-weight: 500 !important;
    padding: 12px 20px !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(2,132,199,0.1) !important;
    color: var(--text-primary) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(2,132,199,0.15), rgba(5,150,105,0.1)) !important;
    color: var(--text-primary) !important;
    border: 2px solid var(--border-accent) !important;
}

/* Buttons */
.stButton > button {
    background: var(--bg-card) !important;
    border: 2px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
}

.stButton > button:hover {
    background: rgba(2,132,199,0.1) !important;
    border-color: var(--border-accent) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(2,132,199,0.15) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0284c7, #059669) !important;
    color: white !important;
    font-weight: 600 !important;
    border: none !important;
}

/* Metrics */
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    color: var(--accent) !important;
    font-size: 1.8rem !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: var(--bg-card) !important;
    border: 2px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--border-accent) !important;
    box-shadow: 0 0 0 3px rgba(2,132,199,0.1) !important;
}

.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 2px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

.stSelectbox > div > div * {
    color: var(--text-primary) !important;
}

/* DataFrames & Tables - LIGHT THEME WITH VISIBLE BORDERS */
.stDataFrame, [data-testid="stDataFrame"] {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    border: 2px solid var(--border) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}

.stDataFrame td, .stDataFrame th,
[data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
    color: var(--text-primary) !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    padding: 12px !important;
}

.stDataFrame th, [data-testid="stDataFrame"] th {
    background: var(--bg-secondary) !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
}

/* st.table - FIXED BORDERS */
.stTable {
    border-collapse: collapse !important;
    width: 100% !important;
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 2px solid var(--border) !important;
}

.stTable td, .stTable th {
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    padding: 14px !important;
    text-align: left !important;
}

.stTable th {
    background: var(--bg-secondary) !important;
    font-weight: 600 !important;
}

.stTable tr:nth-child(even) td {
    background: var(--bg-secondary) !important;
}

.stTable tr:hover td {
    background: rgba(2,132,199,0.05) !important;
}

/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
    border-radius: 10px !important;
}

.stProgress > div {
    background: var(--border) !important;
    border-radius: 10px !important;
}

/* Alerts & Info boxes */
.stAlert {
    background: var(--bg-card) !important;
    border: 2px solid var(--border) !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}

.stAlert p, .stAlert span {
    color: var(--text-primary) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 2px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}

.streamlit-expanderContent {
    background: var(--bg-card) !important;
    border: 2px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
}

/* Code blocks */
.stCodeBlock {
    background: var(--bg-secondary) !important;
    border: 2px solid var(--border) !important;
    border-radius: 12px !important;
}

.stCodeBlock code {
    color: var(--text-primary) !important;
}

/* Checkboxes */
.stCheckbox label span {
    color: var(--text-primary) !important;
}

/* Radio buttons */
.stRadio label span {
    color: var(--text-primary) !important;
}

/* Slider */
.stSlider label {
    color: var(--text-primary) !important;
}

/* Custom cards - LIGHT */
.info-card {
    background: var(--bg-card);
    border: 2px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.info-card:hover {
    border-color: var(--border-accent);
    box-shadow: 0 4px 16px rgba(2,132,199,0.1);
}

.stat-badge {
    display: inline-block;
    background: rgba(2,132,199,0.1);
    border: 2px solid rgba(2,132,199,0.3);
    border-radius: 20px;
    padding: 6px 14px;
    margin: 4px;
    font-size: 0.9rem;
    color: var(--text-primary) !important;
}

.score-high { color: #059669 !important; font-weight: 600; }
.score-med { color: #0284c7 !important; font-weight: 600; }
.score-low { color: #d97706 !important; font-weight: 600; }
.score-bad { color: #dc2626 !important; font-weight: 600; }

/* Markdown tables */
.stMarkdown table {
    border-collapse: collapse !important;
    width: 100% !important;
    background: var(--bg-card) !important;
    border: 2px solid var(--border) !important;
    border-radius: 12px !important;
    margin: 16px 0 !important;
}

.stMarkdown table td, .stMarkdown table th {
    border: 1px solid var(--border) !important;
    padding: 12px 16px !important;
    color: var(--text-primary) !important;
}

.stMarkdown table th {
    background: var(--bg-secondary) !important;
    font-weight: 600 !important;
}

.stMarkdown table tr:nth-child(even) td {
    background: rgba(241, 245, 249, 0.5) !important;
}

/* Hide Streamlit branding */
#MainMenu, footer { visibility: hidden; }

/* Scrollbar - Light */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-secondary); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-dim); }
</style>
"""

# Apply CSS
st.markdown(get_css(), unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════════════════════════
# PHYSICS CALCULATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def calc_luminosity(teff, rad):
    """Calculate stellar luminosity in solar units using Stefan-Boltzmann law.
    L = R² × (T/T☉)⁴ where T☉ = 5778K
    """
    if not teff or not rad or teff <= 0 or rad <= 0:
        return 1.0
    return (rad ** 2) * ((teff / 5778) ** 4)


def calc_equilibrium_temp(teff, srad, orbit, albedo=0.3):
    """Calculate planetary equilibrium temperature.
    Teq = T★ × √(R★/(2a)) × (1-A)^0.25
    Where A = albedo, a = orbital distance in AU
    """
    if not teff or not srad or not orbit or orbit <= 0:
        return None
    r_au = srad * 0.00465047  # Solar radii to AU
    return teff * math.sqrt(r_au / (2 * orbit)) * ((1 - albedo) ** 0.25)


def calc_orbit_from_period(period, stellar_mass=1.0):
    """Calculate semi-major axis from orbital period using Kepler's 3rd law.
    a = (P²/365.25² × M★)^(1/3) [AU]
    """
    if not period or period <= 0:
        return None
    return ((period / 365.25) ** 2 * (stellar_mass or 1)) ** (1/3)


def calc_habitable_zone(teff, srad, luminosity=None):
    """Calculate conservative habitable zone boundaries.
    Inner: 0.75√L AU (runaway greenhouse limit)
    Outer: 1.77√L AU (CO₂ condensation limit)
    """
    L = luminosity if luminosity and luminosity > 0 else calc_luminosity(teff, srad)
    inner = 0.75 * math.sqrt(L)
    outer = 1.77 * math.sqrt(L)
    return inner, outer, L


def calc_esi(radius, temp):
    """Calculate Earth Similarity Index (ESI).
    ESI = √[(1-|R-1|/(R+1))^0.57 × (1-|T-288|/(T+288))^5.58]
    Where R = radius in Earth radii, T = temperature in Kelvin
    ESI = 1.0 means identical to Earth
    """
    if not radius or not temp or radius <= 0 or temp <= 0:
        return 0
    esi_r = (1 - abs((radius - 1) / (radius + 1))) ** 0.57
    esi_t = (1 - abs((temp - 288) / (temp + 288))) ** 5.58
    return round(math.sqrt(esi_r * esi_t), 3)


def calc_surface_gravity(mass, radius):
    """Calculate surface gravity relative to Earth.
    g = M/R² where M and R are in Earth units
    """
    if not mass or not radius or radius <= 0:
        return None
    return mass / (radius ** 2)


def calc_density(mass, radius):
    """Calculate mean density relative to Earth.
    ρ = M/R³ where M and R are in Earth units
    Earth density = 5.51 g/cm³
    """
    if not mass or not radius or radius <= 0:
        return None
    return mass / (radius ** 3)


def calc_escape_velocity(mass, radius):
    """Calculate escape velocity in km/s.
    v_esc = 11.2 × √(M/R) where Earth's v_esc = 11.2 km/s
    """
    if not mass or not radius or radius <= 0:
        return None
    return 11.2 * math.sqrt(mass / radius)


def calc_surface_pressure(mass, radius, temp, has_atmosphere=True):
    """Estimate surface atmospheric pressure relative to Earth.
    Based on mass, radius, and temperature considerations.
    """
    if not mass or not radius:
        return None
    if not has_atmosphere:
        return 0
    
    g = mass / (radius ** 2)  # Surface gravity
    
    # Small planets can't retain atmosphere
    if radius < 0.5:
        return 0
    # Hot planets lose atmosphere
    if temp and temp > 1000:
        return 0
    # Gas giants have extreme pressure
    if radius > 4:
        return 100 + (radius - 4) * 50
    
    # Rocky planets - rough estimate
    base_pressure = g * radius
    if temp and temp > 500:
        base_pressure *= 0.3
    
    return round(max(0.01, min(base_pressure, 1000)), 2)


def calc_year_length(period):
    """Convert orbital period (days) to Earth years."""
    if not period:
        return None
    return period / 365.25


def calc_day_length(period, radius):
    """Estimate day length in hours.
    Close-in planets are likely tidally locked.
    """
    if not period or not radius:
        return None
    # Tidally locked if period < 20 days
    if period < 20:
        return None  # Tidally locked
    # Rough estimate based on size
    return 24 * (1 / (radius ** 0.5))


def estimate_magnetic_field(mass, radius):
    """Estimate presence and strength of magnetic field.
    Based on mass, radius, and implied internal structure.
    """
    if not mass or not radius:
        return t('unknown')
    
    density = mass / (radius ** 3)
    lang = st.session_state.get('lang', 'ru')
    
    responses = {
        'likely': {
            'ru': 'Вероятно (железное ядро)',
            'en': 'Likely (iron core dynamo)',
            'kz': 'Ықтимал (темір ядросы)'
        },
        'strong': {
            'ru': 'Сильное (металлический H)',
            'en': 'Strong (metallic hydrogen)',
            'kz': 'Күшті (металл сутегі)'
        },
        'uncertain': {
            'ru': 'Неопределённо',
            'en': 'Uncertain',
            'kz': 'Белгісіз'
        },
        'weak': {
            'ru': 'Слабое или отсутствует',
            'en': 'Weak or absent',
            'kz': 'Әлсіз немесе жоқ'
        },
        'unlikely': {
            'ru': 'Маловероятно',
            'en': 'Unlikely',
            'kz': 'Екіталай'
        }
    }
    
    if radius <= 2 and density >= 0.7:
        if mass >= 0.5:
            return responses['likely'][lang]
        return responses['weak'][lang]
    if radius > 4:
        return responses['strong'][lang]
    if 2 < radius <= 4:
        return responses['uncertain'][lang]
    return responses['unlikely'][lang]


def estimate_moons(mass, orbit_au, stellar_mass=1.0):
    """Estimate moon count based on Hill sphere size.
    Hill sphere = a × (m/(3M★))^(1/3)
    """
    if not mass or not orbit_au:
        return t('unknown'), 0
    
    hill_radius = orbit_au * (mass / (3 * stellar_mass)) ** (1/3)
    lang = st.session_state.get('lang', 'ru')
    
    responses = {
        'unlikely': {'ru': 'Маловероятно', 'en': 'Unlikely', 'kz': 'Екіталай'},
        'many': {'ru': 'Много (10-80)', 'en': 'Many (10-80)', 'kz': 'Көп (10-80)'},
        'possible_many': {'ru': 'Возможно (1-5)', 'en': 'Possible (1-5)', 'kz': 'Мүмкін (1-5)'},
        'possible_few': {'ru': 'Возможно (0-2)', 'en': 'Possible (0-2)', 'kz': 'Мүмкін (0-2)'}
    }
    
    if hill_radius < 0.001:
        return responses['unlikely'][lang], 0
    elif mass > 10:
        return responses['many'][lang], random.randint(10, 80)
    elif mass > 1:
        return responses['possible_many'][lang], random.randint(0, 5)
    else:
        return responses['possible_few'][lang], random.randint(0, 2)


def get_planet_type(radius, mass, temp):
    """Determine planet type based on physical parameters.
    Returns: (type_name, description, emoji)
    """
    lang = st.session_state.get('lang', 'ru')
    
    types = {
        'dwarf': {
            'name': {'ru': 'Карликовая', 'en': 'Dwarf', 'kz': 'Ергежейлі'},
            'desc': {'ru': 'Субпланетный объект без атмосферы', 'en': 'Sub-planetary body, no atmosphere', 'kz': 'Атмосферасыз субпланеталық дене'},
            'emoji': '🪨'
        },
        'sub_earth': {
            'name': {'ru': 'Суб-Земля', 'en': 'Sub-Earth', 'kz': 'Суб-Жер'},
            'desc': {'ru': 'Марсоподобный, тонкая атмосфера', 'en': 'Mars-like, thin atmosphere', 'kz': 'Марсқа ұқсас, жұқа атмосфера'},
            'emoji': '🔴'
        },
        'earth_like': {
            'name': {'ru': 'Землеподобная', 'en': 'Earth-like', 'kz': 'Жерге ұқсас'},
            'desc': {'ru': 'Потенциально обитаемая, возможна тектоника', 'en': 'Potentially habitable, possible tectonics', 'kz': 'Мекендеуге жарамды, тектоника мүмкін'},
            'emoji': '🌍'
        },
        'super_earth': {
            'name': {'ru': 'Супер-Земля', 'en': 'Super-Earth', 'kz': 'Супер-Жер'},
            'desc': {'ru': 'Крупная каменистая планета, плотная атмосфера', 'en': 'Large rocky world, thick atmosphere', 'kz': 'Үлкен тасты әлем, қалың атмосфера'},
            'emoji': '🌎'
        },
        'mini_neptune': {
            'name': {'ru': 'Мини-Нептун', 'en': 'Mini-Neptune', 'kz': 'Мини-Нептун'},
            'desc': {'ru': 'Водный мир или газовая оболочка', 'en': 'Water world or gas envelope', 'kz': 'Су әлемі немесе газ қабаты'},
            'emoji': '💧'
        },
        'neptune_like': {
            'name': {'ru': 'Нептуноподобная', 'en': 'Neptune-like', 'kz': 'Нептунға ұқсас'},
            'desc': {'ru': 'Ледяной гигант с глубокой атмосферой', 'en': 'Ice giant with deep atmosphere', 'kz': 'Терең атмосферасы бар мұзды алып'},
            'emoji': '🔵'
        },
        'gas_giant': {
            'name': {'ru': 'Газовый гигант', 'en': 'Gas Giant', 'kz': 'Газ алыбы'},
            'desc': {'ru': 'Юпитероподобная, H₂/He атмосфера', 'en': 'Jupiter-like, H₂/He atmosphere', 'kz': 'Юпитерге ұқсас, H₂/He атмосферасы'},
            'emoji': '🪐'
        },
        'super_jupiter': {
            'name': {'ru': 'Супер-Юпитер', 'en': 'Super-Jupiter', 'kz': 'Супер-Юпитер'},
            'desc': {'ru': 'Массивный гигант, близко к коричневому карлику', 'en': 'Massive giant, near brown dwarf', 'kz': 'Үлкен алып, қоңыр ергежейліге жақын'},
            'emoji': '🟤'
        },
        'unknown': {
            'name': {'ru': 'Неизвестно', 'en': 'Unknown', 'kz': 'Белгісіз'},
            'desc': {'ru': 'Недостаточно данных', 'en': 'Insufficient data', 'kz': 'Деректер жеткіліксіз'},
            'emoji': '❓'
        }
    }
    
    if radius is None:
        ptype = 'unknown'
    elif radius < 0.5:
        ptype = 'dwarf'
    elif radius < 0.8:
        ptype = 'sub_earth'
    elif radius <= 1.25:
        ptype = 'earth_like'
    elif radius <= 1.75:
        ptype = 'super_earth'
    elif radius <= 2.5:
        ptype = 'mini_neptune'
    elif radius <= 6:
        ptype = 'neptune_like'
    elif radius <= 15:
        ptype = 'gas_giant'
    else:
        ptype = 'super_jupiter'
    
    t_data = types[ptype]
    return t_data['name'][lang], t_data['desc'][lang], t_data['emoji']


def predict_atmosphere(radius, mass, temp, in_hz, stellar_teff=None):
    """Predict atmospheric composition based on planetary parameters."""
    lang = st.session_state.get('lang', 'ru')
    
    if not radius:
        return t('unknown'), []
    
    if radius > 6:  # Gas giant
        atmo_type = {'ru': 'H₂/He доминирует', 'en': 'H₂/He dominated', 'kz': 'H₂/He басым'}
        components = ["H₂ (90%)", "He (10%)", "CH₄", "NH₃", "H₂O"]
    elif radius > 2.5:  # Mini-Neptune/Neptune
        atmo_type = {'ru': 'H₂/He с летучими веществами', 'en': 'H₂/He with volatiles', 'kz': 'H₂/He ұшқыш заттармен'}
        components = ["H₂", "He", "H₂O", "CH₄", "NH₃"]
    elif radius > 1.75:  # Super-Earth
        if temp and temp > 500:
            atmo_type = {'ru': 'Горячая, вулканическая', 'en': 'Hot, volcanic', 'kz': 'Ыстық, вулкандық'}
            components = ["CO₂", "SO₂", "N₂"]
        else:
            atmo_type = {'ru': 'Плотная N₂/CO₂', 'en': 'Dense N₂/CO₂', 'kz': 'Тығыз N₂/CO₂'}
            components = ["N₂", "CO₂", "H₂O", "Ar"]
    elif radius >= 0.8:  # Earth-like
        if in_hz and temp and 220 <= temp <= 320:
            atmo_type = {'ru': 'Потенциально земная', 'en': 'Potentially Earth-like', 'kz': 'Жерге ұқсас мүмкін'}
            components = ["N₂", "O₂ (при жизни)", "H₂O", "CO₂", "Ar"]
        elif temp and temp > 400:
            atmo_type = {'ru': 'Плотная CO₂ (Венера)', 'en': 'Dense CO₂ (Venus-like)', 'kz': 'Тығыз CO₂ (Шолпанға ұқсас)'}
            components = ["CO₂ (96%)", "N₂", "SO₂", "H₂SO₄"]
        elif temp and temp < 200:
            atmo_type = {'ru': 'Холодная, тонкая', 'en': 'Cold, thin', 'kz': 'Суық, жұқа'}
            components = ["CO₂", "N₂", "Ar", "CO₂ лёд"]
        else:
            atmo_type = {'ru': 'CO₂/N₂ смесь', 'en': 'CO₂/N₂ mix', 'kz': 'CO₂/N₂ қоспасы'}
            components = ["CO₂", "N₂", "Ar"]
    else:  # Sub-Earth
        atmo_type = {'ru': 'Тонкая или отсутствует', 'en': 'Thin or none', 'kz': 'Жұқа немесе жоқ'}
        components = ["CO₂ (тонкий)", "N₂", "Ar"]
    
    # M-dwarf warning
    if stellar_teff and stellar_teff < 4000:
        warning = {'ru': '⚠️ Риск UV/рентген эрозии', 'en': '⚠️ UV/X-ray stripping risk', 'kz': '⚠️ UV/рентген эрозия қаупі'}
        components.append(warning[lang])
    
    return atmo_type[lang], components


def predict_hazards(temp, gravity, radius, orbit, stellar_teff, period=None):
    """Comprehensive hazard assessment with translations."""
    hazards = []
    lang = st.session_state.get('lang', 'ru')
    
    # Temperature hazards
    if temp:
        if temp > 700:
            hazards.append({
                'ru': ('🔥 СМЕРТЕЛЬНЫЙ ЖАР', f'{temp:.0f}K — поверхность расплавлена'),
                'en': ('🔥 LETHAL HEAT', f'{temp:.0f}K — surface molten'),
                'kz': ('🔥 ӨЛІМДІ ЫСТЫҚ', f'{temp:.0f}K — бет балқыған')
            })
        elif temp > 450:
            hazards.append({
                'ru': ('🌡️ Экстремальная жара', f'{temp:.0f}K — свинец плавится'),
                'en': ('🌡️ Extreme Heat', f'{temp:.0f}K — lead melts'),
                'kz': ('🌡️ Экстремалды ыстық', f'{temp:.0f}K — қорғасын ериді')
            })
        elif temp > 350:
            hazards.append({
                'ru': ('🌡️ Сильная жара', f'{temp:.0f}K — вода кипит'),
                'en': ('🌡️ Severe Heat', f'{temp:.0f}K — water boils'),
                'kz': ('🌡️ Қатты ыстық', f'{temp:.0f}K — су қайнайды')
            })
        elif temp < 100:
            hazards.append({
                'ru': ('🧊 КРИОГЕННЫЙ ХОЛОД', f'{temp:.0f}K — кислород жидкий'),
                'en': ('🧊 CRYOGENIC', f'{temp:.0f}K — oxygen liquefies'),
                'kz': ('🧊 КРИОГЕНДІК', f'{temp:.0f}K — оттегі сұйық')
            })
        elif temp < 180:
            hazards.append({
                'ru': ('❄️ Экстремальный холод', f'{temp:.0f}K — CO₂ замерзает'),
                'en': ('❄️ Extreme Cold', f'{temp:.0f}K — CO₂ freezes'),
                'kz': ('❄️ Экстремалды суық', f'{temp:.0f}K — CO₂ қатады')
            })
    
    # Gravity hazards
    if gravity:
        if gravity > 5:
            hazards.append({
                'ru': ('⚖️ ДАВЯЩАЯ ГРАВИТАЦИЯ', f'{gravity:.1f}g — движение невозможно'),
                'en': ('⚖️ CRUSHING GRAVITY', f'{gravity:.1f}g — movement impossible'),
                'kz': ('⚖️ БАСЫП ТҰРҒАН ГРАВИТАЦИЯ', f'{gravity:.1f}g — қозғалу мүмкін емес')
            })
        elif gravity > 2:
            hazards.append({
                'ru': ('🏋️ Высокая гравитация', f'{gravity:.1f}g — утомительно'),
                'en': ('🏋️ High Gravity', f'{gravity:.1f}g — exhausting'),
                'kz': ('🏋️ Жоғары гравитация', f'{gravity:.1f}g — шаршататын')
            })
        elif gravity < 0.3:
            hazards.append({
                'ru': ('🪶 Низкая гравитация', f'{gravity:.2f}g — проблемы со здоровьем'),
                'en': ('🪶 Low Gravity', f'{gravity:.2f}g — health issues'),
                'kz': ('🪶 Төмен гравитация', f'{gravity:.2f}g — денсаулық мәселелері')
            })
    
    # Radiation hazards
    if orbit and stellar_teff:
        if orbit < 0.1 and stellar_teff < 4000:
            hazards.append({
                'ru': ('☢️ Звёздные вспышки', 'M-карлик — частые UV/рентген вспышки'),
                'en': ('☢️ Stellar Flares', 'M-dwarf — frequent UV/X-ray flares'),
                'kz': ('☢️ Жұлдыздық жарқылдар', 'M-ергежейлі — жиі UV/рентген жарқылдары')
            })
        if orbit < 0.05:
            hazards.append({
                'ru': ('💫 Экстремальная радиация', f'{orbit:.3f} AU — сильный звёздный ветер'),
                'en': ('💫 Extreme Radiation', f'{orbit:.3f} AU — intense stellar wind'),
                'kz': ('💫 Экстремалды радиация', f'{orbit:.3f} AU — қарқынды жұлдыз желі')
            })
    
    # Tidal locking
    if period and period < 10:
        hazards.append({
            'ru': ('🌊 Приливной захват', f'P={period:.1f}d — одна сторона всегда к звезде'),
            'en': ('🌊 Tidal Locking', f'P={period:.1f}d — one side always facing star'),
            'kz': ('🌊 Толқындық байланыс', f'P={period:.1f}d — бір жағы әрқашан жұлдызға')
        })
    
    # No hazards
    if not hazards:
        hazards.append({
            'ru': ('✅ Нет серьёзных угроз', 'Параметры в пределах нормы'),
            'en': ('✅ No Major Hazards', 'Parameters within survivable range'),
            'kz': ('✅ Қауіпті қатер жоқ', 'Параметрлер қалыпты шегінде')
        })
    
    return [(h[lang][0], h[lang][1]) for h in hazards]


def predict_life_potential(temp, radius, in_hz, esi, atmo_type):
    """Assess potential for life with scoring and explanations."""
    lang = st.session_state.get('lang', 'ru')
    
    if not temp or not radius:
        return t('unknown'), 0, []
    
    score = 0
    factors = []
    
    # Temperature assessment
    if 260 <= temp <= 310:
        score += 30
        factors.append({'ru': '✅ Идеальная температура для воды', 'en': '✅ Ideal temperature for liquid water', 'kz': '✅ Су үшін тамаша температура'})
    elif 220 <= temp <= 350:
        score += 15
        factors.append({'ru': '⚠️ Пограничная температура', 'en': '⚠️ Marginal temperature', 'kz': '⚠️ Шекаралық температура'})
    else:
        factors.append({'ru': '❌ Температура вне диапазона воды', 'en': '❌ Temperature outside water range', 'kz': '❌ Су ауқымынан тыс температура'})
    
    # Size assessment
    if 0.8 <= radius <= 1.5:
        score += 25
        factors.append({'ru': '✅ Земной размер', 'en': '✅ Earth-like size', 'kz': '✅ Жер өлшемі'})
    elif 0.5 <= radius <= 2:
        score += 10
        factors.append({'ru': '⚠️ Пограничный размер', 'en': '⚠️ Marginal size', 'kz': '⚠️ Шекаралық өлшем'})
    else:
        factors.append({'ru': '❌ Размер неподходящий', 'en': '❌ Size unsuitable', 'kz': '❌ Өлшем жарамсыз'})
    
    # Habitable zone
    if in_hz:
        score += 25
        factors.append({'ru': '✅ В обитаемой зоне', 'en': '✅ In habitable zone', 'kz': '✅ Мекендеуге жарамды аймақта'})
    else:
        factors.append({'ru': '❌ Вне обитаемой зоны', 'en': '❌ Outside habitable zone', 'kz': '❌ Мекендеуге жарамды аймақтан тыс'})
    
    # ESI
    if esi and esi >= 0.8:
        score += 15
        factors.append({'ru': f'✅ Высокий ESI ({esi})', 'en': f'✅ High ESI ({esi})', 'kz': f'✅ Жоғары ESI ({esi})'})
    elif esi and esi >= 0.6:
        score += 8
        factors.append({'ru': f'⚠️ Средний ESI ({esi})', 'en': f'⚠️ Moderate ESI ({esi})', 'kz': f'⚠️ Орташа ESI ({esi})'})
    
    # Atmosphere
    if atmo_type and ('земн' in atmo_type.lower() or 'earth' in atmo_type.lower()):
        score += 5
        factors.append({'ru': '✅ Благоприятная атмосфера', 'en': '✅ Favorable atmosphere', 'kz': '✅ Қолайлы атмосфера'})
    
    # Life type determination
    if score >= 70:
        life_type = {'ru': '🌱 Углеродная жизнь ВЕРОЯТНА', 'en': '🌱 Carbon-based life LIKELY', 'kz': '🌱 Көміртегі негізіндегі өмір ЫҚТИМАЛ'}
    elif score >= 50:
        life_type = {'ru': '🦠 Микробная жизнь возможна', 'en': '🦠 Microbial life possible', 'kz': '🦠 Микробты өмір мүмкін'}
    elif score >= 30:
        life_type = {'ru': '🧫 Экзотическая жизнь гипотетична', 'en': '🧫 Exotic life speculative', 'kz': '🧫 Экзотикалық өмір болжамды'}
    else:
        life_type = {'ru': '❌ Жизнь маловероятна', 'en': '❌ Life unlikely', 'kz': '❌ Өмір екіталай'}
    
    return life_type[lang], min(score, 100), [f[lang] for f in factors]
# ═══════════════════════════════════════════════════════════════════════════════
# NASA EXOPLANET ARCHIVE API
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_nasa_data(star_name):
    """
    Fetch exoplanet data from NASA Exoplanet Archive TAP service.
    
    The query retrieves all planets in a system along with stellar parameters.
    Uses the Planetary Systems (ps) table with default_flag=1 for primary data.
    """
    try:
        # Build TAP query URL
        base_url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
        
        # Query for exact hostname match
        query = f"""
        select pl_name, pl_orbper, pl_rade, pl_eqt, pl_bmasse, pl_orbsmax,
               hostname, st_spectype, st_teff, st_rad, st_lum, st_mass, 
               st_met, st_age, sy_dist
        from ps 
        where hostname='{star_name}' and default_flag=1
        """
        
        url = f"{base_url}?query={query.replace(' ', '+')}&format=json"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200 and response.json():
            return response.json()
        
        # Try LIKE query for partial match
        query_like = f"""
        select pl_name, pl_orbper, pl_rade, pl_eqt, pl_bmasse, pl_orbsmax,
               hostname, st_spectype, st_teff, st_rad, st_lum, st_mass,
               st_met, st_age, sy_dist
        from ps 
        where hostname like '{star_name}%' and default_flag=1
        """
        
        url_like = f"{base_url}?query={query_like.replace(' ', '+')}&format=json"
        response_like = requests.get(url_like, timeout=15)
        
        if response_like.status_code == 200 and response_like.json():
            data = response_like.json()
            # Filter to single system
            if data:
                hostname = data[0].get('hostname')
                return [p for p in data if p.get('hostname') == hostname]
        
        return None
        
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.RequestException:
        return None
    except Exception:
        return None


def process_planet_data(planet_raw, star_data):
    """
    Process raw NASA data into a comprehensive analyzed planet dictionary.
    
    This function applies all physics calculations and generates predictions
    for atmospheric composition, hazards, and life potential.
    """
    # Extract basic parameters
    radius = planet_raw.get('pl_rade') or 1.0
    mass = planet_raw.get('pl_bmasse')
    period = planet_raw.get('pl_orbper')
    orbit = planet_raw.get('pl_orbsmax')
    temp_measured = planet_raw.get('pl_eqt')
    distance = planet_raw.get('sy_dist')
    
    # Extract stellar parameters
    stellar_teff = star_data.get('st_teff')
    stellar_rad = star_data.get('st_rad')
    stellar_lum = star_data.get('st_lum')
    stellar_mass = star_data.get('st_mass', 1.0) or 1.0
    
    # Calculate luminosity if not provided
    if not stellar_lum and stellar_teff and stellar_rad:
        stellar_lum = calc_luminosity(stellar_teff, stellar_rad)
    
    # Calculate orbit from period if not provided
    if not orbit and period:
        orbit = calc_orbit_from_period(period, stellar_mass)
    
    # Calculate habitable zone
    hz_inner, hz_outer, luminosity = calc_habitable_zone(
        stellar_teff, stellar_rad, stellar_lum
    ) if stellar_teff and stellar_rad else (0.75, 1.77, 1.0)
    
    # Determine if in habitable zone
    in_hz = hz_inner <= (orbit or 0) <= hz_outer if orbit else False
    
    # Calculate temperature (use measured or calculate)
    if temp_measured:
        temp = temp_measured
        temp_source = {'ru': '📡 Измерено', 'en': '📡 Measured', 'kz': '📡 Өлшенген'}
    else:
        temp = calc_equilibrium_temp(stellar_teff, stellar_rad, orbit) if stellar_teff and stellar_rad and orbit else 300
        temp_source = {'ru': '📐 Вычислено', 'en': '📐 Calculated', 'kz': '📐 Есептелген'}
    
    # Calculate ESI
    esi = calc_esi(radius, temp)
    
    # Calculate derived parameters
    gravity = calc_surface_gravity(mass, radius)
    density = calc_density(mass, radius)
    escape_velocity = calc_escape_velocity(mass, radius)
    pressure = calc_surface_pressure(mass, radius, temp)
    year_length = calc_year_length(period)
    day_length = calc_day_length(period, radius)
    mag_field = estimate_magnetic_field(mass, radius)
    moon_desc, moon_count = estimate_moons(mass or 1, orbit or 1, stellar_mass)
    
    # Get planet type
    planet_type, type_desc, emoji = get_planet_type(radius, mass, temp)
    
    # Predict atmosphere
    atmo_type, atmo_components = predict_atmosphere(radius, mass, temp, in_hz, stellar_teff)
    
    # Calculate habitability score
    hab_score = 0
    if temp:
        if 230 <= temp <= 310:
            hab_score += 40
        elif 200 <= temp <= 350:
            hab_score += 20
        elif 180 <= temp <= 400:
            hab_score += 10
    
    if 0.8 <= radius <= 1.5:
        hab_score += 25
    elif 0.5 <= radius <= 2.0:
        hab_score += 15
    elif radius <= 4:
        hab_score += 5
    
    if in_hz:
        hab_score += 25
    
    if esi and esi >= 0.8:
        hab_score += 10
    elif esi and esi >= 0.6:
        hab_score += 5
    
    hab_score = min(hab_score, 100)
    
    # Build comprehensive planet dictionary
    lang = st.session_state.get('lang', 'ru')
    
    return {
        # Identity
        'name': planet_raw.get('pl_name', '?'),
        'emoji': emoji,
        'type': planet_type,
        'type_desc': type_desc,
        
        # Physical parameters
        'radius': radius,
        'mass': mass,
        'density': density,
        'gravity': gravity,
        'escape_v': escape_velocity,
        'pressure': pressure,
        
        # Orbital parameters
        'orbit_au': orbit,
        'period': period,
        'year_len': year_length,
        'day_len': day_length,
        
        # Temperature
        'temp': temp,
        'temp_source': temp_source[lang],
        
        # Habitability
        'esi': esi,
        'in_hz': in_hz,
        'hab_score': hab_score,
        'hz_inner': hz_inner,
        'hz_outer': hz_outer,
        
        # Predictions
        'atmo_type': atmo_type,
        'atmo_comp': atmo_components,
        'mag_field': mag_field,
        'moon_desc': moon_desc,
        'moon_count': moon_count,
        
        # System data
        'distance': distance,
        'hostname': planet_raw.get('hostname'),
        
        # Raw data for reference
        'raw': planet_raw
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def save_system(hostname, star_data, planets):
    """
    Save a star system to research history.
    
    Prevents duplicates and updates statistics.
    """
    if hostname not in st.session_state.saved_systems:
        st.session_state.saved_systems[hostname] = {
            'star': star_data,
            'planets': planets,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'best_score': max((p['hab_score'] for p in planets), default=0),
            'planet_count': len(planets),
            'distance': planets[0].get('distance') if planets else None
        }
        st.session_state.scan_count += 1
        st.session_state.habitable_count += sum(1 for p in planets if p['hab_score'] >= 50)
        return True
    return False


def load_system(hostname):
    """
    Load a saved system for viewing.
    
    Sets the current system state for display.
    """
    if hostname in st.session_state.saved_systems:
        data = st.session_state.saved_systems[hostname]
        st.session_state['planets'] = data['planets']
        st.session_state['star'] = data['star']
        st.session_state['selected_idx'] = 0
        st.session_state['current_system'] = hostname
        return True
    return False


def mark_star_scanned(star_name):
    """Mark a star as scanned to avoid re-scanning."""
    st.session_state.scanned_stars.add(star_name)


def is_star_scanned(star_name):
    """Check if a star has been scanned."""
    return star_name in st.session_state.scanned_stars


def get_unscanned_stars(catalog_key, skip_scanned=True):
    """Get list of unscanned stars from a catalog."""
    catalog = CATALOGS.get(catalog_key, CATALOGS['nearby'])
    stars = catalog['stars']
    if skip_scanned:
        return [s for s in stars if not is_star_scanned(s)]
    return stars


def get_all_planets():
    """Get all planets from all saved systems for analysis."""
    all_planets = []
    for hostname, data in st.session_state.saved_systems.items():
        for planet in data['planets']:
            planet_copy = planet.copy()
            planet_copy['hostname'] = hostname
            planet_copy['star'] = data['star']
            all_planets.append(planet_copy)
    return all_planets


def get_top_candidates(n=10):
    """Get top N habitable candidates across all systems."""
    all_planets = get_all_planets()
    sorted_planets = sorted(all_planets, key=lambda x: x['hab_score'], reverse=True)
    return sorted_planets[:n]


# ═══════════════════════════════════════════════════════════════════════════════
# STELLAR COORDINATES (for star map)
# ═══════════════════════════════════════════════════════════════════════════════

# Approximate 3D coordinates of known star systems (in light-years from Sun)
STELLAR_COORDINATES = {
    'Sun': (0, 0, 0),
    'Proxima Centauri': (1.3, -0.9, -3.8),
    'TRAPPIST-1': (-12.1, 38.4, -6.9),
    'Ross 128': (-5.8, -10.1, -1.1),
    'Luyten': (-4.5, 7.2, -9.3),
    'Wolf 1061': (-4.3, -11.8, 5.0),
    'GJ 1061': (-3.7, -11.0, -0.6),
    'Teegarden': (8.0, -9.5, 3.3),
    'YZ Ceti': (-1.7, -11.8, -3.2),
    'GJ 273': (-4.4, -9.0, 7.1),
    "Kapteyn's Star": (3.8, 1.2, -12.6),
    'TOI-700': (-30, 85, 40),
    'LHS 1140': (-25, 35, 15),
    'K2-18': (-45, 100, 50),
    'Kepler-442': (400, 800, 600),
    'Kepler-62': (350, 900, 450),
    'Kepler-186': (250, 450, 300),
    'Kepler-452': (450, 1200, 700),
    'HD-209458': (50, 100, 80),
    '51 Pegasi': (-15, 48, 12),
    'GJ 357': (-20, 25, 15),
}

def get_star_coordinates(hostname, distance=None):
    """
    Get 3D coordinates for a star system.
    
    Uses known coordinates if available, otherwise generates
    pseudo-random coordinates based on distance.
    """
    # Check known coordinates (normalize hostname)
    for known_name, coords in STELLAR_COORDINATES.items():
        if known_name.lower().replace(' ', '').replace('-', '') in hostname.lower().replace(' ', '').replace('-', ''):
            return coords
    
    # Generate coordinates based on distance
    if distance:
        # Use hostname as seed for reproducibility
        seed = sum(ord(c) for c in hostname)
        np.random.seed(seed)
        
        # Random spherical coordinates
        phi = np.random.uniform(0, 2 * np.pi)
        theta = np.arccos(np.random.uniform(-1, 1))
        
        x = distance * np.sin(theta) * np.cos(phi)
        y = distance * np.sin(theta) * np.sin(phi)
        z = distance * np.cos(theta)
        
        return (x, y, z)
    
    # Default: random position at ~100 ly
    seed = sum(ord(c) for c in hostname)
    np.random.seed(seed)
    return (
        np.random.uniform(-100, 100),
        np.random.uniform(-100, 100),
        np.random.uniform(-50, 50)
    )
# ═══════════════════════════════════════════════════════════════════════════════
# VISUALIZATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_system_3d(planets, star, selected_idx):
    """
    Create an interactive 3D visualization of a planetary system.
    
    Features:
    - Central star with color based on temperature
    - Planetary orbits as rings
    - Habitable zone visualization
    - Color-coded planets by habitability score
    - Interactive selection
    """
    fig = go.Figure()
    
    # Stellar parameters
    stellar_teff = star.get('st_teff', 5500)
    stellar_rad = star.get('st_rad', 1) or 1
    
    # Determine star color from temperature
    if stellar_teff > 7500:
        star_color = '#aabfff'  # Blue-white
    elif stellar_teff > 6000:
        star_color = '#fff4ea'  # Yellow-white
    elif stellar_teff > 5000:
        star_color = '#ffd2a1'  # Yellow
    elif stellar_teff > 3500:
        star_color = '#ffaa77'  # Orange
    else:
        star_color = '#ff6b6b'  # Red
    
    # Calculate scale for visualization
    hz_inner = planets[0]['hz_inner'] if planets else 0.75
    hz_outer = planets[0]['hz_outer'] if planets else 1.77
    max_orbit = max([p['orbit_au'] or 0.05 for p in planets] + [hz_outer * 1.2])
    scale = 14 / max_orbit
    
    # Add star at center
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(
            size=max(15, min(stellar_rad * 18, 30)),
            color=star_color,
            line=dict(width=2, color='rgba(255,255,255,0.3)')
        ),
        name=f"⭐ {star.get('st_spectype', 'G')} • {stellar_teff}K",
        hovertemplate=(
            f"<b>Host Star</b><br>"
            f"Type: {star.get('st_spectype', '?')}<br>"
            f"Temp: {stellar_teff}K<br>"
            f"Radius: {stellar_rad:.2f} R☉<extra></extra>"
        )
    ))
    
    # Habitable zone boundaries
    n_points = 80
    theta = np.linspace(0, 2 * np.pi, n_points)
    
    # Inner HZ boundary
    x_inner = hz_inner * scale * np.cos(theta)
    y_inner = hz_inner * scale * np.sin(theta)
    fig.add_trace(go.Scatter3d(
        x=x_inner, y=y_inner, z=np.zeros(n_points),
        mode='lines',
        line=dict(color='rgba(0,255,100,0.5)', width=3),
        name=f"🌿 HZ Inner ({hz_inner:.2f} AU)",
        showlegend=True
    ))
    
    # Outer HZ boundary
    x_outer = hz_outer * scale * np.cos(theta)
    y_outer = hz_outer * scale * np.sin(theta)
    fig.add_trace(go.Scatter3d(
        x=x_outer, y=y_outer, z=np.zeros(n_points),
        mode='lines',
        line=dict(color='rgba(0,255,100,0.3)', width=2),
        name=f"🌿 HZ Outer ({hz_outer:.2f} AU)",
        showlegend=True
    ))
    
    # Add planets
    orbit_points = np.linspace(0, 2 * np.pi, 60)
    
    for idx, planet in enumerate(planets):
        orbit_scaled = (planet['orbit_au'] or 0.05) * scale
        angle = idx * (2 * np.pi / max(len(planets), 1)) + 0.5
        px, py = orbit_scaled * np.cos(angle), orbit_scaled * np.sin(angle)
        
        # Color by habitability score
        score = planet['hab_score']
        if score >= 70:
            color = '#00ff88'
        elif score >= 50:
            color = '#00d4ff'
        elif score >= 30:
            color = '#ffbb00'
        else:
            color = '#ff6666'
        
        # Size based on radius
        size = max(8, min(planet['radius'] * 4 + 5, 18))
        
        # Highlight selected planet
        if idx == selected_idx:
            size += 5
            color = '#ff00ff'
        
        # Orbit ring
        fig.add_trace(go.Scatter3d(
            x=orbit_scaled * np.cos(orbit_points),
            y=orbit_scaled * np.sin(orbit_points),
            z=np.zeros(60),
            mode='lines',
            line=dict(color='rgba(255,255,255,0.12)', width=1),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Planet marker
        hz_marker = "★ " if planet['in_hz'] else ""
        fig.add_trace(go.Scatter3d(
            x=[px], y=[py], z=[0],
            mode='markers',
            marker=dict(
                size=size,
                color=color,
                line=dict(width=3 if idx == selected_idx else 1, color='white')
            ),
            name=f"{hz_marker}{planet['name']} ({score})",
            hovertemplate=(
                f"<b>{planet['name']}</b><br>"
                f"Score: {score}/100<br>"
                f"R: {planet['radius']:.2f} R⊕<br>"
                f"T: {planet['temp']:.0f}K<br>"
                f"Orbit: {planet['orbit_au']:.4f} AU<extra></extra>"
            )
        ))
    
    # Layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[-16, 16]),
            yaxis=dict(visible=False, range=[-16, 16]),
            zaxis=dict(visible=False, range=[-8, 8]),
            aspectmode='cube',
            bgcolor='rgba(0,0,0,0)',
            camera=dict(eye=dict(x=0, y=-1.5, z=0.8))
        ),
        margin=dict(l=0, r=0, t=10, b=0),
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            y=0.95,
            x=1.0,
            bgcolor='rgba(15,15,30,0.9)',
            font=dict(color='white', size=11),
            bordercolor='rgba(0,212,255,0.3)',
            borderwidth=1
        )
    )
    
    return fig


def create_stellar_neighborhood_map():
    """
    Create a 3D map of all explored star systems relative to the Sun.
    
    This visualization shows the spatial distribution of explored systems
    with color coding by best habitability score.
    """
    fig = go.Figure()
    
    # Add Sun at center
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers+text',
        marker=dict(size=15, color='#fff4ea', symbol='circle'),
        text=['☀️ Sun'],
        textposition='top center',
        textfont=dict(size=12, color='white'),
        name='☀️ Sun',
        hovertemplate="<b>Sun</b><br>Our home<extra></extra>"
    ))
    
    # Add explored systems
    if st.session_state.saved_systems:
        for hostname, data in st.session_state.saved_systems.items():
            distance = data.get('distance')
            coords = get_star_coordinates(hostname, distance)
            
            best_score = data['best_score']
            planet_count = data['planet_count']
            
            # Color by best habitability score
            if best_score >= 70:
                color = '#00ff88'
            elif best_score >= 50:
                color = '#00d4ff'
            elif best_score >= 30:
                color = '#ffbb00'
            else:
                color = '#ff6666'
            
            # Size by planet count
            size = 8 + planet_count * 2
            
            fig.add_trace(go.Scatter3d(
                x=[coords[0]],
                y=[coords[1]],
                z=[coords[2]],
                mode='markers+text',
                marker=dict(size=size, color=color, opacity=0.8),
                text=[hostname],
                textposition='top center',
                textfont=dict(size=10, color='white'),
                name=hostname,
                hovertemplate=(
                    f"<b>{hostname}</b><br>"
                    f"Distance: {distance:.1f} ly<br>" if distance else f"<b>{hostname}</b><br>"
                    f"Planets: {planet_count}<br>"
                    f"Best score: {best_score}<extra></extra>"
                )
            ))
            
            # Connection line to Sun
            fig.add_trace(go.Scatter3d(
                x=[0, coords[0]],
                y=[0, coords[1]],
                z=[0, coords[2]],
                mode='lines',
                line=dict(color='rgba(255,255,255,0.1)', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    # Layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title='X (ly)',
                gridcolor='rgba(255,255,255,0.1)',
                color='rgba(255,255,255,0.5)'
            ),
            yaxis=dict(
                title='Y (ly)',
                gridcolor='rgba(255,255,255,0.1)',
                color='rgba(255,255,255,0.5)'
            ),
            zaxis=dict(
                title='Z (ly)',
                gridcolor='rgba(255,255,255,0.1)',
                color='rgba(255,255,255,0.5)'
            ),
            bgcolor='rgba(5,5,15,1)',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.0))
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        height=550,
        paper_bgcolor='rgba(0,0,0,0)',
        title=dict(
            text='',
            font=dict(color='white')
        ),
        showlegend=False
    )
    
    return fig


def create_radar_chart(planets_data):
    """
    Create a radar chart comparing multiple planets across key metrics.
    """
    if not planets_data:
        return go.Figure()
    
    categories = ['Radius', 'Mass', 'Temp', 'ESI', 'Gravity', 'Distance']
    colors = ['#00d4ff', '#00ff88', '#ff6b9d', '#ffd93d', '#9d4edd', '#ff8c42']
    
    fig = go.Figure()
    
    for idx, (name, data) in enumerate(planets_data.items()):
        # Normalize values to 0-1 scale
        values = [
            min(data.get('radius', 1) / 3, 1),
            min(data.get('mass', 1) / 10, 1) if data.get('mass') else 0.5,
            1 - abs(data.get('temp', 288) - 288) / 500 if data.get('temp') else 0.5,
            data.get('esi', 0.5),
            min(data.get('gravity', 1) / 3, 1) if data.get('gravity') else 0.5,
            1 - min(data.get('distance', 100) / 1000, 1) if data.get('distance') else 0.5
        ]
        values.append(values[0])  # Close the radar
        
        color = colors[idx % len(colors)]
        rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor=f'rgba({rgb[0]},{rgb[1]},{rgb[2]},0.2)',
            line=dict(color=color, width=2),
            name=name
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], showticklabels=False),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=380,
        margin=dict(l=60, r=60, t=40, b=40)
    )
    
    return fig


def create_bar_comparison(planets_data):
    """
    Create a bar chart comparing ESI and temperature scores.
    """
    if not planets_data:
        return go.Figure()
    
    names = list(planets_data.keys())
    esi_values = [planets_data[n].get('esi', 0) for n in names]
    temp_scores = [
        1 - abs(planets_data[n].get('temp', 288) - 288) / 500
        for n in names
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='ESI',
        x=names,
        y=esi_values,
        marker_color='#00d4ff'
    ))
    
    fig.add_trace(go.Bar(
        name='Temp Score',
        x=names,
        y=temp_scores,
        marker_color='#00ff88'
    ))
    
    fig.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=380,
        margin=dict(l=40, r=20, t=40, b=60),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', range=[0, 1]),
        legend=dict(orientation='h', y=1.1)
    )
    
    return fig


def create_travel_animation(progress, destination_name):
    """
    Create an animated visualization of interstellar travel.
    """
    fig = go.Figure()
    
    # Stars background
    np.random.seed(42)
    n_stars = 100
    star_x = np.random.uniform(-10, 10, n_stars)
    star_y = np.random.uniform(-5, 5, n_stars)
    star_sizes = np.random.uniform(1, 4, n_stars)
    
    # Parallax effect
    star_x_moved = star_x - progress * 2
    star_x_moved = np.where(star_x_moved < -10, star_x_moved + 20, star_x_moved)
    
    fig.add_trace(go.Scatter(
        x=star_x_moved,
        y=star_y,
        mode='markers',
        marker=dict(size=star_sizes, color='white', opacity=0.7),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Ship position
    ship_x = -8 + progress * 14
    
    # Engine trail
    if progress > 0:
        trail_x = np.linspace(ship_x - 2, ship_x - 0.3, 8)
        trail_sizes = np.linspace(15, 3, 8)
        trail_opacities = np.linspace(0.8, 0.1, 8)
        
        for i in range(len(trail_x)):
            fig.add_trace(go.Scatter(
                x=[trail_x[i]],
                y=[0],
                mode='markers',
                marker=dict(
                    size=trail_sizes[i],
                    color=f'rgba(0,212,255,{trail_opacities[i]})'
                ),
                showlegend=False,
                hoverinfo='skip'
            ))
    
    # Ship
    fig.add_trace(go.Scatter(
        x=[ship_x],
        y=[0],
        mode='markers+text',
        marker=dict(size=25, symbol='triangle-right', color='#00d4ff'),
        text=['🚀'],
        textposition='middle center',
        textfont=dict(size=30),
        showlegend=False
    ))
    
    # Destination planet
    fig.add_trace(go.Scatter(
        x=[8],
        y=[0],
        mode='markers+text',
        marker=dict(size=40, color='#00ff88'),
        text=['🪐'],
        textposition='middle center',
        textfont=dict(size=40),
        name=destination_name,
        showlegend=False
    ))
    
    fig.update_layout(
        xaxis=dict(visible=False, range=[-12, 12]),
        yaxis=dict(visible=False, range=[-6, 6]),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10,10,30,1)',
        height=200,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig


def create_score_distribution_chart():
    """
    Create a histogram showing distribution of habitability scores.
    """
    all_planets = get_all_planets()
    
    if not all_planets:
        return go.Figure()
    
    scores = [p['hab_score'] for p in all_planets]
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=scores,
        nbinsx=10,
        marker_color='#00d4ff',
        opacity=0.7
    ))
    
    fig.update_layout(
        title=dict(
            text=t('score') + ' Distribution',
            font=dict(color='white')
        ),
        xaxis=dict(
            title=t('score'),
            gridcolor='rgba(255,255,255,0.1)',
            color='white'
        ),
        yaxis=dict(
            title='Count',
            gridcolor='rgba(255,255,255,0.1)',
            color='white'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        margin=dict(l=50, r=20, t=50, b=50)
    )
    
    return fig


def create_planet_types_pie():
    """Create pie chart of planet types distribution."""
    all_planets = get_all_planets()
    if not all_planets:
        return go.Figure()
    
    types = {}
    for p in all_planets:
        ptype = p.get('type', 'Unknown')
        types[ptype] = types.get(ptype, 0) + 1
    
    colors = ['#00d4ff', '#00ff88', '#ff6b9d', '#ffd93d', '#9d4edd', '#ff8c42', '#4ecdc4']
    
    fig = go.Figure(data=[go.Pie(
        labels=list(types.keys()),
        values=list(types.values()),
        hole=0.4,
        marker_colors=colors[:len(types)]
    )])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=300,
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=True,
        legend=dict(font=dict(size=10))
    )
    
    return fig


def create_temp_vs_radius_scatter():
    """Create scatter plot of temperature vs radius with habitability coloring."""
    all_planets = get_all_planets()
    if not all_planets:
        return go.Figure()
    
    fig = go.Figure()
    
    # Add habitable zone reference
    fig.add_shape(
        type="rect",
        x0=0.8, x1=1.5, y0=250, y1=310,
        fillcolor="rgba(0,255,136,0.1)",
        line=dict(color="rgba(0,255,136,0.3)", width=2),
    )
    
    # Color by habitability score
    colors = [p['hab_score'] for p in all_planets]
    
    fig.add_trace(go.Scatter(
        x=[p['radius'] for p in all_planets],
        y=[p['temp'] for p in all_planets],
        mode='markers',
        marker=dict(
            size=12,
            color=colors,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Score')
        ),
        text=[p['name'] for p in all_planets],
        hovertemplate="<b>%{text}</b><br>R: %{x:.2f} R⊕<br>T: %{y:.0f}K<extra></extra>"
    ))
    
    # Add Earth reference
    fig.add_trace(go.Scatter(
        x=[1.0], y=[288],
        mode='markers+text',
        marker=dict(size=15, color='#00ff88', symbol='star'),
        text=['🌍 Earth'],
        textposition='top center',
        showlegend=False
    ))
    
    fig.update_layout(
        xaxis=dict(title='Radius (R⊕)', gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(title='Temperature (K)', gridcolor='rgba(255,255,255,0.1)'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=350,
        margin=dict(l=50, r=20, t=30, b=50)
    )
    
    return fig


def create_distance_histogram():
    """Create histogram of system distances."""
    all_planets = get_all_planets()
    if not all_planets:
        return go.Figure()
    
    distances = [p['distance'] for p in all_planets if p.get('distance')]
    
    if not distances:
        return go.Figure()
    
    fig = go.Figure(data=[go.Histogram(
        x=distances,
        nbinsx=15,
        marker_color='#00d4ff',
        opacity=0.7
    )])
    
    fig.update_layout(
        xaxis=dict(title='Distance (ly)', gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(title='Count', gridcolor='rgba(255,255,255,0.1)'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=280,
        margin=dict(l=50, r=20, t=20, b=50)
    )
    
    return fig
# ═══════════════════════════════════════════════════════════════════════════════
# SMART ATLAS - AI ANALYSIS & HYPOTHESIS GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def generate_recommendations():
    """
    Analyze all explored systems and generate research recommendations.
    
    The recommendation engine considers:
    - Which catalogs haven't been explored
    - Similar systems to successful finds
    - Gaps in the research coverage
    """
    lang = st.session_state.get('lang', 'ru')
    recommendations = []
    
    saved = st.session_state.saved_systems
    scanned = st.session_state.scanned_stars
    
    # Recommendation 1: Unexplored catalogs
    for cat_key, cat_data in CATALOGS.items():
        unscanned = [s for s in cat_data['stars'] if s not in scanned]
        if len(unscanned) >= len(cat_data['stars']) * 0.7:  # 70%+ unexplored
            rec = {
                'ru': {
                    'title': f"📁 Исследуйте каталог: {cat_data['name']['ru']}",
                    'reason': f"{len(unscanned)} из {len(cat_data['stars'])} звёзд не изучены",
                    'action': f"Запустите миссию с каталогом '{cat_key}'"
                },
                'en': {
                    'title': f"📁 Explore catalog: {cat_data['name']['en']}",
                    'reason': f"{len(unscanned)} of {len(cat_data['stars'])} stars unexplored",
                    'action': f"Run mission with catalog '{cat_key}'"
                },
                'kz': {
                    'title': f"📁 Каталогты зерттеңіз: {cat_data['name']['kz']}",
                    'reason': f"{len(cat_data['stars'])} жұлдыздан {len(unscanned)} зерттелмеген",
                    'action': f"'{cat_key}' каталогымен миссия іске қосыңыз"
                }
            }
            recommendations.append(rec[lang])
    
    # Recommendation 2: Follow up on high-score systems
    if saved:
        top_systems = sorted(
            saved.items(), 
            key=lambda x: x[1]['best_score'], 
            reverse=True
        )[:3]
        
        for hostname, data in top_systems:
            if data['best_score'] >= 60:
                rec = {
                    'ru': {
                        'title': f"🎯 Приоритетная цель: {hostname}",
                        'reason': f"Балл обитаемости {data['best_score']}/100 — один из лучших результатов",
                        'action': "Загрузите систему для детального анализа планет"
                    },
                    'en': {
                        'title': f"🎯 Priority target: {hostname}",
                        'reason': f"Habitability score {data['best_score']}/100 — one of best results",
                        'action': "Load system for detailed planet analysis"
                    },
                    'kz': {
                        'title': f"🎯 Басым мақсат: {hostname}",
                        'reason': f"Мекендеуге жарамдылық бағасы {data['best_score']}/100 — ең жақсы нәтижелердің бірі",
                        'action': "Планеталарды егжей-тегжейлі талдау үшін жүйені жүктеңіз"
                    }
                }
                recommendations.append(rec[lang])
    
    # Recommendation 3: Nearby stars priority
    nearby_scanned = sum(1 for s in CATALOGS['nearby']['stars'] if s in scanned)
    if nearby_scanned < 5:
        rec = {
            'ru': {
                'title': "🌟 Приоритет: ближайшие звёзды",
                'reason': "Только " + str(nearby_scanned) + " из 10 ближайших звёзд изучены",
                'action': "Ближайшие системы — приоритет для будущих миссий"
            },
            'en': {
                'title': "🌟 Priority: nearby stars",
                'reason': f"Only {nearby_scanned} of 10 nearest stars explored",
                'action': "Nearby systems should be priority for future missions"
            },
            'kz': {
                'title': "🌟 Басымдық: жақын жұлдыздар",
                'reason': f"10 жақын жұлдыздың тек {nearby_scanned} зерттелген",
                'action': "Жақын жүйелер болашақ миссиялар үшін басымдық болуы керек"
            }
        }
        recommendations.append(rec[lang])
    
    # Recommendation 4: Multi-planet systems
    multiplanet_count = sum(1 for h, d in saved.items() if d['planet_count'] >= 3)
    if multiplanet_count < 3:
        rec = {
            'ru': {
                'title': "🌐 Ищите многопланетные системы",
                'reason': f"Найдено только {multiplanet_count} систем с 3+ планетами",
                'action': "Используйте каталог 'multiplanet' для целенаправленного поиска"
            },
            'en': {
                'title': "🌐 Search for multi-planet systems",
                'reason': f"Only {multiplanet_count} systems with 3+ planets found",
                'action': "Use 'multiplanet' catalog for targeted search"
            },
            'kz': {
                'title': "🌐 Көппланеталы жүйелерді іздеңіз",
                'reason': f"3+ планетасы бар тек {multiplanet_count} жүйе табылды",
                'action': "Мақсатты іздеу үшін 'multiplanet' каталогын пайдаланыңыз"
            }
        }
        recommendations.append(rec[lang])
    
    # Recommendation 5: Research strategy
    if len(saved) >= 5:
        avg_score = sum(d['best_score'] for d in saved.values()) / len(saved)
        
        if avg_score < 40:
            rec = {
                'ru': {
                    'title': "📊 Смените стратегию поиска",
                    'reason': f"Средний балл {avg_score:.1f}/100 — низкий результат",
                    'action': "Сфокусируйтесь на каталоге 'habitable' для лучших результатов"
                },
                'en': {
                    'title': "📊 Change search strategy",
                    'reason': f"Average score {avg_score:.1f}/100 — low result",
                    'action': "Focus on 'habitable' catalog for better results"
                },
                'kz': {
                    'title': "📊 Іздеу стратегиясын өзгертіңіз",
                    'reason': f"Орташа балл {avg_score:.1f}/100 — төмен нәтиже",
                    'action': "Жақсы нәтиже үшін 'habitable' каталогына назар аударыңыз"
                }
            }
            recommendations.append(rec[lang])
    
    return recommendations[:5]  # Return top 5 recommendations


def generate_hypotheses():
    """
    Generate scientific hypotheses based on discovered data.
    
    The hypothesis engine analyzes patterns in the data and generates
    scientifically plausible hypotheses that could be investigated further.
    """
    lang = st.session_state.get('lang', 'ru')
    hypotheses = []
    
    all_planets = get_all_planets()
    
    if len(all_planets) < 3:
        return []
    
    # Analyze data patterns
    habitable_planets = [p for p in all_planets if p['hab_score'] >= 50]
    m_dwarf_planets = [p for p in all_planets if p.get('star', {}).get('st_teff', 5500) < 4000]
    earth_like = [p for p in all_planets if 0.8 <= p['radius'] <= 1.5]
    in_hz = [p for p in all_planets if p['in_hz']]
    
    # Hypothesis 1: M-dwarf habitability
    if m_dwarf_planets:
        m_dwarf_habitable = len([p for p in m_dwarf_planets if p['hab_score'] >= 50])
        ratio = m_dwarf_habitable / len(m_dwarf_planets) if m_dwarf_planets else 0
        
        hyp = {
            'ru': {
                'title': "🔴 Обитаемость вокруг красных карликов",
                'hypothesis': f"Из {len(m_dwarf_planets)} планет у M-карликов {m_dwarf_habitable} ({ratio*100:.0f}%) потенциально обитаемы.",
                'analysis': "Несмотря на риск приливного захвата и звёздных вспышек, планеты у M-карликов могут поддерживать жизнь в терминаторной зоне между дневной и ночной сторонами.",
                'evidence': f"Найдено {m_dwarf_habitable} кандидатов с благоприятными условиями",
                'further_study': "Требуется анализ атмосферной эрозии и магнитной защиты"
            },
            'en': {
                'title': "🔴 Habitability around red dwarfs",
                'hypothesis': f"Of {len(m_dwarf_planets)} M-dwarf planets, {m_dwarf_habitable} ({ratio*100:.0f}%) are potentially habitable.",
                'analysis': "Despite risks of tidal locking and stellar flares, M-dwarf planets may support life in the terminator zone between day and night sides.",
                'evidence': f"Found {m_dwarf_habitable} candidates with favorable conditions",
                'further_study': "Atmospheric erosion and magnetic protection analysis required"
            },
            'kz': {
                'title': "🔴 Қызыл ергежейлілер айналасындағы мекендеуге жарамдылық",
                'hypothesis': f"{len(m_dwarf_planets)} M-ергежейлі планетасынан {m_dwarf_habitable} ({ratio*100:.0f}%) мекендеуге жарамды болуы мүмкін.",
                'analysis': "Толқындық байланыс пен жұлдыздық жарқылдар қаупіне қарамастан, M-ергежейлі планеталары күндізгі және түнгі жақтар арасындағы терминатор аймағында өмірді қолдай алады.",
                'evidence': f"Қолайлы жағдайлары бар {m_dwarf_habitable} үміткер табылды",
                'further_study': "Атмосфералық эрозия мен магниттік қорғаныс талдауы қажет"
            }
        }
        hypotheses.append(hyp[lang])
    
    # Hypothesis 2: Super-Earth water worlds
    super_earths = [p for p in all_planets if 1.25 < p['radius'] <= 2.0]
    if super_earths:
        water_candidates = len([p for p in super_earths if p['in_hz']])
        
        hyp = {
            'ru': {
                'title': "💧 Супер-Земли как водные миры",
                'hypothesis': f"Обнаружено {len(super_earths)} супер-Земель, из них {water_candidates} в обитаемой зоне.",
                'analysis': "Супер-Земли с радиусом 1.25-2 R⊕ могут содержать глобальные океаны глубиной сотни километров. Высокое давление на дне может создать слой льда-VII, изолирующий каменистое ядро.",
                'evidence': f"{water_candidates} планет находятся в зоне жидкой воды",
                'further_study': "Спектроскопия атмосферы для поиска водяного пара необходима"
            },
            'en': {
                'title': "💧 Super-Earths as water worlds",
                'hypothesis': f"Found {len(super_earths)} super-Earths, {water_candidates} in habitable zone.",
                'analysis': "Super-Earths with radius 1.25-2 R⊕ may contain global oceans hundreds of kilometers deep. High pressure at bottom may create ice-VII layer, insulating rocky core.",
                'evidence': f"{water_candidates} planets are in liquid water zone",
                'further_study': "Atmospheric spectroscopy for water vapor detection needed"
            },
            'kz': {
                'title': "💧 Супер-Жер су әлемдері ретінде",
                'hypothesis': f"{len(super_earths)} супер-Жер табылды, {water_candidates} мекендеуге жарамды аймақта.",
                'analysis': "1.25-2 R⊕ радиусы бар супер-Жерлер жүздеген километр тереңдіктегі ғаламдық мұхиттарды қамтуы мүмкін. Түбіндегі жоғары қысым тасты ядроны оқшаулайтын мұз-VII қабатын жасай алады.",
                'evidence': f"{water_candidates} планета сұйық су аймағында",
                'further_study': "Су буын анықтау үшін атмосфералық спектроскопия қажет"
            }
        }
        hypotheses.append(hyp[lang])
    
    # Hypothesis 3: Earth-like planet frequency
    if earth_like:
        hz_earth_like = len([p for p in earth_like if p['in_hz']])
        
        hyp = {
            'ru': {
                'title': "🌍 Частота землеподобных планет",
                'hypothesis': f"Из {len(all_planets)} изученных планет {len(earth_like)} ({len(earth_like)/len(all_planets)*100:.1f}%) имеют земной размер.",
                'analysis': f"Из них {hz_earth_like} находятся в обитаемой зоне. Это указывает на высокую частоту потенциально обитаемых миров в галактике.",
                'evidence': f"ESI > 0.8 у {len([p for p in earth_like if p['esi'] >= 0.8])} планет",
                'further_study': "Статистический анализ на большей выборке для уточнения η⊕"
            },
            'en': {
                'title': "🌍 Earth-like planet frequency",
                'hypothesis': f"Of {len(all_planets)} studied planets, {len(earth_like)} ({len(earth_like)/len(all_planets)*100:.1f}%) are Earth-sized.",
                'analysis': f"Of these, {hz_earth_like} are in habitable zone. This indicates high frequency of potentially habitable worlds in galaxy.",
                'evidence': f"ESI > 0.8 for {len([p for p in earth_like if p['esi'] >= 0.8])} planets",
                'further_study': "Statistical analysis on larger sample needed to refine η⊕"
            },
            'kz': {
                'title': "🌍 Жерге ұқсас планеталар жиілігі",
                'hypothesis': f"{len(all_planets)} зерттелген планетадан {len(earth_like)} ({len(earth_like)/len(all_planets)*100:.1f}%) Жер өлшемінде.",
                'analysis': f"Олардың {hz_earth_like} мекендеуге жарамды аймақта. Бұл галактикадағы мекендеуге жарамды әлемдердің жоғары жиілігін көрсетеді.",
                'evidence': f"{len([p for p in earth_like if p['esi'] >= 0.8])} планетада ESI > 0.8",
                'further_study': "η⊕ нақтылау үшін үлкен іріктемеде статистикалық талдау қажет"
            }
        }
        hypotheses.append(hyp[lang])
    
    # Hypothesis 4: Temperature-habitability correlation
    if habitable_planets:
        temps = [p['temp'] for p in habitable_planets if p['temp']]
        if temps:
            avg_temp = sum(temps) / len(temps)
            
            hyp = {
                'ru': {
                    'title': "🌡️ Температурный оптимум обитаемости",
                    'hypothesis': f"Средняя температура обитаемых кандидатов: {avg_temp:.0f}K (Земля: 288K).",
                    'analysis': f"Планеты с температурой 250-310K показывают наибольший потенциал. Отклонение от земной температуры не исключает жизнь — экстремофилы расширяют диапазон.",
                    'evidence': f"Найдено {len(habitable_planets)} планет с благоприятной температурой",
                    'further_study': "Моделирование климата для оценки стабильности температуры"
                },
                'en': {
                    'title': "🌡️ Temperature optimum for habitability",
                    'hypothesis': f"Average temperature of habitable candidates: {avg_temp:.0f}K (Earth: 288K).",
                    'analysis': f"Planets with temperature 250-310K show highest potential. Deviation from Earth temperature doesn't exclude life — extremophiles extend the range.",
                    'evidence': f"Found {len(habitable_planets)} planets with favorable temperature",
                    'further_study': "Climate modeling to assess temperature stability"
                },
                'kz': {
                    'title': "🌡️ Мекендеуге жарамдылықтың температуралық оптимумы",
                    'hypothesis': f"Мекендеуге жарамды үміткерлердің орташа температурасы: {avg_temp:.0f}K (Жер: 288K).",
                    'analysis': f"250-310K температурасы бар планеталар ең жоғары әлеуетті көрсетеді. Жер температурасынан ауытқу өмірді жоққа шығармайды — экстремофилдер ауқымды кеңейтеді.",
                    'evidence': f"Қолайлы температурасы бар {len(habitable_planets)} планета табылды",
                    'further_study': "Температура тұрақтылығын бағалау үшін климаттық модельдеу"
                }
            }
            hypotheses.append(hyp[lang])
    
    # Hypothesis 5: Radius valley and habitability
    valley_planets = [p for p in all_planets if 1.5 <= p['radius'] <= 2.0]
    if len(valley_planets) >= 2:
        hyp = {
            'ru': {
                'title': "📊 'Долина радиусов' и эволюция атмосфер",
                'hypothesis': f"Обнаружено {len(valley_planets)} планет в 'долине радиусов' (1.5-2 R⊕).",
                'analysis': "Это переходная зона между суперземлями и мини-нептунами. Планеты здесь либо потеряли водородную оболочку, либо сохранили её — критический фактор обитаемости.",
                'evidence': "Дефицит планет в этом диапазоне подтверждает теорию фотоиспарения",
                'further_study': "Анализ возраста систем для проверки временной эволюции"
            },
            'en': {
                'title': "📊 Radius valley and atmospheric evolution",
                'hypothesis': f"Found {len(valley_planets)} planets in 'radius valley' (1.5-2 R⊕).",
                'analysis': "This is transition zone between super-Earths and mini-Neptunes. Planets here either lost hydrogen envelope or retained it — critical for habitability.",
                'evidence': "Deficit of planets in this range confirms photoevaporation theory",
                'further_study': "System age analysis to verify temporal evolution"
            },
            'kz': {
                'title': "📊 'Радиус алқабы' және атмосфера эволюциясы",
                'hypothesis': f"'Радиус алқабында' (1.5-2 R⊕) {len(valley_planets)} планета табылды.",
                'analysis': "Бұл супер-Жерлер мен мини-Нептундар арасындағы өтпелі аймақ. Мұндағы планеталар не сутегі қабатын жоғалтты, не сақтады — мекендеуге жарамдылық үшін маңызды.",
                'evidence': "Бұл ауқымдағы планеталар тапшылығы фотобулану теориясын растайды",
                'further_study': "Уақыттық эволюцияны тексеру үшін жүйе жасын талдау"
            }
        }
        hypotheses.append(hyp[lang])
    
    return hypotheses[:5]  # Return top 5 hypotheses


def generate_system_analysis(hostname):
    """
    Generate detailed AI analysis for a specific star system.
    """
    lang = st.session_state.get('lang', 'ru')
    
    if hostname not in st.session_state.saved_systems:
        return None
    
    data = st.session_state.saved_systems[hostname]
    planets = data['planets']
    star = data['star']
    
    # Analyze system characteristics
    planet_count = len(planets)
    best_planet = max(planets, key=lambda x: x['hab_score'])
    hz_planets = [p for p in planets if p['in_hz']]
    stellar_type = star.get('st_spectype', 'G')
    stellar_teff = star.get('st_teff', 5500)
    
    # Generate analysis text
    analyses = {
        'ru': {
            'system_type': f"🌟 **{hostname}** — {'многопланетная система' if planet_count > 2 else 'система'} с {planet_count} {'планетами' if planet_count > 1 else 'планетой'}",
            'star_analysis': f"Звезда класса **{stellar_type}** с температурой **{stellar_teff}K**. " + 
                ("Оптимальна для жизни (G/K тип)." if 4000 < stellar_teff < 6500 else 
                 "M-карлик — риск вспышек и приливного захвата." if stellar_teff < 4000 else
                 "Горячая звезда — короткий срок жизни."),
            'hz_analysis': f"В обитаемой зоне находится **{len(hz_planets)}** {'планета' if len(hz_planets) == 1 else 'планет'}." if hz_planets else "Нет планет в обитаемой зоне.",
            'best_candidate': f"Лучший кандидат: **{best_planet['name']}** с баллом **{best_planet['hab_score']}/100**",
            'recommendation': "🎯 Высокий приоритет для дальнейшего исследования!" if best_planet['hab_score'] >= 60 else 
                            "📊 Умеренный интерес — требуется дополнительный анализ." if best_planet['hab_score'] >= 40 else
                            "📉 Низкий потенциал обитаемости."
        },
        'en': {
            'system_type': f"🌟 **{hostname}** — {'multi-planet system' if planet_count > 2 else 'system'} with {planet_count} {'planets' if planet_count > 1 else 'planet'}",
            'star_analysis': f"Star class **{stellar_type}** with temperature **{stellar_teff}K**. " +
                ("Optimal for life (G/K type)." if 4000 < stellar_teff < 6500 else
                 "M-dwarf — flare and tidal locking risks." if stellar_teff < 4000 else
                 "Hot star — short lifespan."),
            'hz_analysis': f"**{len(hz_planets)}** {'planet' if len(hz_planets) == 1 else 'planets'} in habitable zone." if hz_planets else "No planets in habitable zone.",
            'best_candidate': f"Best candidate: **{best_planet['name']}** with score **{best_planet['hab_score']}/100**",
            'recommendation': "🎯 High priority for further study!" if best_planet['hab_score'] >= 60 else
                            "📊 Moderate interest — additional analysis required." if best_planet['hab_score'] >= 40 else
                            "📉 Low habitability potential."
        },
        'kz': {
            'system_type': f"🌟 **{hostname}** — {planet_count} {'планетасы' if planet_count > 1 else 'планетасы'} бар {'көппланеталы жүйе' if planet_count > 2 else 'жүйе'}",
            'star_analysis': f"**{stellar_type}** класты жұлдыз, температурасы **{stellar_teff}K**. " +
                ("Өмір үшін оңтайлы (G/K түрі)." if 4000 < stellar_teff < 6500 else
                 "M-ергежейлі — жарқылдар мен толқындық байланыс қаупі." if stellar_teff < 4000 else
                 "Ыстық жұлдыз — қысқа өмір сүру."),
            'hz_analysis': f"Мекендеуге жарамды аймақта **{len(hz_planets)}** планета бар." if hz_planets else "Мекендеуге жарамды аймақта планета жоқ.",
            'best_candidate': f"Ең жақсы үміткер: **{best_planet['name']}**, бағасы **{best_planet['hab_score']}/100**",
            'recommendation': "🎯 Одан әрі зерттеу үшін жоғары басымдық!" if best_planet['hab_score'] >= 60 else
                            "📊 Орташа қызығушылық — қосымша талдау қажет." if best_planet['hab_score'] >= 40 else
                            "📉 Мекендеуге жарамдылық әлеуеті төмен."
        }
    }
    
    return analyses[lang]


def get_ai_response(question, context_planets=None):
    """
    Smart AI response system that analyzes user's discoveries.
    Features: comparisons, filters, recommendations, statistics, explanations.
    """
    lang = st.session_state.get('lang', 'ru')
    q_lower = question.lower()
    
    # Get all data
    all_planets = get_all_planets() if context_planets is None else context_planets
    saved_systems = st.session_state.get('saved_systems', {})
    current_system = st.session_state.get('current_system')
    
    # Compute statistics
    stats = {
        'total': len(all_planets),
        'systems': len(saved_systems),
        'habitable': len([p for p in all_planets if p['hab_score'] >= 50]),
        'earth_like': len([p for p in all_planets if 0.8 <= p['radius'] <= 1.5]),
        'super_earth': len([p for p in all_planets if 1.25 < p['radius'] <= 2.0]),
        'gas_giants': len([p for p in all_planets if p['radius'] > 6]),
        'in_hz': len([p for p in all_planets if p['in_hz']]),
        'avg_score': sum(p['hab_score'] for p in all_planets) / len(all_planets) if all_planets else 0,
        'best': max(all_planets, key=lambda x: x['hab_score']) if all_planets else None,
        'worst': min(all_planets, key=lambda x: x['hab_score']) if all_planets else None,
        'nearest': min(all_planets, key=lambda x: x.get('distance') or 9999) if all_planets else None,
        'hottest': max(all_planets, key=lambda x: x.get('temp') or 0) if all_planets else None,
        'coldest': min(all_planets, key=lambda x: x.get('temp') or 9999) if all_planets else None,
    }
    
    # ═══════════════════════════════════════════════════════════════════════
    # COMPARISON DETECTION: "сравни X и Y", "compare X and Y"
    # ═══════════════════════════════════════════════════════════════════════
    compare_words = ['сравни', 'сравнить', 'compare', 'vs', 'versus', 'салыстыр']
    if any(w in q_lower for w in compare_words):
        # Find planet names in question
        found_planets = []
        for p in all_planets:
            if p['name'].lower() in q_lower:
                found_planets.append(p)
        
        # Also check known planets
        for name in KNOWN_PLANETS:
            if name.lower() in q_lower and name not in [p['name'] for p in found_planets]:
                found_planets.append({'name': name, **KNOWN_PLANETS[name], 'hab_score': int(KNOWN_PLANETS[name].get('esi', 0.5) * 100)})
        
        if len(found_planets) >= 2:
            p1, p2 = found_planets[0], found_planets[1]
            comparison = {
                'ru': f"""## ⚖️ Сравнение: {p1['name']} vs {p2['name']}

| Параметр | {p1['name']} | {p2['name']} | Лучше |
|----------|-------------|-------------|-------|
| **Радиус** | {p1.get('radius', '?'):.2f} R⊕ | {p2.get('radius', '?'):.2f} R⊕ | {'🌍' if abs(p1.get('radius',1)-1) < abs(p2.get('radius',1)-1) else '🔵'} |
| **Температура** | {p1.get('temp', '?'):.0f}K | {p2.get('temp', '?'):.0f}K | {'🌍' if abs(p1.get('temp',288)-288) < abs(p2.get('temp',288)-288) else '🔵'} |
| **ESI** | {p1.get('esi', '?')} | {p2.get('esi', '?')} | {'🌍' if (p1.get('esi',0) or 0) > (p2.get('esi',0) or 0) else '🔵'} |
| **Балл** | {p1.get('hab_score', '?')}/100 | {p2.get('hab_score', '?')}/100 | {'🌍' if p1.get('hab_score',0) > p2.get('hab_score',0) else '🔵'} |

**Вывод:** {'**' + p1['name'] + '** более перспективна' if p1.get('hab_score',0) > p2.get('hab_score',0) else '**' + p2['name'] + '** более перспективна'} для поиска жизни.""",
                'en': f"""## ⚖️ Comparison: {p1['name']} vs {p2['name']}

| Parameter | {p1['name']} | {p2['name']} | Better |
|-----------|-------------|-------------|--------|
| **Radius** | {p1.get('radius', '?'):.2f} R⊕ | {p2.get('radius', '?'):.2f} R⊕ | {'🌍' if abs(p1.get('radius',1)-1) < abs(p2.get('radius',1)-1) else '🔵'} |
| **Temperature** | {p1.get('temp', '?'):.0f}K | {p2.get('temp', '?'):.0f}K | {'🌍' if abs(p1.get('temp',288)-288) < abs(p2.get('temp',288)-288) else '🔵'} |
| **ESI** | {p1.get('esi', '?')} | {p2.get('esi', '?')} | {'🌍' if (p1.get('esi',0) or 0) > (p2.get('esi',0) or 0) else '🔵'} |
| **Score** | {p1.get('hab_score', '?')}/100 | {p2.get('hab_score', '?')}/100 | {'🌍' if p1.get('hab_score',0) > p2.get('hab_score',0) else '🔵'} |

**Conclusion:** {'**' + p1['name'] + '** is more promising' if p1.get('hab_score',0) > p2.get('hab_score',0) else '**' + p2['name'] + '** is more promising'} for life search.""",
                'kz': f"""## ⚖️ Салыстыру: {p1['name']} vs {p2['name']}

**Қорытынды:** {'**' + p1['name'] + '**' if p1.get('hab_score',0) > p2.get('hab_score',0) else '**' + p2['name'] + '**'} өмір іздеу үшін перспективті."""
            }
            return comparison[lang]
    
    # ═══════════════════════════════════════════════════════════════════════
    # FILTER/SEARCH: "найди планеты с температурой > 250K"
    # ═══════════════════════════════════════════════════════════════════════
    filter_words = ['найди', 'покажи', 'какие', 'find', 'show', 'which', 'filter', 'список', 'list', 'тап', 'көрсет']
    if any(w in q_lower for w in filter_words) and all_planets:
        results = all_planets.copy()
        filter_applied = False
        filter_desc = ""
        
        # Temperature filters
        if 'тепл' in q_lower or 'warm' in q_lower or 'hot' in q_lower or 'горяч' in q_lower:
            results = [p for p in results if p.get('temp', 0) > 280]
            filter_desc = "температура > 280K"
            filter_applied = True
        elif 'холод' in q_lower or 'cold' in q_lower:
            results = [p for p in results if p.get('temp', 999) < 260]
            filter_desc = "температура < 260K"
            filter_applied = True
        
        # Size filters
        if 'земн' in q_lower or 'earth' in q_lower:
            results = [p for p in results if 0.8 <= p.get('radius', 0) <= 1.5]
            filter_desc = "земной размер (0.8-1.5 R⊕)"
            filter_applied = True
        elif 'супер' in q_lower or 'super' in q_lower:
            results = [p for p in results if 1.25 < p.get('radius', 0) <= 2.0]
            filter_desc = "супер-Земли (1.25-2 R⊕)"
            filter_applied = True
        elif 'гигант' in q_lower or 'giant' in q_lower:
            results = [p for p in results if p.get('radius', 0) > 6]
            filter_desc = "газовые гиганты (>6 R⊕)"
            filter_applied = True
        
        # HZ filter
        if 'hz' in q_lower or 'обитаем' in q_lower or 'habitable' in q_lower:
            results = [p for p in results if p.get('in_hz')]
            filter_desc = "в зоне обитаемости"
            filter_applied = True
        
        # High score filter
        if 'лучш' in q_lower or 'best' in q_lower or 'топ' in q_lower or 'top' in q_lower:
            results = sorted(results, key=lambda x: x['hab_score'], reverse=True)[:5]
            filter_desc = "топ-5 по баллу"
            filter_applied = True
        
        if filter_applied and results:
            planet_list = "\n".join([f"• **{p['name']}** — {p['hab_score']}/100, {p.get('temp',0):.0f}K, {p.get('radius',0):.2f} R⊕" for p in results[:8]])
            response = {
                'ru': f"🔍 **Найдено {len(results)} планет** ({filter_desc}):\n\n{planet_list}",
                'en': f"🔍 **Found {len(results)} planets** ({filter_desc}):\n\n{planet_list}",
                'kz': f"🔍 **{len(results)} планета табылды** ({filter_desc}):\n\n{planet_list}"
            }
            return response[lang]
    
    # ═══════════════════════════════════════════════════════════════════════
    # CURRENT SYSTEM ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════
    system_words = ['систем', 'system', 'текущ', 'current', 'загружен', 'loaded', 'жүйе']
    if any(w in q_lower for w in system_words) and current_system:
        data = saved_systems.get(current_system, {})
        planets = data.get('planets', [])
        star = data.get('star', {})
        
        if planets:
            best = max(planets, key=lambda x: x['hab_score'])
            hz_count = len([p for p in planets if p['in_hz']])
            
            analysis = {
                'ru': f"""## 🌟 Система: {current_system}

**Звезда:** {star.get('st_spectype', '?')} типа, {star.get('st_teff', '?')}K

**Планеты:** {len(planets)} шт.
{chr(10).join([f"• {p['name']} — {p['hab_score']}/100 {'✅ HZ' if p['in_hz'] else ''}" for p in planets])}

**Анализ:**
• В зоне обитаемости: {hz_count} планет
• Лучший кандидат: **{best['name']}** (ESI: {best['esi']}, {best['temp']:.0f}K)
• {'⭐ Высокий потенциал!' if best['hab_score'] >= 60 else '📊 Умеренный интерес' if best['hab_score'] >= 40 else '📉 Низкий потенциал'}""",
                'en': f"""## 🌟 System: {current_system}

**Star:** {star.get('st_spectype', '?')} type, {star.get('st_teff', '?')}K

**Planets:** {len(planets)}
{chr(10).join([f"• {p['name']} — {p['hab_score']}/100 {'✅ HZ' if p['in_hz'] else ''}" for p in planets])}

**Analysis:**
• In habitable zone: {hz_count} planets
• Best candidate: **{best['name']}** (ESI: {best['esi']}, {best['temp']:.0f}K)
• {'⭐ High potential!' if best['hab_score'] >= 60 else '📊 Moderate interest' if best['hab_score'] >= 40 else '📉 Low potential'}""",
                'kz': f"""## 🌟 Жүйе: {current_system}

**Жұлдыз:** {star.get('st_spectype', '?')} түрі, {star.get('st_teff', '?')}K
**Планеталар:** {len(planets)}
**Үздік:** {best['name']} ({best['hab_score']}/100)"""
            }
            return analysis[lang]
    
    # ═══════════════════════════════════════════════════════════════════════
    # RECOMMENDATIONS
    # ═══════════════════════════════════════════════════════════════════════
    rec_words = ['рекоменд', 'совет', 'recommend', 'suggest', 'что исслед', 'what to', 'куда', 'where', 'ұсын']
    if any(w in q_lower for w in rec_words):
        recs = []
        
        # Check unexplored catalogs
        for cat_key, cat_data in CATALOGS.items():
            scanned = st.session_state.get('scanned_stars', set())
            unscanned = [s for s in cat_data['stars'] if s not in scanned]
            if len(unscanned) >= 5:
                recs.append(f"📁 Каталог **{cat_key}**: {len(unscanned)} неисследованных звёзд")
        
        # Check for patterns
        if stats['in_hz'] < 3:
            recs.append("🌱 Сфокусируйтесь на каталоге **habitable** для поиска планет в HZ")
        
        if stats['avg_score'] < 40:
            recs.append("📊 Средний балл низкий — попробуйте каталог **nearby** (ближайшие звёзды)")
        
        if not recs:
            recs.append("✅ Вы на правильном пути! Продолжайте исследования.")
        
        response = {
            'ru': "## 💡 Рекомендации:\n\n" + "\n".join(recs[:5]),
            'en': "## 💡 Recommendations:\n\n" + "\n".join(recs[:5]),
            'kz': "## 💡 Ұсыныстар:\n\n" + "\n".join(recs[:5])
        }
        return response[lang]
    
    # ═══════════════════════════════════════════════════════════════════════
    # STATISTICS (detailed)
    # ═══════════════════════════════════════════════════════════════════════
    stat_words = ['статистик', 'statistic', 'сколько', 'how many', 'итог', 'summary', 'қанша', 'результат', 'result']
    if any(w in q_lower for w in stat_words):
        if not all_planets:
            return {'ru': "📭 Пока нет данных. Запустите миссию!", 'en': "📭 No data yet. Run a mission!", 'kz': "📭 Деректер жоқ. Миссия іске қосыңыз!"}[lang]
        
        response = {
            'ru': f"""## 📊 Полная статистика исследований

**Общие данные:**
• Систем изучено: **{stats['systems']}**
• Планет найдено: **{stats['total']}**
• Средний балл: **{stats['avg_score']:.1f}/100**

**По типам:**
• 🌍 Земного размера: **{stats['earth_like']}**
• 🌎 Супер-Земли: **{stats['super_earth']}**
• 🪐 Газовые гиганты: **{stats['gas_giants']}**

**Обитаемость:**
• В зоне HZ: **{stats['in_hz']}**
• Потенциально обитаемых (>50): **{stats['habitable']}**

**Рекорды:**
• 🏆 Лучшая: **{stats['best']['name']}** ({stats['best']['hab_score']}/100)
• 📍 Ближайшая: **{stats['nearest']['name']}** ({stats['nearest'].get('distance', '?'):.1f} св.лет)
• 🔥 Горячая: **{stats['hottest']['name']}** ({stats['hottest'].get('temp', '?'):.0f}K)
• 🧊 Холодная: **{stats['coldest']['name']}** ({stats['coldest'].get('temp', '?'):.0f}K)""" if stats['best'] else "📭 Нет данных",
            'en': f"""## 📊 Full Research Statistics

**Overview:**
• Systems explored: **{stats['systems']}**
• Planets found: **{stats['total']}**
• Average score: **{stats['avg_score']:.1f}/100**

**By type:**
• 🌍 Earth-sized: **{stats['earth_like']}**
• 🌎 Super-Earths: **{stats['super_earth']}**
• 🪐 Gas giants: **{stats['gas_giants']}**

**Habitability:**
• In HZ: **{stats['in_hz']}**
• Potentially habitable (>50): **{stats['habitable']}**

**Records:**
• 🏆 Best: **{stats['best']['name']}** ({stats['best']['hab_score']}/100)
• 📍 Nearest: **{stats['nearest']['name']}** ({stats['nearest'].get('distance', '?'):.1f} ly)""" if stats['best'] else "📭 No data",
            'kz': f"""## 📊 Зерттеу статистикасы

• Жүйелер: **{stats['systems']}**
• Планеталар: **{stats['total']}**
• Орташа балл: **{stats['avg_score']:.1f}/100**
• HZ-да: **{stats['in_hz']}**
• Үздік: **{stats['best']['name']}** ({stats['best']['hab_score']}/100)""" if stats['best'] else "📭 Деректер жоқ"
        }
        return response[lang]
    
    # ═══════════════════════════════════════════════════════════════════════
    # SCIENTIFIC EXPLANATIONS
    # ═══════════════════════════════════════════════════════════════════════
    explanations = {
        'esi': {
            'ru': """## 🌍 ESI (Earth Similarity Index)

**Что это:** Индекс подобия Земле от 0 до 1.

**Формула:**
```
ESI = √[(1-|R-1|/(R+1))^0.57 × (1-|T-288|/(T+288))^5.58]
```

**Интерпретация:**
• **ESI > 0.9** — почти близнец Земли (очень редко!)
• **ESI 0.8-0.9** — отличный кандидат для жизни
• **ESI 0.6-0.8** — условия отличаются, но жизнь возможна
• **ESI < 0.6** — значительные отличия от Земли

**Важно:** ESI учитывает только размер и температуру. Атмосфера, вода, магнитное поле — не учитываются!""",
            'en': """## 🌍 ESI (Earth Similarity Index)

**What it is:** Earth similarity from 0 to 1.

**Formula:**
```
ESI = √[(1-|R-1|/(R+1))^0.57 × (1-|T-288|/(T+288))^5.58]
```

**Interpretation:**
• **ESI > 0.9** — almost Earth twin (very rare!)
• **ESI 0.8-0.9** — excellent life candidate
• **ESI 0.6-0.8** — different conditions, but life possible
• **ESI < 0.6** — significant differences from Earth"""
        },
        'hz': {
            'ru': """## 🌱 Зона обитаемости (Habitable Zone)

**Что это:** Область вокруг звезды, где возможна жидкая вода на поверхности планеты.

**Границы:**
• **Внутренняя:** 0.75 × √L AU (убегающий парниковый эффект)
• **Внешняя:** 1.77 × √L AU (замерзание CO₂)

где L — светимость звезды в солнечных единицах.

**Для разных звёзд:**
• ☀️ Солнце (G): 0.95 - 1.37 AU
• 🔴 M-карлик: 0.1 - 0.4 AU (очень близко!)
• 🔵 F-звезда: 1.5 - 2.5 AU

**Важно:** Нахождение в HZ не гарантирует обитаемость! Нужна атмосфера, магнитное поле, и многое другое.""",
            'en': """## 🌱 Habitable Zone (HZ)

**What it is:** Region around a star where liquid water can exist on a planet's surface.

**Boundaries:**
• **Inner:** 0.75 × √L AU (runaway greenhouse)
• **Outer:** 1.77 × √L AU (CO₂ freezing)

where L = stellar luminosity in solar units."""
        },
        'trappist': {
            'ru': """## 🔴 Система TRAPPIST-1

**Звезда:** Ультрахолодный красный карлик (M8V)
• Расстояние: **40.7 световых лет**
• Температура: ~2,566K (в 2 раза холоднее Солнца)
• Размер: 12% от Солнца

**7 планет земного размера!**
• TRAPPIST-1b, c — слишком горячие
• **TRAPPIST-1d, e, f** — в зоне обитаемости! ⭐
• TRAPPIST-1g, h — возможно слишком холодные

**Почему важна:**
• Все 7 планет можно изучать транзитным методом
• 3-4 планеты потенциально обитаемы
• Ближайшая система с таким количеством землеподобных планет

**Риски:**
• ⚠️ Приливной захват (одна сторона всегда к звезде)
• ⚠️ Звёздные вспышки (M-карлики активны)
• ⚠️ Возможная потеря атмосферы""",
            'en': """## 🔴 TRAPPIST-1 System

**Star:** Ultracool red dwarf (M8V)
• Distance: **40.7 light years**
• Temperature: ~2,566K

**7 Earth-sized planets!**
• **TRAPPIST-1d, e, f** — in habitable zone! ⭐

**Risks:**
• ⚠️ Tidal locking
• ⚠️ Stellar flares"""
        }
    }
    
    # Check for explanation keywords
    if 'esi' in q_lower or 'индекс' in q_lower:
        return explanations['esi'].get(lang, explanations['esi']['en'])
    if 'hz' in q_lower or 'обитаем' in q_lower or 'habitable' in q_lower or 'зона' in q_lower:
        return explanations['hz'].get(lang, explanations['hz']['en'])
    if 'trappist' in q_lower:
        return explanations['trappist'].get(lang, explanations['trappist']['en'])
    
    # ═══════════════════════════════════════════════════════════════════════
    # GREETING
    # ═══════════════════════════════════════════════════════════════════════
    greet_words = ['привет', 'hello', 'hi', 'здравств', 'сәлем', 'хай', 'hey']
    if any(w in q_lower for w in greet_words):
        response = {
            'ru': f"""👋 Привет! Я ИИ-ассистент ATLAS.

{'📊 У вас уже есть данные: ' + str(stats["total"]) + ' планет в ' + str(stats["systems"]) + ' системах.' if stats["total"] > 0 else '🚀 Запустите миссию, чтобы начать исследования!'}

**Что я умею:**
• 📊 Статистика — "покажи статистику"
• 🔍 Поиск — "найди планеты в HZ"
• ⚖️ Сравнение — "сравни TRAPPIST-1e и Proxima b"
• 💡 Рекомендации — "что исследовать?"
• 🌟 Анализ — "расскажи про текущую систему"
• 📚 Объяснения — "что такое ESI?"

Спрашивайте!""",
            'en': f"""👋 Hello! I'm the ATLAS AI assistant.

{'📊 You have data: ' + str(stats["total"]) + ' planets in ' + str(stats["systems"]) + ' systems.' if stats["total"] > 0 else '🚀 Run a mission to start exploring!'}

**What I can do:**
• 📊 Statistics — "show statistics"
• 🔍 Search — "find planets in HZ"
• ⚖️ Compare — "compare TRAPPIST-1e and Proxima b"
• 💡 Recommendations — "what to explore?"
• 📚 Explanations — "what is ESI?"

Ask me anything!""",
            'kz': f"""👋 Сәлем! Мен ATLAS AI көмекшісімін.

{'📊 Деректер бар: ' + str(stats["total"]) + ' планета.' if stats["total"] > 0 else '🚀 Зерттеуді бастау үшін миссия іске қосыңыз!'}

Сұрақтарыңызды қойыңыз!"""
        }
        return response[lang]
    
    # ═══════════════════════════════════════════════════════════════════════
    # SPECIFIC PLANET QUERY
    # ═══════════════════════════════════════════════════════════════════════
    for p in all_planets:
        if p['name'].lower() in q_lower:
            return {
                'ru': f"""## 🪐 {p['name']}

**Тип:** {p.get('type', '?')} {p.get('emoji', '')}

**Физические параметры:**
• Радиус: **{p.get('radius', '?'):.2f} R⊕**
• Температура: **{p.get('temp', '?'):.0f}K**
• ESI: **{p.get('esi', '?')}**
• Гравитация: **{p.get('gravity', '?'):.2f}g**

**Обитаемость:**
• Балл: **{p['hab_score']}/100**
• В зоне HZ: **{'Да ✅' if p.get('in_hz') else 'Нет ❌'}**
• Атмосфера: {p.get('atmo_type', '?')}

**Оценка:** {'🌱 Отличный кандидат для жизни!' if p['hab_score'] >= 70 else '📊 Умеренный потенциал' if p['hab_score'] >= 50 else '❄️ Низкий потенциал'}""",
                'en': f"""## 🪐 {p['name']}

**Type:** {p.get('type', '?')} {p.get('emoji', '')}

**Physical:**
• Radius: **{p.get('radius', '?'):.2f} R⊕**
• Temperature: **{p.get('temp', '?'):.0f}K**
• ESI: **{p.get('esi', '?')}**

**Habitability:**
• Score: **{p['hab_score']}/100**
• In HZ: **{'Yes ✅' if p.get('in_hz') else 'No ❌'}**"""
            }[lang]
    
    # ═══════════════════════════════════════════════════════════════════════
    # DEFAULT RESPONSE
    # ═══════════════════════════════════════════════════════════════════════
    default = {
        'ru': f"""🤔 Интересный вопрос! Вот что я могу:

**Попробуйте спросить:**
• "Покажи статистику"
• "Найди планеты в зоне обитаемости"
• "Сравни Earth и TRAPPIST-1e"
• "Что такое ESI?"
• "Расскажи про систему TRAPPIST-1"
• "Какая планета лучшая?"
• "Что исследовать дальше?"

{'📊 У вас ' + str(stats["total"]) + ' планет для анализа!' if stats["total"] > 0 else '🚀 Запустите миссию для начала!'}""",
        'en': f"""🤔 Interesting question! Here's what I can do:

**Try asking:**
• "Show statistics"
• "Find planets in habitable zone"
• "Compare Earth and TRAPPIST-1e"
• "What is ESI?"
• "What to explore next?"

{'📊 You have ' + str(stats["total"]) + ' planets to analyze!' if stats["total"] > 0 else '🚀 Run a mission to start!'}""",
        'kz': """🤔 Қызықты сұрақ! Мен көмектесе аламын:

• "Статистиканы көрсет"
• "HZ-дағы планеталарды тап"
• "ESI дегеніміз не?"

🚀 Миссия іске қосыңыз!"""
    }
    return default[lang]


def get_lm_studio_response(question, context_data):
    """
    Get response from LM Studio local LLM server.
    Falls back to pattern matching if server unavailable.
    """
    if not st.session_state.get('lm_studio_enabled', False):
        return None
    
    ip = st.session_state.get('lm_studio_ip', 'localhost')
    port = st.session_state.get('lm_studio_port', '1234')
    lang = st.session_state.get('lang', 'ru')
    
    # Build context from discoveries
    all_planets = get_all_planets()
    stats = {
        'total': len(all_planets),
        'systems': len(st.session_state.get('saved_systems', {})),
        'habitable': len([p for p in all_planets if p['hab_score'] >= 50]),
        'in_hz': len([p for p in all_planets if p['in_hz']]),
        'best': max(all_planets, key=lambda x: x['hab_score']) if all_planets else None
    }
    
    current_system = st.session_state.get('current_system')
    current_planets = []
    if current_system and current_system in st.session_state.get('saved_systems', {}):
        current_planets = st.session_state['saved_systems'][current_system].get('planets', [])
    
    # Language instruction
    lang_instruction = {
        'ru': 'Отвечай на русском языке. Будь кратким но информативным.',
        'en': 'Respond in English. Be concise but informative.',
        'kz': 'Қазақ тілінде жауап бер. Қысқа бірақ ақпаратты бол.'
    }
    
    # Build system prompt (shorter for faster response)
    system_prompt = f"""{lang_instruction.get(lang, 'Respond in Russian.')}

You are ATLAS AI - exoplanet research assistant.

User's data: {stats['total']} planets, {stats['systems']} systems, {stats['habitable']} habitable candidates.
{f"Best: {stats['best']['name']} (score {stats['best']['hab_score']}/100)" if stats['best'] else 'No data yet.'}
{f"Current system: {current_system}" if current_system else ""}

You know: ESI formula, habitable zones, stellar types (OBAFGKM), planet classification.
Be helpful, scientific, reference user's discoveries when relevant."""

    try:
        # Combine system prompt with user question (some models don't support system role)
        combined_prompt = f"""{system_prompt}

User question: {question}

Your response:"""

        response = requests.post(
            f"http://{ip}:{port}/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": combined_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500,
                "stream": False
            },
            timeout=180
        )
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0].get("message", {}).get("content", "")
                if content:
                    return content
                return "⚠️ Empty response from LLM"
            return "⚠️ No choices in response"
        else:
            return f"⚠️ Error {response.status_code}: {response.text[:100]}"
            
    except requests.exceptions.ConnectionError as e:
        return f"⚠️ Connection error: {str(e)[:50]}"
    except requests.exceptions.Timeout:
        return "⚠️ Timeout - LLM is taking too long. Try shorter question."
    except Exception as e:
        return f"⚠️ Error: {str(e)[:50]}"


def get_smart_response(question):
    """
    Main function to get AI response.
    Tries LM Studio first, falls back to pattern matching.
    """
    # Try LM Studio if enabled
    if st.session_state.get('lm_studio_enabled', False):
        lm_response = get_lm_studio_response(question, None)
        if lm_response:
            # Check if it's an error message
            if lm_response.startswith("⚠️"):
                # Show error but also provide pattern matching response
                pattern_response = get_ai_response(question)
                return f"{lm_response}\n\n---\n**Fallback response:**\n\n{pattern_response}", "⚠️ Error"
            return lm_response, "🧠 LLM"
    
    # Fallback to pattern matching
    return get_ai_response(question), "⚡ Local"
# ═══════════════════════════════════════════════════════════════════════════════
# ENCYCLOPEDIA DATA (Multilingual)
# ═══════════════════════════════════════════════════════════════════════════════

ENCYCLOPEDIA = {
    'star_types': {
        'title': {'ru': '⭐ Типы звёзд', 'en': '⭐ Star Types', 'kz': '⭐ Жұлдыз түрлері'},
        'content': {
            'ru': """
### Спектральная классификация звёзд (O-B-A-F-G-K-M)

| Класс | Температура | Цвет | Масса | Время жизни | Примеры |
|-------|-------------|------|-------|-------------|---------|
| O | 30,000-50,000K | Голубой | 16-150 M☉ | <10 млн лет | Минтака, Алнилам |
| B | 10,000-30,000K | Бело-голубой | 2-16 M☉ | 10-300 млн лет | Ригель, Спика |
| A | 7,500-10,000K | Белый | 1.4-2.1 M☉ | 0.3-2 млрд лет | Сириус, Вега |
| F | 6,000-7,500K | Жёлто-белый | 1.0-1.4 M☉ | 2-7 млрд лет | Процион, Канопус |
| G | 5,200-6,000K | Жёлтый | 0.8-1.04 M☉ | 7-15 млрд лет | **Солнце**, Альфа Центавра A |
| K | 3,700-5,200K | Оранжевый | 0.45-0.8 M☉ | 15-50 млрд лет | Альфа Центавра B, Эпсилон Эридана |
| M | 2,400-3,700K | Красный | 0.08-0.45 M☉ | 50+ млрд лет | Проксима Центавра, TRAPPIST-1 |

#### Оптимальные для жизни
**G и K типы** — достаточно света для фотосинтеза, стабильны миллиарды лет. Солнце — звезда G-типа.

#### Проблемные для жизни
**M-карлики** — частые вспышки, планеты в приливном захвате (одна сторона всегда к звезде).
**O/B типы** — слишком горячие, слишком недолговечные для эволюции жизни.
            """,
            'en': """
### Stellar Spectral Classification (O-B-A-F-G-K-M)

| Class | Temperature | Color | Mass | Lifespan | Examples |
|-------|-------------|-------|------|----------|----------|
| O | 30,000-50,000K | Blue | 16-150 M☉ | <10 Myr | Mintaka, Alnilam |
| B | 10,000-30,000K | Blue-White | 2-16 M☉ | 10-300 Myr | Rigel, Spica |
| A | 7,500-10,000K | White | 1.4-2.1 M☉ | 0.3-2 Gyr | Sirius, Vega |
| F | 6,000-7,500K | Yellow-White | 1.0-1.4 M☉ | 2-7 Gyr | Procyon, Canopus |
| G | 5,200-6,000K | Yellow | 0.8-1.04 M☉ | 7-15 Gyr | **Sun**, Alpha Centauri A |
| K | 3,700-5,200K | Orange | 0.45-0.8 M☉ | 15-50 Gyr | Alpha Centauri B, Epsilon Eridani |
| M | 2,400-3,700K | Red | 0.08-0.45 M☉ | 50+ Gyr | Proxima Centauri, TRAPPIST-1 |

#### Best for Life
**G and K types** — enough light for photosynthesis, stable for billions of years. Sun is G-type star.

#### Problematic for Life
**M-dwarfs** — frequent flares, planets tidally locked (one side always facing star).
**O/B types** — too hot, too short-lived for life evolution.
            """,
            'kz': """
### Жұлдыздардың спектрлік жіктелуі (O-B-A-F-G-K-M)

| Класс | Температура | Түс | Масса | Өмір ұзақтығы | Мысалдар |
|-------|-------------|-----|-------|---------------|----------|
| O | 30,000-50,000K | Көк | 16-150 M☉ | <10 млн жыл | Минтака, Алнилам |
| B | 10,000-30,000K | Ақ-көк | 2-16 M☉ | 10-300 млн жыл | Ригель, Спика |
| A | 7,500-10,000K | Ақ | 1.4-2.1 M☉ | 0.3-2 млрд жыл | Сириус, Вега |
| F | 6,000-7,500K | Сары-ақ | 1.0-1.4 M☉ | 2-7 млрд жыл | Процион |
| G | 5,200-6,000K | Сары | 0.8-1.04 M☉ | 7-15 млрд жыл | **Күн**, Альфа Центавра A |
| K | 3,700-5,200K | Сарғыш | 0.45-0.8 M☉ | 15-50 млрд жыл | Альфа Центавра B |
| M | 2,400-3,700K | Қызыл | 0.08-0.45 M☉ | 50+ млрд жыл | Проксима Центавра, TRAPPIST-1 |

#### Өмір үшін оңтайлы
**G және K түрлері** — фотосинтез үшін жеткілікті жарық, миллиардтаған жылдар бойы тұрақты.

#### Өмір үшін проблемалы
**M-ергежейлілер** — жиі жарқылдар, планеталар толқындық байланыста.
**O/B түрлері** — тым ыстық, өмір эволюциясы үшін тым қысқа өмірлі.
            """
        }
    },
    
    'planet_types': {
        'title': {'ru': '🪐 Типы планет', 'en': '🪐 Planet Types', 'kz': '🪐 Планета түрлері'},
        'content': {
            'ru': """
### Классификация экзопланет по размеру

| Тип | Радиус (R⊕) | Описание | Примеры |
|-----|-------------|----------|---------|
| 🪨 Карликовая | <0.5 | Астероидоподобное тело без атмосферы | Церера |
| 🔴 Суб-Земля | 0.5-0.8 | Марсоподобная, тонкая атмосфера | Марс, Kepler-138b |
| 🌍 Земная | 0.8-1.25 | Потенциально обитаемая, тектоника плит | Земля, Kepler-442b |
| 🌎 Супер-Земля | 1.25-2.0 | Толстая атмосфера, возможны океаны | LHS-1140b, K2-18b |
| 💧 Мини-Нептун | 2.0-4.0 | Водяной мир или газовая оболочка | TOI-270d, Kepler-11f |
| 🔵 Нептуноподобная | 4-6 | Ледяной гигант, глубокая H₂/He атмосфера | Уран, Нептун |
| 🪐 Газовый гигант | 6-15 | Юпитероподобная, металлический водород | Юпитер, HD-209458b |
| 🟤 Супер-Юпитер | >15 | Грань коричневого карлика | KELT-9b |

#### "Долина радиусов" (1.5-2.0 R⊕)
В этом диапазоне наблюдается дефицит планет — переходная зона между каменистыми и газовыми мирами. 
Причина: фотоиспарение атмосферы под действием звёздного излучения.
            """,
            'en': """
### Exoplanet Classification by Size

| Type | Radius (R⊕) | Description | Examples |
|------|-------------|-------------|----------|
| 🪨 Dwarf | <0.5 | Asteroid-like body without atmosphere | Ceres |
| 🔴 Sub-Earth | 0.5-0.8 | Mars-like, thin atmosphere | Mars, Kepler-138b |
| 🌍 Terrestrial | 0.8-1.25 | Potentially habitable, plate tectonics | Earth, Kepler-442b |
| 🌎 Super-Earth | 1.25-2.0 | Thick atmosphere, possible oceans | LHS-1140b, K2-18b |
| 💧 Mini-Neptune | 2.0-4.0 | Water world or gas envelope | TOI-270d, Kepler-11f |
| 🔵 Neptune-like | 4-6 | Ice giant, deep H₂/He atmosphere | Uranus, Neptune |
| 🪐 Gas Giant | 6-15 | Jupiter-like, metallic hydrogen | Jupiter, HD-209458b |
| 🟤 Super-Jupiter | >15 | Near brown dwarf boundary | KELT-9b |

#### "Radius Valley" (1.5-2.0 R⊕)
Deficit of planets in this range — transition zone between rocky and gaseous worlds.
Cause: photoevaporation of atmosphere by stellar radiation.
            """,
            'kz': """
### Экзопланеталардың өлшемі бойынша жіктелуі

| Түр | Радиус (R⊕) | Сипаттама | Мысалдар |
|-----|-------------|-----------|----------|
| 🪨 Ергежейлі | <0.5 | Атмосферасыз астероид тәрізді дене | Церера |
| 🔴 Суб-Жер | 0.5-0.8 | Марсқа ұқсас, жұқа атмосфера | Марс, Kepler-138b |
| 🌍 Жер тәрізді | 0.8-1.25 | Мекендеуге жарамды, плиталар тектоникасы | Жер, Kepler-442b |
| 🌎 Супер-Жер | 1.25-2.0 | Қалың атмосфера, мұхиттар мүмкін | LHS-1140b, K2-18b |
| 💧 Мини-Нептун | 2.0-4.0 | Су әлемі немесе газ қабаты | TOI-270d |
| 🔵 Нептунға ұқсас | 4-6 | Мұзды алып, терең H₂/He атмосферасы | Уран, Нептун |
| 🪐 Газ алыбы | 6-15 | Юпитерге ұқсас, металл сутегі | Юпитер, HD-209458b |
| 🟤 Супер-Юпитер | >15 | Қоңыр ергежейлі шекарасында | KELT-9b |

#### "Радиус алқабы" (1.5-2.0 R⊕)
Бұл ауқымда планеталар тапшылығы — тасты және газды әлемдер арасындағы өтпелі аймақ.
            """
        }
    },
    
    'habitability': {
        'title': {'ru': '🌱 Критерии обитаемости', 'en': '🌱 Habitability Criteria', 'kz': '🌱 Мекендеуге жарамдылық критерийлері'},
        'content': {
            'ru': """
### Основные критерии обитаемости планеты

#### 1. Зона обитаемости (HZ)
Область вокруг звезды, где возможна жидкая вода на поверхности.
- **Внутренняя граница**: 0.75√L AU (парниковый эффект)
- **Внешняя граница**: 1.77√L AU (конденсация CO₂)
- L — светимость звезды в солнечных единицах

#### 2. Размер и масса
- **Оптимально**: 0.8-1.5 R⊕, 0.5-5 M⊕
- Планета должна удержать атмосферу, но не стать газовым гигантом

#### 3. Температура
- **Идеально**: 250-310K (жидкая вода)
- **Расширенно**: 200-350K (экстремофилы)

#### 4. Атмосфера
- N₂/O₂ (биогенная) или N₂/CO₂ (абиотическая)
- Давление: 0.5-5 атм для стабильности воды

#### 5. Магнитное поле
Защита от звёздного ветра и космических лучей. Требуется жидкое железное ядро + вращение.

#### 6. Стабильность звезды
- **Оптимально**: G, K типы
- **Риски**: M-карлики (вспышки), O/B (короткая жизнь)

### Индекс подобия Земле (ESI)
```
ESI = √[(1-|R-1|/(R+1))^0.57 × (1-|T-288|/(T+288))^5.58]
```
ESI > 0.8 = кандидат типа Земли
            """,
            'en': """
### Key Planetary Habitability Criteria

#### 1. Habitable Zone (HZ)
Region around star where liquid water can exist on surface.
- **Inner boundary**: 0.75√L AU (runaway greenhouse)
- **Outer boundary**: 1.77√L AU (CO₂ condensation)
- L — stellar luminosity in solar units

#### 2. Size and Mass
- **Optimal**: 0.8-1.5 R⊕, 0.5-5 M⊕
- Planet must retain atmosphere but not become gas giant

#### 3. Temperature
- **Ideal**: 250-310K (liquid water)
- **Extended**: 200-350K (extremophiles)

#### 4. Atmosphere
- N₂/O₂ (biogenic) or N₂/CO₂ (abiotic)
- Pressure: 0.5-5 atm for water stability

#### 5. Magnetic Field
Protection from stellar wind and cosmic rays. Requires liquid iron core + rotation.

#### 6. Stellar Stability
- **Optimal**: G, K types
- **Risks**: M-dwarfs (flares), O/B (short-lived)

### Earth Similarity Index (ESI)
```
ESI = √[(1-|R-1|/(R+1))^0.57 × (1-|T-288|/(T+288))^5.58]
```
ESI > 0.8 = Earth-like candidate
            """,
            'kz': """
### Планетаның мекендеуге жарамдылығының негізгі критерийлері

#### 1. Мекендеуге жарамды аймақ (HZ)
Жұлдыз айналасындағы бетінде сұйық су болуы мүмкін аймақ.
- **Ішкі шекара**: 0.75√L AU (жүгірмелі парник)
- **Сыртқы шекара**: 1.77√L AU (CO₂ конденсациясы)

#### 2. Өлшем және масса
- **Оңтайлы**: 0.8-1.5 R⊕, 0.5-5 M⊕
- Планета атмосфераны ұстап тұруы керек

#### 3. Температура
- **Идеал**: 250-310K (сұйық су)
- **Кеңейтілген**: 200-350K (экстремофилдер)

#### 4. Атмосфера
- N₂/O₂ (биогендік) немесе N₂/CO₂ (абиотикалық)
- Қысым: 0.5-5 атм

#### 5. Магнит өрісі
Жұлдыз желі мен ғарыштық сәулелерден қорғау.

#### 6. Жұлдыз тұрақтылығы
- **Оңтайлы**: G, K түрлері
- **Қауіптер**: M-ергежейлілер (жарқылдар)

### Жерге ұқсастық индексі (ESI)
```
ESI = √[(1-|R-1|/(R+1))^0.57 × (1-|T-288|/(T+288))^5.58]
```
ESI > 0.8 = Жер тәрізді үміткер
            """
        }
    },
    
    'detection': {
        'title': {'ru': '🔭 Методы обнаружения', 'en': '🔭 Detection Methods', 'kz': '🔭 Анықтау әдістері'},
        'content': {
            'ru': """
### Методы обнаружения экзопланет

#### 1. Транзитный метод (Kepler, TESS) — 76% открытий
Планета проходит перед звездой → падение яркости 0.01-1%
- **Даёт**: радиус, период, наклон орбиты
- **Требует**: орбита "ребром" к наблюдателю

#### 2. Метод радиальных скоростей (RV) — 19% открытий
Звезда "качается" под действием гравитации планеты → допплеровский сдвиг спектра
- **Даёт**: минимальную массу (M·sin i), период
- **Точность**: до 1 м/с (планеты типа Земли)

#### 3. Прямое наблюдение — 2% открытий
Блокирование звезды коронографом → свет от планеты
- **Даёт**: атмосферу, температуру, орбиту
- **Ограничение**: только далёкие гиганты

#### 4. Микролинзирование
Гравитация планеты искривляет свет фоновой звезды
- **Одноразовое** событие, нет повтора
- Открывает далёкие планеты

#### 5. Астрометрия (Gaia)
Точное измерение покачивания звезды на небе
- **Даёт**: массу и орбиту
- **Требует**: высокую точность

### Статистика открытий (2024)
- **5,500+** подтверждённых экзопланет
- **70+** потенциально обитаемых
- **Kepler**: 2,700+ планет
- **TESS**: 500+ планет
            """,
            'en': """
### Exoplanet Detection Methods

#### 1. Transit Method (Kepler, TESS) — 76% of discoveries
Planet passes in front of star → brightness dip 0.01-1%
- **Provides**: radius, period, orbital inclination
- **Requires**: edge-on orbit

#### 2. Radial Velocity (RV) — 19% of discoveries
Star "wobbles" due to planet's gravity → Doppler shift in spectrum
- **Provides**: minimum mass (M·sin i), period
- **Precision**: down to 1 m/s (Earth-like planets)

#### 3. Direct Imaging — 2% of discoveries
Block star with coronagraph → light from planet
- **Provides**: atmosphere, temperature, orbit
- **Limitation**: only distant giants

#### 4. Microlensing
Planet's gravity bends background star light
- **One-time** event, no repeat
- Discovers distant planets

#### 5. Astrometry (Gaia)
Precise measurement of star wobble on sky
- **Provides**: mass and orbit
- **Requires**: high precision

### Discovery Statistics (2024)
- **5,500+** confirmed exoplanets
- **70+** potentially habitable
- **Kepler**: 2,700+ planets
- **TESS**: 500+ planets
            """,
            'kz': """
### Экзопланеталарды анықтау әдістері

#### 1. Транзит әдісі (Kepler, TESS) — ашылымдардың 76%
Планета жұлдыздың алдынан өтеді → жарықтық 0.01-1% төмендеуі
- **Береді**: радиус, период, орбита көлбеуі

#### 2. Радиалды жылдамдық (RV) — ашылымдардың 19%
Жұлдыз планета гравитациясынан "тербеледі" → спектрдің Доплер жылжуы
- **Береді**: минималды масса, период

#### 3. Тікелей бақылау — ашылымдардың 2%
Жұлдызды коронографпен бұғаттау → планетадан жарық
- **Береді**: атмосфера, температура, орбита

#### 4. Микролинзалау
Планета гравитациясы фондық жұлдыз жарығын бүгеді
- **Бір реттік** оқиға

#### 5. Астрометрия (Gaia)
Жұлдыздың аспандағы тербелісін дәл өлшеу
- **Береді**: масса және орбита

### Ашылым статистикасы (2024)
- **5,500+** расталған экзопланеталар
- **70+** мекендеуге жарамды
- **Kepler**: 2,700+ планета
- **TESS**: 500+ планета
            """
        }
    },
    
    'formulas': {
        'title': {'ru': '📐 Формулы', 'en': '📐 Formulas', 'kz': '📐 Формулалар'},
        'content': {
            'ru': """
### Основные астрофизические формулы

#### Светимость звезды (закон Стефана-Больцмана)
```
L = R² × (T/5778)⁴ [L☉]
```
R — радиус в R☉, T — температура в K

#### Равновесная температура планеты
```
Teq = T★ × √(R★/(2a)) × (1-A)^0.25
```
A — альбедо (~0.3), a — орбита в AU

#### Границы зоны обитаемости
```
HZ_inner = 0.75 × √L [AU]
HZ_outer = 1.77 × √L [AU]
```

#### Третий закон Кеплера
```
a³ = (P/365.25)² × M★ [AU]
```
P — период в днях, M★ — масса звезды в M☉

#### Поверхностная гравитация
```
g = M/R² [g⊕]
```
M, R — масса и радиус в земных единицах

#### Вторая космическая скорость
```
v_esc = 11.2 × √(M/R) [км/с]
```
Для Земли: 11.2 км/с

#### Плотность
```
ρ = M/R³ [ρ⊕]
```
Земля: 5.51 г/см³

#### Индекс подобия Земле (ESI)
```
ESI = √[(1-|R-1|/(R+1))^0.57 × (1-|T-288|/(T+288))^5.58]
```

#### Сфера Хилла (стабильность спутников)
```
r_Hill = a × (m/(3M★))^(1/3)
```
            """,
            'en': """
### Key Astrophysical Formulas

#### Stellar Luminosity (Stefan-Boltzmann Law)
```
L = R² × (T/5778)⁴ [L☉]
```
R — radius in R☉, T — temperature in K

#### Planetary Equilibrium Temperature
```
Teq = T★ × √(R★/(2a)) × (1-A)^0.25
```
A — albedo (~0.3), a — orbit in AU

#### Habitable Zone Boundaries
```
HZ_inner = 0.75 × √L [AU]
HZ_outer = 1.77 × √L [AU]
```

#### Kepler's Third Law
```
a³ = (P/365.25)² × M★ [AU]
```
P — period in days, M★ — stellar mass in M☉

#### Surface Gravity
```
g = M/R² [g⊕]
```
M, R — mass and radius in Earth units

#### Escape Velocity
```
v_esc = 11.2 × √(M/R) [km/s]
```
Earth: 11.2 km/s

#### Density
```
ρ = M/R³ [ρ⊕]
```
Earth: 5.51 g/cm³

#### Earth Similarity Index (ESI)
```
ESI = √[(1-|R-1|/(R+1))^0.57 × (1-|T-288|/(T+288))^5.58]
```

#### Hill Sphere (moon stability)
```
r_Hill = a × (m/(3M★))^(1/3)
```
            """,
            'kz': """
### Негізгі астрофизикалық формулалар

#### Жұлдыз жарықтығы (Стефан-Больцман заңы)
```
L = R² × (T/5778)⁴ [L☉]
```

#### Планетаның тепе-теңдік температурасы
```
Teq = T★ × √(R★/(2a)) × (1-A)^0.25
```

#### Мекендеуге жарамды аймақ шекаралары
```
HZ_inner = 0.75 × √L [AU]
HZ_outer = 1.77 × √L [AU]
```

#### Кеплердің үшінші заңы
```
a³ = (P/365.25)² × M★ [AU]
```

#### Бетіндегі гравитация
```
g = M/R² [g⊕]
```

#### Екінші ғарыштық жылдамдық
```
v_esc = 11.2 × √(M/R) [км/с]
```

#### Тығыздық
```
ρ = M/R³ [ρ⊕]
```

#### Жерге ұқсастық индексі (ESI)
```
ESI = √[(1-|R-1|/(R+1))^0.57 × (1-|T-288|/(T+288))^5.58]
```

#### Хилл сферасы
```
r_Hill = a × (m/(3M★))^(1/3)
```
            """
        }
    }
}
# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🛰️ ATLAS")
    st.caption("Autonomous Terrestrial Life Analysis System")
    
    st.markdown("---")
    
    # Language selector
    st.markdown(f"### {t('sidebar_lang')}")
    lang_cols = st.columns(3)
    for i, (code, flag) in enumerate([('ru', '🇷🇺'), ('en', '🇬🇧'), ('kz', '🇰🇿')]):
        if lang_cols[i].button(flag, key=f"lang_{code}", use_container_width=True,
                               type="primary" if st.session_state.lang == code else "secondary"):
            st.session_state.lang = code
            st.rerun()
    
    # Theme selector
    st.markdown(f"### {t('sidebar_theme')}")
    theme_cols = st.columns(2)
    if theme_cols[0].button(t('theme_dark'), use_container_width=True,
                            type="primary" if st.session_state.theme == 'dark' else "secondary"):
        st.session_state.theme = 'dark'
        st.rerun()
    if theme_cols[1].button(t('theme_light'), use_container_width=True,
                            type="primary" if st.session_state.theme == 'light' else "secondary"):
        st.session_state.theme = 'light'
        st.rerun()
    
    st.markdown("---")
    
    # Statistics
    st.markdown(f"### {t('sidebar_stats')}")
    st.metric(f"🔍 {t('stat_systems')}", len(st.session_state.saved_systems))
    st.metric(f"🌱 {t('stat_habitable')}", st.session_state.habitable_count)
    st.metric(f"⏭️ {t('stat_skipped')}", len(st.session_state.scanned_stars))
    
    st.markdown("---")
    
    # Quick search
    st.markdown(f"### {t('sidebar_search')}")
    search_input = st.text_input("🔍", placeholder="TRAPPIST-1, TOI-700...", label_visibility="collapsed")
    
    if st.button(t('search'), use_container_width=True, type="primary"):
        if search_input:
            with st.spinner(t('loading')):
                result = fetch_nasa_data(search_input)
                if result:
                    star = {k: result[0].get(k) for k in ['st_teff', 'st_rad', 'st_lum', 'st_mass', 'st_spectype', 'st_age', 'st_met']}
                    planets = [process_planet_data(p, star) for p in result]
                    hostname = result[0].get('hostname', search_input)
                    save_system(hostname, star, planets)
                    mark_star_scanned(search_input)
                    load_system(hostname)
                    st.success(f"{t('found')} {len(planets)} {t('planets')}!")
                    st.rerun()
                else:
                    st.warning(t('not_found'))
    
    # Quick buttons
    quick_stars = ["TRAPPIST-1", "TOI-700", "Kepler-442", "Proxima"]
    cols = st.columns(2)
    for i, star_name in enumerate(quick_stars):
        scanned = is_star_scanned(star_name)
        label = f"{'✓ ' if scanned else ''}{star_name}"
        if cols[i % 2].button(label, key=f"q_{star_name}", use_container_width=True, disabled=scanned):
            result = fetch_nasa_data(star_name)
            if result:
                star = {k: result[0].get(k) for k in ['st_teff', 'st_rad', 'st_lum', 'st_mass', 'st_spectype', 'st_age', 'st_met']}
                planets = [process_planet_data(p, star) for p in result]
                hostname = result[0].get('hostname', star_name)
                save_system(hostname, star, planets)
                mark_star_scanned(star_name)
                load_system(hostname)
                st.rerun()
    
    st.markdown("---")
    
    # LM Studio Settings
    st.markdown("### 🧠 AI Settings")
    
    lm_enabled = st.toggle(
        "LM Studio",
        value=st.session_state.get('lm_studio_enabled', False),
        help="Connect to local LLM server"
    )
    st.session_state['lm_studio_enabled'] = lm_enabled
    
    if lm_enabled:
        col1, col2 = st.columns([2, 1])
        with col1:
            ip = st.text_input(
                "IP",
                value=st.session_state.get('lm_studio_ip', 'localhost'),
                label_visibility="collapsed",
                placeholder="localhost"
            )
            st.session_state['lm_studio_ip'] = ip
        with col2:
            port = st.text_input(
                "Port",
                value=st.session_state.get('lm_studio_port', '1234'),
                label_visibility="collapsed",
                placeholder="1234"
            )
            st.session_state['lm_studio_port'] = port
        
        # Test connection
        if st.button("🔌 Test", use_container_width=True):
            try:
                test_url = f"http://{ip}:{port}/v1/models"
                resp = requests.get(test_url, timeout=5)
                if resp.status_code == 200:
                    st.success("✅ Connected!")
                else:
                    st.error(f"❌ Error: {resp.status_code}")
            except:
                st.error("❌ Cannot connect")
        
        st.caption("💡 Start LM Studio → Local Server")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"<h1 style='text-align:center; margin-bottom:5px;'>{t('app_title')}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; opacity:0.6; margin-bottom:25px;'>{t('app_subtitle')}</p>", unsafe_allow_html=True)

# Create tabs (removed Presentation, added NASA Eyes and AI Chat)
tabs = st.tabs([
    t('tab_missions'),
    t('tab_system'),
    t('tab_starmap'),
    t('tab_analysis'),
    t('tab_compare'),
    t('tab_encyclopedia'),
    t('tab_history'),
    "🌌 NASA Eyes",
    "🤖 AI Chat"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 0: MISSIONS
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown(f"### {t('mission_control')}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Catalog selection
        lang = st.session_state.lang
        catalog_options = {k: v['name'][lang] for k, v in CATALOGS.items()}
        selected_catalog = st.selectbox(
            t('select_catalog'),
            options=list(catalog_options.keys()),
            format_func=lambda x: catalog_options[x],
            index=list(catalog_options.keys()).index(st.session_state.selected_catalog)
        )
        st.session_state.selected_catalog = selected_catalog
        
        # Available stars info
        all_stars = CATALOGS[selected_catalog]['stars']
        unscanned = get_unscanned_stars(selected_catalog, skip_scanned=True)
        st.info(f"📊 {len(unscanned)}/{len(all_stars)} {t('stars_available')}")
        
        # Options
        skip_scanned = st.checkbox(t('skip_scanned'), value=True)
        max_targets = len(unscanned) if skip_scanned else len(all_stars)
        target_count = st.slider(t('targets'), 1, max(1, min(10, max_targets)), min(5, max_targets))
        
        # Clear button
        if st.button(t('clear_scanned'), use_container_width=True):
            st.session_state.scanned_stars = set()
            st.rerun()
    
    with col2:
        # Mission button
        can_start = len(unscanned) > 0 if skip_scanned else True
        start_mission = st.button(
            f"🚀 {t('start_mission')}",
            use_container_width=True,
            type="primary",
            disabled=not can_start
        )
        
        # Progress and log placeholders
        progress_area = st.empty()
        log_area = st.empty()
        results_area = st.container()
    
    # Execute mission
    if start_mission:
        stars_to_scan = unscanned[:target_count] if skip_scanned else all_stars[:target_count]
        
        if stars_to_scan:
            results = []
            log_lines = []
            
            with progress_area.container():
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            # Phase 1: Initialize
            status_text.info("🔧 Initializing ATLAS systems...")
            log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🔧 Initializing...")
            log_area.code('\n'.join(log_lines), language=None)
            time.sleep(0.4)
            
            log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Systems online")
            log_area.code('\n'.join(log_lines), language=None)
            progress_bar.progress(0.1)
            time.sleep(0.3)
            
            # Phase 2: Connect
            status_text.info("📡 Connecting to NASA Exoplanet Archive...")
            log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📡 Connecting to NASA API...")
            log_area.code('\n'.join(log_lines), language=None)
            time.sleep(0.4)
            
            log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Connection established")
            log_area.code('\n'.join(log_lines), language=None)
            progress_bar.progress(0.15)
            time.sleep(0.3)
            
            # Phase 3: Scan stars
            for i, star_name in enumerate(stars_to_scan):
                progress = 0.15 + (i + 1) / len(stars_to_scan) * 0.75
                
                status_text.info(f"🔍 Scanning {star_name}...")
                log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Scanning {star_name}...")
                log_area.code('\n'.join(log_lines), language=None)
                time.sleep(0.3)
                
                data = fetch_nasa_data(star_name)
                
                if data:
                    star = {k: data[0].get(k) for k in ['st_teff', 'st_rad', 'st_lum', 'st_mass', 'st_spectype', 'st_age', 'st_met']}
                    planets = [process_planet_data(p, star) for p in data]
                    hostname = data[0].get('hostname', star_name)
                    
                    save_system(hostname, star, planets)
                    mark_star_scanned(star_name)
                    
                    log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {hostname}: {len(planets)} planets found")
                    log_area.code('\n'.join(log_lines), language=None)
                    
                    for p in planets:
                        if p['hab_score'] >= 40:
                            results.append({'planet': p, 'star': star, 'host': hostname})
                            log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}]    ⭐ {p['name']} — Score {p['hab_score']}")
                            log_area.code('\n'.join(log_lines), language=None)
                else:
                    log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ {star_name}: No data")
                    log_area.code('\n'.join(log_lines), language=None)
                
                progress_bar.progress(progress)
                time.sleep(0.2)
            
            # Phase 4: Complete
            progress_bar.progress(1.0)
            status_text.success(f"{t('mission_complete')} {len(results)} {t('candidates_found')}")
            
            log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] ════════════════════════════")
            log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ MISSION COMPLETE")
            log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Systems: {len(stars_to_scan)} | Candidates: {len(results)}")
            log_area.code('\n'.join(log_lines), language=None)
            
            st.session_state.atlas_results = results
            
            # Display results
            if results:
                with results_area:
                    st.markdown(f"### 🏆 {t('slide_top')} Candidates")
                    sorted_results = sorted(results, key=lambda x: x['planet']['hab_score'], reverse=True)[:6]
                    
                    cols = st.columns(min(len(sorted_results), 3))
                    for i, r in enumerate(sorted_results):
                        p = r['planet']
                        with cols[i % 3]:
                            score_color = '#00ff88' if p['hab_score'] >= 70 else '#00d4ff' if p['hab_score'] >= 50 else '#ffbb00'
                            st.markdown(f"""
                            <div style='background: rgba(0,50,80,0.3); border: 2px solid {score_color}; 
                                        border-radius: 16px; padding: 20px; text-align: center; margin: 5px 0;'>
                                <div style='font-size: 2.5rem;'>{p['emoji']}</div>
                                <h4 style='margin: 10px 0; color: white;'>{p['name']}</h4>
                                <div style='font-size: 2.2rem; color: {score_color}; font-weight: bold;'>{p['hab_score']}</div>
                                <div style='opacity: 0.6;'>/100</div>
                                <div style='margin-top: 12px; font-size: 0.9rem; opacity: 0.8;'>
                                    ESI: {p['esi']} • R: {p['radius']:.2f} R⊕<br>
                                    {p['temp']:.0f}K • {'✅ HZ' if p['in_hz'] else '❌ HZ'}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Load best button
                    if st.button(t('load_best'), use_container_width=True):
                        best = sorted_results[0]
                        load_system(best['host'])
                        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: SYSTEM VIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    if 'planets' in st.session_state and st.session_state['planets']:
        planets = st.session_state['planets']
        star = st.session_state.get('star', {})
        sel_idx = st.session_state.get('selected_idx', 0)
        
        hostname = planets[0].get('hostname', '?')
        best = max(planets, key=lambda x: x['hab_score'])
        
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {t('system_view')}: {hostname}")
            st.markdown(f"**{len(planets)}** {t('planets')} • {t('best')}: **{best['name']}** ({best['hab_score']}/100)")
        
        with col2:
            st.markdown(f"""
            <div style='background: rgba(255,200,100,0.1); border: 2px solid rgba(255,200,100,0.3); 
                        border-radius: 12px; padding: 15px; text-align: center;'>
                <div style='font-size: 1.8rem;'>⭐</div>
                <div style='font-weight: bold;'>{star.get('st_spectype', '?')}</div>
                <div style='opacity: 0.7; font-size: 0.9rem;'>{star.get('st_teff', '?')}K</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 3D System visualization
        st.plotly_chart(create_system_3d(planets, star, sel_idx), use_container_width=True)
        
        # Planet selector
        st.markdown(f"### {t('select_planet')}")
        cols = st.columns(min(len(planets), 5))
        
        for i, p in enumerate(planets):
            with cols[i % 5]:
                is_selected = (i == sel_idx)
                score_color = '#00ff88' if p['hab_score'] >= 70 else '#00d4ff' if p['hab_score'] >= 50 else '#ffbb00' if p['hab_score'] >= 30 else '#ff6666'
                
                if st.button(f"{p['emoji']} {p['name']}", key=f"pl_{i}", use_container_width=True,
                            type="primary" if is_selected else "secondary"):
                    st.session_state['selected_idx'] = i
                    st.rerun()
                
                st.markdown(f"""
                <div style='text-align: center; font-size: 0.85rem;'>
                    <span style='color: {score_color}; font-weight: bold;'>{p['hab_score']}</span>/100<br>
                    R: {p['radius']:.2f} • {p['temp']:.0f}K
                </div>
                """, unsafe_allow_html=True)
        
        # Detailed analysis
        st.markdown("---")
        sel_p = planets[sel_idx]
        
        st.markdown(f"### {t('detailed_analysis')}: {sel_p['name']}")
        
        # Type card
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(0,100,180,0.15), rgba(120,0,180,0.1));
                    border: 2px solid rgba(0,212,255,0.3); border-radius: 16px; padding: 20px; margin: 15px 0;'>
            <h3 style='margin: 0 0 10px 0;'>{sel_p['emoji']} {sel_p['type']}</h3>
            <p style='margin: 0; opacity: 0.8;'>{sel_p['type_desc']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Four columns of detailed data
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.markdown(f"#### {t('physical')}")
            st.metric(t('radius'), f"{sel_p['radius']:.3f} R⊕")
            st.metric(t('mass'), f"{sel_p['mass']:.2f} M⊕" if sel_p['mass'] else t('unknown'))
            st.metric(t('density'), f"{sel_p['density']:.2f} ρ⊕" if sel_p['density'] else t('unknown'))
            st.metric(t('gravity'), f"{sel_p['gravity']:.2f} g" if sel_p['gravity'] else t('unknown'))
            st.metric(t('escape_v'), f"{sel_p['escape_v']:.1f} km/s" if sel_p['escape_v'] else t('unknown'))
            st.metric(t('pressure'), f"{sel_p['pressure']:.1f} atm" if sel_p['pressure'] else t('unknown'))
        
        with c2:
            st.markdown(f"#### {t('orbital')}")
            st.metric(t('orbit'), f"{sel_p['orbit_au']:.4f} AU" if sel_p['orbit_au'] else t('unknown'))
            st.metric(t('period'), f"{sel_p['period']:.2f} d" if sel_p['period'] else t('unknown'))
            st.metric(t('year_len'), f"{sel_p['year_len']:.3f} yr" if sel_p['year_len'] else t('unknown'))
            day_str = f"{sel_p['day_len']:.1f} h" if sel_p['day_len'] else "Tidally locked?"
            st.metric("Day", day_str)
            st.metric(t('distance'), f"{sel_p['distance']:.1f} ly" if sel_p['distance'] else t('unknown'))
            st.metric(t('temp'), f"{sel_p['temp']:.0f} K ({sel_p['temp_source']})")
        
        with c3:
            st.markdown(f"#### {t('habitability')}")
            st.metric(t('score'), f"{sel_p['hab_score']}/100")
            st.metric(t('esi'), f"{sel_p['esi']}")
            st.metric(t('in_hz'), t('yes') if sel_p['in_hz'] else t('no'))
            st.metric(t('mag_field'), sel_p['mag_field'])
            st.metric(t('moons'), sel_p['moon_desc'])
        
        with c4:
            st.markdown(f"#### {t('star_params')}")
            st.metric("Type", star.get('st_spectype', t('unknown')))
            st.metric(t('temp'), f"{star.get('st_teff', '?')} K")
            st.metric(t('radius'), f"{star.get('st_rad', '?')} R☉")
            st.metric(t('mass'), f"{star.get('st_mass', '?')} M☉")
            age_str = f"{star.get('st_age')} Gyr" if star.get('st_age') else t('unknown')
            st.metric("Age", age_str)
            hz_range = f"{sel_p['hz_inner']:.2f} - {sel_p['hz_outer']:.2f} AU"
            st.metric("HZ Range", hz_range)
        
        # Atmosphere & Hazards
        st.markdown("---")
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown(f"#### {t('atmosphere')}")
            st.info(f"**Type:** {sel_p['atmo_type']}")
            if sel_p['atmo_comp']:
                st.markdown("**Composition:**")
                for comp in sel_p['atmo_comp']:
                    st.markdown(f"• {comp}")
        
        with c2:
            st.markdown(f"#### {t('hazards')}")
            hazards = predict_hazards(sel_p['temp'], sel_p['gravity'], sel_p['radius'],
                                      sel_p['orbit_au'], star.get('st_teff'), sel_p['period'])
            for h_name, h_desc in hazards:
                if any(x in h_name for x in ['LETHAL', 'CRUSHING', 'CRYOGENIC', 'СМЕРТЕЛЬНЫЙ', 'ДАВЯЩАЯ', 'КРИОГЕННЫЙ', 'ӨЛІМДІ']):
                    st.error(f"**{h_name}**\n\n{h_desc}")
                elif '✅' in h_name:
                    st.success(f"**{h_name}**\n\n{h_desc}")
                else:
                    st.warning(f"**{h_name}**\n\n{h_desc}")
        
        # Biosignatures
        st.markdown(f"#### {t('biosignatures')}")
        life_type, life_score, life_factors = predict_life_potential(
            sel_p['temp'], sel_p['radius'], sel_p['in_hz'], sel_p['esi'], sel_p['atmo_type'])
        
        st.info(life_type)
        st.progress(life_score / 100)
        
        with st.expander("Details"):
            for factor in life_factors:
                st.markdown(f"• {factor}")
        
        # Add to compare
        if st.button(t('add_compare'), use_container_width=True):
            if sel_p['name'] not in st.session_state.compare:
                st.session_state.compare.append(sel_p['name'])
                st.session_state.custom_planets[sel_p['name']] = {
                    'radius': sel_p['radius'],
                    'mass': sel_p['mass'],
                    'temp': sel_p['temp'],
                    'esi': sel_p['esi'],
                    'gravity': sel_p['gravity'],
                    'distance': sel_p['distance'],
                    'emoji': sel_p['emoji']
                }
                st.success(f"✅ {sel_p['name']} added!")
    
    else:
        st.info(t('no_system'))


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: STAR MAP
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown(f"### {t('starmap_title')}")
    st.markdown(f"*{t('starmap_desc')}*")
    
    if st.session_state.saved_systems:
        # Statistics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(f"🔍 {t('stat_systems')}", len(st.session_state.saved_systems))
        
        total_planets = sum(d['planet_count'] for d in st.session_state.saved_systems.values())
        c2.metric(f"🪐 {t('planets')}", total_planets)
        
        distances = [d['distance'] for d in st.session_state.saved_systems.values() if d.get('distance')]
        if distances:
            c3.metric("📏 Nearest", f"{min(distances):.1f} ly")
            c4.metric("📏 Farthest", f"{max(distances):.1f} ly")
        
        # 3D Star Map
        st.plotly_chart(create_stellar_neighborhood_map(), use_container_width=True)
        
        # Legend
        st.markdown("""
        **Legend:** 
        🟢 High habitability (70+) • 
        🔵 Moderate (50-69) • 
        🟡 Low (30-49) • 
        🔴 Minimal (<30)
        """)
        
        # System list
        st.markdown("---")
        st.markdown(f"### {t('saved_systems')}")
        
        sorted_systems = sorted(
            st.session_state.saved_systems.items(),
            key=lambda x: x[1].get('distance') or 9999
        )
        
        for hostname, data in sorted_systems[:10]:
            dist_str = f"{data['distance']:.1f} ly" if data.get('distance') else "?"
            score_color = '#00ff88' if data['best_score'] >= 70 else '#00d4ff' if data['best_score'] >= 50 else '#ffbb00'
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**🌟 {hostname}** — {dist_str} — {data['planet_count']} planets — Best: <span style='color:{score_color}'>{data['best_score']}</span>", unsafe_allow_html=True)
            with col2:
                if st.button(t('load_system'), key=f"map_load_{hostname}"):
                    load_system(hostname)
                    st.rerun()
    else:
        st.info(t('starmap_empty'))


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: AI ANALYSIS (ENHANCED)
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown(f"### {t('analysis_title')}")
    
    all_planets = get_all_planets()
    
    if len(st.session_state.saved_systems) >= 1 and all_planets:
        # Overview metrics row
        st.markdown("#### 📈 Research Overview")
        m1, m2, m3, m4, m5 = st.columns(5)
        
        scores = [p['hab_score'] for p in all_planets]
        m1.metric("🔍 Systems", len(st.session_state.saved_systems))
        m2.metric("🪐 Planets", len(all_planets))
        m3.metric("⭐ Avg Score", f"{sum(scores)/len(scores):.1f}")
        m4.metric("🌱 In HZ", sum(1 for p in all_planets if p['in_hz']))
        m5.metric("🌍 Earth-like", sum(1 for p in all_planets if 0.8 <= p['radius'] <= 1.5))
        
        st.markdown("---")
        
        # Visualizations grid
        st.markdown("#### 📊 Data Visualizations")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            st.markdown("**🌡️ Temperature vs Radius**")
            st.caption("Green zone = Earth-like conditions")
            st.plotly_chart(create_temp_vs_radius_scatter(), use_container_width=True)
        
        with viz_col2:
            st.markdown("**🪐 Planet Types Distribution**")
            st.plotly_chart(create_planet_types_pie(), use_container_width=True)
        
        viz_col3, viz_col4 = st.columns(2)
        
        with viz_col3:
            st.markdown("**📊 Habitability Score Distribution**")
            st.plotly_chart(create_score_distribution_chart(), use_container_width=True)
        
        with viz_col4:
            st.markdown("**📏 Distance Distribution**")
            st.plotly_chart(create_distance_histogram(), use_container_width=True)
        
        st.markdown("---")
        
        # Generate analysis button
        st.markdown("#### 🧠 AI Analysis")
        if st.button(t('generate_analysis'), use_container_width=True, type="primary"):
            st.session_state.recommendations = generate_recommendations()
            st.session_state.hypotheses = generate_hypotheses()
            st.rerun()
        
        # Display in two columns
        rec_col, hyp_col = st.columns(2)
        
        with rec_col:
            if st.session_state.recommendations:
                st.markdown(f"##### {t('recommendations')}")
                for i, rec in enumerate(st.session_state.recommendations[:3]):
                    with st.expander(rec['title'], expanded=(i == 0)):
                        st.markdown(f"**{rec['reason']}**")
                        st.info(f"💡 {rec['action']}")
        
        with hyp_col:
            if st.session_state.hypotheses:
                st.markdown(f"##### {t('hypotheses')}")
                for i, hyp in enumerate(st.session_state.hypotheses[:3]):
                    with st.expander(hyp['title'], expanded=(i == 0)):
                        st.markdown(f"**{hyp['hypothesis']}**")
                        st.caption(hyp['analysis'][:200] + "...")
        
        # Current system analysis
        if st.session_state.get('current_system'):
            st.markdown("---")
            hostname = st.session_state['current_system']
            analysis = generate_system_analysis(hostname)
            
            if analysis:
                st.markdown(f"#### 🔬 Current System: {hostname}")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(analysis['system_type'])
                    st.markdown(analysis['star_analysis'])
                with col2:
                    st.markdown(analysis['hz_analysis'])
                    st.markdown(analysis['best_candidate'])
                st.info(analysis['recommendation'])
    
    else:
        st.info(t('no_data_analysis'))
# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: COMPARE (FIXED TABLE with HTML styling)
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown(f"### {t('compare_title')}")
    
    # Get available planets
    available_planets = {}
    
    # Add known reference planets
    for name, data in KNOWN_PLANETS.items():
        available_planets[name] = data
    
    # Add custom discovered planets
    for name, data in st.session_state.custom_planets.items():
        available_planets[name] = data
    
    if len(available_planets) >= 2:
        # Planet selector
        st.markdown(f"**{t('select_planets')}**")
        
        selected_planets = st.multiselect(
            "Planets",
            options=list(available_planets.keys()),
            default=st.session_state.compare[:4] if st.session_state.compare else list(available_planets.keys())[:3],
            max_selections=6,
            label_visibility="collapsed"
        )
        
        if st.button(t('clear_selection')):
            st.session_state.compare = []
            st.rerun()
        
        if selected_planets and len(selected_planets) >= 2:
            selected_data = {name: available_planets[name] for name in selected_planets}
            
            # Charts
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown(f"#### {t('radar_chart')}")
                st.plotly_chart(create_radar_chart(selected_data), use_container_width=True)
            
            with c2:
                st.markdown(f"#### {t('bar_chart')}")
                st.plotly_chart(create_bar_comparison(selected_data), use_container_width=True)
            
            # FIXED Comparison table using HTML with explicit colors
            st.markdown(f"#### {t('comparison_table')}")
            
            # Build HTML table with inline styles
            html = """
            <style>
            .atlas-table {
                width: 100%;
                border-collapse: collapse;
                margin: 16px 0;
                font-family: 'Inter', sans-serif;
            }
            .atlas-table th {
                background: #1e3a5f !important;
                color: #ffffff !important;
                padding: 14px 12px;
                text-align: left;
                font-weight: 600;
                border-bottom: 2px solid #00d4ff;
            }
            .atlas-table td {
                background: #0d1b2a !important;
                color: #e0e0e0 !important;
                padding: 12px;
                border-bottom: 1px solid #1e3a5f;
            }
            .atlas-table tr:hover td {
                background: #162d4a !important;
            }
            .atlas-table .planet-name {
                color: #00d4ff !important;
                font-weight: 600;
            }
            </style>
            <table class="atlas-table">
            <thead>
                <tr>
                    <th>🪐 Planet</th>
                    <th>Radius (R⊕)</th>
                    <th>Mass (M⊕)</th>
                    <th>Temp (K)</th>
                    <th>ESI</th>
                    <th>Gravity (g)</th>
                    <th>Distance (ly)</th>
                </tr>
            </thead>
            <tbody>
            """
            
            for name in selected_planets:
                p = available_planets[name]
                emoji = p.get('emoji', '🪐')
                radius = f"{p.get('radius', 0):.2f}" if isinstance(p.get('radius'), (int, float)) else '?'
                mass = f"{p.get('mass', 0):.2f}" if isinstance(p.get('mass'), (int, float)) else '?'
                temp = f"{p.get('temp', 0):.0f}" if isinstance(p.get('temp'), (int, float)) else '?'
                esi = f"{p.get('esi', 0):.3f}" if isinstance(p.get('esi'), (int, float)) else '?'
                gravity = f"{p.get('gravity', 0):.2f}" if isinstance(p.get('gravity'), (int, float)) else '?'
                distance = f"{p.get('distance', 0):.1f}" if isinstance(p.get('distance'), (int, float)) else '?'
                
                html += f"""
                <tr>
                    <td class="planet-name">{emoji} {name}</td>
                    <td>{radius}</td>
                    <td>{mass}</td>
                    <td>{temp}</td>
                    <td>{esi}</td>
                    <td>{gravity}</td>
                    <td>{distance}</td>
                </tr>
                """
            
            html += """
            </tbody>
            </table>
            """
            
            st.markdown(html, unsafe_allow_html=True)
        
        elif selected_planets:
            st.info("Select at least 2 planets to compare")
    
    else:
        st.info("Explore more systems to unlock comparison features!")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5: ENCYCLOPEDIA
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown(f"### {t('encyclopedia_title')}")
    
    lang = st.session_state.lang
    
    # Topic selector
    topic_options = {
        'star_types': ENCYCLOPEDIA['star_types']['title'][lang],
        'planet_types': ENCYCLOPEDIA['planet_types']['title'][lang],
        'habitability': ENCYCLOPEDIA['habitability']['title'][lang],
        'detection': ENCYCLOPEDIA['detection']['title'][lang],
        'formulas': ENCYCLOPEDIA['formulas']['title'][lang]
    }
    
    cols = st.columns(5)
    selected_topic = st.session_state.get('encyclopedia_topic', 'star_types')
    
    for i, (key, title) in enumerate(topic_options.items()):
        with cols[i]:
            if st.button(title, key=f"enc_{key}", use_container_width=True,
                        type="primary" if selected_topic == key else "secondary"):
                st.session_state.encyclopedia_topic = key
                st.rerun()
    
    st.markdown("---")
    
    # Display content
    topic_data = ENCYCLOPEDIA.get(selected_topic, ENCYCLOPEDIA['star_types'])
    st.markdown(topic_data['content'][lang])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6: HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown(f"### {t('history_title')}")
    
    if st.session_state.saved_systems:
        # Sort by timestamp (newest first)
        sorted_systems = sorted(
            st.session_state.saved_systems.items(),
            key=lambda x: x[1].get('timestamp', ''),
            reverse=True
        )
        
        # Clear button
        if st.button(t('clear_history'), type="secondary"):
            st.session_state.saved_systems = {}
            st.session_state.scanned_stars = set()
            st.session_state.scan_count = 0
            st.session_state.habitable_count = 0
            st.rerun()
        
        st.markdown("---")
        
        # Display systems
        for hostname, data in sorted_systems:
            score_color = '#00ff88' if data['best_score'] >= 70 else '#00d4ff' if data['best_score'] >= 50 else '#ffbb00' if data['best_score'] >= 30 else '#ff6666'
            
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"**🌟 {hostname}**")
                st.caption(f"📅 {data.get('timestamp', '?')}")
            
            with col2:
                st.markdown(f"🪐 **{data['planet_count']}** planets")
            
            with col3:
                st.markdown(f"<span style='color:{score_color}; font-weight:bold;'>⭐ {data['best_score']}/100</span>", unsafe_allow_html=True)
            
            with col4:
                if st.button(t('load_system'), key=f"hist_{hostname}"):
                    load_system(hostname)
                    st.rerun()
            
            st.markdown("---")
    
    else:
        st.info(t('history_empty'))


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7: NASA EYES (replaces Travel)
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[7]:
    st.markdown("### 🌌 NASA Eyes on the Solar System")
    
    lang = st.session_state.lang
    desc = {
        'ru': "Интерактивная 3D визуализация Солнечной системы от NASA. Исследуйте планеты, спутники и экзопланеты!",
        'en': "Interactive 3D visualization of the Solar System by NASA. Explore planets, moons, and exoplanets!",
        'kz': "NASA-ның Күн жүйесінің интерактивті 3D визуализациясы. Планеталарды, серіктерді және экзопланеталарды зерттеңіз!"
    }
    st.markdown(f"*{desc[lang]}*")
    
    # Quick navigation buttons
    st.markdown("**Quick Navigation:**")
    nav_cols = st.columns(6)
    
    destinations = [
        ("🏠 Home", "home"),
        ("🌍 Earth", "earth"),
        ("🔴 Mars", "mars"),
        ("🪐 Jupiter", "jupiter"),
        ("💫 Saturn", "saturn"),
        ("🌌 Exoplanets", "exoplanets")
    ]
    
    current_dest = st.session_state.get('nasa_eyes_dest', 'home')
    
    for i, (label, dest) in enumerate(destinations):
        with nav_cols[i]:
            if st.button(label, key=f"nasa_{dest}", use_container_width=True,
                        type="primary" if current_dest == dest else "secondary"):
                st.session_state.nasa_eyes_dest = dest
                st.rerun()
    
    # Build iframe URL
    base_url = "https://eyes.nasa.gov/apps/solar-system/"
    params = "?logo=false&shareButton=false&collapseSettingsOptions=true"
    
    if current_dest == 'exoplanets':
        iframe_url = f"https://eyes.nasa.gov/apps/exo/{params}"
    else:
        iframe_url = f"{base_url}{params}#/{current_dest}"
    
    # Embed iframe using streamlit components
    import streamlit.components.v1 as components
    
    components.iframe(iframe_url, height=600, scrolling=False)
    
    # Info about controls
    with st.expander("🎮 Controls / Управление"):
        controls = {
            'ru': """
            - **Мышь**: Вращение камеры
            - **Колёсико**: Приближение/отдаление
            - **Клик на объект**: Информация
            - **Двойной клик**: Фокус на объекте
            """,
            'en': """
            - **Mouse**: Rotate camera
            - **Scroll**: Zoom in/out
            - **Click object**: Show info
            - **Double-click**: Focus on object
            """,
            'kz': """
            - **Тінтуір**: Камераны айналдыру
            - **Айналдыру**: Үлкейту/кішірейту
            - **Объектіге басу**: Ақпарат көрсету
            """
        }
        st.markdown(controls[lang])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 8: AI CHAT (with LM Studio support)
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[8]:
    st.markdown("### 🤖 AI Assistant")
    
    lang = st.session_state.lang
    
    # Show connection status
    if st.session_state.get('lm_studio_enabled', False):
        st.success("🧠 LM Studio connected — Full AI mode")
    else:
        st.info("⚡ Local mode — Enable LM Studio in sidebar for smarter responses")
    
    subtitle = {
        'ru': "Задайте вопрос об экзопланетах, ваших открытиях или астрофизике",
        'en': "Ask about exoplanets, your discoveries, or astrophysics",
        'kz': "Экзопланеталар, ашылымдарыңыз немесе астрофизика туралы сұраңыз"
    }
    st.markdown(f"*{subtitle[lang]}*")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat display area
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.chat_history[-10:]:  # Show last 10 messages
            if msg['role'] == 'user':
                st.markdown(f"""
                <div style='background: rgba(0,100,200,0.2); border-radius: 12px; padding: 12px 16px; 
                            margin: 8px 0; margin-left: 20%; border-left: 3px solid #00d4ff;'>
                    <strong>👤 You:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                source_badge = msg.get('source', '')
                st.markdown(f"""
                <div style='background: rgba(0,150,100,0.15); border-radius: 12px; padding: 12px 16px; 
                            margin: 8px 0; margin-right: 10%; border-left: 3px solid #00ff88;'>
                    <strong>🤖 ATLAS {source_badge}:</strong>
                    
{msg['content']}
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick question buttons
    quick_q = {
        'ru': ["📊 Статистика", "🌍 Что такое ESI?", "🌱 Зона обитаемости", "🔴 TRAPPIST-1", "🏆 Лучшая находка"],
        'en': ["📊 Statistics", "🌍 What is ESI?", "🌱 Habitable zone", "🔴 TRAPPIST-1", "🏆 Best find"],
        'kz': ["📊 Статистика", "🌍 ESI дегеніміз?", "🌱 Мекендеуге жарамды аймақ", "🔴 TRAPPIST-1", "🏆 Үздік табыс"]
    }
    
    st.markdown("**Quick questions:**")
    q_cols = st.columns(5)
    
    for i, q in enumerate(quick_q[lang]):
        with q_cols[i]:
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state.chat_history.append({'role': 'user', 'content': q})
                response, source = get_smart_response(q)
                st.session_state.chat_history.append({'role': 'assistant', 'content': response, 'source': source})
                st.rerun()
    
    # Text input
    user_input = st.text_input(
        "Message",
        placeholder="Ask me anything about exoplanets...",
        label_visibility="collapsed",
        key="chat_input"
    )
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        if st.button("📤 Send", use_container_width=True, type="primary"):
            if user_input:
                st.session_state.chat_history.append({'role': 'user', 'content': user_input})
                with st.spinner("🧠 Thinking..."):
                    response, source = get_smart_response(user_input)
                st.session_state.chat_history.append({'role': 'assistant', 'content': response, 'source': source})
                st.rerun()
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; opacity: 0.6;'>
    <p>🛰️ <b>ATLAS v21</b> — Autonomous Terrestrial Life Analysis System</p>
    <p>Diploma Project • 2024-2025 • Powered by NASA Exoplanet Archive</p>
    <p style='font-size: 0.8rem;'>Data source: NASA Exoplanet Archive TAP Service</p>
</div>
""", unsafe_allow_html=True)