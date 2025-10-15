# 🌾 AgroMind AI - 智慧農業建議系統 (OpenVINO 視窗版)

## 🧩 專案簡介
AgroMind AI 是一款以 Python 開發的 **智慧農業 AI 系統**，結合 Intel OpenVINO 推論引擎，
模擬作物環境並提供灌溉與施肥建議。使用者可透過圖形化視窗（Tkinter）操作，
輸入作物種類、地區與時間，即時取得 AI 推論結果與建議，
並可匯出 **繁體中文 PDF 報告**。

---

## 💻 功能特色
1. **AI 智慧推論**  
   - 使用 OpenVINO MLP 模型模擬智慧農業決策  
   - 依據天氣與作物需水係數生成「灌溉」與「施肥」建議

2. **可視化操作介面 (GUI)**  
   - Tkinter 製作的圖形化應用程式，背景配色為 `#0080FF`  
   - 一鍵執行 AI 推論或匯出 PDF 報告  
   - 內建「關閉程式」按鈕

3. **PDF 報告匯出**  
   - 自動生成包含天氣特徵與 AI 建議的報告  
   - 完整支援繁體中文（需提供字型檔 NotoSansTC-Regular.ttf / Bold.ttf）

4. **完全離線執行**  
   - 無需網路，所有推論與運算皆在本機完成

---

## 🧰 系統架構
```
agromind_gui_project/
├─ agromind_ai.py          # AI 模組（OpenVINO 推論邏輯）
├─ agromind_gui.py         # Tkinter 視窗主程式
├─ fonts/                  # 中文字型（需自行放入 NotoSansTC 字型）
└─ requirements.txt        # 套件需求清單
```

---

## ⚙️ 安裝與執行步驟

### 1️⃣ 建立虛擬環境
```bash
python -m venv .venv
.\.venv\Scriptsctivate
```

### 2️⃣ 安裝所需套件
```bash
pip install -r requirements.txt
```

### 3️⃣ 執行程式
```bash
python agromind_gui.py
```

---

## 📦 套件需求
主要套件如下（完整版本請參考 requirements.txt）：
```
openvino
numpy
reportlab
tkinter (Python 內建)
```

---

## 🧾 字型設定（避免中文亂碼）
1. 建立資料夾：`fonts/`
2. 下載字型：[Noto Sans TC (Google Fonts)](https://fonts.google.com/noto/specimen/Noto+Sans+TC)
3. 放入以下檔案：
   - `NotoSansTC-Regular.ttf`
   - `NotoSansTC-Bold.ttf`
4. 若無字型，程式會自動嘗試使用 Windows 的 `msjh.ttc`。

---

## 📋 專案用途
- 智慧農業 AI 模擬展示  
- AI 推論應用教學  
- 軟體工程或資料科學專題作品展示  

---

## 🧠 作者與參考
**作者：** Panas ziyi  
**架構參考：**  
[1] Intel OpenVINO™ Toolkit Documentation.  
[2] ReportLab PDF Library.  
[3] Tkinter Official Documentation (Python 3.10+).  

---

© 2025 AgroMind AI Project
