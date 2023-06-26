import datetime
from dataclasses import dataclass, asdict
from typing import Tuple

from pymongo import MongoClient

from src.parser import get_medication


@dataclass(frozen=True)
class med:
    med_name: str
    dose_times: int
    dose_pills: int
    prescribed: datetime.datetime
    expiration: datetime.datetime


def check_medication_exists(medication_name):
    # Connect to the MongoDB server
    client = MongoClient('mongodb://localhost:27017')

    try:
        # Access the database and collection
        db = client['mydatabase']
        collection = db['tblMedications']

        # Query the collection for the medication name
        medication = collection.find_one({'med_name.med_name': medication_name})
        print(f"Medication name: {medication}")

        if medication:
            # Medication already exists in the collection
            return True
        else:
            # Medication does not exist in the collection
            return False

    except Exception as e:
        # Handle any exceptions
        print(f"An error occurred: {str(e)}")
        return False

    finally:
        # Close the MongoDB connection
        client.close()


def insert_medication(medication_name, **params):
    # Connect to the MongoDB server
    client = MongoClient('mongodb://localhost:27017')

    try:
        # Access the database and collection
        db = client['mydatabase']
        collection = db['tblMedications']

        # Check if the medication already exists
        existing_medication = collection.find_one({'med_name.med_name': medication_name})
        if existing_medication:
            print("Medication already exists.")
            return

        # Create a new medication document
        new_medication = {'med_name': medication_name}
        new_medication.update(params)

        # Insert the new medication record
        result = collection.insert_one(new_medication)
        if result.inserted_id:
            print("Medication record inserted successfully.")

    except Exception as e:
        # Handle any exceptions
        print(f"An error occurred: {str(e)}")

    finally:
        # Close the MongoDB connection
        client.close()


def check_medication_administration(medication_name, current_time):
    # Connect to the MongoDB server
    client = MongoClient('mongodb://localhost:27017')

    try:
        # Access the database and collection
        db = client['mydatabase']
        collection = db['tblMedications']
        print(collection.find())

        # Find the medication record by name
        medication = collection.find_one({'med_name.med_name': medication_name})
        print(medication)

        if medication:
            print("Medication found")
            last_administration = medication.get('lastadministration')
            next_administration = medication.get('nextadministration')
            print(last_administration)
            print(next_administration)

            if current_time > next_administration:
                # Update last administration to current time if it's past the next administration
                last_administration = current_time
                next_administration = current_time + datetime.timedelta(hours=24)


            # Check if the current time is within the last administration and next administration range
            if last_administration is not None and (last_administration <= current_time <= next_administration):
                print("Duplicate administration detected.")
                return False
            else:
                if last_administration is None:
                    # Create last administration and next administration if they don't exist
                    last_administration = current_time
                    next_administration = current_time + datetime.timedelta(hours=24)
                    # Update the medication record with the updated last administration and next administration
                    collection.update_one(
                        {'_id': medication['_id']},
                        {'$set': {'lastadministration': last_administration, 'nextadministration': next_administration}}
                    )

                print("Medication administration accepted.")
                return True

        else:
            print("Medication not found.")

    except Exception as e:
        # Handle any exceptions
        print(f"An error occurred: {str(e)}")

    finally:
        # Close the MongoDB connection
        client.close()


def handle_event(image_path: str) -> bool:
    med_name, dose_days, dose_pills, datep, datee = get_medication(image_path)
    if not check_medication_exists(med_name):
        medication = med(med_name, dose_days, dose_pills, datep, datee)
        insert_medication(asdict(medication))
        return True
    if not check_medication_administration(med_name, datetime.datetime.now()):
        print("checking med administration")
        return False
    else:
        print("Not getting here")
    return True
