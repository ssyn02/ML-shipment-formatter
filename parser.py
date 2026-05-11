from flask import json
from docx import Document
from docx.shared import Pt
from datetime import datetime, timedelta, UTC
from collections import defaultdict
import requests

def main():
    with open("tokens.json", "r") as f:
        tokens = json.load(f)

    user_id = 123456789  # reemplazar con tu user id
    offset = 0
    limit = 50
    date_from = (
        datetime.now(UTC) - timedelta(days=4)
    ).strftime("%Y-%m-%dT%H:%M:%S.000-00:00")

    LOGISTIC_TYPES = {
        "self_service": "Flex",
        "cross_docking": "Colecta",
    }

    duplicated = set()
    grouped = defaultdict(list)

    while True:
        orders = requests.get(
            f"https://api.mercadolibre.com/orders/search",
            params={
                "seller": user_id,
                "sort": "date_desc",
                "limit": limit,
                "offset": offset,
                "order.date_created.from": date_from
            },
            headers={
                "Authorization": f"Bearer {tokens['access_token']}",
                "x-format-new": "true"
            }
        ).json()["results"]

        if not orders:
            break

        for order in orders:
            shipping = order.get("shipping")

            if not shipping:
                continue

            shipment_id = shipping["id"]

            if shipment_id in duplicated:
                continue

            duplicated.add(shipment_id)

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

            grouped[shipment["logistic_type"]].append(shipment)

        print("Procesados: ", len(grouped["self_service"]) + len(grouped["cross_docking"]))
        offset += limit

    document = Document()

    style = document.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(12)

    for logistic_type, shipments in grouped.items():
        document.add_paragraph(LOGISTIC_TYPES[logistic_type].capitalize())

        for shipment in shipments:
            for item in shipment.get("shipping_items", []):
                prods = document.add_paragraph()
                prods.add_run(f"{item['quantity']} {item['description']}".upper()).bold = True
            recipient = document.add_paragraph()
            recipient.add_run(shipment["receiver_address"]["receiver_name"]+ "\n\n")

    document.save("shipments.docx")
    print(f"Documento creado en carpeta raiz.")


if __name__ == "__main__":
    main()