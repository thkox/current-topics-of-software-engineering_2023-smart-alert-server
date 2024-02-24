import re
from typing import Any

# Dependencies for callable functions.
from firebase_functions import https_fn, options, db_fn

# Dependencies for writing to Realtime Database.
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

        db.reference(f"alertsByPhenomenonAndLocation/{phenomenon}/{place}/{event.params['formID']}").set(essential_data_by_phenomenon_and_location)

    except Exception as e:
        print(f"Error during processing: {e}")


@db_fn.on_value_written(reference=r"/alertForms/{formID}", region="us-central1")
def handle_alert_upload(event):
    asyncio.run(categorize_and_store_alert(event))
