import requests
import utilities as u


def create_item_dict(api_item, filepath):
    """
    format of item is Wikimedia {{Artwork}} template.
    """
    item_dict = {
        'path' : None,
        'artist': None,
        'author': None,
        'title': None,
        'description': None,
        'depicted_people': None,
        'depicted_place': None,
        'date': None,
        'medium': None,
        'dimensions': None,
        'institution': None,
        'department': None,
        'accession_number': None,
        'place_of_creation': None,
        'place_of_discovery': None,
        'object_history': None,
        'exhibition_history': None,
        'credit_line': None,
        'inscriptions': None,
        'notes': None,
        'references': None,
        'source': None,
        'permission': None,
        'other_versions': None,
        'wikidata': None,
        'categories' : None
            }

    # for key, val in api_item.items():
    #     print(f"key : {key}\nval : {val}\n")
    #print(api_item["location"])

    if filepath:
        item_dict["path"] = filepath

    if type(api_item["name"]) == list:
        item_dict["artist"] = api_item["name"][0]["namePart"]
    elif type(api_item["name"]) == dict:
        item_dict["artist"] = api_item["name"]["namePart"]

    if type(api_item["name"]) == list:
        item_dict["author"] = api_item["name"][0]["namePart"]
    elif type(api_item["name"]) == dict:
        item_dict["author"] = api_item["name"]["namePart"]

    item_dict["title"] = api_item["titleInfo"]["title"]
    #print(f"\n{item_dict['title']}\n")

    descriptions = []

    #print(f"\napi['relatedItem'] = {api_item['relatedItem']}\n")
    if type(api_item["relatedItem"]) == dict:
        #taxonomic classification
        if api_item["relatedItem"]["subject"] and len(api_item["relatedItem"]["subject"].values()) == 2:
            descriptions.append(f"{api_item['relatedItem']['subject']['@displayLabel']}: {api_item['relatedItem']['subject']['topic']}")
        #Common name
        if api_item["relatedItem"]["titleInfo"] and type(api_item["relatedItem"]["titleInfo"]) == dict and len(api_item["relatedItem"]["titleInfo"].values()) == 2:
            descriptions.append(f"{api_item['relatedItem']['titleInfo']['@displayLabel']}: {api_item['relatedItem']['titleInfo']['title']}")
        if api_item["relatedItem"]["titleInfo"] and type(api_item["relatedItem"]["titleInfo"]) == list:
            for name in api_item["relatedItem"]["titleInfo"]:
                descriptions.append(f"{name['@displayLabel']}: {name['title']}")
        #speciment collected
        try:
            if "Specimen Collection Date" in api_item['relatedItem']["originInfo"]["dateOther"]["@type"]:
                descriptions.append(f"Specimen Collection Date: {api_item['relatedItem']['originInfo']['dateOther']['#text']}")
        except:
            print("skipped it")
        item_dict["description"] = ". ".join(descriptions)
    if type(api_item['relatedItem']) == list:
        for api_piece in api_item['relatedItem']:
            if api_piece["subject"] and type(api_piece['subject']) == dict and len(api_piece["subject"]) == 2:
                descriptions.append(f"{api_piece['subject']['@displayLabel']}: {api_piece['subject']['topic']}")
                item_dict["description"] = ".".join(descriptions)

    originInfo = api_item.get("originInfo")
    if originInfo:
        datetest = originInfo.get('dateCreated')
        if datetest:
            item_dict["date"] = originInfo["dateCreated"]

    for material_datum in api_item['physicalDescription']["form"]:
        if material_datum["@type"] == "materialsTechniques":
            material_technique = material_datum["#text"]
        if material_datum["@type"] == "support":
            support = material_datum['#text']
    if material_technique and support:
        item_dict['medium'] = f'{material_technique} on {support}'

    item_dict['dimensions'] = api_item["physicalDescription"]['extent']
    item_dict['institution'] = "[[wikidata:Q13371|Harvard University]]"
    item_dict['department'] = "[[wikidata:Q53528757|Ernst Mayr Library]]"

    attribution = api_item["recordInfo"]['recordIdentifier']['@source']
    acc_num = api_item["recordInfo"]['recordIdentifier']['#text']

    item_dict["accession_number"] = f"{attribution} {acc_num}"


    note_list = []
    if type(api_item["note"]) == list:
        for annotation in api_item["note"]:
            #print("\n",annotation,"\n")
            if type(annotation) == dict and annotation["@type"] == "annotation":
                note_list.append(str(annotation["#text"]))
            # elif type(annotation) == str:
            #     note_list.append(annotation)
        item_dict['inscriptions'] = ". ".join(note_list)
    elif type(api_item["note"]) == dict:
        annotation = api_item['note']
        if annotation["@type"] == "annotation":
            item_dict['inscriptions'] = annotation['#text']

    note_test = api_item["physicalDescription"].get("note")
    if note_test:
        item_dict["notes"] = api_item["physicalDescription"]["note"]

    item_curiosity_location = None
    for location in api_item['location'][0]['url']:
        if location.get('@displayLabel') == "Jacques Burkhardt Scientific Drawings":
            item_curiosity_location = location["#text"]
    item_dict["source"] = f"Harvard CURIOSity Collection - Jacques Burkhardt Scientific Drawings: {item_curiosity_location} "

    item_dict["permission"] = "The organization that has made the Item available believes that the Item is in the Public Domain under the laws of the United States, but a determination was not made as to its copyright status under the copyright laws of other countries. The Item may not be in the Public Domain under the laws of other countries. Please refer to the organization that has made the Item available for more information (URI: https://rightsstatements.org/page/NoC-US/1.0/?language=en)"
    item_dict["categories"] = "Harvard University;Harvard University Library;Harvard CURIOSity Collections;Jacques Burkhardt Scientific Drawings;Ernst Mayr Library"

    return item_dict


def main():
    completed_entries = [["path","artist", "author", "title", "description", "date", "medium", "dimensions", "institution", "department", "inscriptions", "notes", "accession_number", "source", "permission", "categories"]]

    filenames = []

    limits = ["0", "251", "501", "750"]
    for limit in limits:
        api = f"https://api.lib.harvard.edu/v2/items.json?setSpec_exact=jbsd&start={limit}&limit=250"
        items = requests.get(api).json()["items"]["mods"]
        for item in items:

            #-downloading image; comment out after first use-

            img_url = item['location'][0]['url'][0]['#text']
            if "https://nrs.harvard.edu/" not in img_url:
                img_url = "https://nrs.harvard.edu/" + img_url
            filename = f"{item['titleInfo']['title']}{img_url.split('/')[-1]}"
            if filename in filenames:
                # print("rename error found")
                filename = filename+"_2"
            filenames.append(filename)
            bad_characters = ("#",'[',']','{','}')
            for character in bad_characters:
                if character in filename:
                    filename = filename.replace(character, "")
            # print(filename)
            # response = requests.get(img_url)
            # with open(f"WikiImages/{filename}.png", "wb") as f:
            #     f.write(response.content)

            #-establishing image filepath-

            img_filpath = f"/Users/gregorymccollum/Desktop/Python/Harvard/WikiImages/{filename}.png"
           # print(img_filpath)

             #-starting item dictionary_
            item_dict = create_item_dict(item, img_filpath)

            item_list = [item_dict["path"], item_dict["artist"], item_dict["author"], item_dict["title"], item_dict["description"], item_dict["date"],item_dict["medium"], item_dict["dimensions"], item_dict["institution"], item_dict["department"], item_dict["inscriptions"], item_dict["notes"], item_dict["accession_number"], item_dict["source"], item_dict["permission"], item_dict["categories"]]
            #print(item_list)
            completed_entries.append(item_list)


        # print(len(items))
        # print("\n-------------")
    u.write_csv("jbsd_wikimedia_upload.csv", completed_entries)


if __name__ == "__main__":
    main()
    print(f"done")