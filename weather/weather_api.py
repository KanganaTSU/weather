import requests

def get_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "is_day",
            "precipitation",
            "weather_code",
            "wind_speed_10m"
        ],

        "hourly": [
            "temperature_2m",
            "precipitation_probability",
            "weather_code"
        ],

        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "sunrise",
            "sunset",
            "precipitation_probability_max"
        ],

        "timezone": "auto",
        "forecast_days": 7
    }

    response = requests.get(url, params=params, timeout=15)

    response.raise_for_status()

    return response.json()