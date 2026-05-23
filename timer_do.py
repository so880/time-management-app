import streamlit as st
import time
import pandas as pd
import random
from datetime import datetime, date
import streamlit.components.v1 as components
import plotly.graph_objects as go

# ==========================================
# セッションステートの初期化
# ==========================================
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'study_time_total' not in st.session_state:
    st.session_state.study_time_total = 0 
if 'refresh_time_total' not in st.session_state:
    st.session_state.refresh_time_total = 0
if 'last_was_refresh' not in st.session_state:
    st.session_state.last_was_refresh = False
if 'logs' not in st.session_state:
    st.session_state.logs = [] 
if 'current_task' not in st.session_state:
    st.session_state.current_task = None
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'rolled_options' not in st.session_state:
    st.session_state.rolled_options = None
if 'mock_exam_done' not in st.session_state:
    st.session_state.mock_exam_done = False

# ==========================================
# UI/UX カスタムデザイン（CSSインジェクション）
# ==========================================
st.markdown("""
<style>
    /* 全体の背景とフォント */
    .stApp {
        background-color: #0E1117;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 上部の数値（メトリクス）をカード風に */
    div[data-testid="metric-container"] {
        background-color: #1E1E1E;
        border: 1px solid #333;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border-left: 5px solid #4CAF50;
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(76, 175, 80, 0.2);
    }

    /* ルーレットボタンをネオン風に */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        border: 2px solid #4CAF50;
        background-color: transparent;
        color: #4CAF50;
        font-weight: bold;
        font-size: 1.2rem;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #4CAF50;
        color: #000;
        box-shadow: 0 0 15px rgba(76, 175, 80, 0.5);
        transform: scale(1.02);
    }
    
    /* 終了ボタン（赤色） */
    button[kind="primary"] {
        border: 2px solid #ff4b4b !important;
        color: #ff4b4b !important;
    }
    button[kind="primary"]:hover {
        background-color: #ff4b4b !important;
        color: #fff !important;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.5) !important;
    }

    /* UI改修: マイルストーンカードのリッチ化とパルスアニメーション */
    @keyframes pulse {
        0% { transform: scale(1); text-shadow: 0 0 10px rgba(255, 235, 59, 0.5); }
        50% { transform: scale(1.03); text-shadow: 0 0 25px rgba(255, 235, 59, 1); }
        100% { transform: scale(1); text-shadow: 0 0 10px rgba(255, 235, 59, 0.5); }
    }
    .milestone-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
        border: 1px solid #444;
        border-left: 6px solid #ffeb3b;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.5);
        margin-top: 10px;
    }
    .glowing-hours {
        animation: pulse 2s infinite;
        color: #ffeb3b;
        font-size: 3.5rem;
        font-weight: 900;
        line-height: 1.2;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# スト6 コンボ練習アプリのHTML/JSコード
# ==========================================
SF6_HTML_CODE = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>SF6 Command Analyzer</title>
<style>
  body { background-color: #121212; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 10px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; margin: 0;}
  #status { color: #ffeb3b; margin-bottom: 10px; font-size: 1.2em; font-family: monospace; }
  .combo-panel { background-color: #1e1e1e; border: 2px solid #4caf50; border-radius: 8px; padding: 15px; margin-bottom: 15px; display: flex; flex-direction: column; gap: 10px; }
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
  .history-panel { width: 220px; background-color: #1e1e1e; border: 2px solid #333; border-radius: 8px; padding: 10px; overflow-y: hidden; display: flex; flex-direction: column; }
  .history-panel h3 { margin: 0 0 10px 0; font-size: 0.9em; color: #888; text-align: center; border-bottom: 1px solid #333; padding-bottom: 5px; }
  #history-list { display: flex; flex-direction: column; gap: 4px; }
  .history-item { display: flex; align-items: center; justify-content: space-between; background-color: #2a2a2a; padding: 6px 12px; border-radius: 6px; border-left: 4px solid #444; }
  .history-item.neutral-item { background-color: #1a1a1a; border-left-color: #222; }
  .history-item.punch-item { border-left-color: #f44336; }
  .history-item.kick-item { border-left-color: #2196f3; }
  .icon-container { display: flex; align-items: center; justify-content: center; width: 30px; }
  .frame-text { font-family: monospace; font-size: 1.1em; color: #bbb; width: 50px; text-align: right; }
  .log-panel { flex: 1; background-color: #1e1e1e; border: 2px solid #333; border-radius: 8px; padding: 15px; overflow-y: auto; }
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

# ==========================================
# リスト定義
# ==========================================
STUDY_BASE_LIST = [
    "Santa Part7長文の写経", 
    "英語の記事の写経", 
    "Gemini提案英文の写経", 
    "プログラミング(paiza)",
    "洋楽の本気カラオケ(英語発音)",
    "Santa Part3・4のオーバーラッピング",
    "海外車レビュー記事の音読・写経",
    "Santa 単語",
    "Geminiと面接練習"
]

def get_current_study_pool():
    pool = list(STUDY_BASE_LIST)
    pool.extend(["大学の履修について考える"] * 3)
    if not st.session_state.mock_exam_done:
        pool.append("TOEIC模擬試験(2時間)")
    return pool

REFRESH_BASE_LIST = [
    "料理探し", "読書", "仮眠", "腕立て30回",
    "腹筋30回", "ダンベル30回", "洋楽カラオケ",
    "机の掃除", "床の片づけ", "掃除機掛け", "スト6 コンボ練習"
]

GAME_LIST = ["イナイレ", "スト６", "バウンティ", "ドラゴンボールスクアドラ"]

BGM_LIST = ["日本語ラジオ", "英語ラジオ", "カフェ", "雨音"]
SOS_LIST = ["瞑想", "深呼吸", "腹筋30回", "昼寝", "読書", "Geminiと話す"]

def log_activity(task_name, category, duration, bgm_used, note=""):
    st.session_state.logs.append({
        "日付": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "カテゴリ": category,
        "内容": task_name,
        "BGM": bgm_used,
        "経過時間(分)": duration,
        "メモ": note
    })

# ==========================================
# 画面1: ダッシュボード
# ==========================================
if st.session_state.page == 'dashboard':
    st.title("フォーカス＆ルーレット")
    
    # ----------------------------------------------------
    # UI改修: マイルストーン設定（タブ化による整理）
    # ----------------------------------------------------
    with st.expander("⚙️ マイルストーン設定（日付と1日の作業時間）", expanded=True):
        tab1, tab2 = st.tabs(["📘 TOEIC", "💼 夏インターン"])
        
        with tab1:
            col_d1, col_h1 = st.columns(2)
            with col_d1:
                toeic_date = st.date_input("📅 ターゲット日", value=date(2026, 5, 24), key="t_date")
            with col_h1:
                daily_hours_toeic = st.number_input("⏱️ 1日あたりの作業時間 (時間)", min_value=1, max_value=24, value=3, step=1, key="t_hours")
                
        with tab2:
            col_d2, col_h2 = st.columns(2)
            with col_d2:
                intern_date = st.date_input("📅 ターゲット日", value=date(2026, 6, 1), key="i_date")
            with col_h2:
                daily_hours_intern = st.number_input("⏱️ 1日あたりの作業時間 (時間)", min_value=1, max_value=24, value=2, step=1, key="i_hours")

    # カウントダウン計算
    today = datetime.now().date()
    days_to_toeic = max((toeic_date - today).days, 0)
    days_to_intern = max((intern_date - today).days, 0)

    # ----------------------------------------------------
    # マイルストーン表示
    # ----------------------------------------------------
    st.subheader("🏁 デッドライン・マイルストーン")
    c1, c2 = st.columns(2)
    
    with c1:
        st.metric("TOEIC L&R 公開テストまで", f"あと {days_to_toeic} 日", delta_color="inverse")
        st.caption(f"📅 ターゲット日: {toeic_date.strftime('%Y-%m-%d')} (目標800点)")
        st.markdown(f"""
        <div class='milestone-card'>
            <div style='font-size: 1.1rem; color: #ccc; font-weight: normal;'>🔥 残り作業可能時間</div>
            <div class='glowing-hours'>{days_to_toeic * daily_hours_toeic} <span style='font-size: 1.5rem; color: #fff; text-shadow: none;'>時間</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.metric("夏インターン選考ピークまで", f"あと {days_to_intern} 日", delta_color="inverse")
        st.caption(f"📅 ターゲット日: {intern_date.strftime('%Y-%m-%d')} (ES提出〆切ラッシュ)")
        st.markdown(f"""
        <div class='milestone-card'>
            <div style='font-size: 1.1rem; color: #ccc; font-weight: normal;'>🔥 残り作業可能時間</div>
            <div class='glowing-hours'>{days_to_intern * daily_hours_intern} <span style='font-size: 1.5rem; color: #fff; text-shadow: none;'>時間</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    
    # ----------------------------------------------------
    # 今日の進捗の可視化（円グラフ）
    # ----------------------------------------------------
    st.subheader("📊 今日の進捗")
    
    target_time = st.number_input("今日の目標勉強時間(分)", min_value=30, value=180, step=30)
    
    current_study = st.session_state.study_time_total
    current_refresh = st.session_state.refresh_time_total
    
    progress_percent = min(current_study / target_time, 1.0) if target_time > 0 else 1.0
    remaining_time = max(0, target_time - current_study)

    fig = go.Figure(go.Pie(
        values=[current_study, remaining_time] if current_study < target_time else [current_study],
        labels=["勉強済み", "残り目標"] if current_study < target_time else ["目標達成!"],
        hole=0.75,
        marker=dict(
            colors=["#4CAF50", "#2b2b2b"] if current_study < target_time else ["#4CAF50"],
            line=dict(color="#0E1117", width=2)
        ),
        textinfo="none",
        hoverinfo="label+value"
    ))
    
    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        height=200,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b>{int(progress_percent*100)}%</b>", 
            x=0.5, y=0.5, font_size=36, font_color="#4CAF50", showarrow=False
        )]
    )

    col1, col2, col3 = st.columns([1.2, 1, 1])
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.write("<br>", unsafe_allow_html=True)
        st.metric("今日の勉強時間", f"{current_study} 分")
        st.caption(f"目標まであと: {remaining_time} 分")
    with col3:
        st.write("<br>", unsafe_allow_html=True)
        st.metric("今日の気分転換", f"{current_refresh} 分")

    st.divider()
    
    # ----------------------------------------------------
    # ロック解除判定
    # ----------------------------------------------------
    current_hour = datetime.now().hour
    current_study = st.session_state.study_time_total
    
    is_time_ok = (current_hour >= 20 or current_hour <= 3)
    is_study_ok = (current_study >= target_time)
    can_play_game = is_time_ok and is_study_ok
    
    if can_play_game:
        st.success("🎉 解放条件クリア！ルーレットに「本物のゲーム」が追加されています！")
    else:
        st.info(f"🔒 【ゲーム解放までの道のり】\n・勉強時間: {current_study} / {target_time}分以上\n・時間帯: 現在 {current_hour}時 (20時以降に解放)")

    # ----------------------------------------------------
    # ルーレット処理
    # ----------------------------------------------------
    if st.button("🎲 ルーレットを回す！", use_container_width=True):
        study_pool = get_current_study_pool()
        if st.session_state.last_was_refresh:
            st.session_state.rolled_options = {
                "勉強": random.choice(study_pool),
                "気分転換": "なし（連続プレイ防止のためお休み）",
                "BGM": random.choice(BGM_LIST)
            }
        else:
            refresh_pool = REFRESH_BASE_LIST + GAME_LIST if can_play_game else REFRESH_BASE_LIST
            st.session_state.rolled_options = {
                "勉強": random.choice(study_pool),
                "気分転換": random.choice(refresh_pool),
                "BGM": random.choice(BGM_LIST)
            }
        
    if st.session_state.rolled_options:
        opts = st.session_state.rolled_options
        st.subheader("🎲 今回の選択肢")
        
        with st.form("selection_form"):
            st.write("どっちをやる？")
            
            choices = [f"【勉強】 {opts['勉強']}"]
            
            if not st.session_state.last_was_refresh:
                choices.append(f"【気分転換】 {opts['気分転換']}")
            else:
                st.warning("⚠️ 前回、気分転換を実行したため、今回は強制的に「勉強」になります。机に向かいましょう！")
                
            selected_main = st.radio("実行するタスクを選んでください:", choices)
            
            st.write("---")
            st.write(f"🎧 今回のBGM: **{opts['BGM']}**")
            use_bgm = st.checkbox("このBGMを使用する（チェックなしの場合は無音として記録）", value=True)
            
            submitted = st.form_submit_button("この内容でスタート！")
            
            if submitted:
                cat = "勉強" if "【勉強】" in selected_main else "気分転換"
                task_name = selected_main.replace(f"【{cat}】 ", "")
                
                if task_name == "TOEIC模擬試験(2時間)":
                    task_duration = 120
                    st.session_state.mock_exam_done = True
                elif cat == "勉強":
                    task_duration = random.randint(30, 60)
                else:
                    task_duration = random.randint(15, 30)
                
                st.session_state.current_task = {
                    "カテゴリ": cat,
                    "タスク": task_name,
                    "BGM": opts['BGM'] if use_bgm else "使用せず",
                    "duration": task_duration
                }
                st.session_state.start_time = time.time()
                st.session_state.last_was_refresh = (cat == "気分転換")
                
                st.session_state.rolled_options = None 
                st.session_state.page = 'active'
                st.rerun()

# ==========================================
# 画面2: アクティブ（集中モード＆特殊ロック）
# ==========================================
elif st.session_state.page == 'active':
    task = st.session_state.current_task
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; font-size: 3rem;'>{task['タスク']}</h1>", unsafe_allow_html=True)
    
    if task['タスク'] == "スト6 コンボ練習":
        st.info("🎮 スト6 コマンド練習モードがアクティブです！（※キーボード操作の場合、下の黒い画面を一度クリックしてから入力してください）")
        components.html(SF6_HTML_CODE, height=600, scrolling=True)

    duration_ms = task['duration'] * 60 * 1000
    show_timer_js = "true" if task['カテゴリ'] == "気分転換" else "false"
    
    js_code = f"""
    <div id="timer-box" style="text-align: center; margin-top: 20px;">
        <div id="countdown-timer" style="font-size: 6rem; font-weight: bold; color: #ff4b4b; font-family: monospace;"></div>
        <div id="alarm-msg" style="display: none; font-size: 4rem; font-weight: bold; color: white; background-color: red; padding: 20px; border-radius: 10px;">⏰ 終了時間です！</div>
    </div>

    <script>
    if (!sessionStorage.getItem('startTime')) {{
        sessionStorage.setItem('startTime', Date.now());
    }}
    
    const startTime = parseInt(sessionStorage.getItem('startTime'));
    const durationMs = {duration_ms};
    const endTime = startTime + durationMs;
    const showTimer = {show_timer_js};
    
    const timerDisplay = document.getElementById('countdown-timer');
    const alarmMsg = document.getElementById('alarm-msg');
    
    let endBtn = null;
    let studyEndMsg = null;
    
    const findButtonInterval = setInterval(() => {{
        try {{
            const parentDoc = window.parent.document;
            const buttons = Array.from(parentDoc.querySelectorAll('button'));
            endBtn = buttons.find(b => b.innerText.includes('終了して記録する'));
            
            if (endBtn) {{
                if (!showTimer) {{
                    studyEndMsg = parentDoc.getElementById('study-end-msg');
                    if (!studyEndMsg) {{
                        studyEndMsg = parentDoc.createElement('div');
                        studyEndMsg.id = 'study-end-msg';
                        studyEndMsg.innerText = '✅ 規定時間が終了しました！記録して終了できます。';
                        studyEndMsg.style.color = '#d32f2f';
                        studyEndMsg.style.fontWeight = 'bold';
                        studyEndMsg.style.fontSize = '1.2rem';
                        studyEndMsg.style.marginBottom = '15px';
                        studyEndMsg.style.padding = '10px';
                        studyEndMsg.style.border = '2px solid #ef5350';
                        studyEndMsg.style.borderRadius = '5px';
                        studyEndMsg.style.backgroundColor = '#ffebee';
                        studyEndMsg.style.textAlign = 'center';
                        studyEndMsg.style.display = 'none';
                        endBtn.parentNode.insertBefore(studyEndMsg, endBtn);
                    }}
                    
                    const nowInit = Date.now();
                    if (nowInit < endTime) {{
                        endBtn.style.display = 'none';
                    }}
                }}
                clearInterval(findButtonInterval);
            }}
        }} catch(e) {{
            console.error("DOM Access Error", e);
            clearInterval(findButtonInterval);
        }}
    }}, 100);
    
    function playBeep() {{
        try {{
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioCtx.createOscillator();
            oscillator.type = 'square';
            oscillator.frequency.setValueAtTime(440, audioCtx.currentTime);
            oscillator.connect(audioCtx.destination);
            oscillator.start();
            setTimeout(() => {{ oscillator.stop(); }}, 1500);
        }} catch(e) {{ console.log("Audio play failed"); }}
    }}

    const checkInterval = setInterval(() => {{
        const now = Date.now();
        const remain = Math.max(0, endTime - now);
        
        if (showTimer) {{
            const minutes = Math.floor(remain / 60000).toString().padStart(2, '0');
            const seconds = Math.floor((remain % 60000) / 1000).toString().padStart(2, '0');
            timerDisplay.innerText = minutes + ":" + seconds;

            if (now >= endTime && !sessionStorage.getItem('endPlayed')) {{
                clearInterval(checkInterval);
                sessionStorage.setItem('endPlayed', 'true');
                timerDisplay.style.display = 'none';
                alarmMsg.style.display = 'inline-block';
                playBeep();
                setInterval(() => {{
                    document.body.style.backgroundColor = document.body.style.backgroundColor === 'red' ? 'white' : 'red';
                }}, 500);
            }}
        }} else {{
            timerDisplay.innerText = "予定時間: ？？？ 分（見事達成するまで終了ボタンは出現しません）";
            timerDisplay.style.fontSize = "1.5rem";
            timerDisplay.style.color = "gray";
            
            if (now >= endTime) {{
                clearInterval(checkInterval);
                sessionStorage.setItem('endPlayed', 'true');
                if (endBtn) endBtn.style.display = 'inline-flex';
                if (studyEndMsg) studyEndMsg.style.display = 'block';
            }}
        }}
    }}, 250);
    </script>
    """
    
    components.html(js_code, height=200)

    # --- ボタン類 ---
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("■ 終了して記録する", use_container_width=True, type="primary"):
            elapsed_minutes = int((time.time() - st.session_state.start_time) / 60)
            if task['カテゴリ'] == "勉強":
                st.session_state.study_time_total += elapsed_minutes
            else:
                st.session_state.refresh_time_total += elapsed_minutes
                
            log_activity(task['タスク'], task['カテゴリ'], elapsed_minutes, task['BGM'])
            
            components.html("<script>sessionStorage.clear();</script>", height=0)
            time.sleep(0.5)
            
            st.session_state.page = 'dashboard'
            st.rerun()
            
    with col2:
        if task['カテゴリ'] == "勉強":
            if st.button("🚨 集中切れ！(SOS)", use_container_width=True):
                elapsed_minutes = int((time.time() - st.session_state.start_time) / 60)
                st.session_state.study_time_total += elapsed_minutes
                log_activity(task['タスク'], "勉強(中断)", elapsed_minutes, task['BGM'], "集中切れSOS")
                
                components.html("<script>sessionStorage.clear();</script>", height=0)
                time.sleep(0.5)
                
                st.session_state.sos_task = random.choice(SOS_LIST)
                st.session_state.page = 'sos'
                st.rerun()

# ==========================================
# 画面3: SOS（緊急リセットモード）
# ==========================================
elif st.session_state.page == 'sos':
    st.warning("集中力が切れましたね。自分を責めず、一旦リセットしましょう！")
    st.markdown(f"<h2 style='text-align: center;'>緊急指令：【{st.session_state.sos_task}】 を実行せよ！</h2>", unsafe_allow_html=True)
    
    if st.session_state.sos_task == "Geminiと話す":
        st.info("💡 チャットを開いて、「今集中が切れて辛い」「何が原因か分からない」と正直に打ち明けてみてください。いつでも壁打ち相手になります。")

    if st.button("リセット完了！ダッシュボードへ戻る", use_container_width=True):
        log_activity(st.session_state.sos_task, "SOSリセット", 0, "なし", "SOS完了")
        st.session_state.page = 'dashboard'
        st.rerun()

# --- サイドバー：ログの確認とエクスポート ---
with st.sidebar:
    st.header("データ管理")
    st.write("※アプリを閉じる前に必ずダウンロードしてください")
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("履歴をCSVでダウンロード", data=csv, file_name="activity_log.csv", mime="text/csv")