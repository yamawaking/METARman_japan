import folium
import requests
import re
from datetime import datetime
import time
import random

# --- 1. 飛行場データ (全地点 + 救済地点) ---
AIRPORTS = {
    "RJCC": {"name": "新千歳空港", "lat": 42.7752, "lon": 141.6923}, "RJCH": {"name": "函館空港", "lat": 41.7700, "lon": 140.8219},
    "RJCK": {"name": "釧路空港", "lat": 43.0411, "lon": 144.1931}, "RJCB": {"name": "帯広空港", "lat": 42.7333, "lon": 143.2170},
    "RJCW": {"name": "稚内空港", "lat": 45.4039, "lon": 141.8020}, "RJCM": {"name": "女満別空港", "lat": 43.8803, "lon": 144.1640},
    "RJCA": {"name": "旭川空港", "lat": 43.6708, "lon": 142.4475}, "RJCN": {"name": "中標津空港", "lat": 43.5775, "lon": 144.9589},
    "RJCO": {"name": "札幌(丘珠)", "lat": 43.1161, "lon": 141.3783}, "RJEC": {"name": "旭川(陸自)", "lat": 43.7947, "lon": 142.3653},
    "RJSS": {"name": "仙台空港", "lat": 38.1397, "lon": 140.9169}, "RJST": {"name": "松島基地", "lat": 38.4033, "lon": 141.2133},
    "RJSU": {"name": "霞目(陸自)", "lat": 38.2367, "lon": 140.9189}, "RJSA": {"name": "青森空港", "lat": 40.7347, "lon": 140.6908},
    "RJSB": {"name": "三沢基地/空港", "lat": 40.7031, "lon": 141.3681}, "RJSM": {"name": "三沢(射爆場)", "lat": 40.8522, "lon": 141.3850},
    "RJSH": {"name": "八戸飛行場", "lat": 40.5544, "lon": 141.4658}, "RJSI": {"name": "花巻空港", "lat": 39.4286, "lon": 141.1353},
    "RJSK": {"name": "秋田空港", "lat": 39.6156, "lon": 140.2186}, "RJSY": {"name": "庄内空港", "lat": 38.8125, "lon": 139.7875},
    "RJSC": {"name": "山形空港", "lat": 38.4117, "lon": 140.3711}, "RJSF": {"name": "福島空港", "lat": 37.2264, "lon": 140.4347},
    "RJSN": {"name": "新潟空港", "lat": 37.9564, "lon": 139.1214}, "RJTT": {"name": "羽田空港", "lat": 35.5494, "lon": 139.7798},
    "RJAA": {"name": "成田空港", "lat": 35.7647, "lon": 140.3863}, "RJTY": {"name": "横田基地", "lat": 35.7486, "lon": 139.3486},
    "RJTJ": {"name": "入間基地", "lat": 35.8414, "lon": 139.4122}, "RJAH": {"name": "百里基地", "lat": 36.1811, "lon": 140.4147},
    "RJTA": {"name": "厚木基地", "lat": 35.4547, "lon": 139.4500}, "RJTL": {"name": "下総基地", "lat": 35.8028, "lon": 140.0114},
    "RJTU": {"name": "宇都宮(陸自)", "lat": 36.5147, "lon": 139.8689}, "RJTK": {"name": "木更津(陸自)", "lat": 35.3986, "lon": 139.9114},
    "RJTC": {"name": "立川(陸自)", "lat": 35.7139, "lon": 139.4019}, "RJTF": {"name": "調布飛行場", "lat": 35.6722, "lon": 139.5272},
    "RJTI": {"name": "東京ヘリポート", "lat": 35.6367, "lon": 139.8453}, "RJTO": {"name": "大島空港", "lat": 34.7820, "lon": 139.3603},
    "RJTH": {"name": "八丈島空港", "lat": 33.1147, "lon": 139.7867}, "RJAF": {"name": "松本空港", "lat": 36.1667, "lon": 137.9192},
    "RJNK": {"name": "小松基地/空港", "lat": 36.3947, "lon": 136.4072}, "RJNT": {"name": "富山空港", "lat": 36.6475, "lon": 137.1875},
    "RJNS": {"name": "静岡空港", "lat": 34.7961, "lon": 138.1794}, "RJGG": {"name": "中部国際空港", "lat": 34.8583, "lon": 136.8053},
    "RJNA": {"name": "名古屋(小牧)", "lat": 35.2461, "lon": 136.9244}, "RJNY": {"name": "静浜基地", "lat": 34.8144, "lon": 138.2978},
    "RJME": {"name": "明野飛行場", "lat": 34.5292, "lon": 136.6694}, "RJBB": {"name": "関西国際空港", "lat": 34.4347, "lon": 135.2441},
    "RJOO": {"name": "伊丹空港", "lat": 34.7855, "lon": 135.4382}, "RJBE": {"name": "神戸空港", "lat": 34.6328, "lon": 135.2239},
    "RJBD": {"name": "南紀白浜空港", "lat": 33.6622, "lon": 135.3556}, "RJBK": {"name": "岡山空港", "lat": 34.7567, "lon": 133.8550},
    "RJOA": {"name": "広島空港", "lat": 34.4400, "lon": 132.9197}, "RJOH": {"name": "米子/美保基地", "lat": 35.4922, "lon": 133.2364},
    "RJOC": {"name": "出雲空港", "lat": 35.4131, "lon": 132.8900}, "RJOT": {"name": "高松空港", "lat": 34.2142, "lon": 134.0156},
    "RJOM": {"name": "松山空港", "lat": 33.8272, "lon": 132.6997}, "RJOK": {"name": "高知空港", "lat": 33.5469, "lon": 133.6694},
    "RJOS": {"name": "徳島空港", "lat": 34.1328, "lon": 134.6067}, "RJOW": {"name": "石見空港", "lat": 34.6756, "lon": 131.7903},
    "RJOP": {"name": "小月飛行場", "lat": 34.0450, "lon": 131.0531}, "RJFF": {"name": "福岡空港", "lat": 33.5859, "lon": 130.4507},
    "RJFU": {"name": "長崎空港", "lat": 32.9169, "lon": 129.9136}, "RJFT": {"name": "熊本空港", "lat": 32.8372, "lon": 130.8550},
    "RJFM": {"name": "宮崎空港", "lat": 31.8772, "lon": 131.4486}, "RJFK": {"name": "鹿児島空港", "lat": 31.8033, "lon": 130.7194},
    "RJFN": {"name": "新田原基地", "lat": 32.0833, "lon": 131.4517}, "RJFY": {"name": "鹿屋基地", "lat": 31.3686, "lon": 130.8447},
    "RJDA": {"name": "天草飛行場", "lat": 32.4819, "lon": 130.1586}, "ROAH": {"name": "那覇空港/基地", "lat": 26.2044, "lon": 127.6461},
    "RODN": {"name": "嘉手納基地", "lat": 26.3556, "lon": 127.7675}, "ROMC": {"name": "普天間基地", "lat": 26.2731, "lon": 127.7581},
    "RORA": {"name": "奄美空港", "lat": 28.4308, "lon": 129.7125}, "ROIG": {"name": "新石垣空港", "lat": 24.3964, "lon": 124.2450},
    "ROMY": {"name": "宮古空港", "lat": 24.7831, "lon": 125.2953}, "ROYN": {"name": "与那国空港", "lat": 24.4678, "lon": 122.9769},
}

def colorize_metar(metar):
    if not metar or "No" in metar: return metar
    tokens = metar.split()
    colored_tokens = []
    weather_codes = ["RA", "SN", "DZ", "GR", "GS", "SG", "IC", "PL", "FG", "BR", "HZ", "VA", "DU", "SA", "FU", "TS", "SQ", "FC", "SS", "DS", "PO", "VCSH", "VCTS", "VC"]
    for token in tokens:
        ct = token
        if token.endswith("KT") and len(token) >= 7:
            ct = re.sub(r'(G\d+KT)', r'<span style="color: yellow;">\1</span>', token) if 'G' in token else f'<span style="color: white;">{token}</span>'
        elif re.fullmatch(r'\d{4}', token):
            ct = f'<span style="color: cyan;">{token}</span>' if token != "9999" else f'<span style="color: white;">{token}</span>'
        else:
            clean = token.lstrip('+-')
            if any(c in clean for c in weather_codes):
                ct = f'<span style="color: red;">{token}</span>'
            elif re.match(r'(FEW|SCT|BKN|OVC|VV)\d{3}', token):
                ct = f'<span style="color: lime;">{token}</span>' if token.startswith(("BKN", "OVC", "VV")) else f'<span style="color: white;">{token}</span>'
        colored_tokens.append(ct)
    return " ".join(colored_tokens)

def get_fallback_metar(icao):
    """キャッシュ破棄して最新1件を取得"""
    url = f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao}.TXT?v={random.randint(1,9999)}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            lines = r.text.splitlines()
            if len(lines) >= 2:
                metar = lines[1].strip()
                if icao in metar:
                    return [metar[metar.find(icao):].replace('=', '')]
    except: pass
    return []

def main():
    icao_list = list(AIRPORTS.keys())
    metar_storage = {icao: [] for icao in icao_list}
    
    # --- 1. API一括取得 (24時間分) ---
    chunks = [icao_list[i:i + 20] for i in range(0, len(icao_list), 20)]
    for chunk in chunks:
        ids_str = ",".join(chunk)
        url = f"https://www.aviationweather.gov/api/data/metar?ids={ids_str}&format=raw&hours=24&v={random.randint(1,999)}"
        try:
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
            if res.status_code == 200:
                lines = res.text.splitlines()
                for line in lines:
                    line = line.strip()
                    for icao in chunk:
                        if re.search(rf"(?:^|\s){icao}\s\d{{6}}Z", line):
                            clean_line = line[line.find(icao):].replace('=', '')
                            if len(clean_line) > 10: metar_storage[icao].append(clean_line)
        except: pass
        time.sleep(1)

    # --- 2. 救済措置 (特定地点が空、または古い場合に強制取得) ---
    rescue_targets = ["RJST", "RJSB", "RJSM", "RJTU", "RJTJ", "RJTC", "RJAH", "RJNA"]
    for icao in rescue_targets:
        if icao in metar_storage and not metar_storage[icao]:
            rd = get_fallback_metar(icao)
            if rd: metar_storage[icao] = rd

    # --- 3. マップ作成 ---
    m = folium.Map(location=[36.5, 137.5], zoom_start=5, tiles='CartoDB positron')
    for icao, info in AIRPORTS.items():
        # 履歴を重複排除して新しい順にソート
        logs = sorted(list(set(metar_storage.get(icao, []))), reverse=True)
        current = colorize_metar(logs[0]) if logs else '<span style="color: gray;">No recent data</span>'
        
        # 履歴テーブル (元通りの形式)
        hist_rows = "".join([f'<tr><td style="border-bottom:1px solid #444; padding:5px 0; font-size:13px; font-family:monospace;">{colorize_metar(l)}</td></tr>' for l in logs[1:10]])
        
        pop_html = f"""<div style="width: 480px; background-color: #1a1a1a; color: white; padding: 15px; border-radius: 10px;">
            <h3 style="margin: 0 0 10px 0; border-bottom: 2px solid #555;">{info['name']} ({icao})</h3>
            <div style="margin-bottom: 10px;"><div style="font-size: 11px; color: #0f0;">● LATEST</div><div style="background-color: #000; padding: 10px; border-radius: 5px; font-size: 16px; font-weight: bold; border-left: 5px solid {("#0f0" if logs else "#555")};">{current}</div></div>
            <div style="font-size: 11px; color: #888;">HISTORY (24h)</div>
            <div style="max-height: 150px; overflow-y: auto; background-color: #000; padding: 5px 10px; border-radius: 5px;"><table style="width: 100%;">{hist_rows if hist_rows else "<tr><td>No history</td></tr>"}</table></div>
        </div>"""
        
        folium.Marker(
            [info['lat'], info['lon']], 
            popup=folium.Popup(pop_html, max_width=500), 
            tooltip=f"{info['name']} ({icao})", 
            icon=folium.Icon(color="blue" if logs else "gray")
        ).add_to(m)

    # UTC時計
    m.get_root().html.add_child(folium.Element('<div id="utc" style="position:fixed; top:20px; left:60px; width:160px; height:45px; background:rgba(0,0,0,0.8); color:#0f0; border:1px solid #555; border-radius:5px; z-index:9999; display:flex; flex-direction:column; align-items:center; justify-content:center; font-family:monospace;"><div style="font-size:9px; color:#fff;">UTC</div><div id="utct" style="font-size:20px; font-weight:bold;">00:00:00</div></div><script>setInterval(()=>{const n=new Date();document.getElementById("utct").textContent=n.toISOString().substr(11,8)},1000)</script>'))
    
    m.save("index.html")
    print("✅ 復元完了：全地点収録・履歴表示復活版です。ゆっくり休んでください！")

if __name__ == "__main__":
    main()
