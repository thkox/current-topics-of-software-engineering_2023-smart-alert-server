import re
from typing import Any
import datetime  # For timestamp comparison

from flask import abort
import logging

# Dependencies for callable functions.
from firebase_functions import https_fn, options, db_fn, scheduler_fn

# Dependencies for writing to Realtime Database and Cloud Scheduler.
from firebase_admin import db, initialize_app
import asyncio
import requests

app = initialize_app()


@https_fn.on_call()
def userIsEmployee(req: https_fn.CallableRequest) -> Any:
    """Checks if the user is Employee or not"""

    try:
        # get the user's email
        email = req.auth.token.get("email", "")

        if email.endswith('civilprotection.gr'):
            return {'isCP': True}
        else:
            return {'isCP': False}

    except KeyError:
        print("Error: The key 'email' was not found in the token")
    except TypeError:
        print("Error: The token is not of the correct type")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


async def get_location_name(latitude, longitude):
    response = requests.get(
        f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key=AIzaSyBM31FS8qWSsNewQM5NGzpYm7pdr8q5azY"
    )
    if response.status_code == 200:
        return response.json()["results"][0]["address_components"][3]["long_name"]
    else:
        raise ValueError("Geocoding failed")


async def categorize_and_store_alert(event: db_fn.Event[db_fn.Change]):
    alert_form = event.data.after  # Get the data after the change

    # Data validation
    if not all(key in alert_form for key in ["location", "criticalWeatherPhenomenon"]):
        return  # Or raise an exception

    try:
        place = await get_location_name(alert_form["location"]["latitude"], alert_form["location"]["longitude"])
        phenomenon = alert_form["criticalWeatherPhenomenon"]

        # Store critical data in the database
        essential_data_by_phenomenon_and_location = {
            'location': alert_form.get('location'),
            'timestamp': alert_form.get('timestamp'),
            'criticalLevel': alert_form.get('criticalLevel'),
            'message': alert_form.get('message')
        }
        # Get the current count
        counter_ref = db.reference(f"alertsByPhenomenonAndLocationCountLast24h/{phenomenon}/{place}")
        counter = counter_ref.get() or 0

        # Increment the counter when a new alertForm per Critical Weather Phenomenon per Place is added
        counter += 1

        # Update the counter in the database
        counter_ref.set(counter)

        # Store the alertForm data
        db.reference(f"alertsByPhenomenonAndLocationLast24h/{phenomenon}/{place}/{event.params['formID']}").set(
            essential_data_by_phenomenon_and_location)

    except Exception as e:
        print(f"Error during processing: {e}")


@db_fn.on_value_written(reference=r"/alertForms/{formID}", region="us-central1")
def handle_alert_upload(event):
    asyncio.run(categorize_and_store_alert(event))


@https_fn.on_request()
def hourly_cleanup_http(req: https_fn.Request) -> Any:
    logging.info("Function triggered")

    # Verify that the request is a POST request
    if req.method != 'POST':
        logging.error("Function received a non-POST request")
        return abort(405)

    # Placeholder for your updated cleanup logic:
    now = datetime.datetime.now()
    current_timestamp = now.timestamp()

    # Fetch all alert categories (phenomena)
    phenomena = db.reference("alertsByPhenomenonAndLocationLast24h").get() or {}
    logging.info(f"Found {len(phenomena)} phenomena")

    count = 0

    for phenomenon, places in phenomena.items():
        for place, alerts in places.items():
            for alert_id, alert_data in alerts.items():
                if alert_data['timestamp']:
                    # Calculate if the alert is older than 24 hours.
                    alert_timestamp = alert_data['timestamp']
                    if current_timestamp - alert_timestamp >= 86400:
                        logging.info(f"Deleting alert {alert_id} from {phenomenon}/{place}")
                        count = count + 1
                        # Remove the alert from alertsByPhenomenonAndLocationLast24h
                        db.reference(f"alertsByPhenomenonAndLocationLast24h/{phenomenon}/{place}/{alert_id}").delete()

                        # Decrement the counter
                        counter_ref = db.reference(f"alertsByPhenomenonAndLocationCountLast24h/{phenomenon}/{place}")
                        counter = counter_ref.get() or 0
                        counter = max(0, counter - 1)
                        counter_ref.set(counter)

    # Update lastCleanupTimestamp
    last_cleanup_ref = db.reference("lastCleanupTimestamp")
    last_cleanup_ref.set(current_timestamp)

    last_count_of_deleted_events = db.reference("numOfDeletedEvents")
    last_count_of_deleted_events.set(count)

    logging.info("Cleanup completed")
    return 'Cleanup completed', 200
