import sys
import re
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from datetime import datetime, timezone


def http_get(url, headers=None):
    req = Request(url, headers=headers or {})
    with urlopen(req) as resp:
        return resp.read().decode("utf-8")


def http_post(url, body, headers=None):
    data = body.encode("utf-8")
    req = Request(url, data=data, headers=headers or {})
    with urlopen(req) as resp:
        return resp.read().decode("utf-8")


def extract_place_and_intents(text):
    lower = text.lower()
    want_weather = any(k in lower for k in ["temperature", "weather", "rain"])
    want_places = any(k in lower for k in ["plan my trip", "places", "visit"])
    candidates = []
    patterns = [
        r"\bgo to\s+([^\.,\?;:]+)",
        r"\bin\s+([^\.,\?;:]+)",
        r"\bto\s+([^\.,\?;:]+)",
    ]
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if val.lower().startswith("go to "):
                val = val[6:].strip()
            candidates.append(val)
    place = candidates[0] if candidates else None
    return place, want_weather, want_places


def geocode_place(query):
    params = {
        "q": query,
        "format": "jsonv2",
        "limit": 1,
    }
    url = "https://nominatim.openstreetmap.org/search?" + urlencode(params)
    headers = {
        "User-Agent": "MultiAgentTourism/1.0",
        "Accept-Language": "en",
    }
    raw = http_get(url, headers=headers)
    results = json.loads(raw)
    if not results:
        return None
    r = results[0]
    name = r.get("display_name") or query
    lat = float(r["lat"]) if "lat" in r else None
    lon = float(r["lon"]) if "lon" in r else None
    if lat is None or lon is None:
        return None
    return {"name": name.split(",")[0], "lat": lat, "lon": lon}


def get_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m",
        "hourly": "precipitation_probability",
        "timezone": "auto",
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urlencode(params)
    raw = http_get(url)
    data = json.loads(raw)
    temp = None
    precip_prob = None
    current = data.get("current") or {}
    if "temperature_2m" in current:
        temp = current.get("temperature_2m")
    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []
    probs = hourly.get("precipitation_probability") or []
    if times and probs and len(times) == len(probs):
        now = datetime.now(timezone.utc)
        best_idx = 0
        best_diff = None
        for i, t in enumerate(times):
            try:
                dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
            except Exception:
                continue
            diff = abs((dt - now).total_seconds())
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_idx = i
        precip_prob = probs[best_idx]
    return {"temperature_c": temp, "precipitation_chance": precip_prob}


def get_places(lat, lon, limit=5):
    q = """
    [out:json][timeout:25];
    (
      nwr(around:8000, {lat}, {lon})[tourism=attraction];
      nwr(around:8000, {lat}, {lon})[amenity=park];
      nwr(around:8000, {lat}, {lon})[tourism=museum];
      nwr(around:8000, {lat}, {lon})[tourism=zoo];
      nwr(around:8000, {lat}, {lon})[leisure=park];
      nwr(around:8000, {lat}, {lon})[tourism=gallery];
      nwr(around:8000, {lat}, {lon})[tourism=theme_park];
      nwr(around:8000, {lat}, {lon})[tourism=palace];
      nwr(around:8000, {lat}, {lon})[leisure=garden];
      nwr(around:8000, {lat}, {lon})[tourism=botanical_garden];
    );
    out tags center;
    """.strip().format(lat=lat, lon=lon)
    body = "data=" + urlencode({"": q})[1:]
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    raw = http_post("https://overpass-api.de/api/interpreter", body, headers=headers)
    data = json.loads(raw)
    names = []
    seen = set()
    for el in data.get("elements", []):
        tags = el.get("tags") or {}
        name = tags.get("name") or tags.get("alt_name") or tags.get("official_name")
        if not name:
            continue
        key = name.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        names.append(name.strip())
        if len(names) >= limit:
            break
    return names


def compose_response(user_text):
    place_guess, want_weather, want_places = extract_place_and_intents(user_text)
    query_for_geo = place_guess or user_text
    geo = geocode_place(query_for_geo)
    if not geo:
        return "It doesn’t know this place exist"
    loc_name = geo["name"]
    lat = geo["lat"]
    lon = geo["lon"]
    if not want_weather and not want_places:
        want_places = True
    weather_text = None
    places_text = None
    if want_weather:
        w = get_weather(lat, lon)
        temp = w.get("temperature_c")
        prob = w.get("precipitation_chance")
        temp_str = f"{round(temp)}°C" if isinstance(temp, (int, float)) else "unknown"
        prob_val = int(round(prob)) if isinstance(prob, (int, float)) else None
        if prob_val is None:
            weather_text = f"In {loc_name} it’s currently {temp_str}."
        else:
            weather_text = f"In {loc_name} it’s currently {temp_str} with a chance of {prob_val}% to rain."
    if want_places:
        names = get_places(lat, lon, limit=5)
        if names:
            header = f"In {loc_name} these are the places you can go," if not want_weather else "And these are the places you can go:"
            places_text = header + "\n" + "\n".join(names)
        else:
            places_text = f"No nearby attractions found for {loc_name}."
    if weather_text and places_text:
        return weather_text + " " + places_text
    if weather_text:
        return weather_text
    if places_text:
        return places_text
    return f"In {loc_name} these are the places you can go,\n" + "\n".join(get_places(lat, lon, limit=5))


def main():
    if len(sys.argv) > 1:
        user_text = " ".join(sys.argv[1:])
    else:
        user_text = input("Enter your trip query: ").strip()
    print(compose_response(user_text))


if __name__ == "__main__":
    main()