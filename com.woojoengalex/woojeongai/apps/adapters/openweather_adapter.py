from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import requests

OPENWEATHER_CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
OPENWEATHER_ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"


@dataclass(frozen=True)
class WeatherCity:
    id: str
    name: str
    name_ko: str
    query: str
    lat: float
    lon: float
    timezone: str


WEATHER_CITIES: dict[str, WeatherCity] = {
    "seoul": WeatherCity(
        id="seoul",
        name="Seoul",
        name_ko="서울",
        query="Seoul",
        lat=37.5665,
        lon=126.9780,
        timezone="Asia/Seoul",
    ),
    "tokyo": WeatherCity(
        id="tokyo",
        name="Tokyo",
        name_ko="도쿄",
        query="Tokyo,JP",
        lat=35.6762,
        lon=139.6503,
        timezone="Asia/Tokyo",
    ),
    "new_york": WeatherCity(
        id="new_york",
        name="New York",
        name_ko="뉴욕",
        query="New York,US",
        lat=40.7128,
        lon=-74.0060,
        timezone="America/New_York",
    ),
    "london": WeatherCity(
        id="london",
        name="London",
        name_ko="런던",
        query="London,GB",
        lat=51.5074,
        lon=-0.1278,
        timezone="Europe/London",
    ),
}

CITY_ORDER: tuple[str, ...] = ("seoul", "tokyo", "new_york", "london")


class OpenWeatherAdapter:
    @staticmethod
    def _params(api_key: str) -> dict[str, str]:
        return {
            "appid": api_key,
            "units": "metric",
            "lang": "kr",
        }

    @staticmethod
    def get_city(city_id: str) -> WeatherCity:
        city = WEATHER_CITIES.get(city_id)
        if city is None:
            raise KeyError(city_id)
        return city

    @staticmethod
    def fetch_current(api_key: str, city: WeatherCity) -> dict[str, int | str | None]:
        response = requests.get(
            OPENWEATHER_CURRENT_URL,
            params={
                **OpenWeatherAdapter._params(api_key),
                "q": city.query,
            },
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        weather = payload["weather"][0]
        return {
            "temp": round(payload["main"]["temp"]),
            "description": weather["description"],
            "icon": weather.get("icon"),
        }

    @staticmethod
    def fetch_seoul_celsius(api_key: str) -> dict[str, int | str]:
        data = OpenWeatherAdapter.fetch_current(api_key, WEATHER_CITIES["seoul"])
        return {"temp": int(data["temp"]), "description": str(data["description"])}

    @staticmethod
    def fetch_weekly(
        api_key: str, city: WeatherCity, days: int = 7
    ) -> list[dict[str, int | str | None]]:
        try:
            return OpenWeatherAdapter._fetch_onecall_daily(api_key, city, days)
        except requests.HTTPError:
            return OpenWeatherAdapter._aggregate_forecast(api_key, city, days)

    @staticmethod
    def fetch_seoul_weekly(api_key: str, days: int = 7) -> list[dict[str, int | str | None]]:
        return OpenWeatherAdapter.fetch_weekly(api_key, WEATHER_CITIES["seoul"], days)

    @staticmethod
    def _city_tz(city: WeatherCity) -> timezone:
        return ZoneInfo(city.timezone)

    @staticmethod
    def _fetch_onecall_daily(
        api_key: str, city: WeatherCity, days: int
    ) -> list[dict[str, int | str | None]]:
        response = requests.get(
            OPENWEATHER_ONECALL_URL,
            params={
                **OpenWeatherAdapter._params(api_key),
                "lat": str(city.lat),
                "lon": str(city.lon),
                "exclude": "current,minutely,hourly,alerts",
            },
            timeout=10,
        )
        response.raise_for_status()
        tz = OpenWeatherAdapter._city_tz(city)
        daily = response.json().get("daily", [])[:days]
        result: list[dict[str, int | str | None]] = []
        for item in daily:
            weather = item["weather"][0]
            result.append(
                {
                    "date": datetime.fromtimestamp(item["dt"], tz=tz).date().isoformat(),
                    "temp": round(item["temp"]["day"]),
                    "temp_min": round(item["temp"]["min"]),
                    "temp_max": round(item["temp"]["max"]),
                    "description": weather["description"],
                    "icon": weather.get("icon"),
                }
            )
        return result

    @staticmethod
    def _aggregate_forecast(
        api_key: str, city: WeatherCity, days: int
    ) -> list[dict[str, int | str | None]]:
        response = requests.get(
            OPENWEATHER_FORECAST_URL,
            params={
                **OpenWeatherAdapter._params(api_key),
                "q": city.query,
                "cnt": 40,
            },
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
        tz_offset = payload.get("city", {}).get("timezone", 0)
        tz = timezone(timedelta(seconds=int(tz_offset)))
        by_date: dict[str, list[dict]] = defaultdict(list)
        for item in payload.get("list", []):
            day = datetime.fromtimestamp(item["dt"], tz=tz).date().isoformat()
            by_date[day].append(item)

        result: list[dict[str, int | str | None]] = []
        for day in sorted(by_date.keys())[:days]:
            entries = by_date[day]
            temps = [e["main"]["temp"] for e in entries]
            noon = max(entries, key=lambda e: e["dt"])
            weather = noon["weather"][0]
            result.append(
                {
                    "date": day,
                    "temp": round(sum(temps) / len(temps)),
                    "temp_min": round(min(temps)),
                    "temp_max": round(max(temps)),
                    "description": weather["description"],
                    "icon": weather.get("icon"),
                }
            )
        return result
