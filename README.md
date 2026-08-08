# Soil Temp (ClearAPI)

<p align="center">
<img src="https://img.shields.io/github/stars/ljmerza/soil-temp?style=for-the-badge&label=Stars&color=orange" alt="Stars">
<a href="https://github.com/ljmerza/soil-temp/releases/latest"><img src="https://img.shields.io/github/v/release/ljmerza/soil-temp?style=for-the-badge&color=purple" alt="Version"></a>
<a href="https://github.com/ljmerza/soil-temp/blob/main/LICENSE"><img src="https://img.shields.io/github/license/ljmerza/soil-temp?style=for-the-badge&label=License&color=green" alt="License"></a>
</p>

<p align="center">
<a href="https://www.buymeacoffee.com/JMISm06AD"><img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee"></a>
</p>

Home Assistant custom integration that polls [ClearAPI's `/v1.1/daily/soil`](https://ag.us.clearapis.com) endpoint for the home coordinates configured in Home Assistant and exposes the returned soil temperature and moisture metrics as sensors.

## Install via HACS

1. Add this repository as a HACS *custom repository* (Integrations).
2. Install **Soil Temp (ClearAPI)** and restart Home Assistant.
3. Settings → Devices & Services → Add Integration → **Soil Temp (ClearAPI)**.
4. Confirm the form. The integration uses your HA home coordinates automatically — set them under Settings → System → General first if you haven't.

## Sensors created

Primary metrics:

- Soil temperature avg / max / min (0–10 cm), °F (HA auto-converts to your preferred unit)
- Soil temperature 24-hour and 5-day rolling averages (0–10 cm)
- Soil moisture (0–10 cm), inches
- Soil moisture (0–200 cm), inches

Diagnostic / scaled metrics (grouped under the device's "Diagnostic" section):

- Normalized soil temperature anomaly (0–10 cm)
- Scaled, absolute-scaled, plant-available-water-scaled, and normalized variants of soil moisture for both depths

Each entity exposes the source `observation_date`, `fetched_at` timestamp, `api_unit`, and `location` as state attributes.

## Options

- **Poll interval (hours)** — default 6, range 1–24. The endpoint returns daily data so polling more often than once an hour wastes API calls.

## Notes

- API credentials are the public demo `app_id`/`app_key` from ClearAPI's documentation, hardcoded in `const.py`. Swap them in the source if you have your own.
- One config entry per home location; HA's configured `latitude`/`longitude` is read fresh on every poll, so moving your HA home location is reflected on the next refresh without a reload.
