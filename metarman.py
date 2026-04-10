import folium
import requests
import re
from datetime import datetime, timezone
import time
import random
from concurrent.futures import ThreadPoolExecutor

# --- 1. 飛行場データ（そのまま継承） ---
AIRPORTS = {
    # 北海道
    "RJCC": {"name": "新千歳空港", "lat": 42.7752, "lon": 141.6923}, "RJCH": {"name": "函館空港", "lat": 41.7700, "lon": 140.8219},
    "RJCK": {"name": "釧路空港", "lat": 43.0411, "lon": 144.1931}, "RJCB": {"name": "帯広空港", "lat": 42.7333, "lon": 143.2170},
    "RJCW": {"name": "稚内空港", "lat": 45.4039, "lon": 141.8020}, "RJCM": {"name": "女満別空港", "lat": 43.8803, "lon": 144.1640},
    "RJCA": {"name": "旭川空港", "lat": 43.6708, "lon": 142.4475}, "RJCN": {"name": "中標津空港", "lat": 43.5775, "lon": 144.9589},
    "RJCO": {"name": "札幌(丘珠)", "lat": 43.1161, "lon": 141.3783}, "RJEC": {"name": "旭川(陸自)", "lat": 43.7947, "lon": 142.3653},
    # 東北
    "RJSS": {"name": "仙台空港", "lat": 38.1397, "lon": 140.9169}, "RJST": {"name": "松島基地", "lat": 38.4033, "lon": 141.2133},
    "RJSU": {"name": "霞目(陸自)", "lat": 38.2367, "lon": 140.9189}, "RJSA": {"name": "青森空港", "lat": 40.7347, "lon": 140.6908},
    "RJSB": {"name": "三沢基地", "lat": 40.7031, "lon": 141.3681}, "RJSM": {"name": "三沢(射爆場)", "lat": 40.8522, "lon": 141.3850},
    "RJSH": {"name": "八戸飛行場", "lat": 40.5544, "lon": 141.4658}, "RJSI": {"name": "花巻空港", "lat": 39.4286, "lon": 141.1353},
    "RJSK": {"name": "秋田空港", "lat": 39.6156, "lon": 140.2186}, "RJSY": {"name": "庄内空港", "lat": 38.8125, "lon": 139.7875},
    "RJSC": {"name": "山形空港", "lat": 38.4117, "lon": 140.3711}, "RJSF": {"name": "福島空港", "lat": 37.2264, "lon": 140.4347},
    # 関東・甲信越
    "RJSN": {"name": "新潟空港", "lat": 37.9564, "lon": 139.1214}, "RJTT": {"name": "羽田空港", "lat": 35.5494, "lon": 139.7798},
    "RJAA": {"name": "成田空港", "lat": 35.7647, "lon": 140.3863}, "RJTY": {"name": "横田基地", "lat": 35.7486, "lon": 139.3486},
    "RJTJ": {"name": "入間基地", "lat": 35.8414, "lon": 139.4122}, "RJAH": {"name": "百里基地", "lat": 36.1811, "lon": 140.4147},
    "RJTA": {"name": "厚木基地", "lat": 35.4547, "lon": 139.4500}, "RJTL": {"name": "下総基地", "lat": 35.8028, "lon": 140.0114},
    "RJTU": {"name": "宇都宮(陸自)", "lat": 36.5147, "lon": 139.8689}, "RJTK": {"name": "木更津(陸自)", "lat": 35.3986, "lon": 139.9114},
    "RJTC": {"name": "立川(陸自)", "lat": 35.7139, "lon": 139.4019}, "RJTF": {"name": "調布飛行場", "lat": 35.6722, "lon": 139.5272},
    "RJTI": {"name": "東京ヘリ", "lat": 35.6367, "lon": 139.8453}, "RJAF": {"name": "松本空港", "lat": 36.1667, "lon": 137.9192},
    # 中部・北陸
    "RJNK": {"name": "小松基地", "lat": 36.3947, "lon": 136.4072}, "RJNT": {"name": "富山空港", "lat": 36.6475, "lon": 137.1875},
    "RJNS": {"name": "静岡空港", "lat": 34.7961, "lon": 138.1794}, "RJGG": {"name": "中部国際", "lat": 34.8583, "lon": 136.8053},
    "RJNA": {"name": "名古屋(小牧)", "lat": 35.2461, "lon": 136.9244}, "RJNY": {"name": "静浜基地", "lat": 34.8144, "lon": 138.2978},
    "RJME": {"name": "明野飛行場", "lat": 34.5292, "lon": 136.6694}, "RJNW": {"name": "能登空港", "lat": 37.2944, "lon": 136.9606},
    # 近畿・中国・四国
    "RJBB": {"name": "関西国際", "lat": 34.4347, "lon": 135.2441}, "RJOO": {"name": "伊丹空港", "lat": 34.7855, "lon": 135.4382},
    "RJBE": {"name": "神戸空港", "lat": 34.6328, "lon": 135.2239}, "RJBK": {"name": "岡山空港", "lat": 34.7567, "lon": 133.8550},
    "RJOA": {"name": "広島空港", "lat": 34.4400, "lon": 132.9197}, "RJOH": {"name": "米子基地", "lat": 35.4922, "lon": 133.2364},
    "RJOT": {"name": "高松空港", "lat": 34.2142, "lon": 134.0156}, "RJOM": {"name": "松山空港", "lat": 33.8272, "lon": 132.6997},
    "RJOK": {"name": "高知空港", "lat": 33.5469, "lon": 133.6694}, "RJOS": {"name": "徳島空港", "lat": 34.1328, "lon": 134.6067},
    # 九州・沖縄
    "RJFF": {"name": "福岡空港", "lat": 33.5859, "lon": 130.4507}, "RJFU": {"name": "長崎空港", "lat": 32.9169, "lon": 129.9136},
    "RJFT": {"name": "熊本空港", "lat": 32.8372, "lon": 130.8550}, "RJFM": {"name": "宮崎空港", "lat": 31.8772, "lon": 131.4486},
    "RJFK": {"name": "鹿児島空港", "lat": 31.8033, "lon": 130.7194}, "RJFN": {"name": "新田原基地", "lat": 32.0833, "lon": 131.4517},
    "RJFY": {"name": "鹿屋基地", "lat": 31.3686, "lon": 130.8447}, "RJDM": {"name": "目達原駐屯地", "lat": 33.3242, "lon": 130.4039},
    "ROAH": {"name": "那覇空港/基地", "lat": 26.2044, "lon": 127.6461}, "RODN": {"name": "嘉手納基地", "lat": 26.3556, "lon": 127.7675},
    "ROMC": {"name": "普天間基地", "lat": 26.2731, "lon": 127.7581}, "ROIG": {"name": "新石垣空港", "lat": 24.3964, "lon": 124.2450},
}

def get_status(metar_line):
    if not metar_line: return "lightgray", "NO DATA"
    try:
        match = re.search(r'(\d{2})(\d{2})(\d{2})Z', metar_line)
        if not match: return "lightgray", "UNKNOWN"
        day, hour, minute = map(int, match.groups())
        now = datetime.now(timezone.utc)
        rep_time = now.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
        diff = (now - rep_time).total_seconds()
        if 0 <= diff < 10800: return "blue", "ACTIVE"
        elif diff < 86400: return "orange", "DELAYED"
        else: return "lightgray", "STALE"
    except: return "lightgray", "ERROR"

def colorize_metar(metar):
    if not metar: return ""
    tokens = metar.split()
    res = []
    weather_codes = ["RA", "SN", "FG", "TS", "BR", "HZ", "DZ", "VCSH", "SHRA"]
    for t in tokens:
        # 1. 風速(KT)の判定
        if "KT" in t:
            if "G" in t:
                res.append(f'<span style="color:yellow;">{t}</span>') # ガストは黄色
            else:
                res.append(f'<span style="color:white;">{t}</span>') # 通常は白
        
        # 2. 視程(4桁数字)の判定
        elif re.fullmatch(r'\d{4}', t):
            if t == "9999":
                res.append(f'<span style="color:white;">{t}</span>') # 9999は白
            else:
                res.append(f'<span style="color:cyan;">{t}</span>') # 9999未満は水色
        
        # 3. その他（天気現象や雲量）の着色（そのまま継承）
        elif any(c in t for c in weather_codes): 
            res.append(f'<span style="color:red;">{t}</span>')
        elif t.startswith(("BKN","OVC","VV")): 
            res.append(f'<span style="color:lime;">{t}</span>')
            
        else:
            res.append(t)
    return " ".join(res)

def fetch_url(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200: return res.text
    except: pass
    return None

def main():
    icao_list = list(AIRPORTS.keys())
    metar_storage = {icao: [] for icao in icao_list}
    
    # --- 並列処理でデータ取得速度を向上 ---
    urls = [
        f"https://www.aviationweather.gov/api/data/metar?ids={','.join(icao_list)}&format=raw&hours=24&v={random.randint(1,999)}",
        f"https://tgftp.nws.noaa.gov/data/observations/metar/cycles/{(datetime.now(timezone.utc).minute // 10 * 10):02d}Z.TXT"
    ]
    
    print("🚀 高速データ取得中...")
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(fetch_url, urls))

    # データ解析
    for text in results:
        if not text: continue
        for line in text.splitlines():
            for icao in icao_list:
                if icao in line and re.search(rf"{icao}\s\d{{6}}Z", line):
                    clean = line[line.find(icao):].replace('=', '').strip()
                    if len(clean) > 10: metar_storage[icao].append(clean)

    # マップ作成
    m = folium.Map(location=[36.5, 137.5], zoom_start=5, tiles='CartoDB positron')
    
    # UTC Clock UI (そのまま継承)
    clock_html = '''
    <div id="utc_box" style="position:fixed; top:20px; left:60px; width:150px; height:45px; 
    background:rgba(0,0,0,0.85); color:#0f0; border:1px solid #555; border-radius:5px; 
    z-index:9999; display:flex; flex-direction:column; align-items:center; justify-content:center; 
    font-family:monospace; box-shadow: 2px 2px 10px rgba(0,0,0,0.5);">
        <div style="font-size:9px; color:#fff;">UTC CLOCK</div>
        <div id="utc_time" style="font-size:20px; font-weight:bold;">00:00:00</div>
    </div>
    <script>
        setInterval(() => {
            const now = new Date();
            const h = String(now.getUTCHours()).padStart(2, '0');
            const m = String(now.getUTCMinutes()).padStart(2, '0');
            const s = String(now.getUTCSeconds()).padStart(2, '0');
            document.getElementById('utc_time').textContent = `${h}:${m}:${s}`;
        }, 1000);
    </script>
    '''
    m.get_root().html.add_child(folium.Element(clock_html))

    for icao, info in AIRPORTS.items():
        logs = sorted(list(set(metar_storage[icao])), reverse=True)
        color, status_text = get_status(logs[0] if logs else None)
        
        current = colorize_metar(logs[0]) if logs else '<span style="color:gray;">No Data</span>'
        hist_rows = "".join([f'<tr><td style="border-bottom:1px solid #444; padding:5px 0; font-family:monospace; font-size:11px;">{colorize_metar(l)}</td></tr>' for l in logs[1:6]])

        # ポップアップのデザイン修正：widthを260pxに制限
        pop_html = f"""<div style="width:260px; background-color:#1a1a1a; color:white; padding:12px; border-radius:10px; font-family:sans-serif;">
            <div style="display:flex; border-bottom:2px solid #555; padding-bottom:5px; align-items:center;">
                <span style="font-size:14px; font-weight:bold;">{info['name']} ({icao})</span>
                <span style="margin-left:auto; background:{color}; color:white; padding:2px 6px; border-radius:4px; font-size:9px;">{status_text}</span>
            </div>
            <div style="margin:8px 0;">
                <div style="font-size:10px; color:#0f0; margin-bottom:2px;">● LATEST</div>
                <div style="background:#000; padding:8px; border-radius:5px; font-size:13px; border-left:4px solid {color}; line-height:1.4; font-family:monospace;">{current}</div>
            </div>
            <div style="font-size:10px; color:#aaa; margin-bottom:2px;">PAST LOGS</div>
            <div style="max-height:100px; overflow-y:auto; background:#000; padding:5px 8px; border-radius:5px;">
                <table style="width:100%; border-collapse:collapse;">{hist_rows if hist_rows else "<tr><td style='font-size:11px;'>No History</td></tr>"}</table>
            </div>
        </div>"""

        folium.Marker(
            [info['lat'], info['lon']],
            popup=folium.Popup(pop_html, max_width=300),
            icon=folium.Icon(color=color)
        ).add_to(m)

    m.save("index.html")
    print(f"✅ 全{len(AIRPORTS)}地点、高速処理完了。")

if __name__ == "__main__":
    main()
