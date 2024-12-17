import flet as ft
import requests
import json

# 気象庁APIエンドポイント
FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{region_code}.json"
AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"

def fetch_area_data():
    """地域データをAPIから取得"""
    try:
        response = requests.get(AREA_URL)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"地域データの取得に失敗しました: {e}")
        return None

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.scroll = "adaptive"

    # タイトルをページの一番上に追加
    title_text = ft.Container(
        content=ft.Text(
            value="天気予報",
            size=32,
            weight="bold",
            color="blue",
        ),
        alignment=ft.alignment.center,
        padding=10,
    )
    page.add(title_text)

    # 地域データを取得
    area_data = fetch_area_data()
    if not area_data:
        page.add(ft.Text(value="地域データの取得に失敗しました。アプリを再起動してください。", color="red"))
        return

    centers = area_data["centers"]
    offices = area_data["offices"]

    def fetch_weather_forecast(region_code):
        """天気予報を取得する"""
        try:
            response = requests.get(FORECAST_URL.format(region_code=region_code))
            response.raise_for_status()
            data = response.json()
            return data[0]["timeSeries"][0]["areas"][0]["weathers"][0]
        except Exception as e:
            return f"天気情報の取得に失敗しました: {e}"

    def on_region_selected(region_code):
        """地域選択時の処理"""
        weather = fetch_weather_forecast(region_code)
        weather_text.value = f"{offices[region_code]['name']}の天気:\n{weather}"
        page.update()

    # 地域を選ぶドロップダウンリストを作成
    region_dropdown = ft.Dropdown(
        label="地域を選択",
        options=[ft.dropdown.Option(offices[code]["name"], data=code) for code in offices],
        on_change=lambda e: on_region_selected(e.control.data)  # 修正箇所: dataを使用
    )

    # 天気予報を表示するテキスト
    weather_text = ft.Text(value="選択した地域の天気がここに表示されます", size=20, weight="bold", color="gray")

    # レイアウトを構築
    layout = ft.Column(
        [
            title_text,
            region_dropdown,
            ft.Divider(),
            weather_text,
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # ページに追加
    page.add(layout)

# アプリを起動
ft.app(target=main)
