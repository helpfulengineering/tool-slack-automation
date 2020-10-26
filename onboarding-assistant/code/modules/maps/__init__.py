"""Interface with the Google Maps API.
This module provides useful functions to resolve and manipulate location data.
>>> maps.address("")
"""
import googlemaps
import amazon

def address(identifier):
    """Resolve a Google Maps identifier to its physical address."""
    token = amazon.configuration["google_maps_token"]
    result = googlemaps.Client(key=token).place(
        identifier,
        fields=[
            "address_component",
            "formatted_address",
            "geometry"
            ]
        )["result"]
    return {
        "address": result["formatted_address"],
        "location": [
            result["geometry"]["location"]["lat"],
            result["geometry"]["location"]["lng"]],
        **{
            type: component["long_name"]
            for component in result["address_components"]
            for type in [
                "country",
                "locality",
                "postal_code",
                "administrative_area_level_1",
                "administrative_area_level_2",
                ]
            if type in component["types"]
            }
        }
