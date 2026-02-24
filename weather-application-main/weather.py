from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Get latitude & longitude from city name
def get_coordinates(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city,
        "count": 1
    }
    response = requests.get(url, params=params).json()

    if "results" not in response:
        return None, None

    lat = response["results"][0]["latitude"]
    lon = response["results"][0]["longitude"]
    return lat, lon


@app.route("/", methods=["GET", "POST"])
def home():
    city = ""
    current_weather = None
    forecast = None
    error = None
    forecast_type = "1"   # default = Today

    if request.method == "POST":
        city = request.form.get("city")
        forecast_type = request.form.get("forecast_type", "1")

        lat, lon = get_coordinates(city)

        if lat is None:
            error = "City not found. Please enter a valid city."
        else:
            try:
                weather_url = "https://api.open-meteo.com/v1/forecast"
                params = {
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": True,
                    "daily": "temperature_2m_max,temperature_2m_min,weathercode",
                    "timezone": "auto"
                }

                data = requests.get(weather_url, params=params).json()

                # Current weather
                current_weather = {
                    "temperature": data["current_weather"]["temperature"],
                    "windspeed": data["current_weather"]["windspeed"]
                }

                # Forecast
                days = int(forecast_type)
                dates = data["daily"]["time"][:days]
                max_temp = data["daily"]["temperature_2m_max"][:days]
                min_temp = data["daily"]["temperature_2m_min"][:days]
                codes = data["daily"]["weathercode"][:days]

                forecast = list(zip(dates, max_temp, min_temp, codes))

            except Exception:
                error = "Unable to fetch weather data. Try again later."

    return render_template(
        "we.html",
        city=city,
        current_weather=current_weather,
        forecast=forecast,
        forecast_type=forecast_type,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
