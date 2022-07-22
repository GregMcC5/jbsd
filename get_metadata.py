import requests
import csv

def write_csv(filepath, data, headers=None, encoding='utf-8', newline=''):
    """
    This function has been taken directly from Professor Anthony Whyte's SI 506 class (Python I)
    at the University of Michigan School of Information, Fall 2021 semester.

    Takes filepath and data and writes CSV of data to specified filepath.
    """

    with open(filepath, 'w', encoding=encoding, newline=newline) as file_obj:
        writer = csv.writer(file_obj)
        if headers:
            writer.writerow(headers)
            for row in data:
                writer.writerow(row)
        else:
            writer.writerows(data)


def create_item_dict(api_item, filepath):
    """
    Takes an LibraryCloud item and filepath and return dictionary of metadata crosswalked into Wikimedia {{Artwork}} template
    """
    #--establishing dictionary--
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
    
    #--crosswalking metadata--
    #-filepath
    if filepath:
        item_dict["path"] = filepath
    
    #-artist
    if type(api_item["name"]) == list:
        if api_item["name"][0]["namePart"] == 'Burkhardt, Jacques':
            item_dict["artist"] = "[[wikidata:Q53499085|Burkhardt, Jacques]]"
        else:
            item_dict["artist"] = api_item["name"][0]["namePart"]
    elif type(api_item["name"]) == dict:
        if api_item["titleInfo"]["title"] == 'Burkhardt, Jacques':
            item_dict["artist"] = "[[wikidata:Q53499085|Burkhardt, Jacques]]"
        else:
            item_dict["artist"] = api_item["name"]["namePart"]
    #-author
    if type(api_item["name"]) == list:
        if api_item["name"][0]["namePart"] == 'Burkhardt, Jacques':
            item_dict["author"] = "[[wikidata:Q53499085|Burkhardt, Jacques]]"
        else:
            item_dict["author"] = api_item["name"][0]["namePart"]
    elif type(api_item["name"]) == dict:
        if api_item["titleInfo"]["title"] == 'Burkhardt, Jacques':
            item_dict["author"] = "[[wikidata:Q53499085|Burkhardt, Jacques]]"
        else:
            item_dict["author"] = api_item["name"]["namePart"]
    #-title
    item_dict["title"] = api_item["titleInfo"]["title"].replace("#","").replace("[", "").replace("]","").replace("{", "").replace("}", "")
    #print(f"\n{item_dict['title']}\n")

    #-description
    descriptions = []

    #print(f"\napi['relatedItem'] = {api_item['relatedItem']}\n")
    if type(api_item["relatedItem"]) == dict:
        #Taxonomic classification
        if api_item["relatedItem"]["subject"] and len(api_item["relatedItem"]["subject"].values()) == 2:
            descriptions.append(f"{api_item['relatedItem']['subject']['@displayLabel']}: {api_item['relatedItem']['subject']['topic']}")
        #Common name
        if api_item["relatedItem"]["titleInfo"] and type(api_item["relatedItem"]["titleInfo"]) == dict and len(api_item["relatedItem"]["titleInfo"].values()) == 2:
            descriptions.append(f"{api_item['relatedItem']['titleInfo']['@displayLabel']}: {api_item['relatedItem']['titleInfo']['title']}")
        if api_item["relatedItem"]["titleInfo"] and type(api_item["relatedItem"]["titleInfo"]) == list:
            for name in api_item["relatedItem"]["titleInfo"]:
                descriptions.append(f"{name['@displayLabel']}: {name['title']}")
        #Speciment collected
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

    #-date Created
    originInfo = api_item.get("originInfo")
    if originInfo:
        datetest = originInfo.get('dateCreated')
        if datetest:
            item_dict["date"] = originInfo["dateCreated"]

    #-medium
    for material_datum in api_item['physicalDescription']["form"]:
        if material_datum["@type"] == "materialsTechniques":
            material_technique = material_datum["#text"]
        if material_datum["@type"] == "support":
            support = material_datum['#text']
    if material_technique and support:
        item_dict['medium'] = f'{material_technique} on {support}'

    #-dimensions
    item_dict['dimensions'] = api_item["physicalDescription"]['extent']

    #-institutions
    item_dict['institution'] = "[[wikidata:Q13371|Harvard University]]"

    #-department
    item_dict['department'] = "[[wikidata:Q53528757|Ernst Mayr Library]]"

    #-accession number
    attribution = api_item["recordInfo"]['recordIdentifier']['@source']
    acc_num = api_item["recordInfo"]['recordIdentifier']['#text']

    item_dict["accession_number"] = f"{attribution} {acc_num}"

    #-notes
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

    #-source
    item_curiosity_location = None
    for location in api_item['location'][0]['url']:
        if location.get('@displayLabel') == "Jacques Burkhardt Scientific Drawings":
            item_curiosity_location = location["#text"]
    item_dict["source"] = f"Harvard CURIOSity Collection - Jacques Burkhardt Scientific Drawings: {item_curiosity_location} "

    #-permission
    item_dict["permission"] = "The organization that has made the Item available believes that the Item is in the Public Domain under the laws of the United States, but a determination was not made as to its copyright status under the copyright laws of other countries. The Item may not be in the Public Domain under the laws of other countries. Please refer to the organization that has made the Item available for more information (URI: https://rightsstatements.org/page/NoC-US/1.0/?language=en)"

    #-categories
    item_dict["categories"] = "Jacques Burkhardt Scientific Drawings"

    return item_dict


def main():
    #--establishing headers for completed entries list--
    completed_entries = [["path","artist", "author", "title", "description", "date", "medium", "dimensions", "institution", "department", "inscriptions", "notes", "accession_number", "source", "permission", "categories"]]

    filenames = []

    limits = ["0", "251", "501", "750"]
    for limit in limits:
        api = f"https://api.lib.harvard.edu/v2/items.json?setSpec_exact=jbsd&start={limit}&limit=250"
        items = requests.get(api).json()["items"]["mods"]
        for item in items:

            #--accessing item image, establishing filename, checking for filename duplicates, and downloading image--

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
            print(filename)
            #--downloading image, comment out after first use--

            # response = requests.get(img_url)
            # with open(f"WikiImages/{filename}.jpg", "wb") as f:
            #     f.write(response.content)

            #--establishing image filepath--

            img_filpath = f"/Users/gregorymccollum/Desktop/Python/Harvard/WikiImages/{filename}.jpg"

             #--creating item dict--
            item_dict = create_item_dict(item, img_filpath)

            item_list = [item_dict["path"], item_dict["artist"], item_dict["author"], item_dict["title"], item_dict["description"], item_dict["date"],item_dict["medium"], item_dict["dimensions"], item_dict["institution"], item_dict["department"], item_dict["inscriptions"], item_dict["notes"], item_dict["accession_number"], item_dict["source"], item_dict["permission"], item_dict["categories"]]
            completed_entries.append(item_list)

    #--writing csv--
    u.write_csv("jbsd_wikimedia_upload.csv", completed_entries)


if __name__ == "__main__":
    main()
    print(f"done")
