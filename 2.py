import flet as ft
import requests

# 気象庁の地域リストを取得するエンドポイント
AREA_LIST_URL = "http://www.jma.go.jp/bosai/common/const/area.json"

# 気象庁の天気予報を取得するエンドポイントのベースURL
WEATHER_FORECAST_BASE_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/"

def main(page):
    page.title = "天気予報アプリ"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20  # 余白を追加

    # ページのヘッダー
    header = ft.Text(value="天気予報アプリ", style="displayLarge", text_align=ft.TextAlign.CENTER)

    # 地域リストを取得
    response = requests.get(AREA_LIST_URL)
    if response.status_code != 200:
        print("Failed to fetch area list")
        return
    area_list = response.json()

    # NavigationRailのアイテムを作成する関数
    def create_navigation_rail_destinations(area_list):
        destinations = []
        region_codes = []

        for region, data in area_list['offices'].items():
            # 事務所名が存在する地域だけを選択します
            if data['officeName'] != "-":
                destinations.append(
                    ft.NavigationRailDestination(
                        icon=ft.icons.LABEL,
                        selected_icon=ft.icons.LABEL_OUTLINE,
                        label=data['officeName']
                    )
                )
                region_codes.append(region)

        return destinations, region_codes

    destinations, region_codes = create_navigation_rail_destinations(area_list)

    # 天気予報を表示する関数
    def display_weather_forecast(event=None):
        if event:
            region_index = event.control.selected_index
        else:
            region_index = 0  # 初期表示用に0を設定

        if not region_codes:
            print("No region codes available")
            return

        region_code = region_codes[region_index]
        weather_url = f"{WEATHER_FORECAST_BASE_URL}{region_code}.json"

        print(f"Fetching weather data for region code: {region_code}")
        response = requests.get(weather_url)
        if response.status_code != 200:
            print(f"Failed to fetch weather data for region code: {region_code}")
            return

        weather_forecast = response.json()

        # 表示をクリア
        content_column.controls.clear()

        # デバッグ用ログ
        print(f"Retrieved weather data: {weather_forecast}")

        # 各地域ごとの天気予報を表示するカードの作成
        if weather_forecast:
            areas = weather_forecast[0]['timeSeries'][0]['areas']
            for area in areas:
                area_name = area['area']['name']
                area_weather_forecast = ft.Text(value=f"{area_name}の天気予報:\n", style="headlineMedium")
                content_column.controls.append(area_weather_forecast)
                for time, weather in zip(weather_forecast[0]['timeSeries'][0]['timeDefines'], area['weathers']):
                    weather_card = ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(value=f"日時: {time}"),
                                    ft.Text(value=f"天気: {weather}"),
                                ]
                            ),
                            padding=10
                        )
                    )
                    content_column.controls.append(weather_card)

        else:
            content_column.controls.append(ft.Text(value="天気予報が利用できません"))

        page.update()

    # ナビゲーションレールの設定
    nav_rail = ft.NavigationRail(
        selected_index=0,
        on_change=display_weather_forecast,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=destinations,
        expand=True,
    )

    # コンテンツカラム（メインコンテンツ）の定義
    content_column = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    # コンテントを包むコンテナの定義
    content_container = ft.Container(
        content=content_column,
        expand=True,
        padding=20
    )

    # ナビゲーションレールを包むコンテナの定義
    nav_container = ft.Container(
        content=nav_rail,
        height=page.height,  # ヘッダーの高さを除いた固定の高さを定義
        width=200,
        expand=True,
        padding=20
    )

    # 全体レイアウトの定義
    main_layout = ft.Row(
        controls=[nav_container, content_container],
        expand=True
    )

    # ページの追加
    page.add(header)
    page.add(main_layout)

    # 初期の天気予報を表示
    display_weather_forecast()

    page.update()

ft.app(target=main)