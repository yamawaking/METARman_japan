import folium
import requests
import re
from datetime import datetime, timezone
import time
import random
from concurrent.futures import ThreadPoolExecutor

# --- 1. 飛行場データ（大幅拡充） ---
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
    """METARから色とガストの有無を判定する"""
    if not metar_line or metar_line == "No data":
        return "gray", False
    
    # ガスト判定: 文字列に "G" と "KT" があればガストありとみなす
    has_gust = "G" in metar_line and "KT" in metar_line
    
    if "FG" in metar_line or "BR" in metar_line:
        return "orange", has_gust
    if has_gust:
        return "orange", True
        
    return "blue", False

def main():
    # 地図の初期化
    m = folium.Map(location=[35.0, 135.0], zoom_start=5)

    # UTC時計の埋め込み
    utc_clock_html = '''
    <div style="position: fixed; top: 10px; left: 50px; width: 150px; height: 40px; 
                background-color: rgba(255,255,255,0.8); border:2px solid grey; z-index:9999; 
                font-size:14px; font-weight:bold; text-align:center; line-height:40px; border-radius:5px;">
        UTC: <span id="utc_clock"></span>
    </div>
    <script>
        function updateClock() {
            var now = new Date();
            var utc = now.toISOString().replace('T', ' ').substring(0, 19);
            document.getElementById('utc_clock').innerHTML = utc.split(' ')[1];
        }
        setInterval(updateClock, 1000);
    </script>
    '''
    m.get_root().html.add_child(folium.Element(utc_clock_html))

    # 各空港のマーカー作成
    for icao, info in AIRPORTS.items():
        metar = get_metar(icao)
        history = get_history(icao)
        color_name, gust_flag = get_status(metar)
        
        # 1. 履歴テーブルHTML
        history_html = "<table style='width:100%; font-size:10px; border-collapse: collapse;'>"
        history_html += "<tr style='background:#eee;'><th>Time</th><th>METAR</th></tr>"
        for h_time, h_metar in history:
            history_html += f"<tr><td style='border-bottom:1px solid #ddd;'>{h_time}</td><td style='border-bottom:1px solid #ddd;'>{h_metar}</td></tr>"
        history_html += "</table>"

        # 2. ポップアップの中身 (必ず popup_obj を作る前に定義)
        content = f"""
        <div style="font-family: sans-serif; width: 240px;">
            <div style="font-size: 14px; font-weight: bold; border-bottom: 2px solid {color_name}; margin-bottom: 5px;">
                {icao} ({info['name']})
            </div>
            <div style="font-size: 11px; background: #f9f9f9; padding: 5px; border-radius: 3px; margin-bottom: 10px; word-wrap: break-word;">
                <strong>Latest:</strong> {metar}
                {' <b style="color:orange;">(GUST!)</b>' if gust_flag else ''}
            </div>
            <div style="font-size: 11px; font-weight: bold; margin-bottom: 3px;">24h History:</div>
            <div style="max-height: 120px; overflow-y: auto; border: 1px solid #ccc;">
                {history_html}
            </div>
        </div>
        """

        # 3. Popupオブジェクト作成
        popup_obj = folium.Popup(content, max_width=260)

        # 4. マーカー追加
        folium.Marker(
            location=info["coords"],
            popup=popup_obj,
            icon=folium.Icon(color=color_name, icon="plane", prefix="fa")
        ).add_to(m)

    # 保存
    m.save("index.html")

# プログラムの実行
if __name__ == "__main__":
    main()
