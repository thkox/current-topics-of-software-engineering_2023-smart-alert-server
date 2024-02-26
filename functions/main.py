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
def user_is_employee(req: https_fn.CallableRequest) -> Any:
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

        # Convert timestamp to "HH:SS" time Athens
        timestamp = datetime.datetime.fromtimestamp(alert_form["timestamp"] / 1000)
        timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
        timestamp = timestamp + datetime.timedelta(hours=2) # Athens timezone
        timestamp = timestamp.astimezone().strftime("%H:%M")

        # Store critical data in the database
        essential_data_by_phenomenon_and_location = {
            'location': alert_form.get('location'),
            'timestamp': timestamp,
            'imageURL': alert_form.get('imageURL'),
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


@db_fn.on_value_written(reference=r"/alertForms/{uid}/{formID}", region="us-central1")
def handle_alert_upload(event):
    asyncio.run(categorize_and_store_alert(event))


@https_fn.on_request()
def hourly_cleanup_http(req: https_fn.Request) -> Any:
    """Needs to be deployed with Cloud Scheduler: https://console.cloud.google.com/cloudscheduler"""
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

    # Set counter for deleted alertForms
    num_of_deleted_alerts = 0

    for phenomenon, places in phenomena.items():
        for place, alerts in places.items():
            for alert_id, alert_data in alerts.items():
                if alert_data['timestamp']:
                    # Calculate if the alert is older than 24 hours.
                    alert_timestamp_seconds = alert_data['timestamp'] / 1000
                    if current_timestamp - alert_timestamp_seconds >= 86400:
                        num_of_deleted_alerts = num_of_deleted_alerts + 1
                        logging.info(f"Deleting alert {alert_id} from {phenomenon}/{place}")
                        # Remove the alert from alertsByPhenomenonAndLocationLast24h
                        db.reference(f"alertsByPhenomenonAndLocationLast24h/{phenomenon}/{place}/{alert_id}").delete()

                        # Decrement the counter
                        counter_ref = db.reference(f"alertsByPhenomenonAndLocationCountLast24h/{phenomenon}/{place}")
                        counter = counter_ref.get() or 0
                        counter = max(0, counter - 1)
                        if counter == 0:
                            db.reference(f"alertsByPhenomenonAndLocationCountLast24h/{phenomenon}/{place}").delete()
                        else:
                            counter_ref.set(counter)

    # Update lastCleanupTimestamp
    last_cleanup_ref = db.reference("lastCleanupTimestamp")
    last_cleanup_ref.set(current_timestamp)

    num_of_deleted_alerts_ref = db.reference("lastNumOfDeletedAlerts")
    num_of_deleted_alerts_ref.set(num_of_deleted_alerts)

    logging.info("Cleanup completed")
    return 'Cleanup completed', 200


@https_fn.on_call()
def delete_alerts_by_location(req: https_fn.CallableRequest) -> Any:
    """Deletes alerts by phenomenon and location"""

    try:
        # Get the phenomenon and location from the request
        phenomenon = req.data.get("phenomenon", "")
        place = req.data.get("place", "")

        # Fetch all alert categories (phenomena)
        phenomena = db.reference("alertsByPhenomenonAndLocationLast24h").get() or {}

        # Check if the phenomenon exists
        if phenomenon in phenomena:
            # Check if the place exists for the phenomenon
            if place in phenomena[phenomenon]:
                # Delete the alerts for the phenomenon and place
                db.reference(f"alertsByPhenomenonAndLocationLast24h/{phenomenon}/{place}").delete()

                # Delete the counter
                db.reference(f"alertsByPhenomenonAndLocationCountLast24h/{phenomenon}/{place}").delete()

                return {'success': True}
            else:
                return {'success': False, 'message': 'Place not found'}
        else:
            return {'success': False, 'message': 'Phenomenon not found'}

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return {'success': False, 'message': 'An unexpected error occurred'}


@https_fn.on_call()
def delete_alert_by_phenomenon_and_location(req: https_fn.CallableRequest) -> Any:
    """Deletes a specific alert by phenomenon and location"""

    try:
        # Get the phenomenon, location, and alertID from the request
        phenomenon = req.data.get("phenomenon", "")
        place = req.data.get("place", "")
        alert_id = req.data.get("alertID", "")

        # Fetch all alert categories (phenomena)
        phenomena = db.reference("alertsByPhenomenonAndLocationLast24h").get() or {}

        # Check if the phenomenon exists
        if phenomenon in phenomena:
            # Check if the place exists for the phenomenon
            if place in phenomena[phenomenon]:
                # Check if the alertID exists for the phenomenon and place
                if alert_id in phenomena[phenomenon][place]:
                    # Delete the specific alert for the phenomenon, place, and alertID
                    db.reference(f"alertsByPhenomenonAndLocationLast24h/{phenomenon}/{place}/{alert_id}").delete()

                    # Decrement the counter
                    counter_ref = db.reference(f"alertsByPhenomenonAndLocationCountLast24h/{phenomenon}/{place}")
                    counter = counter_ref.get() or 0
                    counter = max(0, counter - 1)
                    if counter == 0:
                        db.reference(f"alertsByPhenomenonAndLocationCountLast24h/{phenomenon}/{place}").delete()
                    else:
                        counter_ref.set(counter)

                    return {'success': True}
                else:
                    return {'success': False, 'message': 'Alert not found'}
            else:
                return {'success': False, 'message': 'Place not found'}
        else:
            return {'success': False, 'message': 'Phenomenon not found'}

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return {'success': False, 'message': 'An unexpected error occurred'}