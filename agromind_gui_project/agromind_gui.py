#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import threading
import os
from pathlib import Path

# 你的 AI 模組（OpenVINO 推論）
from agromind_ai import recommend

# ===== 顏色設定 =====
BG = "#0080FF"      # 主背景
CARD_BG = "#f2f6ff" # 區塊（卡片）背景
FG = "#ffffff"      # 白字
TEXT_BG = "#0f172a" # 輸出框底色
TEXT_FG = "#e6edf3" # 輸出框文字
BTN_BG = "#005ad3"  # 按鈕底色
BTN_FG = "#ffffff"  # 按鈕文字

# ===== GUI 初始化 =====
root = tk.Tk()
root.title("🌾 AgroMind AI - 智慧農業建議系統 (OpenVINO)")
root.geometry("780x720")
root.configure(bg=BG)

# ---- 頂部列：標題（左） + 關閉程式按鈕（右） ----
topbar = tk.Frame(root, bg=BG)
topbar.pack(fill="x", padx=12, pady=(14, 6))

title_label = tk.Label(
    topbar,
    text="AgroMind AI 智慧農業建議（OpenVINO）",
    font=("Microsoft JhengHei", 18, "bold"),
    fg=FG,
    bg=BG
)
title_label.pack(side="left")

def style_button(b: tk.Button, width=18):
    b.configure(bg=BTN_BG, fg=BTN_FG, activebackground="#004ab0", activeforeground=BTN_FG,
                relief="ridge", bd=2, font=("Microsoft JhengHei", 11), width=width)

btn_quit = tk.Button(topbar, text="關閉程式", command=root.destroy)
style_button(btn_quit, width=10)
btn_quit.pack(side="right")

# 外層容器
container = tk.Frame(root, bg=BG)
container.pack(padx=16, pady=8, fill="both", expand=True)

# ====== 輸入卡片 ======
card = tk.Frame(container, bg=CARD_BG, bd=0, highlightthickness=1, highlightbackground="#c3d7ff")
card.pack(fill="x", pady=8)
header = tk.Label(card, text="輸入參數", bg=CARD_BG, fg="#0b0f14", font=("Microsoft JhengHei", 12, "bold"))
header.grid(row=0, column=0, padx=12, pady=(12, 4), sticky="w", columnspan=2)

tk.Label(card, text="作物種類：", bg=CARD_BG, fg="#0b0f14", font=("Microsoft JhengHei", 11)).grid(row=1, column=0, padx=12, pady=8, sticky="e")
crop_var = tk.StringVar(value="rice")
crop_combo = ttk.Combobox(card, textvariable=crop_var, values=["rice", "corn", "wheat", "soybean", "leafy", "fruit"], width=22)
crop_combo.grid(row=1, column=1, padx=12, pady=8, sticky="w")

tk.Label(card, text="地區名稱：", bg=CARD_BG, fg="#0b0f14", font=("Microsoft JhengHei", 11)).grid(row=2, column=0, padx=12, pady=8, sticky="e")
loc_entry = ttk.Entry(card, width=25)
loc_entry.insert(0, "台南市永康區")
loc_entry.grid(row=2, column=1, padx=12, pady=8, sticky="w")

tk.Label(card, text="日期（可留空）：", bg=CARD_BG, fg="#0b0f14", font=("Microsoft JhengHei", 11)).grid(row=3, column=0, padx=12, pady=8, sticky="e")
date_entry = ttk.Entry(card, width=25)
date_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
date_entry.grid(row=3, column=1, padx=12, pady=8, sticky="w")

# ====== 按鈕列 ======
btns = tk.Frame(container, bg=BG)
btns.pack(fill="x", pady=(6, 0))

btn_run = tk.Button(btns, text="執行 AI 建議")
style_button(btn_run)
btn_run.pack(side="left", padx=8, pady=6)

btn_export = tk.Button(btns, text="匯出 PDF 報告")
style_button(btn_export)
btn_export.pack(side="left", padx=8, pady=6)

# ====== 輸出區 ======
out_card = tk.Frame(container, bg=CARD_BG, bd=0, highlightthickness=1, highlightbackground="#c3d7ff")
out_card.pack(fill="both", expand=True, pady=10)
out_header = tk.Label(out_card, text="分析結果", bg=CARD_BG, fg="#0b0f14", font=("Microsoft JhengHei", 12, "bold"))
out_header.pack(anchor="w", padx=12, pady=(12, 6))

output_box = tk.Text(out_card, height=22, wrap="word", bg=TEXT_BG, fg=TEXT_FG, insertbackground="white", font=("Consolas", 11))
output_box.pack(padx=12, pady=12, fill="both", expand=True)
output_box.insert("end", "（尚未執行建議）\n")

_last_result = None  # 最近一次分析結果

# ====== 執行 AI 建議 ======
def run_recommend():
    crop = crop_var.get().strip()
    location = loc_entry.get().strip()
    date_iso = date_entry.get().strip()
    output_box.delete("1.0", "end")
    output_box.insert("end", "正在分析中...\n")

    def task():
        global _last_result
        try:
            data = recommend(crop, location, date_iso if date_iso else None)
            _last_result = data
            if not data.get("ok"):
                root.after(0, lambda: output_box.insert("end", f"❌ 錯誤：{data.get('error')}\n"))
                return

            ctx = data["context"]
            sc = data["model_scores"]
            text = (
                f"🌾 作物：{data['input']['crop']}\n"
                f"📍 地區：{data['input']['location']}\n"
                f"🕒 日期：{data['input']['date']}\n\n"
                f"🌤 模擬天氣資料：\n"
                f"  氣溫：{ctx['temp']} °C\n"
                f"  濕度：{ctx['humidity']} %\n"
                f"  降雨量：{ctx['rainfall']} mm\n"
                f"  日照時數：{ctx['sunlight']} 小時\n\n"
                f"📊 AI 推論結果：\n"
                f"  灌溉等級：{sc['irrigation_level']}\n"
                f"  灌溉建議：{sc['irrigation_advice']}\n\n"
                f"  施肥等級：{sc['fertilization_level']}\n"
                f"  施肥建議：{sc['fertilization_advice']}\n"
            )
            def update_ui():
                output_box.delete("1.0", "end")
                output_box.insert("end", text)
            root.after(0, update_ui)

        except Exception as e:
            root.after(0, lambda: output_box.insert("end", f"⚠️ 錯誤發生：{e}\n"))

    threading.Thread(target=task, daemon=True).start()

btn_run.configure(command=run_recommend)

# ====== PDF 報告：中文字型註冊 ======
def _register_cjk_fonts():
    """
    1) 優先使用專案內 ./fonts/NotoSansTC-Regular.ttf / -Bold.ttf
    2) 找不到時，嘗試 Windows 微軟正黑體 msjh.ttc
    回傳 (regular_name, bold_name)
    """
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    except Exception as e:
        raise RuntimeError("ReportLab 尚未安裝，請先：pip install reportlab") from e

    fonts_dir = Path(__file__).parent / "fonts"
    reg_path = fonts_dir / "NotoSansTC-Regular.ttf"
    bold_path = fonts_dir / "NotoSansTC-Bold.ttf"

    if reg_path.exists() and bold_path.exists():
        pdfmetrics.registerFont(TTFont("NSTC", str(reg_path)))
        pdfmetrics.registerFont(TTFont("NSTC-Bold", str(bold_path)))
        return "NSTC", "NSTC-Bold"

    win_font = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "msjh.ttc"
    if win_font.exists():
        try:
            pdfmetrics.registerFont(TTFont("MSJH", str(win_font)))
            pdfmetrics.registerFont(TTFont("MSJH-Bold", str(win_font)))
            return "MSJH", "MSJH-Bold"
        except Exception:
            pass

    try:
        pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
        pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))
        return "HeiseiKakuGo-W5", "HeiseiMin-W3"
    except Exception:
        pass

    raise RuntimeError(
        "找不到可用的中文字型。請建立 fonts/ 並放入 NotoSansTC-Regular.ttf 與 NotoSansTC-Bold.ttf。"
    )

# ====== 匯出 PDF ======
def export_pdf():
    global _last_result
    if not _last_result or not _last_result.get("ok"):
        messagebox.showwarning("匯出 PDF", "尚無可匯出的分析結果，請先執行 AI 建議。")
        return

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        messagebox.showerror(
            "缺少套件",
            "需要安裝 reportlab 才能匯出 PDF。\n\n請在命令列執行：\n    pip install reportlab"
        )
        return

    # 註冊中文字型
    try:
        font_reg, font_bold = _register_cjk_fonts()
    except Exception as e:
        messagebox.showerror("字型錯誤", str(e))
        return

    save_path = filedialog.asksaveasfilename(
        parent=root,
        title="另存新檔 (PDF)",
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not save_path:
        return

    data = _last_result
    ctx = data["context"]
    sc = data["model_scores"]

    doc = SimpleDocTemplate(save_path, pagesize=A4, title="AgroMind AI Report")

    base_styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCJK", parent=base_styles["Title"], fontName=font_bold, wordWrap="CJK")
    h2_style = ParagraphStyle("H2CJK", parent=base_styles["Heading2"], fontName=font_bold, wordWrap="CJK")
    normal_style = ParagraphStyle("NormalCJK", parent=base_styles["Normal"], fontName=font_reg, wordWrap="CJK")
    italic_style = ParagraphStyle("ItalicCJK", parent=base_styles["Italic"], fontName=font_reg, wordWrap="CJK")

    Story = [
        Paragraph("AgroMind AI – 農業建議報告", title_style),
        Spacer(1, 12),
        Paragraph(
            f"產出時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
            f"作物：{data['input']['crop']}　地區：{data['input']['location']}　日期：{data['input']['date']}",
            normal_style
        ),
        Spacer(1, 18),
    ]

    table1 = Table([
        ["項目", "值"],
        ["氣溫 (°C)", f"{ctx['temp']}"],
        ["濕度 (%)", f"{ctx['humidity']}"],
        ["降雨量 (mm)", f"{ctx['rainfall']}"],
        ["日照時數 (hr)", f"{ctx['sunlight']}"],
    ], colWidths=[120, 380])
    table1.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), font_reg),
        ('FONTNAME', (0,0), (-1,0), font_bold),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e6f0ff")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#003366")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#99b8ff")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#c2d6ff")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f7fbff")]),
    ]))
    Story += [Paragraph("一、環境與特徵資料", h2_style), Spacer(1, 6), table1, Spacer(1, 16)]

    table2 = Table([
        ["項目", "等級", "建議"],
        ["灌溉", sc["irrigation_level"], sc["irrigation_advice"]],
        ["施肥", sc["fertilization_level"], sc["fertilization_advice"]],
    ], colWidths=[80, 80, 340])
    table2.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), font_reg),
        ('FONTNAME', (0,0), (-1,0), font_bold),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e6f0ff")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#003366")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#99b8ff")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#c2d6ff")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f7fbff")]),
    ]))
    Story += [Paragraph("二、AI 建議摘要", h2_style), Spacer(1, 6), table2, Spacer(1, 24)]
    Story += [Paragraph("備註：本系統為純軟體示範，資料為模擬之環境參數；實務應搭配感測器資料與在地農藝知識。", italic_style)]

    try:
        doc.build(Story)
        messagebox.showinfo("匯出完成", f"報告已儲存：\n{save_path}")
        try:
            if os.name == "nt":
                os.startfile(os.path.dirname(save_path))
        except Exception:
            pass
    except Exception as e:
        messagebox.showerror("匯出失敗", f"產生 PDF 失敗：{e}")

btn_export.configure(command=export_pdf)

# ====== 啟動 GUI ======
root.mainloop()
