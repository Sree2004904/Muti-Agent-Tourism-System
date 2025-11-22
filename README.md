# 🌍 Multi-Agent Tourism System

A smart tourism assistant built using Python that can understand user queries and provide:
- ✔ Weather information for any location  
- ✔ Top nearby attractions (parks, museums, galleries, gardens, zoos, etc.)  
- ✔ Automatic geocoding of places  
- ✔ Intelligent intent detection (weather / trip planning / attractions)

This system uses multiple APIs (OpenStreetMap, Open-Meteo, Overpass API) to answer questions like:

> *“What is the temperature in Paris?”*  
> *“Plan my trip to Goa”*  
> *“Places to visit in London”*

---

## 🚀 Features

### 1. Intent Detection
Automatically identifies what the user is asking for:
- Weather  
- Tourist attractions  
- Trip planning  
- Location extraction from the text

### 2. Place Geocoding
Uses **Nominatim (OpenStreetMap)** to convert place names into latitude & longitude.

### 3. Weather Information
Uses **Open-Meteo** API to fetch:
- Temperature  
- Probability of rain (derived from closest timestamp)

### 4. Tourist Attractions Nearby
Uses **Overpass API** to find attractions such as:
- Parks  
- Museums  
- Botanical gardens  
- Zoos  
- Art galleries  
- Theme parks  

### 5. Natural Language Response
Generates a readable, human-like response combining weather and tourist spots.

---

## 🛠️ Technologies Used

| Component | Usage |
|----------|--------|
| **Python** | Core program |
| **Nominatim API** | Geocoding (place → coordinates) |
| **Open-Meteo API** | Weather details |
| **Overpass API** | Nearby attractions from OSM |
| **Regex** | Extracting locations from text |
| **datetime** | Matching current weather timestamp |

---

## 📥 Installation

Clone this project:

```sh
git clone https://github.com/Sree2004904/Muti-Agent-Tourism-System.git

How to Run

Run the program in the terminal: python main.py


Or enter your query directly:

python main.py "plan my trip to Delhi"
python main.py "weather in London"
python main.py "places to visit in Mumbai"


When run without arguments:

Enter your trip query: plan my trip to Delhi

How It Works
1. User Text → Intent & Place Extraction

Code identifies keywords like:

weather, temperature, rain

plan my trip, visit, places

go to X, in X, to X

2. Geocoding

The place is resolved using:

https://nominatim.openstreetmap.org/search

3. Weather Fetching

Temperature & rain chance from Open-Meteo:

https://api.open-meteo.com/v1/forecast

4. Finding Attractions

The Overpass Query fetches nearby attractions:

nwr(around:8000, lat, lon)[tourism=attraction];

📌 Example Output

Input:

plan my trip to Paris


Output:

In Paris it’s currently 18°C with a chance of 20% to rain.
And these are the places you can go:
• Eiffel Tower
• Louvre Museum
• Luxembourg Gardens

Project Structure
│ main.py            # Entry point
│ README.md          # Documentation
