import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="TsukuriAI - 作例ギャラリー", page_icon="⬡", layout="wide")

# =====================================================
# グローバルCSS
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
</style>
""", unsafe_allow_html=True)


# =====================================================
# ヘッダー
# =====================================================
header_html = """
<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&family=Noto+Sans+JP:wght@300;400;600;700;900&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter','Noto Sans JP',sans-serif;background:#000;color:#e6edf3;overflow:hidden}
.header{
    position:relative;padding:50px 48px 40px;
    background:radial-gradient(ellipse at 50% 50%,rgba(99,102,241,0.06),transparent 60%),#000;
    border-bottom:1px solid rgba(99,102,241,0.08)
}
.nav{display:flex;align-items:center;justify-content:space-between;margin-bottom:40px}
.nav-logo{font-size:1.3rem;font-weight:800;letter-spacing:-0.5px;
    background:linear-gradient(135deg,#fff,#6366f1);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.nav-badge{padding:5px 14px;border-radius:8px;font-size:0.7rem;font-weight:700;
    letter-spacing:2px;text-transform:uppercase;
    background:rgba(139,92,246,0.1);color:#8b5cf6;border:1px solid rgba(139,92,246,0.2)}
.label{font-size:0.7rem;letter-spacing:6px;color:rgba(99,102,241,0.8);text-transform:uppercase;margin-bottom:10px;
    display:flex;align-items:center;gap:12px}
.label::before{content:'';width:30px;height:1px;background:linear-gradient(90deg,#6366f1,transparent)}
.title{font-size:2.5rem;font-weight:800;color:#fff;letter-spacing:-1px}
.title span{background:linear-gradient(135deg,#8b5cf6,#0ea5e9);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.subtitle{font-size:0.9rem;color:rgba(230,237,243,0.35);margin-top:8px;max-width:550px;line-height:1.7}
</style></head>
<body>
<div class="header">
    <div class="nav">
        <div class="nav-logo">⬡ TsukuriAI</div>
        <div class="nav-badge">Gallery</div>
    </div>
    <p class="label">Use Cases</p>
    <h1 class="title">作例<span>ギャラリー</span></h1>
    <p class="subtitle">TsukuriAIで実際に生成できるパーツの例です。<br>「このプロンプトで作る」ボタンを押すと、メインページに同じ指示がセットされます。</p>
</div>
</body></html>
"""
components.html(header_html, height=280, scrolling=False)


# =====================================================
# SVGピクトグラム（ミニマルなラインアート）
# =====================================================
ICONS = {
    "cable": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9h3a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2H4"/><path d="M20 9h-3a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2h3"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="2" y1="9" x2="2" y2="15"/><line x1="22" y1="9" x2="22" y2="15"/></svg>',
    "rack": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="3" width="16" height="18" rx="1"/><line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="12" y1="3" x2="12" y2="9"/></svg>',
    "remote": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="2" width="12" height="20" rx="3"/><circle cx="12" cy="8" r="2"/><line x1="10" y1="14" x2="14" y2="14"/><line x1="10" y1="17" x2="14" y2="17"/></svg>',
    "laptop": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="2"/><line x1="2" y1="20" x2="22" y2="20"/><path d="M7 20l1-4h8l1 4"/></svg>',
    "headphone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3v5z"/><path d="M3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3v5z"/></svg>',
    "hexpen": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l8 4.5v9L12 20l-8-4.5v-9L12 2z"/><path d="M12 7l4 2.25v4.5L12 16l-4-2.25v-4.5L12 7z"/></svg>',
    "bracket": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4v16h16"/><path d="M4 4l10 10"/><circle cx="8" cy="16" r="1.5"/><circle cx="16" cy="16" r="1.5"/><circle cx="8" cy="8" r="1.5"/></svg>',
    "doorstop": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 20h18"/><path d="M5 20l2-14h4l-3 14"/><line x1="15" y1="8" x2="15" y2="20"/><rect x="13" y="4" width="4" height="4" rx="0.5"/></svg>',
    "cap": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="14" r="6"/><path d="M12 8V3"/><path d="M9 14a3 3 0 0 1 6 0"/><line x1="8" y1="20" x2="16" y2="20"/></svg>',
    "star": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/><circle cx="12" cy="1" r="1"/></svg>',
    "dino": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 4c2 0 3 1 3 3v2l-2 1v3l-3 1v3h-2v-3h-2v3H10v-3l-4-2v-2l-2-1c0-2 1-4 3-4h2l1-1h4l1 1h3z"/><circle cx="17" cy="7" r="0.5" fill="currentColor"/><path d="M7 8l-1 2"/></svg>',
}


# =====================================================
# ギャラリーデータ
# =====================================================
gallery_items = [
    {
        "category": "生活・収納",
        "items": [
            {
                "title": "ケーブルオーガナイザー",
                "desc": "デスク上のケーブルを整理するクリップ型オーガナイザー。3本のケーブルを固定できるスリット付き。",
                "prompt": "デスクに貼り付けるケーブルオーガナイザー。幅60mm、奥行き25mm、高さ15mm。上部に直径5mmのケーブルが通る溝を3本、等間隔で配置。底面はフラットで両面テープで固定できるようにする。角は全て丸くすること。",
                "difficulty": "初級",
                "time": "約10秒",
                "icon": "cable"
            },
            {
                "title": "隙間収納ラック",
                "desc": "冷蔵庫と壁の隙間にぴったり収まるスリムなラック。調味料ボトルが3本並ぶ。",
                "prompt": "幅35mm、奥行き100mm、高さ120mmの縦長のスリム収納ラック。内部に3段の棚板（厚さ2mm）を等間隔に設置。両側面は支柱のみで開放的なデザイン。底面にはすべり止め用の小さな突起を四隅に付ける。",
                "difficulty": "中級",
                "time": "約15秒",
                "icon": "rack"
            },
            {
                "title": "リモコンスタンド",
                "desc": "テレビのリモコンを立てて収納するスタンド。2本まで並べられる。",
                "prompt": "テーブルに置くリモコンスタンド。外寸は幅70mm、奥行き40mm、高さ80mm。内部に仕切りを1つ入れて2つのスロットを作る。各スロットの幅は30mm。前面は斜めにカットして取り出しやすくする。底面は安定するようフラットに。",
                "difficulty": "初級",
                "time": "約10秒",
                "icon": "remote"
            },
        ]
    },
    {
        "category": "デスク・ガジェット",
        "items": [
            {
                "title": "ノートPCスタンド",
                "desc": "ノートPCを傾けて置けるシンプルなスタンド。放熱性も考慮し、底面にスリットを配置。",
                "prompt": "ノートPC用のデスクスタンド。幅250mm、奥行き200mm。角度は15度の傾斜。前面にPCがずれ落ちないようストッパーの突起（高さ5mm）を付ける。底面には放熱用のスリット（幅3mm）を5本並行に配置。厚さは全体的に4mm。",
                "difficulty": "上級",
                "time": "約20秒",
                "icon": "laptop"
            },
            {
                "title": "ヘッドホンハンガー",
                "desc": "机の端に引っ掛けるタイプのヘッドホンハンガー。厚み20mmまでの天板に対応。",
                "prompt": "机の端にクリップで挟むヘッドホンハンガー。クリップ部の内寸は20mm（天板の厚みに対応）。ハンガー部分は下方向に伸びるフック形状で、長さ80mm、幅30mm。フックの先端は丸くしてヘッドバンドが傷まないようにする。全体の厚みは8mm。",
                "difficulty": "中級",
                "time": "約15秒",
                "icon": "headphone"
            },
            {
                "title": "ペンスタンド（六角形）",
                "desc": "六角形のハニカムデザインが美しいペンスタンド。7本までペンを収納。",
                "prompt": "六角形をベースにしたペンスタンド。外接円の直径は70mm、高さ90mm。内部に7つの六角形の穴（直径12mm）をハニカム配列で配置。底面は厚さ3mmの板で塞ぐ。壁の厚みは2mm。",
                "difficulty": "上級",
                "time": "約20秒",
                "icon": "hexpen"
            },
        ]
    },
    {
        "category": "DIY・修理パーツ",
        "items": [
            {
                "title": "L字ブラケット（強化型）",
                "desc": "棚板の固定に使えるL字型の補強ブラケット。M4ネジ対応の穴付き。",
                "prompt": "壁に取り付ける強化L字ブラケット。両辺とも50mm、幅30mm、厚さ5mm。各辺にM4ネジ用の穴（直径4.5mm）を2つずつ等間隔に配置。内側の角にはリブ（補強板、三角形、厚さ3mm）を追加して強度を確保する。",
                "difficulty": "中級",
                "time": "約12秒",
                "icon": "bracket"
            },
            {
                "title": "ドアストッパー",
                "desc": "くさび型のシンプルなドアストッパー。ゴム足なしでも滑りにくい溝付き。",
                "prompt": "くさび型のドアストッパー。長さ100mm、幅40mm。厚い側の高さは25mm、薄い側は2mm。底面に滑り止め用の横溝（深さ1mm、間隔3mm）を全面に入れる。持ちやすいよう上面後端に指をかける窪み（幅20mm、深さ3mm）を付ける。",
                "difficulty": "初級",
                "time": "約10秒",
                "icon": "doorstop"
            },
            {
                "title": "家具の脚キャップ",
                "desc": "椅子やテーブルの脚に被せる保護キャップ。床の傷防止に。",
                "prompt": "丸パイプ脚用の保護キャップ。外径26mm（内径25mmのパイプに被せる）。高さ15mm。内部は空洞で壁の厚みは1.5mm。底面は厚さ2mmで塞いで床と接するようにする。内側上部に脚が抜けにくいよう、直径24.5mmのリブを1周入れる。",
                "difficulty": "中級",
                "time": "約12秒",
                "icon": "cap"
            },
        ]
    },
    {
        "category": "子供の作品・アート",
        "items": [
            {
                "title": "星型のキーホルダー",
                "desc": "子供が喜ぶ星の形のキーホルダー。上部に紐を通す穴付き。",
                "prompt": "五芒星（星型）のキーホルダー。外接円の直径は40mm、厚さは4mm。上部の頂点に紐やリングを通すための穴（直径4mm）を開ける。表面に「STAR」の文字を1mm深さで彫刻する。",
                "difficulty": "初級",
                "time": "約8秒",
                "icon": "star"
            },
            {
                "title": "恐竜のネームプレート",
                "desc": "子供の名前が入るティラノサウルス型のプレート。机やドアに飾れるサイズ。",
                "prompt": "ティラノサウルスのシルエットを模したネームプレート。全体の幅は100mm、高さは60mm、厚さは5mm。恐竜の胴体部分に「TARO」の文字を浮き彫り（高さ1mm）で入れる。背面にフラットな部分を設けて自立できるようにする。",
                "difficulty": "上級",
                "time": "約20秒",
                "icon": "dino"
            },
        ]
    },
]


# =====================================================
# ギャラリー表示
# =====================================================
for section in gallery_items:
    # カテゴリヘッダー
    cat_html = f"""
    <div style="
        font-family:'Inter','Noto Sans JP',sans-serif;
        padding:24px 0 8px;
    ">
        <span style="font-size:0.65rem;letter-spacing:4px;color:rgba(99,102,241,0.6);text-transform:uppercase;font-weight:600;">Category</span>
        <h3 style="font-size:1.4rem;font-weight:700;color:#fff;margin-top:4px;">{section['category']}</h3>
    </div>
    """
    st.markdown(cat_html, unsafe_allow_html=True)
    
    cols = st.columns(len(section["items"]), gap="medium")
    
    for i, item in enumerate(section["items"]):
        with cols[i]:
            # 難易度バッジの色
            if item["difficulty"] == "初級":
                diff_bg = "rgba(16,185,129,0.12)"
                diff_color = "#10b981"
                diff_border = "rgba(16,185,129,0.25)"
            elif item["difficulty"] == "中級":
                diff_bg = "rgba(14,165,233,0.12)"
                diff_color = "#0ea5e9"
                diff_border = "rgba(14,165,233,0.25)"
            else:
                diff_bg = "rgba(139,92,246,0.12)"
                diff_color = "#8b5cf6"
                diff_border = "rgba(139,92,246,0.25)"
            
            icon_svg = ICONS.get(item["icon"], "")
            
            card_html = f"""
            <div style="
                background:linear-gradient(135deg,rgba(15,18,30,0.9),rgba(20,24,38,0.7));
                border:1px solid rgba(99,102,241,0.08);border-radius:18px;
                padding:28px 22px;
                font-family:'Inter','Noto Sans JP',sans-serif;
                min-height:280px;
            ">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                    <div style="width:44px;height:44px;border-radius:12px;
                        background:linear-gradient(135deg,rgba(99,102,241,0.12),rgba(14,165,233,0.08));
                        border:1px solid rgba(99,102,241,0.15);
                        display:flex;align-items:center;justify-content:center;
                        color:rgba(99,102,241,0.8);">
                        <div style="width:22px;height:22px;">{icon_svg}</div>
                    </div>
                    <div style="display:flex;gap:6px;">
                        <span style="padding:3px 10px;border-radius:6px;font-size:0.6rem;font-weight:700;
                            letter-spacing:1px;background:{diff_bg};color:{diff_color};border:1px solid {diff_border}">{item['difficulty']}</span>
                        <span style="padding:3px 10px;border-radius:6px;font-size:0.6rem;font-weight:600;
                            letter-spacing:1px;background:rgba(230,237,243,0.04);color:rgba(230,237,243,0.3);
                            border:1px solid rgba(230,237,243,0.06)">{item['time']}</span>
                    </div>
                </div>
                <h4 style="font-size:1.05rem;font-weight:700;color:#fff;margin-bottom:8px;">{item['title']}</h4>
                <p style="font-size:0.8rem;color:rgba(230,237,243,0.4);line-height:1.7;margin-bottom:12px;">{item['desc']}</p>
                <details style="cursor:pointer;">
                    <summary style="font-size:0.72rem;color:rgba(99,102,241,0.7);font-weight:600;letter-spacing:0.5px;">
                        プロンプトを見る
                    </summary>
                    <p style="font-size:0.72rem;color:rgba(230,237,243,0.3);line-height:1.6;margin-top:8px;
                        padding:10px;background:rgba(99,102,241,0.04);border-radius:8px;border:1px solid rgba(99,102,241,0.08);">
                        {item['prompt']}
                    </p>
                </details>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            if st.button(f"→ このプロンプトで作る", key=f"gallery_{section['category']}_{i}"):
                st.session_state.text_area_input = item['prompt']
                st.switch_page("app.py")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)


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
    <p class="text">© 2026 TsukuriAI Inc. — Gallery</p>
</div>
</body></html>
"""
components.html(footer_html, height=130, scrolling=False)
