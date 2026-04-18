from taipy.gui import Gui
import requests
import pandas as pd
import numpy as np

# =========================
# GET WEATHER (NO API KEY)
# =========================
def get_weather(city_name):
    try:
        url = f"https://wttr.in/{city_name}?format=j1"
        res = requests.get(url, timeout=5)
        data = res.json()

        current = data["current_condition"][0]
        temp_val = current["temp_C"]
        desc_val = current["weatherDesc"][0]["value"]

        dates = []
        temps = []
        icons = []

        for d in data["weather"]:
            dates.append(d["date"])
            temps.append(int(d["avgtempC"]))

            desc = d["hourly"][0]["weatherDesc"][0]["value"].lower()

            if "sun" in desc or "clear" in desc:
                icons.append("☀️")
            elif "cloud" in desc:
                icons.append("☁️")
            elif "rain" in desc:
                icons.append("🌧️")
            else:
                icons.append("🌥️")

        # =========================
        # SMOOTH LINE (INTERPOLATION)
        # =========================
        x = np.arange(len(temps))
        x_smooth = np.linspace(x.min(), x.max(), 50)
        y_smooth = np.interp(x_smooth, x, temps)

        smooth_df = pd.DataFrame({
            "date": x_smooth,
            "temp": y_smooth
        })

        display_df = pd.DataFrame({
            "date": dates,
            "temp": temps,
            "icon": icons
        })

        return temp_val, desc_val, smooth_df, display_df

    except Exception as e:
        print("ERROR:", e)

        smooth_df = pd.DataFrame({
            "date": [0,1,2,3,4],
            "temp": [30,31,29,32,30]
        })

        display_df = pd.DataFrame({
            "date": ["Mon","Tue","Wed","Thu","Fri"],
            "temp": [30,31,29,32,30],
            "icon": ["☀️","☁️","🌧️","☀️","🌥️"]
        })

        return "30", "Clear", smooth_df, display_df


# =========================
# INITIAL STATE
# =========================
city = "Jakarta"
temp, desc, forecast_df, forecast_display = get_weather(city)


# =========================
# UPDATE FUNCTION
# =========================
def update(state):
    t, d, df, disp = get_weather(state.city)
    state.temp = t
    state.desc = d
    state.forecast_df = df
    state.forecast_display = disp


# =========================
# UI PAGE
# =========================
page = """
# 🌙 Weather Dashboard

<|{city}|input|label=Search City|on_change=update|>

---

## 🌡️ Today
Temp: <|{temp}|text|> °C  
Condition: <|{desc}|text|>

---

## 📅 Daily Forecast
<|{forecast_display}|table|>

---

## 📈 Temperature Trend
<|{forecast_df}|chart|type=line|x=date|y=temp|height=300px|>
"""


# =========================
# RUN APP
# =========================
Gui(page).run(
    title="Weather App",
    host="0.0.0.0",
    port=8501,
    use_reloader=False
)
