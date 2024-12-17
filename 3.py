import sqlite3
import requests
from datetime import datetime

def create_tables():
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS area (
        area_id INTEGER PRIMARY KEY AUTOINCREMENT,
        area_name TEXT NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_forecast (
        forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
        area_id INTEGER,
        forecast_date DATE NOT NULL,
        weather TEXT NOT NULL,
        max_temp REAL,
        min_temp REAL,
        FOREIGN KEY (area_id) REFERENCES area(area_id)
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        area_id INTEGER,
        record_date DATE NOT NULL,
        weather TEXT NOT NULL,
        max_temp REAL,
        min_temp REAL,
        FOREIGN KEY (area_id) REFERENCES area(area_id)
    )''')
    
    conn.commit()
    conn.close()

# 天気予報データをAPIから取得
def fetch_weather_data(area_name):
    api_url = f"https://api.weather.com/v1/forecast?area={area_name}&apikey=YOUR_API_KEY"
    response = requests.get(api_url)
    return response.json()

def insert_weather_data(weather_data, area_name):
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO area (area_name) VALUES (?)", (area_name,))
    cursor.execute("SELECT area_id FROM area WHERE area_name = ?", (area_name,))
    area_id = cursor.fetchone()[0]

    for forecast in weather_data['forecasts']:
        cursor.execute('''
        INSERT INTO weather_forecast (area_id, forecast_date, weather, max_temp, min_temp)
        VALUES (?, ?, ?, ?, ?)''', 
        (area_id, 
         datetime.strptime(forecast['date'], "%Y-%m-%d"), 
         forecast['weather'], 
         forecast['max_temp'], 
         forecast['min_temp']))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    area_name = "Tokyo"
    weather_data = fetch_weather_data(area_name)
    insert_weather_data(weather_data, area_name)

    def display_weather_forecast(area_name):
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.area_name, f.forecast_date, f.weather, f.max_temp, f.min_temp
    FROM weather_forecast f
    JOIN area a ON f.area_id = a.area_id
    WHERE a.area_name = ?
    ORDER BY f.forecast_date
    """, (area_name,))

    rows = cursor.fetchall()
    for row in rows:
        print(f"Date: {row[1]}, Area: {row[0]}, Weather: {row[2]}, Max Temp: {row[3]}, Min Temp: {row[4]}")

    conn.close()

# 天気予報を表示
if __name__ == "__main__":
    display_weather_forecast("Tokyo")

def display_past_weather_records(area_name, record_date):
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.area_name, r.record_date, r.weather, r.max_temp, r.min_temp
    FROM weather_records r
    JOIN area a ON r.area_id = a.area_id
    WHERE a.area_name = ? AND r.record_date = ?
    ORDER BY r.record_date
    """, (area_name, record_date))

    rows = cursor.fetchall()
    for row in rows:
        print(f"Date: {row[1]}, Area: {row[0]}, Weather: {row[2]}, Max Temp: {row[3]}, Min Temp: {row[4]}")

    conn.close()

# 過去の予報を表示
if __name__ == "__main__":
    display_past_weather_records("Tokyo", "2023-10-01")