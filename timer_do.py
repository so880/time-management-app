import streamlit as st
import time
import pandas as pd
import random
from datetime import datetime, date
import json
import os
import streamlit.components.v1 as components

# === 1. 初期設定とデータ保存 ===
SETTINGS_FILE = "settings.json"
LOG_FILE = "activity_log.csv"

# 初期設定
DEFAULT_SETTINGS = {
    "toeic_date": "2026-05-24",
    "intern_date": "2026-06-01",
    "daily_hours_toeic": 3,
    "daily_hours_intern": 2,
    "bg_url": "https://images.unsplash.com/photo-1497935586351-b67a49e012bf?q=80&w=2000&auto=format&fit=crop", 
    "study_list": [
        "Santa Part7長文の写経", "英語の記事の写経", "Gemini提案英文の写経",
        "プログラミング(paiza)", "洋楽の本気カラオケ(英語発音)", 
        "Santa Part3・4のオーバーラッピング", "海外車レビュー記事の音読・写経", 
        "Santa 単語", "Geminiと面接練習"
    ],
    "focus_study_list": ["大学の履修について考える"],
    "refresh_list": [
        "料理探し", "読書", "仮眠", "腕立て30回", "腹筋30回", 
        "ダンベル30回", "洋楽カラオケ", "机の掃除", "床の片づけ", 
        "掃除機掛け", "スト6 コンボ練習"
    ]
}

def load_settings():
    s = DEFAULT_SETTINGS.copy()
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            s.update(json.load(f))
    return s

def save_settings(s):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=4)

def load_logs():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE).to_dict(orient="records")
    return []

if 'settings' not in st.session_state: st.session_state.settings = load_settings()
if 'logs' not in st.session_state: st.session_state.logs = load_logs()
if 'page' not in st.session_state: st.session_state.page = 'dashboard'
if 'last_was_refresh' not in st.session_state: st.session_state.last_was_refresh = False
if 'current_task' not in st.session_state: st.session_state.current_task = None
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'rolled_options' not in st.session_state: st.session_state.rolled_options = None
if 'mock_exam_done' not in st.session_state: st.session_state.mock_exam_done = False
if 'compact_mode' not in st.session_state: st.session_state.compact_mode = False

if 'study_time_total' not in st.session_state:
    today_str = datetime.now().strftime("%Y-%m-%d")
    s_tot, r_tot = 0, 0
    for log in st.session_state.logs:
        if str(log["日付"]).startswith(today_str):
            if "勉強" in log["カテゴリ"]: s_tot += int(log["経過時間(分)"])
            elif "気分転換" in log["カテゴリ"]: r_tot += int(log["経過時間(分)"])
    st.session_state.study_time_total = s_tot
    st.session_state.refresh_time_total = r_tot

def log_activity(task_name, category, duration, bgm_used, note=""):
    entry = {
        "日付": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "カテゴリ": category, "内容": task_name, "BGM": bgm_used,
        "経過時間(分)": duration, "メモ": note
    }
    st.session_state.logs.append(entry)
    df = pd.DataFrame([entry])
    if not os.path.exists(LOG_FILE): df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")
    else: df.to_csv(LOG_FILE, mode='a', header=False, index=False, encoding="utf-8-sig")

# === 2. 背景とUI/UXデザイン ===
BG_URL = st.session_state.settings.get("bg_url", DEFAULT_SETTINGS["bg_url"])

components.html(f"""
<script>
    const setBg = () => {{
        const app = window.parent.document.querySelector('.stApp');
        if(app) {{
            app.style.backgroundImage = "url('{BG_URL}')";
            app.style.backgroundSize = "cover";
            app.style.backgroundPosition = "center";
            app.style.backgroundRepeat = "no-repeat";
            app.style.backgroundAttachment = "fixed";
            app.style.backgroundColor = "transparent";
        }}
    }};
    window.parent.addEventListener('load', setBg);
    setInterval(setBg, 1000);
    setBg();
</script>
""", height=0)

st.markdown("""
<style>
    [data-testid="stHeader"] { background-color: transparent !important; }
    
    .block-container {
        background: rgba(14, 17, 23, 0.75) !important;
        border-radius: 15px; padding: 2rem !important; margin-top: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        transition: all 0.3s ease;
    }

    [data-testid="stSidebar"] {
        background: rgba(14, 17, 23, 0.65) !important;
        backdrop-filter: blur(15px); border-right: 1px solid rgba(255,255,255,0.1);
    }

    * { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }

    div[data-testid="metric-container"] {
        background-color: rgba(30, 30, 30, 0.7); border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50;
    }
    
    .stButton>button {
        border-radius: 8px; border: 2px solid #4CAF50; background-color: rgba(0,0,0,0.5);
        color: #4CAF50; font-weight: bold; font-size: 1.2rem; backdrop-filter: blur(5px);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { background-color: #4CAF50; color: #000; box-shadow: 0 0 15px rgba(76,175,80,0.8); }
    
    button[kind="primary"] { border: 2px solid #ff4b4b !important; color: #ff4b4b !important; }
    button[kind="primary"]:hover { background-color: #ff4b4b !important; color: #fff !important; box-shadow: 0 0 15px rgba(255,75,75,0.8) !important; }

    @keyframes pulse { 0% {transform: scale(1); text-shadow: 0 0 10px rgba(255,235,59,0.5);} 50% {transform: scale(1.03); text-shadow: 0 0 25px rgba(255,235,59,1);} 100% {transform: scale(1); text-shadow: 0 0 10px rgba(255,235,59,0.5);} }
    
    .milestone-card {
        background: linear-gradient(135deg, rgba(30,30,30,0.8) 0%, rgba(42,42,42,0.8) 100%);
        border: 1px solid rgba(255,255,255,0.1); border-left: 6px solid #ffeb3b;
        padding: 20px; border-radius: 12px; text-align: center; margin-top: 10px;
    }
    .glowing-hours { animation: pulse 2s infinite; color: #ffeb3b; font-size: 3rem; font-weight: bold; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

if st.session_state.page == 'active' and st.session_state.compact_mode:
    st.markdown("""
    <style>
        .block-container {
            background: transparent !important;
            box-shadow: none !important;
            border: none !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            padding-top: 0rem !important;
            padding-left: 1rem !important;
        }
        .stButton>button {
            padding: 4px 10px !important;
            font-size: 1rem !important;
            width: auto !important;
            background-color: rgba(0,0,0,0.6) !important;
            color: #fff !important;
            border-color: rgba(255,255,255,0.2) !important;
        }
    </style>
    """, unsafe_allow_html=True)


# === 3. YouTubeプレイヤー ===
BGM_PLAYER_HTML = """
<div style="background: rgba(0,0,0,0.4); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); color: white;">
    <h4 style="margin-top: 0; text-align: center; color: #eee;">🎧 環境音コントロール</h4>
    <div style="display: flex; flex-direction: column; gap: 8px;">
        <button onclick="playVid('cafe')" style="padding:10px; border-radius:5px; background:rgba(139,69,19,0.3); color:white; border:1px solid #8B4513; cursor:pointer;">☕ カフェ</button>
        <button onclick="playVid('chat')" style="padding:10px; border-radius:5px; background:rgba(210,105,30,0.3); color:white; border:1px solid #D2691E; cursor:pointer;">🗣️ 雑踏</button>
        <button onclick="playVid('relax')" style="padding:10px; border-radius:5px; background:rgba(70,130,180,0.3); color:white; border:1px solid #4682B4; cursor:pointer;">🐋 波と鯨</button>
        <button onclick="stopVid()" style="padding:10px; border-radius:5px; background:rgba(255,75,75,0.2); color:white; border:1px solid #ff4b4b; cursor:pointer;">🔇 無音</button>
    </div>
    <div id="ytplayer" style="display:none;"></div>
    <script>
        var tag = document.createElement('script'); tag.src = "https://www.youtube.com/iframe_api";
        var firstScriptTag = document.getElementsByTagName('script')[0]; firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
        var player;
        function onYouTubeIframeAPIReady() { player = new YT.Player('ytplayer', { height: '0', width: '0', playerVars: { 'autoplay': 0, 'controls': 0 } }); }
        const vids = { 'cafe': 'e_04ZrNroTo', 'chat': 'bZ2XhA_kXYQ', 'relax': 'vPhg6sc1Mk4' };
        function playVid(t) { if(player) { player.loadPlaylist({playlist:[vids[t]], index:0}); player.setLoop(true); } }
        function stopVid() { if(player) player.stopVideo(); }
    </script>
</div>
"""

# === ★復活: スト6 コンボ練習アプリ (フル実装) ===
SF6_HTML_CODE = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<style>
  body { background-color: rgba(18,18,18,0.9); color: #fff; font-family: 'Segoe UI', sans-serif; padding: 10px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; margin: 0; border-radius: 10px;}
  #status { color: #ffeb3b; margin-bottom: 10px; font-size: 1.2em; font-family: monospace; }
  .combo-panel { background-color: rgba(30,30,30,0.8); border: 2px solid #4caf50; border-radius: 8px; padding: 15px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 10px; }
  .combo-header { display: flex; justify-content: space-between; align-items: center; }
  .combo-header select { background: #333; color: white; border: 1px solid #555; padding: 5px 10px; border-radius: 4px; font-size: 1em; }
  .combo-progress { font-size: 1.4em; font-weight: bold; text-align: center; padding: 10px; background: #111; border-radius: 6px; }
  .step { color: #555; transition: all 0.2s; }
  .step.completed { color: #4caf50; }
  .step.current { color: #ffeb3b; text-shadow: 0 0 8px rgba(255,235,59,0.5); }
  .step-arrow { color: #444; font-size: 0.8em; margin: 0 10px; }
  .container { display: flex; flex: 1; gap: 20px; overflow: hidden; }
  .icon-svg { width: 22px; height: 22px; display: inline-block; vertical-align: middle; filter: drop-shadow(0 2px 2px rgba(0,0,0,0.5)); }
  .icon-arrow { fill: #eee; }
  .icon-neutral { fill: #555; }
  .btn-icon { width: 22px; height: 22px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
  .btn-p { background: linear-gradient(135deg, #f44336, #b71c1c); color: white; border: 2px solid #ffcdd2;}
  .btn-k { background: linear-gradient(135deg, #2196f3, #0d47a1); color: white; border: 2px solid #bbdefb;}
  .history-panel { width: 220px; background-color: rgba(30,30,30,0.8); border: 2px solid #333; border-radius: 8px; padding: 10px; overflow-y: hidden; display: flex; flex-direction: column; }
  .history-panel h3 { margin: 0 0 10px 0; font-size: 0.9em; color: #888; text-align: center; border-bottom: 1px solid #333; padding-bottom: 5px; }
  #history-list { display: flex; flex-direction: column; gap: 4px; }
  .history-item { display: flex; align-items: center; justify-content: space-between; background-color: #2a2a2a; padding: 6px 12px; border-radius: 6px; border-left: 4px solid #444; }
  .history-item.neutral-item { background-color: #1a1a1a; border-left-color: #222; }
  .history-item.punch-item { border-left-color: #f44336; }
  .history-item.kick-item { border-left-color: #2196f3; }
  .icon-container { display: flex; align-items: center; justify-content: center; width: 30px; }
  .frame-text { font-family: monospace; font-size: 1.1em; color: #bbb; width: 50px; text-align: right; }
  .log-panel { flex: 1; background-color: rgba(30,30,30,0.8); border: 2px solid #333; border-radius: 8px; padding: 15px; overflow-y: auto; }
  .log-panel h3 { margin: 0 0 15px 0; font-size: 1em; color: #888; border-bottom: 1px solid #333; padding-bottom: 5px;}
  .success { margin-bottom: 12px; padding: 12px; border-left: 6px solid #4caf50; background: linear-gradient(90deg, rgba(76, 175, 80, 0.15) 0%, rgba(30, 30, 30, 0) 100%); animation: fadein 0.3s; border-radius: 4px;}
  .sa-success { border-left-color: #ff9800; background: linear-gradient(90deg, rgba(255, 152, 0, 0.15) 0%, rgba(30, 30, 30, 0) 100%); }
  .special-success { border-left-color: #2196f3; background: linear-gradient(90deg, rgba(33, 150, 243, 0.15) 0%, rgba(30, 30, 30, 0) 100%); }
  .combo-success-log { border-left: 6px solid #e91e63; background: linear-gradient(90deg, rgba(233, 30, 99, 0.2) 0%, rgba(30, 30, 30, 0) 100%); }
  .eval-excellent { color: #ffeb3b; font-weight: bold; }
  .eval-good { color: #4caf50; font-weight: bold; }
  .eval-slow { color: #9e9e9e; font-weight: bold; }
  .details-box { font-size: 1em; margin-top: 10px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px; display: flex; flex-wrap: wrap; align-items: center; gap: 4px;}
  .warning-text { color: #ff9800; font-size: 0.9em; margin-top: 6px; display: block; border-left: 3px solid #ff9800; padding-left: 8px;}
  .danger-text { color: #f44336; font-size: 0.9em; margin-top: 6px; display: block; border-left: 3px solid #f44336; padding-left: 8px; font-weight: bold;}
  .frame-badge { background: #333; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.9em; margin-left: 2px; margin-right: 6px;}
  .fast-input { color: #4caf50; border: 1px solid #4caf50; }
  .slow-input { color: #ff5252; border: 1px solid #ff5252; background: rgba(244, 67, 54, 0.1); }
  .combo-streak { display: inline-block; background-color: #ff5722; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.85em; margin-left: 10px; font-weight: bold;}
  @keyframes fadein { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
</style>
</head>
<body>
  <div id="status">キーボード受付中 / コントローラー未接続</div>
  <div class="combo-panel">
    <div class="combo-header">
      <span style="font-weight: bold; color: #4caf50;">🎯 コンボ練習モード</span>
      <select id="combo-selector">
        <option value="combo1">基本キャンセル: しゃがみK → 波動拳</option>
        <option value="combo2">昇竜キャンセル: 立ちP → 昇竜拳 → 真空波動拳</option>
        <option value="combo3">竜巻コンボ: しゃがみP → 竜巻旋風脚</option>
      </select>
    </div>
    <div id="combo-progress" class="combo-progress"></div>
  </div>
  <div class="container">
    <div class="history-panel"><h3>INPUT</h3><div id="history-list"></div></div>
    <div class="log-panel"><h3>COMMAND ANALYZER</h3><div id="log"></div></div>
  </div>
<script>
  const statusElement = document.getElementById('status');
  const logElement = document.getElementById('log');
  const historyListElement = document.getElementById('history-list');
  const comboSelector = document.getElementById('combo-selector');
  const comboProgressElement = document.getElementById('combo-progress');
  
  let inputBuffer = [];
  const BUFFER_TIME_LIMIT = 1500;
  const FRAME_MS = 1000 / 60;
  const MAX_VISUAL_HISTORY = 20;

  let prevDir = 5; let prevPunch = false; let prevKick = false; let currentVisualDir = null; 
  let streakCount = 0; let lastSuccessfulCommand = "";

  const COMBO_RECIPES = {
    "combo1": { name: "しゃがみKキャンセル波動", sequence: ["しゃがみK", "波動拳"] },
    "combo2": { name: "昇竜SA3キャンセル", sequence: ["立ちP", "昇竜拳", "真空波動拳"] },
    "combo3": { name: "小足竜巻", sequence: ["しゃがみP", "竜巻旋風脚"] }
  };
  let activeComboId = comboSelector.value; let comboStep = 0; let lastMoveTime = 0;

  comboSelector.addEventListener('change', (e) => { activeComboId = e.target.value; comboStep = 0; renderComboUI(); });

  const baseArrowSVG = `<svg class="icon-svg icon-arrow" viewBox="0 0 24 24"><path d="M12 2L19 10H14V22H10V10H5L12 2Z"/></svg>`;
  const neutralSVG = `<svg class="icon-svg icon-neutral" viewBox="0 0 24 24"><circle cx="12" cy="12" r="6"/></svg>`;

  const dirData = {
    1: { type: 'arrow', rot: 225 }, 2: { type: 'arrow', rot: 180 }, 3: { type: 'arrow', rot: 135 },
    4: { type: 'arrow', rot: 270 }, 5: { type: 'neutral', rot: 0 }, 6: { type: 'arrow', rot: 90 },
    7: { type: 'arrow', rot: 315 }, 8: { type: 'arrow', rot: 0 }, 9: { type: 'arrow', rot: 45 }
  };

  function getIconHtml(val) {
    if (val === 'P') return `<div class="btn-icon btn-p">P</div>`;
    if (val === 'K') return `<div class="btn-icon btn-k">K</div>`;
    const d = dirData[val];
    if (!d) return '';
    if (d.type === 'neutral') return neutralSVG;
    return `<div style="transform: rotate(${d.rot}deg); display: inline-flex;">${baseArrowSVG}</div>`;
  }

  const keys = { ArrowUp: false, ArrowDown: false, ArrowLeft: false, ArrowRight: false, z: false, x: false };
  window.addEventListener('keydown', e => { if (keys.hasOwnProperty(e.key)) { keys[e.key] = true; e.preventDefault(); } });
  window.addEventListener('keyup', e => { if (keys.hasOwnProperty(e.key)) { keys[e.key] = false; e.preventDefault(); } });

  function gameLoop() { pollInput(); requestAnimationFrame(gameLoop); }

  function pollInput() {
    let x = 0, y = 0; let isPunch = keys.z; let isKick = keys.x;

    if (keys.ArrowRight) x = 1; else if (keys.ArrowLeft) x = -1;
    if (keys.ArrowDown) y = 1; else if (keys.ArrowUp) y = -1;

    const gamepads = navigator.getGamepads(); const pad = gamepads[0];
    if (pad) {
      statusElement.textContent = `🎮 接続中: ${pad.id}`; statusElement.style.color = '#4caf50';
      if (pad.axes[0] > 0.5) x = 1; else if (pad.axes[0] < -0.5) x = -1;
      if (pad.axes[1] > 0.5) y = 1; else if (pad.axes[1] < -0.5) y = -1;
      if (pad.buttons[15]?.pressed) x = 1; else if (pad.buttons[14]?.pressed) x = -1;
      if (pad.buttons[13]?.pressed) y = 1; else if (pad.buttons[12]?.pressed) y = -1;
      if (pad.axes.length > 9) {
        const pov = pad.axes[9];
        if (pov > -1.1 && pov < 1.1) {
          const angle = Math.round((pov + 1) * 3.5);
          if (angle === 0 || angle === 1 || angle === 7) y = -1; 
          if (angle === 3 || angle === 4 || angle === 5) y = 1;  
          if (angle === 1 || angle === 2 || angle === 3) x = 1;  
          if (angle === 5 || angle === 6 || angle === 7) x = -1; 
        }
      }
      if (pad.buttons[0]?.pressed || pad.buttons[2]?.pressed || pad.buttons[3]?.pressed) isPunch = true;
      if (pad.buttons[1]?.pressed || pad.buttons[4]?.pressed || pad.buttons[5]?.pressed) isKick = true;
    }

    let currentDir = 5;
    if (y === -1) { if (x === -1) currentDir = 7; else if (x === 0) currentDir = 8; else if (x === 1) currentDir = 9; } 
    else if (y === 1) { if (x === -1) currentDir = 1; else if (x === 0) currentDir = 2; else if (x === 1) currentDir = 3; } 
    else { if (x === -1) currentDir = 4; else if (x === 0) currentDir = 5; else if (x === 1) currentDir = 6; }

    const now = performance.now();

    if (currentDir !== prevDir) {
      if (currentVisualDir) currentVisualDir.frameElement.textContent = `${Math.max(1, Math.round((now - currentVisualDir.startTime) / FRAME_MS))}F`;
      inputBuffer.push({ type: 'dir', val: currentDir, time: now });
      currentVisualDir = addVisualHistory(getIconHtml(currentDir), currentDir === 5 ? 'neutral-item' : '');
    } else if (currentVisualDir) {
      currentVisualDir.frameElement.textContent = `${Math.max(1, Math.round((now - currentVisualDir.startTime) / FRAME_MS))}F`;
    }
    
    if (isPunch && !prevPunch) { inputBuffer.push({ type: 'atk', val: 'P', time: now }); addVisualHistory(getIconHtml('P'), 'punch-item'); checkAllCommands('P', currentDir); }
    if (isKick && !prevKick) { inputBuffer.push({ type: 'atk', val: 'K', time: now }); addVisualHistory(getIconHtml('K'), 'kick-item'); checkAllCommands('K', currentDir); }

    inputBuffer = inputBuffer.filter(input => (now - input.time) < BUFFER_TIME_LIMIT);
    prevDir = currentDir; prevPunch = isPunch; prevKick = isKick;
  }

  function addVisualHistory(iconHtml, className) {
    const div = document.createElement('div'); div.className = `history-item ${className}`;
    div.innerHTML = `<div class="icon-container">${iconHtml}</div><span class="frame-text">1F</span>`;
    historyListElement.prepend(div);
    if (historyListElement.children.length > MAX_VISUAL_HISTORY) historyListElement.removeChild(historyListElement.lastChild);
    return { frameElement: div.querySelector('.frame-text'), startTime: performance.now() };
  }

  function checkAllCommands(atk, currentDir) {
    const b = [...inputBuffer].reverse(); if (b.length === 0) return;
    let match; let detectedMove = null;

    if ((match = matchSequence(b, [atk, 6, 3, 2, 6, 3, 2]))) { detectedMove = "真空波動拳"; showResult(`真空波動拳`, `(236x2+${atk})`, 'sa-success', b, match); }
    else if ((match = matchSequence(b, [atk, 4, 1, 2, 4, 1, 2]))) { detectedMove = "真空竜巻旋風脚"; showResult(`真空竜巻旋風脚`, `(214x2+${atk})`, 'sa-success', b, match); }
    else if ((match = matchSequence(b, [atk, 3, 2, 6]))) { detectedMove = "昇竜拳"; showResult(`昇竜拳`, `(623+${atk})`, 'success', b, match); }
    else if ((match = matchSequence(b, [atk, 6, 3, 2]))) { detectedMove = "波動拳"; showResult(`波動拳`, `(236+${atk})`, 'special-success', b, match); }
    else if ((match = matchSequence(b, [atk, 4, 1, 2]))) { detectedMove = "竜巻旋風脚"; showResult(`竜巻旋風脚`, `(214+${atk})`, 'special-success', b, match); }

    if (!detectedMove) detectedMove = (currentDir === 1 || currentDir === 2 || currentDir === 3) ? `しゃがみ${atk}` : `立ち${atk}`;
    processComboTracking(detectedMove, performance.now());
  }

  function processComboTracking(moveName, time) {
    const targetSeq = COMBO_RECIPES[activeComboId].sequence;
    if (comboStep > 0 && (time - lastMoveTime) > 800) comboStep = 0;
    if (moveName === targetSeq[comboStep]) {
      comboStep++; lastMoveTime = time;
      if (comboStep === targetSeq.length) { showComboSuccessLog(); comboStep = 0; }
    } else { comboStep = (moveName === targetSeq[0]) ? 1 : 0; lastMoveTime = time; }
    renderComboUI();
  }

  function renderComboUI() {
    const seq = COMBO_RECIPES[activeComboId].sequence;
    comboProgressElement.innerHTML = seq.map((s, i) => `<span class="step ${i < comboStep ? 'completed' : i === comboStep ? 'current' : ''}">${s}</span>`).join('<span class="step-arrow">➔</span>');
  }

  function showComboSuccessLog() {
    const div = document.createElement('div'); div.className = `success combo-success-log`;
    div.innerHTML = `<div style="font-weight: bold; font-size: 1.4em; color: #e91e63;">✨ COMBO SUCCESS !!</div><div>【${COMBO_RECIPES[activeComboId].name}】が完璧に繋がりました！</div>`;
    logElement.prepend(div);
  }

  function matchSequence(buffer, sequence) {
    let seqIdx = 0; let matchIndices = [];
    for (let i = 0; i < buffer.length; i++) {
      const input = buffer[i]; const target = sequence[seqIdx];
      if ((typeof target === 'string' && input.val === target) || (typeof target === 'number' && input.val === target)) { matchIndices.push(i); seqIdx++; }
      if (seqIdx === sequence.length) return matchIndices;
    }
    return false;
  }

  function showResult(cmdName, cmdInput, className, buffer, matchIndices) {
    const seq = [...matchIndices].reverse(); 
    const startTime = buffer[seq[0]].time; const endTime = buffer[seq[seq.length - 1]].time;
    const totalFrames = Math.max(1, Math.round((endTime - startTime) / FRAME_MS));
    const dirCount = seq.length - 1; 

    let evaluation = totalFrames <= dirCount * 3 ? "⚡ EXCELLENT" : totalFrames <= dirCount * 5 ? "👍 GOOD" : "🐢 SLOW (遅すぎます)";
    let evalClass = totalFrames <= dirCount * 3 ? "eval-excellent" : totalFrames <= dirCount * 5 ? "eval-good" : "eval-slow";
    
    if (totalFrames <= dirCount * 5) { streakCount = (lastSuccessfulCommand === cmdName + cmdInput) ? streakCount + 1 : 1; lastSuccessfulCommand = cmdName + cmdInput; } 
    else { streakCount = 0; lastSuccessfulCommand = ""; }

    let streakHtml = streakCount >= 2 ? `<span class="combo-streak">🔥 連続成功: ${streakCount}回</span>` : "";
    let wrongDirs = new Set(); let hasNeutralNoise = false;
    
    for (let i = seq[0]; i >= seq[seq.length - 1]; i--) {
      if (!seq.includes(i)) { if (buffer[i].val === 5) hasNeutralNoise = true; else if (typeof buffer[i].val === 'number') wrongDirs.add(buffer[i].val); }
    }

    let noiseHtml = hasNeutralNoise ? `<span class="warning-text">⚠️ 間に [N] が挟まりました (入力がフワついています)</span>` : "";
    if (wrongDirs.size > 0) noiseHtml += `<span class="danger-text">❌ 不要な方向 ${Array.from(wrongDirs).map(v => getIconHtml(v)).join(' ')} が混ざっています</span>`;

    let detailsHtml = '<div class="details-box">';
    for (let i = 0; i < dirCount; i++) {
      const frames = Math.max(1, Math.round((buffer[seq[i+1]].time - buffer[seq[i]].time) / FRAME_MS));
      detailsHtml += `${getIconHtml(buffer[seq[i]].val)}<span class="frame-badge ${frames >= 5 ? 'slow-input' : frames <= 2 ? 'fast-input' : ''}">${frames}F</span>`;
    }
    detailsHtml += `${getIconHtml(buffer[seq[seq.length-1]].val)}</div>`;

    const div = document.createElement('div'); div.className = `success ${className}`;
    div.innerHTML = `<div style="font-weight: bold; font-size: 1.2em;">${cmdName} <span style="font-weight:normal; font-size:0.8em; color:#888;">${cmdInput}</span></div><div class="${evalClass}" style="font-size: 1.1em; margin: 6px 0;">${evaluation} : 合計 ${totalFrames}F ${streakHtml}</div>${detailsHtml}${noiseHtml}`;
    logElement.prepend(div); inputBuffer = []; 
  }

  renderComboUI(); gameLoop();
</script>
</body>
</html>
"""

# === 4. メインロジック ===
def get_pool():
    pool = list(st.session_state.settings["study_list"])
    for t in st.session_state.settings.get("focus_study_list", []): pool.extend([t]*3)
    if not st.session_state.mock_exam_done: pool.append("TOEIC模擬試験(2時間)")
    return pool

GAME_LIST = ["イナイレ", "スト６", "バウンティ", "ドラゴンボールスクアドラ"]
SOS_LIST = ["瞑想", "深呼吸", "腹筋30回", "昼寝", "読書", "Geminiと話す"]

with st.sidebar:
    components.html(BGM_PLAYER_HTML, height=270)
    st.divider()
    app_mode = st.radio("🔄 モード切替", ["🚀 集中モード (Use)", "🛠️ 編集モード (Edit)"])
    st.divider()
    st.write(f"📁 記録数: {len(st.session_state.logs)}件")
    if st.session_state.logs:
        csv = pd.DataFrame(st.session_state.logs).to_csv(index=False).encode('utf-8-sig')
        st.download_button("履歴ダウンロード", csv, "activity_log.csv", "text/csv")
    if app_mode == "🛠️ 編集モード (Edit)" and st.button("全データリセット"):
        st.session_state.logs = []
        if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
        st.rerun()

# ----------------------------------------------------
# ダッシュボード画面
# ----------------------------------------------------
if st.session_state.page == 'dashboard':
    st.title("☕ Focus & Cafe Roulette")
    s = st.session_state.settings
    
    if app_mode == "🛠️ 編集モード (Edit)":
        with st.expander("⚙️ 設定パネル", expanded=True):
            new_bg = st.text_input("🖼️ 背景画像のURL (画像アドレスを貼り付け)", value=s.get("bg_url", ""))
            
            t1, t2 = st.tabs(["TOEIC", "インターン"])
            with t1:
                d1 = st.date_input("ターゲット日", datetime.strptime(s["toeic_date"], "%Y-%m-%d").date(), key="d1")
                h1 = st.number_input("1日の時間", 1, 24, s["daily_hours_toeic"], key="h1")
            with t2:
                d2 = st.date_input("ターゲット日", datetime.strptime(s["intern_date"], "%Y-%m-%d").date(), key="d2")
                h2 = st.number_input("1日の時間", 1, 24, s["daily_hours_intern"], key="h2")
            
            c1, c2, c3 = st.columns(3)
            with c1: n_s = st.text_area("通常勉強", "\n".join(s["study_list"]))
            with c2: n_f = st.text_area("🔥 重点(3倍)", "\n".join(s.get("focus_study_list",[])))
            with c3: n_r = st.text_area("気分転換", "\n".join(s["refresh_list"]))
            
            if st.button("💾 保存して適用", type="primary"):
                s["bg_url"] = new_bg
                s["toeic_date"] = d1.strftime("%Y-%m-%d")
                s["intern_date"] = d2.strftime("%Y-%m-%d")
                s["daily_hours_toeic"], s["daily_hours_intern"] = h1, h2
                s["study_list"] = [x.strip() for x in n_s.split("\n") if x.strip()]
                s["focus_study_list"] = [x.strip() for x in n_f.split("\n") if x.strip()]
                s["refresh_list"] = [x.strip() for x in n_r.split("\n") if x.strip()]
                save_settings(s)
                st.success("保存完了！次回も引き継がれます。")
                time.sleep(1)
                st.rerun()

    td = datetime.now().date()
    dt = max((datetime.strptime(s["toeic_date"], "%Y-%m-%d").date() - td).days, 0)
    di = max((datetime.strptime(s["intern_date"], "%Y-%m-%d").date() - td).days, 0)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='milestone-card'><div style='color:#ccc;'>TOEIC ({s['toeic_date']}) まであと {dt} 日<br>🔥 残り作業可能</div><div class='glowing-hours'>{dt * s['daily_hours_toeic']} <span style='font-size:1.5rem;color:white;'>時間</span></div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='milestone-card'><div style='color:#ccc;'>インターン ({s['intern_date']}) まであと {di} 日<br>🔥 残り作業可能</div><div class='glowing-hours'>{di * s['daily_hours_intern']} <span style='font-size:1.5rem;color:white;'>時間</span></div></div>", unsafe_allow_html=True)

    st.divider()
    
    st.subheader("📊 今日の進捗")
    target_time = st.number_input("今日の目標勉強時間(分)", min_value=30, value=180, step=30)
    current_study = st.session_state.study_time_total
    current_refresh = st.session_state.refresh_time_total
    
    progress_percent = min(current_study / target_time, 1.0) if target_time > 0 else 1.0
    remaining_time = max(0, target_time - current_study)
    
    # 角度を計算（360度中の何パーセントか）
    deg = int(progress_percent * 360)

    # ★ 完全にバグらない「CSS製ドーナツ型円グラフ」
    circle_html = f"""
    <div style="display: flex; justify-content: center; align-items: center; padding: 10px;">
        <div style="
            width: 180px; height: 180px; border-radius: 50%;
            background: conic-gradient(#4CAF50 {deg}deg, rgba(255,255,255,0.1) {deg}deg);
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 0 15px rgba(0,0,0,0.5);
        ">
            <div style="
                width: 140px; height: 140px; border-radius: 50%;
                background-color: rgba(20, 24, 30, 0.95);
                display: flex; flex-direction: column; align-items: center; justify-content: center;
            ">
                <span style="font-size: 2.5rem; font-weight: bold; color: #4CAF50;">{int(progress_percent*100)}%</span>
            </div>
        </div>
    </div>
    """
    
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1: 
        st.markdown(circle_html, unsafe_allow_html=True)
    with c2: 
        st.write("<br><br>", unsafe_allow_html=True)
        st.metric("今日の勉強時間", f"{current_study} 分")
        st.caption(f"目標まであと: {remaining_time} 分")
    with c3: 
        st.write("<br><br>", unsafe_allow_html=True)
        st.metric("今日の気分転換", f"{st.session_state.refresh_time_total} 分")

    st.divider()
    can_game = (datetime.now().hour >= 20 or datetime.now().hour <= 3) and (current_study >= target_time)
    if can_game: st.success("🎉 ゲーム解放条件クリア！")
    else: st.info(f"🔒 ゲーム解放まで: 勉強 {current_study}/{target_time}分 & 20時以降")

    is_rolled = st.session_state.rolled_options is not None
    if st.button("🎲 カフェルーレットを回す！", use_container_width=True, disabled=is_rolled):
        st.session_state.rolled_options = {
            "勉強": random.choice(get_pool()),
            "気分転換": "なし(連続お休み)" if st.session_state.last_was_refresh else random.choice(s["refresh_list"] + GAME_LIST if can_game else s["refresh_list"])
        }
        st.rerun()
        
    if st.session_state.rolled_options:
        st.markdown("<div id='roulette-result'></div>", unsafe_allow_html=True)
        components.html("""
        <script>
            let attempts = 0;
            const scrollInt = setInterval(() => {
                const el = window.parent.document.getElementById('roulette-result');
                if(el) {
                    el.scrollIntoView({behavior: 'smooth', block: 'center'});
                    clearInterval(scrollInt);
                }
                attempts++;
                if(attempts > 20) clearInterval(scrollInt);
            }, 100);
        </script>
        """, height=0)

        ro = st.session_state.rolled_options
        with st.form("sel"):
            ch = [f"【勉強】 {ro['勉強']}"]
            if not st.session_state.last_was_refresh: ch.append(f"【気分転換】 {ro['気分転換']}")
            sm = st.radio("実行タスク:", ch)
            if st.form_submit_button("集中モードへ！"):
                cat = "勉強" if "【勉強】" in sm else "気分転換"
                tn = sm.replace(f"【{cat}】 ", "")
                st.session_state.current_task = {"カテゴリ": cat, "タスク": tn, "duration": 120 if "模試" in tn else random.randint(30,60) if cat=="勉強" else random.randint(15,30)}
                st.session_state.start_time = time.time()
                st.session_state.last_was_refresh = (cat == "気分転換")
                st.session_state.rolled_options = None 
                st.session_state.page = 'active'
                st.session_state.compact_mode = False # アクティブ遷移時は一旦フルサイズにする
                st.rerun()

# ----------------------------------------------------
# 画面2: アクティブ（集中モード）
# ----------------------------------------------------
elif st.session_state.page == 'active':
    t = st.session_state.current_task
    dms = t['duration'] * 60000
    show_timer_js = "true" if t['カテゴリ'] == "気分転換" else "false"

    # ===============================================
    # パターンA： 没入(コンパクト)モード ON
    # ===============================================
    if st.session_state.compact_mode:
        if st.button("🗖 拡大表示に戻す", help="終了する場合はここを押して元の画面に戻ってください"):
            st.session_state.compact_mode = False
            st.rerun()

        # 左上に「文字＋半透明の無地背景（座布団）」のパネルだけを描画し、SOS等のボタンは一切出さない！
        js_compact = f"""
        <style>
            body {{ margin: 0; padding: 0; font-family: sans-serif; }}
            .panel {{
                background: rgba(0, 0, 0, 0.75);
                padding: 15px 25px;
                border-radius: 12px;
                display: inline-block;
                backdrop-filter: blur(5px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            .task-name {{ font-size: 1.2rem; color: #fff; font-weight: bold; margin-bottom: 5px; }}
            .timer {{ font-size: 2.5rem; color: #4CAF50; font-family: monospace; font-weight: bold; text-shadow: 0 0 10px #4CAF50; }}
            .alarm {{ display: none; font-size: 1.2rem; font-weight: bold; color: #ffeb3b; margin-top: 5px; }}
            .stoic-msg {{ font-size: 1rem; color: rgba(255,255,255,0.7); }}
        </style>
        <div class="panel">
            <div class="task-name">{t['タスク']}</div>
            <div class="timer" id="t"></div>
            <div class="alarm" id="alarm-msg">⏰ 終了！拡大して記録してください</div>
        </div>
        
        <script>
            if(!sessionStorage.getItem('s')) sessionStorage.setItem('s', Date.now());
            const e = parseInt(sessionStorage.getItem('s')) + {dms};
            const show = {show_timer_js};
            
            const tick = setInterval(() => {{
                const now = Date.now();
                const remain = Math.max(0, e - now);
                const tEl = document.getElementById('t');
                
                if (show) {{ 
                    tEl.innerText = Math.floor(remain/60000).toString().padStart(2,'0') + ":" + Math.floor((remain%60000)/1000).toString().padStart(2,'0');
                    if (now >= e && !sessionStorage.getItem('played')) {{
                        sessionStorage.setItem('played', 'true');
                        tEl.style.display = 'none';
                        document.getElementById('alarm-msg').style.display = 'block';
                        try {{
                            const actx = new (window.AudioContext || window.webkitAudioContext)();
                            const osc = actx.createOscillator();
                            osc.type = 'square'; osc.frequency.setValueAtTime(440, actx.currentTime);
                            osc.connect(actx.destination); osc.start(); setTimeout(()=>osc.stop(),1500);
                        }} catch(err) {{}}
                    }}
                }} else {{ 
                    if (now < e) {{
                        tEl.innerText = "集中モード実行中...";
                        tEl.className = "stoic-msg";
                    }} else {{
                        tEl.innerText = "✅ 達成！拡大して記録";
                        tEl.style.fontSize = "1.1rem";
                        tEl.style.color = "#ffeb3b";
                        clearInterval(tick);
                    }}
                }}
            }}, 200);
        </script>
        """
        components.html(js_compact, height=150)

    # ===============================================
    # パターンB： 通常表示（フルサイズ）モード
    # ===============================================
    else:
        btn_col, _ = st.columns([1, 15])
        with btn_col:
            if st.button("🗕", help="没入表示（背景メイン）にする"):
                st.session_state.compact_mode = True
                st.rerun()

        st.markdown(f"<h1 style='text-align:center;font-size:3rem;text-shadow:2px 2px 4px #000;'>{t['タスク']}</h1>", unsafe_allow_html=True)
        if "スト6" in t['タスク']: components.html(SF6_HTML_CODE, height=650, scrolling=True)
        
        js_full = f"""
        <div id="t" style="text-align:center;font-size:7rem;color:#4CAF50;font-family:monospace;font-weight:bold;text-shadow:0 0 20px #4CAF50;"></div>
        <div id="alarm-msg" style="display:none; text-align:center; font-size:4rem; font-weight:bold; color:white; background:rgba(255,0,0,0.8); padding:20px; border-radius:10px; backdrop-filter:blur(10px);">⏰ 終了時間です！</div>
        
        <script>
            if(!sessionStorage.getItem('s')) sessionStorage.setItem('s', Date.now());
            const e = parseInt(sessionStorage.getItem('s')) + {dms};
            const show = {show_timer_js};
            
            const tick = setInterval(() => {{
                const now = Date.now();
                const remain = Math.max(0, e - now);
                const tEl = document.getElementById('t');
                
                const btns = Array.from(window.parent.document.querySelectorAll('button'));
                const endBtn = btns.find(b => b.innerText.includes('終了して記録') || b.textContent.includes('終了して記録'));

                if (show) {{ 
                    tEl.innerText = Math.floor(remain/60000).toString().padStart(2,'0') + ":" + Math.floor((remain%60000)/1000).toString().padStart(2,'0');
                    if (now >= e && !sessionStorage.getItem('played')) {{
                        sessionStorage.setItem('played', 'true');
                        tEl.style.display = 'none';
                        document.getElementById('alarm-msg').style.display = 'block';
                        try {{
                            const actx = new (window.AudioContext || window.webkitAudioContext)();
                            const osc = actx.createOscillator();
                            osc.type = 'square'; osc.frequency.setValueAtTime(440, actx.currentTime);
                            osc.connect(actx.destination); osc.start(); setTimeout(()=>osc.stop(),1500);
                        }} catch(err) {{}}
                    }}
                }} else {{ 
                    if (now < e) {{
                        tEl.innerText = "予定時間: ？？？ 分\\n（見事達成するまで終了ボタンは出現しません）";
                        tEl.style.fontSize = "1.5rem";
                        tEl.style.color = "rgba(255,255,255,0.7)";
                        tEl.style.textShadow = "none";
                        if (endBtn) endBtn.style.display = 'none';
                    }} else {{
                        tEl.innerText = "✅ 規定時間が終了しました！\\n記録して終了できます。";
                        tEl.style.fontSize = "2rem";
                        tEl.style.color = "#ffeb3b";
                        if (endBtn) endBtn.style.display = 'inline-flex';
                        clearInterval(tick);
                    }}
                }}
            }}, 200);
        </script>
        """
        components.html(js_full, height=200)

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            if st.button("■ 終了して記録する", use_container_width=True, type="primary"):
                em = int((time.time() - st.session_state.start_time) / 60)
                if t['カテゴリ'] == "勉強": st.session_state.study_time_total += em
                else: st.session_state.refresh_time_total += em
                log_activity(t['タスク'], t['カテゴリ'], em, "設定BGM")
                components.html("<script>sessionStorage.clear();</script>", height=0)
                time.sleep(0.5)
                st.session_state.page = 'dashboard'
                st.rerun()
        with c2:
            if t['カテゴリ'] == "勉強" and st.button("🚨 集中切れ！(SOS)", use_container_width=True):
                em = int((time.time() - st.session_state.start_time) / 60)
                st.session_state.study_time_total += em
                log_activity(t['タスク'], "中断", em, "設定BGM", "集中切れ")
                components.html("<script>sessionStorage.clear();</script>", height=0)
                time.sleep(0.5)
                st.session_state.sos_task = random.choice(SOS_LIST)
                st.session_state.page = 'sos'
                st.rerun()

# ----------------------------------------------------
# 画面3: SOS（緊急リセットモード）
# ----------------------------------------------------
elif st.session_state.page == 'sos':
    st.warning("集中力が切れましたね。自分を責めず、一旦リセットしましょう！")
    st.markdown(f"<h2 style='text-align:center;'>緊急指令：【{st.session_state.sos_task}】</h2>", unsafe_allow_html=True)
    if st.button("ダッシュボードへ戻る", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()
