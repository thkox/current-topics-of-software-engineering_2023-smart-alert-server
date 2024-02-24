import re
from typing import Any

# [START v2imports]
# Dependencies for callable functions.
from firebase_functions import https_fn, options

# Dependencies for writing to Realtime Database.
from firebase_admin import db, initialize_app

# [END v2imports]

initialize_app()


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
