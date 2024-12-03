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

    def create_expansion_tile(center_code):
        """地域センターごとの詳細地域を表示するExpansionTileを作成"""
        children_codes = centers[center_code]["children"]
        return ft.ExpansionTile(
            title=ft.Text(centers[center_code]["name"]),
            controls=[
                ft.ListTile(
                    title=ft.Text(offices[code]["name"]),
                    on_click=lambda e, code=code: on_region_selected(code),
                )
                for code in children_codes if code in offices
            ],
        )

    # NavigationRailを構築
    navigation_rail = ft.Column(
        [
            ft.Text("地域を選択", size=18, weight="bold"),
            ft.Divider(),
            *[
                create_expansion_tile(center_code)
                for center_code in centers
            ],
        ],
        scroll="auto",  # スクロール可能に
        expand=True,
    )

    # 天気予報を表示するテキスト
    weather_text = ft.Text(value="Active View", size=24, weight="bold", color="gray")

    # レイアウトを構築
    layout = ft.Row(
        [
            ft.Container(
                content=navigation_rail,
                width=300,  # 左側の幅
                bgcolor="lightgray",
                padding=10,
                expand=False,
            ),
            ft.VerticalDivider(width=1),
            ft.Container(
                content=weather_text,
                expand=True,
                bgcolor="lightblue",
                alignment=ft.alignment.center,
            ),
        ],
        expand=True,
    )

    # ページに追加
    page.add(layout)

# アプリを起動
ft.app(target=main)
