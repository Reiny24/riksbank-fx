import requests, time, os, schedule
from flask import Flask, jsonify
from manage_db import (
    init_db,
    insert_series,
    get_all_series,
    update_series_latest,
    get_series_history,
)
from dotenv import load_dotenv
load_dotenv()
RIKSBANK_SERIES_URL = os.getenv("RIKSBANK_SERIES_URL")
RIKSBANK_OBS_URL = os.getenv("RIKSBANK_OBS_URL")

app = Flask(__name__)


@app.route("/")
def home():
    return "Home"


@app.route("/fetch-store", methods=["GET"])
def fetch_and_store():
    try:
        response = requests.get(RIKSBANK_SERIES_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        series_ids = [item["seriesId"] for item in data]
        insert_series(series_ids)

        return f"Series stored successfully! Count: {len(series_ids)}"
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/series", methods=["GET"])
def list_series():
    return jsonify(get_all_series())


@app.route("/history/<seriesId>", methods=["GET"])
def list_history(seriesId):
    return jsonify(get_series_history(seriesId))


@app.route("/update-latest", methods=["GET"])
def update_latest_values():
    series_list = get_all_series()
    updated_count = 0

    for s in series_list[:4]:
        try:
            response = requests.get(RIKSBANK_OBS_URL + s["seriesId"], timeout=10)
            response.raise_for_status()
            data = response.json()
            print(data)

            date = data.get("date")
            value = float(data.get("value"))
            update_series_latest(s["seriesId"], date, value)
            updated_count += 1
            if updated_count % 5 == 0:
                time.sleep(60)
        except Exception as e:
            print(f"Failed to update {s['seriesId']}: {e}")

    return jsonify({"message": "Latest values updated", "updated": updated_count})


if not os.path.exists("series.db"):
    init_db()

app.run(debug=True)  # start API


def daily_job():
    print("Running daily job...")
    fetch_and_store()
    update_latest_values()


# run every day at 10:00
schedule.every().day.at("10:00").do(daily_job)

while True:
    schedule.run_pending()
    time.sleep(60)
