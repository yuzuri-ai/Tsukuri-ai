import os
import json
import uuid
import shutil
import base64
import subprocess
from datetime import datetime
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
from dotenv import load_dotenv

# --- 案件管理ユーティリティ ---
ORDERS_DIR = Path(__file__).parent / "orders"
ORDERS_DIR.mkdir(exist_ok=True)
ORDERS_JSON = ORDERS_DIR / "orders.json"

def load_orders():
    if ORDERS_JSON.exists():
        with open(ORDERS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_order(description: str, stl_filename: str, scad_code: str):
    orders = load_orders()
    order_id = str(uuid.uuid4())[:8]
    # STLファイルを案件フォルダにコピー
    dest_stl = ORDERS_DIR / f"{order_id}.stl"
    shutil.copy2(stl_filename, dest_stl)
    # SCADコードも保存
    dest_scad = ORDERS_DIR / f"{order_id}.scad"
    with open(dest_scad, "w", encoding="utf-8") as f:
        f.write(scad_code)
    orders.append({
        "id": order_id,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "status": "open",  # open / accepted / completed
        "stl_file": str(dest_stl),
        "scad_file": str(dest_scad),
    })
    with open(ORDERS_JSON, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)
    return order_id

# --- 設定・初期化 ---
load_dotenv()
st.set_page_config(page_title="TsukuriAI - 思いのままに造ろう", page_icon="⬡", layout="wide")

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
    padding: 0.7rem 2rem; font-size: 1rem; letter-spacing: 0.5px;
    transition: all 0.4s cubic-bezier(0.4,0,0.2,1);
    box-shadow: 0 4px 20px rgba(99,102,241,0.4);
    text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}
div.stButton > button:first-child:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 35px rgba(99,102,241,0.6);
}
div.stDownloadButton > button:first-child {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white; font-weight: 700; border-radius: 12px; border: none;
    padding: 0.7rem 2rem; box-shadow: 0 4px 20px rgba(16,185,129,0.4);
}
textarea {
    background: rgba(15,18,25,0.9) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 14px !important;
    color: #e6edf3 !important; font-size: 1rem !important;
    padding: 16px !important;
}
textarea:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 30px rgba(99,102,241,0.15) !important;
}
</style>
""", unsafe_allow_html=True)

# APIクライアント
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# =====================================================
# バックエンドロジック — 2段階AIパイプライン
# =====================================================

# ステージ1: プロンプトエンハンサー
# 素人の曖昧な入力をプロ仕様の設計要件書に自動変換する
ENHANCER_PROMPT = """あなたは3Dプリント製品の設計コンサルタントです。
ユーザーから受け取った自然言語の要望を分析し、プロのハードウェアエンジニアが設計に必要とする「完全な設計要件書」に変換してください。

## あなたの役割
ユーザーは3Dプリントや設計の素人です。入力には寸法、構造、材質に関する情報が不足していることがほとんどです。
あなたは20年のプロダクトデザイン経験を持つエンジニアとして、不足情報を全て補完してください。

## 補完すべき項目（不足している場合は必ず常識的な値を追加）
1. **全体寸法**: 幅(W)×奥行(D)×高さ(H)をmm単位で。実用品として自然なサイズを推定
2. **壁の厚み**: 最低1.5mm以上。耐荷重部品は3mm以上を推奨
3. **角の処理**: 全ての内角にフィレット（R=1〜3mm）、外角にチャンファー（C=0.5〜1mm）を追加
4. **穴やネジ穴**: 直径+0.4mmのクリアランスを含む。M3穴=3.4mm、M4穴=4.4mm、M5穴=5.4mm
5. **嵌合部品**: はめ合い公差=+0.3mm、スライド部=+0.5mm
6. **構造補強**: 必要に応じてリブ、ガセット、補強板の追加を推奨
7. **底面設計**: 3Dプリントの第一層定着のため、底面はフラット。接地面には微小な面取り(0.3mm)を追加
8. **オーバーハング回避**: 45度以上のオーバーハングが発生しないよう形状を工夫。不可避の場合は面取りで対応
9. **ブリッジ制限**: 支持なしの水平スパンは10mm以内に
10. **印刷方向**: 最適な印刷方向（ビルドプレートに対するパーツの向き）を明記

## 出力フォーマット
以下の形式で、**日本語で**設計要件書を出力してください。余計な前置きは不要。

---
【製品名】(推定した製品名)
【用途】(推定した使用シーン)
【全体寸法】W×D×H mm
【壁厚】○mm
【印刷方向】(底面を下にして印刷 等)
【詳細仕様】
- (箇条書きで全ての設計要件を記述)
- (角の丸め、穴のサイズ、構造補強なども含む)
【特記事項】
- (3Dプリントに関する注意点)
---"""


# ステージ2: エキスパートOpenSCADコード生成
# 設計要件書からプロ品質のOpenSCADコードを生成する
GENERATOR_PROMPT = """あなたは3Dプリント向けOpenSCAD設計のエキスパートエンジニアです。

## ミッション
与えられた設計要件書から、FDM 3Dプリンタで高品質に印刷できるOpenSCADコードを生成してください。

## 必須設計ルール（絶対に守ること）
### 寸法・構造
- 全ての寸法はmm単位
- 壁厚は最低1.5mm（強度が必要な箇所は3mm以上）
- 最小フィーチャーサイズは1mm以上
- テキストの最小サイズは3mm、フォントはsans-serif系
- 角柱・角の内側にはfillet(R≥1mm)を追加
- 外角にはchamfer(C≥0.5mm)を追加
- 穴にはクリアランス+0.4mmを追加

### 3Dプリント最適化
- 底面（ビルドプレート接地面）は完全にフラットにする
- 45度以上のオーバーハングを回避する設計にする
- サポート材が不要なデザインを最優先にする
- ブリッジ（空中水平スパン）は10mm以内に抑える
- 大きな平面にはわずかな面取りを追加（反り防止）
- 嵌合・はめ合い部品には適切な公差(+0.3〜0.5mm)を設ける

### OpenSCADコーディング規約
- $fn=60以上（曲面の滑らかさ）
- 全ての主要寸法をファイル冒頭でパラメータ(変数)として定義する
- 変数名はsnake_caseで分かりやすく命名する（例: wall_thickness, base_width）
- 日本語コメントで各セクションの意図を説明する
- module()を活用して部品を分割し可読性を高める
- minkowski()やhull()でフィレットを実現する
- difference()の際は幾何学的曖昧さを避けるため0.01mmのイプシロンを使う

### 出力
Markdownのコードブロック（```openscad ... ```）で囲んでOpenSCADコードのみを出力してください。
コード以外の説明文は不要です。"""


def enhance_prompt(user_input: str) -> str:
    """ステージ1: ユーザーの曖昧な入力をプロ仕様の設計要件書に変換（コスト最適化: mini使用）"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # テキスト構造化はminiで十分。コスト16分の1
        messages=[
            {"role": "system", "content": ENHANCER_PROMPT},
            {"role": "user", "content": user_input}
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content


def generate_openscad_code(enhanced_spec: str) -> str:
    """ステージ2: 設計要件書からプロ品質のOpenSCADコードを生成"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": GENERATOR_PROMPT},
            {"role": "user", "content": enhanced_spec}
        ],
        temperature=0.2,
    )
    content = response.choices[0].message.content
    if "```openscad" in content:
        code = content.split("```openscad")[1].split("```")[0].strip()
    elif "```" in content:
        code = content.split("```")[1].split("```")[0].strip()
    else:
        code = content.strip()
    return code


def scad_to_stl(scad_code: str, output_filename="output.stl") -> str:
    scad_filename = "temp.scad"
    with open(scad_filename, "w", encoding="utf-8") as f:
        f.write(scad_code)
    openscad_path = "openscad"
    if os.path.exists("/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"):
        openscad_path = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
    cmd = [openscad_path, "-o", output_filename, scad_filename]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return output_filename
    except subprocess.CalledProcessError as e:
        raise Exception(f"OpenSCAD 変換エラー: {e.stderr}")
    except FileNotFoundError:
        raise Exception("OpenSCADコマンドが見つかりません。OpenSCADがインストールされているか確認してください。")


def render_stl_preview(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    b64_data = base64.b64encode(data).decode("utf-8")
    viewer_html = f"""
    <!DOCTYPE html><html><head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/STLLoader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body style="margin:0;background:#08090d;overflow:hidden;border-radius:20px;">
    <div id="v" style="width:100%;height:500px;"></div>
    <script>
    const v=document.getElementById('v'),scene=new THREE.Scene();
    scene.background=new THREE.Color(0x08090d);
    const cam=new THREE.PerspectiveCamera(60,v.clientWidth/v.clientHeight,0.1,2000);
    const r=new THREE.WebGLRenderer({{antialias:true}});
    r.setSize(v.clientWidth,v.clientHeight);r.setPixelRatio(2);
    r.toneMapping=THREE.ACESFilmicToneMapping;r.toneMappingExposure=1.2;
    v.appendChild(r.domElement);
    const ctrl=new THREE.OrbitControls(cam,r.domElement);
    ctrl.enableDamping=true;ctrl.dampingFactor=0.04;ctrl.autoRotate=true;ctrl.autoRotateSpeed=1.2;
    const l1=new THREE.DirectionalLight(0x6366f1,1.5);l1.position.set(3,4,2);scene.add(l1);
    const l2=new THREE.DirectionalLight(0x0ea5e9,0.8);l2.position.set(-2,-1,-3);scene.add(l2);
    const l3=new THREE.PointLight(0x8b5cf6,0.6,100);l3.position.set(0,5,0);scene.add(l3);
    scene.add(new THREE.AmbientLight(0x1e1b4b,0.4));
    const bs=window.atob("{b64_data}");const len=bs.length;const bytes=new Uint8Array(len);
    for(let i=0;i<len;i++)bytes[i]=bs.charCodeAt(i);
    const geo=new THREE.STLLoader().parse(bytes.buffer);
    const mat=new THREE.MeshPhysicalMaterial({{
        color:0x6366f1,metalness:0.3,roughness:0.2,clearcoat:1.0,clearcoatRoughness:0.1,
        transparent:true,opacity:0.92
    }});
    const mesh=new THREE.Mesh(geo,mat);
    geo.computeBoundingBox();const ctr=new THREE.Vector3();geo.boundingBox.getCenter(ctr);
    mesh.position.sub(ctr);scene.add(mesh);
    const d=Math.max(geo.boundingBox.max.x-geo.boundingBox.min.x,geo.boundingBox.max.y-geo.boundingBox.min.y,geo.boundingBox.max.z-geo.boundingBox.min.z);
    cam.position.set(d*0.9,d*0.7,d*1.4);
    // Edge glow
    const edges=new THREE.EdgesGeometry(geo,30);
    const eMat=new THREE.LineBasicMaterial({{color:0x0ea5e9,transparent:true,opacity:0.15}});
    const lines=new THREE.LineSegments(edges,eMat);lines.position.copy(mesh.position);scene.add(lines);
    function animate(){{requestAnimationFrame(animate);ctrl.update();r.render(scene,cam);}}
    animate();
    </script></body></html>
    """
    components.html(viewer_html, height=500)


# =====================================================
# メインUI
# =====================================================
def main():
    # =============================================
    # ⬡ ヒーローセクション — Canvas粒子アニメーション付き
    # =============================================
    hero_html = """
    <!DOCTYPE html><html><head><meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900&family=Noto+Sans+JP:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:'Inter','Noto Sans JP',sans-serif;background:#000;color:#e6edf3;overflow:hidden}
    canvas{position:absolute;top:0;left:0;width:100%;height:100%}
    .hero{position:relative;width:100%;height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center}
    .overlay{position:absolute;top:0;left:0;right:0;bottom:0;
        background:radial-gradient(ellipse at 50% 30%,rgba(99,102,241,0.12) 0%,transparent 55%),
                   radial-gradient(ellipse at 20% 80%,rgba(14,165,233,0.06) 0%,transparent 50%),
                   radial-gradient(ellipse at 80% 70%,rgba(139,92,246,0.06) 0%,transparent 50%)}
    .nav{position:absolute;top:0;left:0;right:0;padding:24px 48px;display:flex;align-items:center;justify-content:space-between;z-index:20}
    .nav-logo{font-size:1.3rem;font-weight:800;letter-spacing:-0.5px;
        background:linear-gradient(135deg,#fff,#6366f1);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .nav-links{display:flex;gap:32px}
    .nav-links a{color:rgba(230,237,243,0.5);text-decoration:none;font-size:0.85rem;font-weight:500;letter-spacing:0.5px;transition:color 0.3s}
    .nav-links a:hover{color:#fff}
    .content{position:relative;z-index:10;text-align:center;padding:0 20px}
    .pill{display:inline-flex;align-items:center;gap:8px;margin-bottom:32px;padding:6px 20px 6px 8px;
        border:1px solid rgba(99,102,241,0.3);border-radius:100px;font-size:0.78rem;color:rgba(99,102,241,0.95);
        letter-spacing:1px;background:rgba(99,102,241,0.06);backdrop-filter:blur(10px)}
    .pill-dot{width:8px;height:8px;border-radius:50%;background:#6366f1;animation:pulse 2s ease-in-out infinite}
    @keyframes pulse{0%,100%{opacity:0.5;transform:scale(1)}50%{opacity:1;transform:scale(1.3)}}
    .logo{font-size:6rem;font-weight:900;letter-spacing:-4px;line-height:1;
        background:linear-gradient(135deg,#fff 0%,#e0e7ff 20%,#6366f1 45%,#8b5cf6 65%,#0ea5e9 100%);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
        animation:shimmer 6s ease-in-out infinite}
    @keyframes shimmer{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
    .tagline{font-size:1.6rem;font-weight:300;color:rgba(230,237,243,0.7);margin-top:12px;letter-spacing:12px}
    .desc{font-size:1rem;color:rgba(230,237,243,0.35);max-width:520px;margin:28px auto 0;line-height:2}
    .cta-row{display:flex;gap:16px;justify-content:center;margin-top:40px}
    .cta{padding:14px 36px;border-radius:14px;font-size:0.9rem;font-weight:700;text-decoration:none;
        letter-spacing:0.5px;transition:all 0.4s cubic-bezier(0.4,0,0.2,1);cursor:pointer;border:none;font-family:inherit}
    .cta-primary{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;
        box-shadow:0 6px 30px rgba(99,102,241,0.4)}
    .cta-primary:hover{transform:translateY(-3px);box-shadow:0 10px 40px rgba(99,102,241,0.6)}
    .cta-ghost{background:transparent;border:1px solid rgba(230,237,243,0.15);color:rgba(230,237,243,0.7)}
    .cta-ghost:hover{border-color:rgba(99,102,241,0.5);color:#fff;background:rgba(99,102,241,0.05)}
    .scroll-ind{position:absolute;bottom:32px;left:50%;transform:translateX(-50%);z-index:20;
        display:flex;flex-direction:column;align-items:center;gap:6px}
    .scroll-ind span{font-size:0.65rem;letter-spacing:5px;color:rgba(230,237,243,0.2);text-transform:uppercase}
    .mouse{width:22px;height:34px;border:1.5px solid rgba(230,237,243,0.2);border-radius:12px;position:relative}
    .mouse::after{content:'';position:absolute;top:6px;left:50%;transform:translateX(-50%);
        width:3px;height:8px;background:rgba(99,102,241,0.8);border-radius:2px;animation:mouseScroll 2s infinite}
    @keyframes mouseScroll{0%{opacity:1;transform:translateX(-50%) translateY(0)}100%{opacity:0;transform:translateX(-50%) translateY(12px)}}
    </style></head>
    <body>
    <div class="hero">
        <canvas id="particles"></canvas>
        <div class="overlay"></div>
        <nav class="nav">
            <div class="nav-logo">⬡ TsukuriAI</div>
            <div class="nav-links">
                <a href="#">Features</a>
                <a href="#">How it works</a>
                <a href="#">Pricing</a>
            </div>
        </nav>
        <div class="content">
            <div class="pill"><span class="pill-dot"></span>Now in Beta — 無料で体験</div>
            <h1 class="logo">TsukuriAI</h1>
            <p class="tagline">思いのままに、造ろう</p>
            <p class="desc">言葉ひとつで、あなたのアイデアが実物になる。<br>AIが設計し、3Dプリンタが形にする。</p>
            <div class="cta-row">
                <button class="cta cta-primary" onclick="window.parent.document.querySelector('[data-testid=stAppViewContainer]').scrollTo({top:9999,behavior:'smooth'})">無料で試す →</button>
                <button class="cta cta-ghost">使い方を見る</button>
            </div>
        </div>
        <div class="scroll-ind"><span>Scroll</span><div class="mouse"></div></div>
    </div>
    <script>
    const canvas=document.getElementById('particles'),ctx=canvas.getContext('2d');
    let w,h,particles=[];
    function resize(){w=canvas.width=window.innerWidth;h=canvas.height=window.innerHeight}
    window.addEventListener('resize',resize);resize();
    class P{
        constructor(){this.reset()}
        reset(){
            this.x=Math.random()*w;this.y=Math.random()*h;
            this.vx=(Math.random()-0.5)*0.3;this.vy=(Math.random()-0.5)*0.3;
            this.r=Math.random()*1.5+0.5;this.a=Math.random()*0.4+0.1;
            this.color=Math.random()>0.5?'99,102,241':'14,165,233'
        }
        update(){this.x+=this.vx;this.y+=this.vy;if(this.x<0||this.x>w||this.y<0||this.y>h)this.reset()}
        draw(){ctx.beginPath();ctx.arc(this.x,this.y,this.r,0,Math.PI*2);ctx.fillStyle=`rgba(${this.color},${this.a})`;ctx.fill()}
    }
    for(let i=0;i<80;i++)particles.push(new P());
    function drawConnections(){
        for(let i=0;i<particles.length;i++){
            for(let j=i+1;j<particles.length;j++){
                const dx=particles[i].x-particles[j].x,dy=particles[i].y-particles[j].y;
                const dist=Math.sqrt(dx*dx+dy*dy);
                if(dist<120){
                    ctx.beginPath();ctx.moveTo(particles[i].x,particles[i].y);
                    ctx.lineTo(particles[j].x,particles[j].y);
                    ctx.strokeStyle=`rgba(99,102,241,${0.06*(1-dist/120)})`;
                    ctx.lineWidth=0.5;ctx.stroke()
                }
            }
        }
    }
    function animate(){
        ctx.clearRect(0,0,w,h);
        particles.forEach(p=>{p.update();p.draw()});
        drawConnections();
        requestAnimationFrame(animate)
    }
    animate();
    </script>
    </body></html>
    """
    components.html(hero_html, height=750, scrolling=False)

    # =============================================
    # 🏆 スタッツバー
    # =============================================
    stats_html = """
    <!DOCTYPE html><html><head><meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;600;800&family=Noto+Sans+JP:wght@300;700&display=swap" rel="stylesheet">
    <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:'Inter','Noto Sans JP',sans-serif;background:#000;overflow:hidden}
    .bar{display:flex;justify-content:center;gap:60px;padding:40px;
        border-top:1px solid rgba(99,102,241,0.1);border-bottom:1px solid rgba(99,102,241,0.1);
        background:linear-gradient(180deg,rgba(99,102,241,0.03),transparent)}
    .stat{text-align:center;opacity:0;animation:fadeUp 0.8s forwards}
    .stat:nth-child(1){animation-delay:0.1s}
    .stat:nth-child(2){animation-delay:0.25s}
    .stat:nth-child(3){animation-delay:0.4s}
    .stat:nth-child(4){animation-delay:0.55s}
    @keyframes fadeUp{0%{opacity:0;transform:translateY(20px)}100%{opacity:1;transform:translateY(0)}}
    .stat-num{font-size:2.2rem;font-weight:800;
        background:linear-gradient(135deg,#6366f1,#0ea5e9);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .stat-label{font-size:0.75rem;color:rgba(230,237,243,0.35);letter-spacing:2px;margin-top:4px;text-transform:uppercase}
    </style></head>
    <body>
    <div class="bar">
        <div class="stat"><div class="stat-num">500+</div><div class="stat-label">生成モデル数</div></div>
        <div class="stat"><div class="stat-num">0.3s</div><div class="stat-label">平均生成速度</div></div>
        <div class="stat"><div class="stat-num">99%</div><div class="stat-label">印刷成功率</div></div>
        <div class="stat"><div class="stat-num">24/7</div><div class="stat-label">稼働時間</div></div>
    </div>
    </body></html>
    """
    components.html(stats_html, height=130, scrolling=False)

    # =============================================
    # ✨ フィーチャーセクション（スクロールアニメーション付き）
    # =============================================
    features_html = """
    <!DOCTYPE html><html><head><meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Noto+Sans+JP:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:'Inter','Noto Sans JP',sans-serif;background:#000;color:#e6edf3}
    .section{padding:80px 48px;max-width:1200px;margin:0 auto}
    .label{font-size:0.7rem;letter-spacing:6px;color:rgba(99,102,241,0.8);text-transform:uppercase;margin-bottom:14px;
        display:flex;align-items:center;gap:12px}
    .label::before{content:'';width:30px;height:1px;background:linear-gradient(90deg,#6366f1,transparent)}
    .title{font-size:2.8rem;font-weight:800;color:#fff;margin-bottom:16px;line-height:1.2;letter-spacing:-1px}
    .title span{background:linear-gradient(135deg,#6366f1,#0ea5e9);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .subtitle{font-size:1rem;color:rgba(230,237,243,0.4);max-width:480px;line-height:1.8;margin-bottom:60px}
    .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
    .card{
        background:linear-gradient(135deg,rgba(15,18,30,0.8),rgba(20,24,38,0.6));
        backdrop-filter:blur(30px);
        border:1px solid rgba(99,102,241,0.08);border-radius:20px;
        padding:40px 28px;
        transition:all 0.5s cubic-bezier(0.4,0,0.2,1);
        position:relative;overflow:hidden;
        opacity:0;transform:translateY(40px);
        animation:revealCard 0.8s forwards
    }
    .card:nth-child(1){animation-delay:0.1s}
    .card:nth-child(2){animation-delay:0.25s}
    .card:nth-child(3){animation-delay:0.4s}
    @keyframes revealCard{to{opacity:1;transform:translateY(0)}}
    .card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
        background:linear-gradient(90deg,transparent,rgba(99,102,241,0.4),transparent);opacity:0;transition:opacity 0.5s}
    .card::after{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;
        background:radial-gradient(circle,rgba(99,102,241,0.04) 0%,transparent 70%);
        opacity:0;transition:opacity 0.5s}
    .card:hover{border-color:rgba(99,102,241,0.25);transform:translateY(-8px);
        box-shadow:0 25px 50px rgba(0,0,0,0.5),0 0 40px rgba(99,102,241,0.08)}
    .card:hover::before{opacity:1}
    .card:hover::after{opacity:1}
    .card-icon{width:56px;height:56px;border-radius:14px;
        background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.1));
        border:1px solid rgba(99,102,241,0.15);
        display:flex;align-items:center;justify-content:center;
        font-size:1.6rem;margin-bottom:24px}
    .card h3{font-size:1.15rem;font-weight:700;color:#fff;margin-bottom:12px}
    .card p{font-size:0.85rem;color:rgba(230,237,243,0.4);line-height:1.8}
    .card-tag{display:inline-block;margin-top:16px;padding:4px 12px;border-radius:6px;font-size:0.65rem;
        font-weight:600;letter-spacing:1px;text-transform:uppercase;
        background:rgba(99,102,241,0.1);color:rgba(99,102,241,0.8);border:1px solid rgba(99,102,241,0.15)}
    </style></head>
    <body>
    <div class="section">
        <p class="label">Features</p>
        <h2 class="title">言葉が、<span>プロダクト</span>になる</h2>
        <p class="subtitle">専門知識は不要。AIがあなたの「作りたい」を理解し、プロ品質の3Dデータを即座に生成します。</p>
        <div class="grid">
            <div class="card">
                <div class="card-icon">⚡</div>
                <h3>AI Instant Design</h3>
                <p>自然言語で入力するだけで、寸法・強度・印刷可能性まで考慮した設計データをAIが瞬時に自動生成。</p>
                <span class="card-tag">GPT-4o Powered</span>
            </div>
            <div class="card">
                <div class="card-icon">◇</div>
                <h3>Real-time 3D Preview</h3>
                <p>生成された3Dモデルをブラウザ上でリアルタイムプレビュー。マウスで自由に回転・ズームし、細部まで確認。</p>
                <span class="card-tag">WebGL Rendering</span>
            </div>
            <div class="card">
                <div class="card-icon">△</div>
                <h3>One-click Manufacturing</h3>
                <p>STLダウンロード、もしくはプラットフォーム上で3Dプリンタオーナーに即時発注。アイデアが最短で実物に。</p>
                <span class="card-tag">C2C Matching</span>
            </div>
        </div>
    </div>
    </body></html>
    """
    components.html(features_html, height=700, scrolling=False)

    # =============================================
    # 📐 ステップセクション（大きなビジュアル付き）
    # =============================================
    steps_html = """
    <!DOCTYPE html><html><head><meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Noto+Sans+JP:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:'Inter','Noto Sans JP',sans-serif;background:#000;color:#e6edf3}
    .section{padding:80px 48px;max-width:1200px;margin:0 auto}
    .label{font-size:0.7rem;letter-spacing:6px;color:rgba(99,102,241,0.8);text-transform:uppercase;margin-bottom:14px;
        display:flex;align-items:center;gap:12px}
    .label::before{content:'';width:30px;height:1px;background:linear-gradient(90deg,#6366f1,transparent)}
    .title{font-size:2.8rem;font-weight:800;color:#fff;margin-bottom:50px;letter-spacing:-1px}
    .title span{background:linear-gradient(135deg,#0ea5e9,#6366f1);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
    .steps{display:flex;flex-direction:column;gap:0}
    .step{display:flex;align-items:stretch;gap:0;
        opacity:0;animation:stepReveal 0.7s forwards}
    .step:nth-child(1){animation-delay:0.1s}
    .step:nth-child(2){animation-delay:0.3s}
    .step:nth-child(3){animation-delay:0.5s}
    @keyframes stepReveal{to{opacity:1}}
    .step-line{width:80px;display:flex;flex-direction:column;align-items:center;padding-top:4px}
    .step-dot{width:48px;height:48px;border-radius:14px;flex-shrink:0;
        background:linear-gradient(135deg,rgba(99,102,241,0.2),rgba(14,165,233,0.15));
        border:1px solid rgba(99,102,241,0.25);
        display:flex;align-items:center;justify-content:center;
        font-size:1rem;font-weight:800;color:#6366f1}
    .connector{flex:1;width:2px;background:linear-gradient(180deg,rgba(99,102,241,0.2),rgba(99,102,241,0.05));margin-top:8px}
    .step-content{flex:1;padding:0 0 48px 16px}
    .step-content h3{font-size:1.2rem;font-weight:700;color:#fff;margin-bottom:8px}
    .step-content p{font-size:0.88rem;color:rgba(230,237,243,0.4);line-height:1.8;max-width:450px}
    .step-content .example{margin-top:14px;padding:14px 18px;border-radius:12px;
        background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.1);
        font-size:0.8rem;color:rgba(99,102,241,0.7);font-style:italic;line-height:1.6}
    </style></head>
    <body>
    <div class="section">
        <p class="label">How it works</p>
        <h2 class="title"><span>3ステップ</span>で、形になる</h2>
        <div class="steps">
            <div class="step">
                <div class="step-line"><div class="step-dot">01</div><div class="connector"></div></div>
                <div class="step-content">
                    <h3>言葉で伝える</h3>
                    <p>頭の中にあるイメージを、日本語でそのまま入力するだけ。専門用語は一切不要。</p>
                    <div class="example">💬 「机の端に引っ掛けるヘッドホンハンガー。厚み20mmまでの天板に対応して」</div>
                </div>
            </div>
            <div class="step">
                <div class="step-line"><div class="step-dot">02</div><div class="connector"></div></div>
                <div class="step-content">
                    <h3>AIが3Dデータを生成</h3>
                    <p>AIエンジニアが設計コードを自動生成。寸法の補完、強度の確保、印刷可能性のチェックまで自動で行います。</p>
                    <div class="example">⚡ 約10秒で設計完了 → ブラウザ上で3Dプレビューが表示</div>
                </div>
            </div>
            <div class="step">
                <div class="step-line"><div class="step-dot">03</div></div>
                <div class="step-content">
                    <h3>ダウンロード or ワンクリック発注</h3>
                    <p>STLファイルをダウンロードして自分で印刷。または、プラットフォーム上の3Dプリンタオーナーにその場で発注できます。</p>
                    <div class="example">🚀 最短翌日にはあなたの手元にオリジナルパーツが届く</div>
                </div>
            </div>
        </div>
    </div>
    </body></html>
    """
    components.html(steps_html, height=650, scrolling=False)

    # =============================================
    # 🏭 ワークスペース（生成UI）
    # =============================================
    workspace_header = """
    <!DOCTYPE html><html><head><meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;700;800&family=Noto+Sans+JP:wght@300;700&display=swap" rel="stylesheet">
    <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:'Inter','Noto Sans JP',sans-serif;background:#000;color:#e6edf3;text-align:center;padding:60px 20px 24px}
    .glow{position:absolute;top:0;left:50%;transform:translateX(-50%);width:400px;height:200px;
        background:radial-gradient(ellipse,rgba(99,102,241,0.08),transparent);pointer-events:none}
    .label{font-size:0.7rem;letter-spacing:6px;color:rgba(99,102,241,0.8);text-transform:uppercase;margin-bottom:14px;position:relative}
    .title{font-size:2.8rem;font-weight:800;color:#fff;margin-bottom:14px;letter-spacing:-1px;position:relative}
    .subtitle{font-size:0.95rem;color:rgba(230,237,243,0.4);max-width:420px;margin:0 auto 30px;position:relative}
    .divider{width:60px;height:2px;background:linear-gradient(90deg,#6366f1,#0ea5e9);margin:0 auto;border-radius:1px;position:relative}
    </style></head>
    <body>
    <div class="glow"></div>
    <p class="label">Workspace</p>
    <h2 class="title">さあ、造ろう</h2>
    <p class="subtitle">テンプレートを選ぶか、自由にテキストで入力してください。</p>
    <div class="divider"></div>
    </body></html>
    """
    components.html(workspace_header, height=220, scrolling=False)

    # テンプレート
    templates = [
        {"name": "L字ブラケット", "prompt": "壁に取り付けるための強化L字型マウントブラケット。一辺は40mm、幅30mm、厚さ5mm。M4ネジ用の穴を2つ開けて。", "emoji": "⬡", "tag": "DIY"},
        {"name": "スマホスタンド", "prompt": "厚さ12mmまでのスマホが置けるシンプルなデスクスタンド。角度は60度。土台は幅60mm、奥行き80mmにして。", "emoji": "◈", "tag": "Desk"},
        {"name": "小物入れトレイ", "prompt": "幅100mm、奥行き70mm、高さ20mmのシンプルな小物入れトレイ。角は丸くして。", "emoji": "▣", "tag": "Organization"},
    ]

    if 'text_area_input' not in st.session_state:
        st.session_state.text_area_input = ""

    tcols = st.columns(3, gap="medium")
    for i, tc in enumerate(tcols):
        with tc:
            card_html = f"""
            <div style="
                background:linear-gradient(135deg,rgba(15,18,30,0.9),rgba(20,24,38,0.7));
                border:1px solid rgba(99,102,241,0.1);
                border-radius:18px;padding:28px 20px;text-align:center;
                font-family:'Inter','Noto Sans JP',sans-serif;
                transition:all 0.4s;position:relative;overflow:hidden;
            ">
                <span style="font-size:2.2rem;display:block;margin-bottom:8px;opacity:0.8">{templates[i]['emoji']}</span>
                <p style="font-weight:700;font-size:1.05rem;margin:8px 0 6px;color:#fff;">{templates[i]['name']}</p>
                <span style="display:inline-block;padding:3px 10px;border-radius:5px;font-size:0.6rem;font-weight:600;
                    letter-spacing:1.5px;text-transform:uppercase;
                    background:rgba(99,102,241,0.1);color:rgba(99,102,241,0.7);border:1px solid rgba(99,102,241,0.12);
                    margin-bottom:10px">{templates[i]['tag']}</span>
                <p style="font-size:0.75rem;color:rgba(230,237,243,0.35);line-height:1.6;">{templates[i]['prompt'][:55]}...</p>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(f"→ {templates[i]['name']}", key=f"btn_{i}"):
                st.session_state.text_area_input = templates[i]['prompt']
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    user_input = st.text_area(
        "テキストで図面を指示する：",
        height=130,
        placeholder="例：「幅50mm、奥行き30mm、厚さ5mmの板で、四隅に直径3mmの穴を開けて」",
        key="text_area_input"
    )

    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        generate_btn = st.button("⬡  Generate 3D Model", use_container_width=True)

    if generate_btn:
        if not user_input.strip():
            st.error("⚠️ 要件を入力してください。")
            return
        try:
            # ステージ1: プロンプトエンハンス（素人入力→プロ仕様に変換）
            with st.spinner("🧠 AIが設計要件を分析・補完中..."):
                enhanced_spec = enhance_prompt(user_input)
            with st.expander("📐 AIが補完した設計要件書を見る", expanded=True):
                st.markdown(enhanced_spec)
            
            # ステージ2: OpenSCADコード生成
            with st.spinner("⚡ プロ品質のOpenSCADコードを生成中..."):
                scad_code = generate_openscad_code(enhanced_spec)
            with st.expander("📝 生成されたOpenSCADコードを見る"):
                st.code(scad_code, language="openscad")
            with st.spinner("◇ STLファイルにコンパイル中..."):
                stl_file = scad_to_stl(scad_code)
            
            # 案件を保存
            order_id = save_order(user_input, stl_file, scad_code)
            st.session_state.last_order_id = order_id
            st.session_state.last_stl_file = stl_file
            st.session_state.last_scad_code = scad_code
            
            st.success("✅ 3Dデータの生成が完了しました！")
            
            # --- 自動見積もり ---
            file_size_bytes = os.path.getsize(stl_file)
            file_size_kb = file_size_bytes / 1024
            # 簡易推定: STLバイナリのファイルサイズから概算（1三角形=50バイト、体積推定）
            est_volume_cm3 = max(0.5, file_size_kb / 50)  # 非常にラフな推定
            est_weight_g = est_volume_cm3 * 1.24  # PLAの密度 1.24 g/cm³
            est_time_min = max(5, est_volume_cm3 * 8)  # 1cm³あたり約8分
            est_cost = max(100, int(est_weight_g * 15 + 300))  # 材料費+基本手数料
            
            estimate_html = f"""
            <div style="
                background:linear-gradient(135deg,rgba(15,18,30,0.9),rgba(20,24,38,0.7));
                border:1px solid rgba(16,185,129,0.15);border-radius:16px;
                padding:24px 28px;margin:16px 0;
                font-family:'Inter','Noto Sans JP',sans-serif;
            ">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
                    <span style="font-size:1.2rem;">📊</span>
                    <span style="font-size:0.85rem;font-weight:700;color:#fff;">自動見積もり</span>
                    <span style="padding:2px 8px;border-radius:4px;font-size:0.55rem;font-weight:600;
                        background:rgba(16,185,129,0.1);color:#10b981;border:1px solid rgba(16,185,129,0.2);
                        letter-spacing:1px;">ESTIMATE</span>
                </div>
                <div style="display:flex;gap:24px;flex-wrap:wrap;">
                    <div>
                        <div style="font-size:0.65rem;color:rgba(230,237,243,0.3);letter-spacing:1px;margin-bottom:2px;">ファイルサイズ</div>
                        <div style="font-size:1.1rem;font-weight:700;color:#0ea5e9;">{file_size_kb:.0f} KB</div>
                    </div>
                    <div>
                        <div style="font-size:0.65rem;color:rgba(230,237,243,0.3);letter-spacing:1px;margin-bottom:2px;">推定重量</div>
                        <div style="font-size:1.1rem;font-weight:700;color:#8b5cf6;">{est_weight_g:.1f} g</div>
                    </div>
                    <div>
                        <div style="font-size:0.65rem;color:rgba(230,237,243,0.3);letter-spacing:1px;margin-bottom:2px;">推定印刷時間</div>
                        <div style="font-size:1.1rem;font-weight:700;color:#6366f1;">{est_time_min:.0f} 分</div>
                    </div>
                    <div>
                        <div style="font-size:0.65rem;color:rgba(230,237,243,0.3);letter-spacing:1px;margin-bottom:2px;">概算費用</div>
                        <div style="font-size:1.1rem;font-weight:700;
                            background:linear-gradient(135deg,#10b981,#059669);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                            ¥{est_cost:,}</div>
                    </div>
                </div>
                <p style="font-size:0.65rem;color:rgba(230,237,243,0.2);margin-top:12px;line-height:1.5;">
                    ※ PLA素材、インフィル20%での概算です。実際の費用はオーナーにより異なります。
                </p>
            </div>
            """
            st.markdown(estimate_html, unsafe_allow_html=True)
            
            st.markdown("#### ◈ 3D Preview — ドラッグで回転")
            render_stl_preview(stl_file)
            col_dl, col_order = st.columns([1, 1])
            with col_dl:
                with open(stl_file, "rb") as f:
                    st.download_button(
                        label="↓ STLをダウンロード",
                        data=f,
                        file_name="tsukuri_ai_model.stl",
                        mime="application/octet-stream",
                        use_container_width=True
                    )
            with col_order:
                if st.button("🚀 プリントを発注する", use_container_width=True):
                    st.success(f"📋 案件 #{order_id} を発注しました！オーナーからの受注をお待ちください。")
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {e}")

    # フッター
    footer_html = """
    <!DOCTYPE html><html><head><meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{font-family:'Inter','Noto Sans JP',sans-serif;background:#000;color:#e6edf3}
    .footer{padding:60px 48px 30px;border-top:1px solid rgba(99,102,241,0.08)}
    .footer-grid{display:flex;justify-content:space-between;align-items:flex-start;max-width:1000px;margin:0 auto}
    .footer-brand .logo{font-size:1.4rem;font-weight:800;
        background:linear-gradient(135deg,#6366f1,#0ea5e9);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px}
    .footer-brand p{font-size:0.8rem;color:rgba(230,237,243,0.3);max-width:280px;line-height:1.7}
    .footer-links h4{font-size:0.7rem;letter-spacing:3px;color:rgba(230,237,243,0.5);text-transform:uppercase;margin-bottom:14px}
    .footer-links a{display:block;font-size:0.82rem;color:rgba(230,237,243,0.3);text-decoration:none;margin-bottom:8px;transition:color 0.3s}
    .footer-links a:hover{color:#6366f1}
    .copyright{text-align:center;margin-top:40px;padding-top:24px;border-top:1px solid rgba(99,102,241,0.05);
        font-size:0.7rem;color:rgba(230,237,243,0.2);letter-spacing:2px}
    </style></head>
    <body>
    <div class="footer">
        <div class="footer-grid">
            <div class="footer-brand">
                <div class="logo">⬡ TsukuriAI</div>
                <p>AIと3Dプリンティングで、誰もがメイカーになれる世界を。</p>
            </div>
            <div class="footer-links">
                <h4>Product</h4>
                <a href="#">Features</a>
                <a href="#">Pricing</a>
                <a href="#">API</a>
            </div>
            <div class="footer-links">
                <h4>Company</h4>
                <a href="#">About</a>
                <a href="#">Blog</a>
                <a href="#">Careers</a>
            </div>
            <div class="footer-links">
                <h4>Legal</h4>
                <a href="#">Privacy</a>
                <a href="#">Terms</a>
            </div>
        </div>
        <p class="copyright">© 2026 TsukuriAI Inc. — All rights reserved.</p>
    </div>
    </body></html>
    """
    components.html(footer_html, height=280, scrolling=False)


if __name__ == "__main__":
    main()
