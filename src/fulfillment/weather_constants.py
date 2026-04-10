WEATHER_CODE_MAP = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "light freezing drizzle",
    57: "dense freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "slight snowfall",
    73: "moderate snowfall",
    75: "heavy snowfall",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail"
}

WEATHER_ICON_MAP = {
    0: "sun", 1: "sun",
    2: "cloud", 3: "cloud", 45: "cloud", 48: "cloud",
    51: "cloud-drizzle", 53: "cloud-drizzle", 55: "cloud-drizzle",
    56: "cloud-drizzle", 57: "cloud-drizzle",
    61: "cloud-rain", 63: "cloud-rain", 65: "cloud-rain",
    66: "cloud-rain", 67: "cloud-rain",
    80: "cloud-rain", 81: "cloud-rain", 82: "cloud-rain",
    71: "cloud-snow", 73: "cloud-snow", 75: "cloud-snow",
    77: "cloud-snow", 85: "cloud-snow", 86: "cloud-snow",
    95: "cloud-lightning", 96: "cloud-lightning", 99: "cloud-lightning"
}

WEATHER_THEME_MAP = {
    "sun": "bg-amber-500/10 border-amber-500/40 text-amber-400",
    "cloud": "bg-slate-700/50 border-slate-600 text-slate-400",
    "cloud-drizzle": "bg-cyan-500/10 border-cyan-400/40 text-cyan-400",
    "cloud-rain": "bg-blue-600/15 border-blue-500/40 text-blue-400",
    "cloud-snow": "bg-indigo-400/10 border-indigo-300/40 text-indigo-200",
    "cloud-lightning": "bg-purple-900/20 border-purple-500/40 text-purple-400"
}