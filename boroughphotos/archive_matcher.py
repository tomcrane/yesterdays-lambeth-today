import json
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join
import requests
import time

images = {}
headers = {
    'User-Agent': 'flaneurtom@gmail.com'
}


def is_jpg(folder, f):
    if isfile(join(folder, f)):
        if f.lower().endswith(".jpg"):
            return True
    return False


def is_five_digits(s):
    return len(s) == 5 and s.isdigit()


def parse_filename(file):
    bp_id = None
    is_archive = False
    name_part = file.split('.')
    if is_five_digits(name_part[0]):
        bp_id = name_part[0]
        is_archive = True
    else:
        sub_parts = name_part[0].split('_')
        if is_five_digits(sub_parts[0]):
            bp_id = sub_parts[0]

    url_safe_name = name_part[0].replace(' ', '_')
    print(
        f"Parsed {bp_id}, is_archive={is_archive}, name_part: {url_safe_name}")
    return (bp_id, is_archive, url_safe_name)


def scrape_borough_photos(img_data):
    time.sleep(1)
    search_template = "https://boroughphotos.org/lambeth/search-results/?fRefNum=" + \
        img_data["bp_id"]
    r = requests.get(search_template, headers=headers)
    soup = BeautifulSoup(r.text)
    result = soup.css.select("#searchResultThumbContainer2 a")[0]
    # print(result)
    img_data["borough_url"] = "https://boroughphotos.org" + result['href']
    img_data["name"] = result['title']
    print(f"Scraped {img_data['borough_url']} for {img_data['name']}")
    return


def get_vips_cmd(file, name):
    return f"'C:\\Program Files\\vips\\vips-dev-8.17\\bin\\vips.exe' dzsave '{file}' {name} --layout iiif"


def get_static_iiif_cmd(file, name):
    return f".\\StaticIIIF.exe '{file}' 'C:\\git\\tomcrane\\yesterdays-lambeth-today-iiif-img\\{name}'"


def get_image_service(name):
    return "https://tomcrane.github.io/yesterdays-lambeth-today-iiif-img/" + name


def process_folder(folder):

    files = [f for f in listdir(folder) if is_jpg(folder, f)]
    counter = 0
    for file in files:

        full_name = join(folder, file)
        print(f"looking at file {full_name}...")
        (bp_id, is_archive, name_part) = parse_filename(file)
        if bp_id is not None:
            counter = counter + 1
            img_data = images.get(bp_id, {
                "bp_id": bp_id,
                "file": None,
                "name_part": None,
                "name": None,
                "borough_url": None,
                "iiif_image_service": None,
                "vips_cmd": None,
                "now_image": None,
                "now_name_part": None,
                "now_image_iiif_image_service": None,
                "now_image_vips_cmd": None,
                "static_iiif_cmd": None,
                "now_image_static_iiif_cmd": None
            })

            if is_archive:
                img_data["file"] = full_name
                img_data["name_part"] = name_part
                img_data["vips_cmd"] = get_vips_cmd(
                    img_data["file"], img_data["name_part"])
                img_data["iiif_image_service"] = get_image_service(
                    img_data["name_part"])
                img_data["static_iiif_cmd"] = get_static_iiif_cmd(
                    img_data["file"], img_data["name_part"])
            else:
                img_data["now_image"] = full_name
                img_data["now_name_part"] = name_part
                img_data["now_image_vips_cmd"] = get_vips_cmd(
                    img_data["now_image"], img_data["now_name_part"])
                img_data["now_image_iiif_image_service"] = get_image_service(
                    img_data["now_name_part"])
                img_data["now_image_static_iiif_cmd"] = get_static_iiif_cmd(
                    img_data["now_image"], img_data["now_name_part"])

            if img_data.get("borough_url", None) is None:
                scrape_borough_photos(img_data)

            images[bp_id] = img_data

        else:
            print("not an archival item or derivative")


def get_canvas(image_api_url, display_name, slug):
    canvas_id = "https://tomcrane.github.io/yesterdays-lambeth-today/iiif/canvas/" + slug
    return {
        "id": canvas_id,
        "type": "Canvas",
        "label": {"en": [display_name]},
        "height": 0,
        "width": 0,
        "items": [
            {
                "id": "https://tomcrane.github.io/yesterdays-lambeth-today/iiif/page/" + slug,
                "type": "AnnotationPage",
                "items": [
                    {
                        "id": "https://tomcrane.github.io/yesterdays-lambeth-today/iiif/painting/" + slug,
                        "type": "Annotation",
                        "motivation": "painting",
                        "body": {
                            "id": image_api_url + "/full/max/0/default.jpg",
                            "type": "Image",
                            "format": "image/jpeg",
                            "service": [
                                {
                                    "id": image_api_url,
                                    "type": "ImageService3",
                                    "profile": "level0"
                                }
                            ],
                            "height": 0,
                            "width": 0
                        },
                        "target": canvas_id
                    }
                ]
            }
        ]
    }


if __name__ == "__main__":

    # Do the earlier one first
    process_folder("C:\\Users\\TomCrane\\Dropbox\\personal\\Lambeth Archives\\220825_Exhibition Lambeth Archives 2208\\Exhibition Layouts 220823 Folder\\Links")
    # This will overwrite a lot of them but that's OK
    process_folder("C:\\Users\\TomCrane\\Dropbox\\personal\\Lambeth Archives\\220825_Exhibition Lambeth Archives 2208\\Exhibition Layouts 220825 Links")    

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(images, f, ensure_ascii=False, indent=4)

    with open("bp_links.csv", 'w', encoding="utf-8") as f:
        for i, (k, v) in enumerate(images.items()):
            f.write(f'"{k}"')
            f.write(',')
            f.write(f'"{v["file"]}"')
            f.write(',')
            f.write(f'"{v["name"]}"')
            f.write(',')
            f.write(f'"{v["iiif_image_service"]}"')
            f.write(',')
            f.write(f'"{v["now_image"]}"')
            f.write(',')
            f.write(f'"{v["now_image_iiif_image_service"]}"')
            f.write(',')
            f.write(f'"{v["borough_url"]}"')
            f.write('\n')

    with open('vips.cmds.txt', 'w', encoding='utf-8') as f:
        for i, (k, v) in enumerate(images.items()):
            archive = v.get("vips_cmd", None)
            if archive is not None:
                f.write(archive)
                f.write('\n')
            now_image = v.get("now_image_vips_cmd", None)
            if now_image is not None:
                f.write(now_image)
                f.write('\n')

    with open('static_iiif.cmds.txt', 'w', encoding='utf-8') as f:
        for i, (k, v) in enumerate(images.items()):
            archive_static_cmd = v.get("static_iiif_cmd", None)
            if archive_static_cmd is not None:
                f.write(archive_static_cmd)
                f.write('\n')
            now_image_static_cmd = v.get("now_image_static_iiif_cmd", None)
            if now_image_static_cmd is not None:
                f.write(now_image_static_cmd)
                f.write('\n')


    manifest = {
        "@context": "http://iiif.io/api/presentation/3/context.json",
        "id": "https://tomcrane.github.io/yesterdays-lambeth-today/iiif/yesterday-and-today-raw.json",
        "type": "Manifest",
        "label": {"en": [ "Yesterday's Lambeth Today: source images"]},
        "items": []
    }
    
    for i, (k, v) in enumerate(images.items()):
        archive_image = v.get("iiif_image_service", None)
        if archive_image is not None:
            canvas = get_canvas(archive_image, f"[{k}] {v['name']}", k)
            canvas["homepage"] = [
                {
                    "id": v["borough_url"],
                    "type": "Text",
                    "label": { "en": [ v["name"] ] },
                    "format": "text/html"
                }
            ]
            manifest["items"].append(canvas)
        
        now_image = v.get("now_image_iiif_image_service", None)
        if now_image is not None:
            canvas_now = get_canvas(now_image, f"2022 - [{k}] {v['name']}", f"{k}_2022")
            manifest["items"].append(canvas_now)

    with open('..\\iiif\\yesterday-and-today-raw.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=4)
