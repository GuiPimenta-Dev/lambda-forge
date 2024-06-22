import json
from dataclasses import dataclass

import requests


@dataclass
class Input:
    pass


@dataclass
class Name:
    title: str
    first: str
    last: str


@dataclass
class Street:
    number: int
    name: str


@dataclass
class Coordinates:
    latitude: str
    longitude: str


@dataclass
class Timezone:
    offset: str
    description: str


@dataclass
class Location:
    street: Street
    city: str
    state: str
    country: str
    postcode: int
    coordinates: Coordinates
    timezone: Timezone


@dataclass
class Login:
    uuid: str
    username: str
    password: str
    salt: str
    md5: str
    sha1: str
    sha256: str


@dataclass
class Output:
    gender: str
    name: Name
    location: Location
    email: str
    login: Login
    phone: str


def lambda_handler(event, context):

    result = requests.get("https://randomuser.me/api").json()["results"][0]

    data = {
        "gender": result["gender"],
        "name": result["name"],
        "location": result["location"],
        "email": result["email"],
        "login": result["login"],
        "phone": result["phone"],
    }

    return {
        "statusCode": 200,
        "body": json.dumps(data),
        "headers": {"Access-Control-Allow-Origin": "*"},
    }
