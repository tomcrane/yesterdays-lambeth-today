import json
import requests

# Do this once the info.jsons are live, to get the thumbnail sizes.

if __name__ == "__main__":

    manifest = {}

    with open('..\\iiif\\yesterday-and-today-raw.json') as f:
        manifest = json.load(f)

    manifest["id"] = manifest["id"].replace("yesterday-and-today-raw.json", "yesterday-and-today.json")

    for canvas in manifest["items"]:
        info_json = canvas["items"][0]["items"][0]["body"]["service"][0]["id"] + "/info.json"
        print("requesting " + info_json)
        image_service_resp = requests.get(info_json)
        image_service = image_service_resp.json()

        canvas["width"] = image_service["width"]
        canvas["height"] = image_service["height"]
        canvas["items"][0]["items"][0]["body"]["width"] = image_service["width"]
        canvas["items"][0]["items"][0]["body"]["height"] = image_service["height"]

        thumb_size = image_service["sizes"][2]

        canvas["thumbnail"] = [
            {
                "id": f"{image_service['id']}/full/{thumb_size['width']},{thumb_size['height']}/0/default.jpg",
                "type": "Image",
                "format": "image/jpeg",
                "service": [
                    image_service
                ]
            }
        ]

        image_service.pop("@context")
        image_service.pop("tiles")
        image_service.pop("preferredFormats")
        image_service.pop("extraFormats")
        image_service.pop("protocol")
        image_service.pop("width")
        image_service.pop("height")

    with open('..\\iiif\\yesterday-and-today.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=4)
    

