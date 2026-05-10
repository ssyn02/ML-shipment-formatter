from flask import json
from collections import defaultdict
import requests

def main():
    with open("tokens.json", "r") as f:
        tokens = json.load(f)

    # user_id =

    LOGISTIC_TYPES = {
        "self_service": "Flex",
        "cross_docking": "Colecta",
    }

    orders = requests.get(
        f"https://api.mercadolibre.com/orders/search?seller={user_id}&sort=date_desc",
        headers={
            "Authorization": f"Bearer {tokens['access_token']}",
            "x-format-new": "true"
        }
    ).json()["results"]

    grouped = defaultdict(list)

    for order in orders:
        shipping = order.get("shipping")

        if not shipping:
            continue

        shipment_id = shipping["id"]

        shipment = requests.get(
            f"https://api.mercadolibre.com/shipments/{shipment_id}",
            headers={
                "Authorization": f"Bearer {tokens['access_token']}"
            }
        ).json()

        if shipment["logistic_type"] == "fulfillment":
            continue

        if shipment["substatus"] != "ready_to_print":
            continue

        grouped[shipment["logistic_type"]].append((shipment))

    for logistic_type, shipments in grouped.items():
        print("\n====================")
        print("LOGISTIC TYPE:", LOGISTIC_TYPES[logistic_type])
        print("====================")

        for shipment in shipments:
            for item in shipment.get("shipping_items", []):
                print(item["quantity"], item["description"])
            print(shipment["receiver_address"]["receiver_name"])
            print("-" * 20)


if __name__ == "__main__":
    main()