import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from streamlit_searchbox import st_searchbox
from pathlib import Path
from geocoding import get_coordinates
from weather_api import get_weather


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="WeatherWise",
    page_icon="🌦️",
    layout="wide"
)


# ==========================================
# LOAD CSS
# ==========================================

def load_css():

    css_path = Path(__file__).parent / "style.css"

    if css_path.exists():

        css = css_path.read_text(encoding="utf-8")

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )

    else:
        st.warning("style.css not found!")


load_css()


# ==========================================
# WEATHER CODE MAPPING
# ==========================================

def get_weather_condition(code):

    conditions = {
        0: ("Clear Sky", "☀️"),
        1: ("Mainly Clear", "🌤️"),
        2: ("Partly Cloudy", "⛅"),
        3: ("Overcast", "☁️"),
        45: ("Foggy", "🌫️"),
        48: ("Foggy", "🌫️"),
        51: ("Light Drizzle", "🌦️"),
        53: ("Drizzle", "🌦️"),
        55: ("Heavy Drizzle", "🌧️"),
        61: ("Light Rain", "🌧️"),
        63: ("Moderate Rain", "🌧️"),
        65: ("Heavy Rain", "🌧️"),
        71: ("Light Snow", "🌨️"),
        73: ("Snow", "❄️"),
        75: ("Heavy Snow", "❄️"),
        80: ("Rain Showers", "🌦️"),
        81: ("Rain Showers", "🌧️"),
        82: ("Heavy Showers", "⛈️"),
        95: ("Thunderstorm", "⛈️"),
        96: ("Thunderstorm", "⛈️"),
        99: ("Heavy Thunderstorm", "⛈️")
    }

    return conditions.get(int(code), ("Unknown", "🌡️"))


# ==========================================
# HEADER
# ==========================================

st.html("""
<div style="
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:10px 0;
    flex-wrap:wrap;
">
    <div style="
        font-size:42px;
        font-weight:800;
        color:white;
    ">
        Weather<span style="
            background:linear-gradient(90deg,#ff72c6,#bd75ff);
            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;
        ">Wise.</span>
    </div>
</div>
""")


# ==========================================
# CITY SEARCH
# ==========================================

@st.cache_data(ttl=86400, show_spinner=False)

def search_cities(searchterm):

    if not searchterm or len(searchterm.strip()) < 3:
        return []

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": searchterm.strip(),
        "count": 5,
        "language": "en",
        "format": "json"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=5
        )

        response.raise_for_status()

        results = response.json().get("results", [])

        suggestions = []

        for place in results:

            name = place.get("name", "")
            state = place.get("admin1", "")
            country = place.get("country", "")

            label = ", ".join(
                part for part in [name, state, country] if part
            )

            suggestions.append((label, {
                "name": name,
                "country": country,
                "latitude": place["latitude"],
                "longitude": place["longitude"]
            }))

        return suggestions

    except requests.RequestException:
        return []


# ==========================================
# CITY SEARCH WITH AUTOCOMPLETE
# ==========================================

col1, col2 = st.columns([4, 1])

with col1:

    selected_location = st_searchbox(
        search_cities,
        placeholder="🔍 Search for a city...",
        key="city_search",
        label="",
        debounce=600,
        style_overrides={
            "searchbox": {

                # SEARCH BAR
                "control": {
                    "backgroundColor": "#241338",
                    "border": "1px solid #A855F7",
                    "borderRadius": "12px",
                    "boxShadow": "0 0 10px rgba(168, 85, 247, 0.3)",
                },

                # DROPDOWN
                "menu": {
                    "backgroundColor": "#241338",
                    "border": "1px solid #A855F7",
                    "borderRadius": "12px",
                },

                "menuList": {
                    "backgroundColor": "#241338",
                    "borderRadius": "12px",
                    "padding": "6px",
                },

                # CITY OPTIONS
                "option": {
                    "color": "#FFFFFF",
                    "backgroundColor": "#241338",
                    "highlightColor": "#F0ABFC",
                },

                "singleValue": {
                    "color": "#FFFFFF",
                },

                "input": {
                    "color": "#FFFFFF",
                },

                "placeholder": {
                    "color": "#C4A5D8",
                },
            }
        }
    )


with col2:

    search = st.button(
        "Search Weather",
        use_container_width=True
    )


# ==========================================
# FETCH WEATHER DATA
# ==========================================

if search:

    if selected_location:

        try:

            with st.spinner("Fetching weather information..."):

                weather_data = get_weather(
                    selected_location["latitude"],
                    selected_location["longitude"]
                )

                st.session_state["weather_data"] = weather_data

                st.session_state["location_data"] = selected_location

        except Exception as e:

            st.error(f"Something went wrong: {e}")

    else:

        st.warning("Please select a city from the suggestions.")


# ==========================================
# DISPLAY WEATHER DASHBOARD
# ==========================================

if (
    "weather_data" in st.session_state
    and "location_data" in st.session_state
):

    data = st.session_state["weather_data"]

    location = st.session_state["location_data"]

    current = data["current"]

    daily = data["daily"]

    hourly = data["hourly"]

    condition, icon = get_weather_condition(
        current["weather_code"]
    )


    # ======================================
    # CURRENT WEATHER
    # ======================================

    st.html(f"""

    <div class="hero-card">

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            gap:20px;
            flex-wrap:wrap;
        ">

            <div>

                <div class="city-name">

                    📍 {location['name']}, {location['country']}

                </div>

                <br>

                <div class="temperature">

                    {current['temperature_2m']}°C

                </div>

                <div class="weather-description">

                    {icon} {condition}

                </div>

                <br>

                <div style="color:#ffe5f6;">

                    Feels like {current['apparent_temperature']}°C

                </div>

            </div>

            <div class="weather-icon">

                {icon}

            </div>

        </div>

    </div>

    """)


    # ======================================
    # WEATHER HIGHLIGHTS
    # ======================================

    st.html("""

    <div class="section-title">

        Weather Highlights

    </div>

    """)

    col1, col2, col3, col4 = st.columns(4)

    metrics = [

        ("💧", "Humidity", f"{current['relative_humidity_2m']}%"),

        ("🌬️", "Wind Speed", f"{current['wind_speed_10m']} km/h"),

        ("🌡️", "Feels Like", f"{current['apparent_temperature']}°C"),

        ("🌧️", "Precipitation", f"{current['precipitation']} mm")

    ]

    for column, metric in zip(
        [col1, col2, col3, col4],
        metrics
    ):

        metric_icon, label, value = metric

        with column:

            st.html(f"""

            <div class="weather-card">

                <div class="card-label">

                    {metric_icon} {label}

                </div>

                <div class="card-value">

                    {value}

                </div>

            </div>

            """)


    # ======================================
    # HOURLY FORECAST
    # ======================================

    st.html("""

    <div class="section-title">

        Hourly Forecast

    </div>

    """)

    hourly_df = pd.DataFrame({

        "Time": pd.to_datetime(hourly["time"][:24]),

        "Temperature": hourly["temperature_2m"][:24],

        "Rain Probability": hourly["precipitation_probability"][:24]

    })

    fig = px.area(
        hourly_df,
        x="Time",
        y="Temperature",
        title="Temperature During the Next 24 Hours"
    )

    fig.update_traces(
        line=dict(color="#F04CA8", width=3),
        fillcolor="rgba(180,70,210,0.20)"
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified"
    )

    fig.update_xaxes(showgrid=False)

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.12)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # ======================================
    # 7-DAY FORECAST
    # ======================================

    st.html("""

    <div class="section-title">

        7-Day Forecast

    </div>

    """)

    number_of_days = min(7, len(daily["time"]))

    forecast_columns = st.columns(number_of_days)

    for i, column in enumerate(forecast_columns):

        code = daily["weather_code"][i]

        forecast_condition, forecast_icon = get_weather_condition(code)

        date = pd.to_datetime(daily["time"][i])

        day = date.strftime("%a")

        max_temp = daily["temperature_2m_max"][i]

        min_temp = daily["temperature_2m_min"][i]

        with column:

            st.html(f"""

            <div class="forecast-card">

                <div class="forecast-day">

                    {day}

                </div>

                <div class="forecast-icon">

                    {forecast_icon}

                </div>

                <div class="forecast-temp">

                    {max_temp}°

                </div>

                <div style="
                    color:#cba9d8;
                    font-size:13px;
                ">

                    {min_temp}°

                </div>

            </div>

            """)


    # ======================================
    # SUNRISE AND SUNSET
    # ======================================

    st.html("""

    <div class="section-title">

        Sunrise & Sunset

    </div>

    """)

    col1, col2 = st.columns(2)

    with col1:

        sunrise = pd.to_datetime(
            daily["sunrise"][0]
        ).strftime("%I:%M %p")

        st.html(f"""

        <div class="weather-card">

            <div class="card-label">

                🌅 Sunrise

            </div>

            <div class="card-value">

                {sunrise}

            </div>

        </div>

        """)


    with col2:

        sunset = pd.to_datetime(
            daily["sunset"][0]
        ).strftime("%I:%M %p")

        st.html(f"""

        <div class="weather-card">

            <div class="card-label">

                🌇 Sunset

            </div>

            <div class="card-value">

                {sunset}

            </div>

        </div>

        """)


# ==========================================
# WELCOME SCREEN
# ==========================================

else:

    st.html("""

    <div class="welcome-container">

        <div class="welcome-glow"></div>

        <div class="welcome-content">

            <div class="welcome-icon">

                🌤️

            </div>

            <h2 class="welcome-heading">

                Welcome to

                <span class="gradient-text">WeatherWise.</span>

            </h2>

            <p class="welcome-description">

                Your Personal Weather Companion 🌍

            </p>

            <p class="welcome-instruction">

                Search for your city above to explore

                real-time weather conditions and forecasts.

            </p>

            <div class="welcome-badge">

                ✨ Discover the weather around you

            </div>

        </div>

    </div>

    """)


# ==========================================
# FOOTER
# ==========================================

st.html("""

<div class="footer">

    Made with 💜 WeatherWise |

    Powered by Open-Meteo

</div>

""")