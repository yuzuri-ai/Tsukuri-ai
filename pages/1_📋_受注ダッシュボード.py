import os
import json
from pathlib import Path
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="TsukuriAI - 受注ダッシュボード", page_icon="⬡", layout="wide")

# =====================================================
# 案件管理ユーティリティ（app.pyと共有）
# =====================================================
ORDERS_DIR = Path(__file__).parent.parent / "orders"
ORDERS_DIR.mkdir(exist_ok=True)
ORDERS_JSON = ORDERS_DIR / "orders.json"

def load_orders():
    if ORDERS_JSON.exists():
        with open(ORDERS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def update_order_status(order_id, new_status):
    orders = load_orders()
    for order in orders:
        if order["id"] == order_id:
            order["status"] = new_status
            order["accepted_at"] = datetime.now().isoformat()
            break
    with open(ORDERS_JSON, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

# =====================================================
# グローバルCSS（ダークテーマ統一）
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Sans+JP:wght@300;400;500;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Noto Sans JP', sans-serif;
    color: #e6edf3;
}
.stApp { background: #000000; }
header[data-testid="stHeader"] { background: transparent !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.block-container { padding-top: 0 !important; max-width: 100% !important; }
iframe { border: none !important; }

div.stButton > button:first-child {
    background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 50%, #8b5cf6 100%);
    color: white; font-weight: 700; border-radius: 12px; border: none;
    padding: 0.6rem 1.5rem; font-size: 0.9rem;
    transition: all 0.4s cubic-bezier(0.4,0,0.2,1);
    box-shadow: 0 4px 20px rgba(99,102,241,0.4);
}
div.stButton > button:first-child:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(99,102,241,0.6);
}
div.stDownloadButton > button:first-child {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white; font-weight: 700; border-radius: 12px; border: none;
    padding: 0.6rem 1.5rem; box-shadow: 0 4px 20px rgba(16,185,129,0.4);
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# ページヘッダー
# =====================================================
header_html = """
<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&family=Noto+Sans+JP:wght@300;400;600;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter','Noto Sans JP',sans-serif;background:#000;color:#e6edf3;overflow:hidden}
.header{
    position:relative;padding:50px 48px 40px;
    background:radial-gradient(ellipse at 30% 50%,rgba(99,102,241,0.08),transparent 60%),
               radial-gradient(ellipse at 80% 30%,rgba(14,165,233,0.05),transparent 50%),#000;
    border-bottom:1px solid rgba(99,102,241,0.08)
}
.nav{display:flex;align-items:center;justify-content:space-between;margin-bottom:40px}
.nav-logo{font-size:1.3rem;font-weight:800;letter-spacing:-0.5px;
    background:linear-gradient(135deg,#fff,#6366f1);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.nav-badge{padding:5px 14px;border-radius:8px;font-size:0.7rem;font-weight:700;
    letter-spacing:2px;text-transform:uppercase;
    background:rgba(14,165,233,0.1);color:#0ea5e9;border:1px solid rgba(14,165,233,0.2)}
.title-row{display:flex;align-items:flex-end;justify-content:space-between}
.label{font-size:0.7rem;letter-spacing:6px;color:rgba(99,102,241,0.8);text-transform:uppercase;margin-bottom:10px;
    display:flex;align-items:center;gap:12px}
.label::before{content:'';width:30px;height:1px;background:linear-gradient(90deg,#6366f1,transparent)}
.title{font-size:2.5rem;font-weight:800;color:#fff;letter-spacing:-1px}
.title span{background:linear-gradient(135deg,#0ea5e9,#6366f1);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.subtitle{font-size:0.9rem;color:rgba(230,237,243,0.35);margin-top:8px}
</style></head>
<body>
<div class="header">
    <div class="nav">
        <div class="nav-logo">⬡ TsukuriAI</div>
        <div class="nav-badge">Owner Dashboard</div>
    </div>
    <p class="label">Dashboard</p>
    <div class="title-row">
        <div>
            <h1 class="title">受注<span>ダッシュボード</span></h1>
            <p class="subtitle">3Dプリンタオーナー向け — 案件の確認・受注・データダウンロード</p>
        </div>
    </div>
</div>
</body></html>
"""
components.html(header_html, height=260, scrolling=False)


# =====================================================
# スタッツ
# =====================================================
orders = load_orders()
open_orders = [o for o in orders if o.get("status") == "open"]
accepted_orders = [o for o in orders if o.get("status") == "accepted"]
completed_orders = [o for o in orders if o.get("status") == "completed"]

stats_html = f"""
<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;600;800&family=Noto+Sans+JP:wght@300;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter','Noto Sans JP',sans-serif;background:#000;overflow:hidden}}
.bar{{display:flex;justify-content:flex-start;gap:24px;padding:30px 48px}}
.stat{{
    flex:1;max-width:220px;
    background:linear-gradient(135deg,rgba(15,18,30,0.9),rgba(20,24,38,0.7));
    border:1px solid rgba(99,102,241,0.08);border-radius:16px;
    padding:24px;
    opacity:0;animation:fadeUp 0.6s forwards
}}
.stat:nth-child(1){{animation-delay:0.05s}}
.stat:nth-child(2){{animation-delay:0.15s}}
.stat:nth-child(3){{animation-delay:0.25s}}
.stat:nth-child(4){{animation-delay:0.35s}}
@keyframes fadeUp{{0%{{opacity:0;transform:translateY(15px)}}100%{{opacity:1;transform:translateY(0)}}}}
.stat-num{{font-size:2rem;font-weight:800;margin-bottom:4px}}
.blue{{background:linear-gradient(135deg,#6366f1,#0ea5e9);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.green{{background:linear-gradient(135deg,#10b981,#059669);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.purple{{background:linear-gradient(135deg,#8b5cf6,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.cyan{{background:linear-gradient(135deg,#0ea5e9,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.stat-label{{font-size:0.72rem;color:rgba(230,237,243,0.35);letter-spacing:2px;text-transform:uppercase}}
</style></head>
<body>
<div class="bar">
    <div class="stat"><div class="stat-num blue">{len(orders)}</div><div class="stat-label">全案件数</div></div>
    <div class="stat"><div class="stat-num cyan">{len(open_orders)}</div><div class="stat-label">受注待ち</div></div>
    <div class="stat"><div class="stat-num purple">{len(accepted_orders)}</div><div class="stat-label">製造中</div></div>
    <div class="stat"><div class="stat-num green">{len(completed_orders)}</div><div class="stat-label">完了</div></div>
</div>
</body></html>
"""
components.html(stats_html, height=130, scrolling=False)


# =====================================================
# 案件一覧
# =====================================================
if not orders:
    # 案件がない場合のエンプティステート
    empty_html = """
    <!DOCTYPE html><html><head><meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Noto+Sans+JP:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:'Inter','Noto Sans JP',sans-serif;background:#000;color:#e6edf3}
    .empty{text-align:center;padding:80px 20px}
    .empty-icon{font-size:4rem;margin-bottom:20px;opacity:0.3}
    .empty h3{font-size:1.3rem;font-weight:600;color:rgba(230,237,243,0.5);margin-bottom:8px}
    .empty p{font-size:0.85rem;color:rgba(230,237,243,0.25);max-width:400px;margin:0 auto;line-height:1.7}
    </style></head>
    <body>
    <div class="empty">
        <div class="empty-icon">⬡</div>
        <h3>まだ案件がありません</h3>
        <p>ユーザーがトップページで3Dデータを生成し「プリントを発注する」ボタンを押すと、ここに案件が表示されます。</p>
    </div>
    </body></html>
    """
    components.html(empty_html, height=300, scrolling=False)
else:
    # セクションタイトル
    section_title_html = """
    <!DOCTYPE html><html><head><meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;600;700;800&family=Noto+Sans+JP:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:'Inter','Noto Sans JP',sans-serif;background:#000;color:#e6edf3;padding:20px 48px 10px}
    .label{font-size:0.7rem;letter-spacing:6px;color:rgba(99,102,241,0.8);text-transform:uppercase;margin-bottom:8px;
        display:flex;align-items:center;gap:12px}
    .label::before{content:'';width:30px;height:1px;background:linear-gradient(90deg,#6366f1,transparent)}
    h2{font-size:1.6rem;font-weight:700;color:#fff;letter-spacing:-0.5px}
    </style></head>
    <body>
    <p class="label">Orders</p>
    <h2>案件一覧</h2>
    </body></html>
    """
    components.html(section_title_html, height=90, scrolling=False)

    # 案件を新しい順に表示
    for order in reversed(orders):
        oid = order["id"]
        desc = order["description"]
        created = order.get("created_at", "")
        status = order.get("status", "open")

        # 日付フォーマット
        try:
            dt = datetime.fromisoformat(created)
            date_str = dt.strftime("%Y/%m/%d %H:%M")
        except:
            date_str = created

        # ステータスに応じたバッジ色
        if status == "open":
            badge_bg = "rgba(14,165,233,0.12)"
            badge_border = "rgba(14,165,233,0.25)"
            badge_color = "#0ea5e9"
            badge_text = "受注待ち"
        elif status == "accepted":
            badge_bg = "rgba(139,92,246,0.12)"
            badge_border = "rgba(139,92,246,0.25)"
            badge_color = "#8b5cf6"
            badge_text = "製造中"
        else:
            badge_bg = "rgba(16,185,129,0.12)"
            badge_border = "rgba(16,185,129,0.25)"
            badge_color = "#10b981"
            badge_text = "完了"

        # 案件カード（HTMLで表示）
        card_html = f"""
        <div style="
            background:linear-gradient(135deg,rgba(15,18,30,0.9),rgba(20,24,38,0.7));
            border:1px solid rgba(99,102,241,0.08);border-radius:18px;
            padding:28px 32px;margin:0 0 2px;
            font-family:'Inter','Noto Sans JP',sans-serif;
            position:relative;overflow:hidden;
        ">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;">
                <div>
                    <span style="font-size:0.7rem;color:rgba(230,237,243,0.25);letter-spacing:2px;font-weight:600;">ORDER #{oid.upper()}</span>
                    <span style="margin-left:12px;display:inline-block;padding:3px 12px;border-radius:6px;font-size:0.65rem;font-weight:700;
                        letter-spacing:1px;background:{badge_bg};color:{badge_color};border:1px solid {badge_border}">{badge_text}</span>
                </div>
                <span style="font-size:0.75rem;color:rgba(230,237,243,0.2);">{date_str}</span>
            </div>
            <p style="font-size:0.92rem;color:rgba(230,237,243,0.7);line-height:1.7;margin-bottom:4px;">
                {desc[:120]}{'...' if len(desc) > 120 else ''}
            </p>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

        # 操作ボタン
        col1, col2, col3 = st.columns([1, 1, 2])
        
        stl_path = order.get("stl_file", "")
        
        with col1:
            if status == "open":
                if st.button(f"✅ 受注する", key=f"accept_{oid}"):
                    update_order_status(oid, "accepted")
                    st.rerun()
            elif status == "accepted":
                if st.button(f"🏁 完了にする", key=f"complete_{oid}"):
                    update_order_status(oid, "completed")
                    st.rerun()
            else:
                st.button("✓ 完了済み", key=f"done_{oid}", disabled=True)
        
        with col2:
            if os.path.exists(stl_path):
                with open(stl_path, "rb") as f:
                    st.download_button(
                        label="↓ CADデータ (STL)",
                        data=f,
                        file_name=f"order_{oid}.stl",
                        mime="application/octet-stream",
                        key=f"dl_{oid}"
                    )
            else:
                st.button("ファイルなし", key=f"nofile_{oid}", disabled=True)
        
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


# =====================================================
# フッター
# =====================================================
footer_html = """
<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter','Noto Sans JP',sans-serif;background:#000;color:#e6edf3}
.footer{text-align:center;padding:50px 48px 24px;border-top:1px solid rgba(99,102,241,0.06)}
.logo{font-size:1.1rem;font-weight:800;
    background:linear-gradient(135deg,#6366f1,#0ea5e9);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:6px}
.text{font-size:0.7rem;color:rgba(230,237,243,0.2);letter-spacing:2px}
</style></head>
<body>
<div class="footer">
    <p class="logo">⬡ TsukuriAI</p>
    <p class="text">© 2026 TsukuriAI Inc. — Owner Dashboard</p>
</div>
</body></html>
"""
components.html(footer_html, height=130, scrolling=False)
