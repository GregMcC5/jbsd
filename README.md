# Jacques Burkhardt Scientific Drawings Wikimedia Upload Project

Gregory McCollum, gregmcc@umich.edu, 2022 Harvard Library UX and Discover Intern



The Python script in this repository was used in a project to upload [Harvard Library's Jacques Burkhardt Scientific Drawings CURIOSity Colleciton](https://curiosity.lib.harvard.edu/jacques-burkhardt-scientific-drawings) to Wikimedia Commons.

The getmetadata.py script in this repository does the following things:

- **Accesses the Jacques Burkhardt collection via Harvard Library's API.** Because the LibraryCloud API limits returns to a maximum 250 results, the get_metdata.py script requests the collection materials from the LibraryCloud four times, resetting the start point each time to capture the whole collection. The materials are returned in JSON.

- **Downloads the image for each item to a local folder.** Each item is isolated and the URL location of the item image is accessed and downloaded locally into a WikiImages folder.

- **Crosswalks each item's metadata to Wikimedia Commons's {{Artwork}} template.** Each item is run through a create_item_dict function that extracts the necessary item metadata and returns a dictionary  that matches the specifications of the Wikimedia {{Artwork}} template populated with the extracted data. From each item dictionary, the necessary fields are then appended as a list (along with the filepath of the downloaded image) to a “completed_entries” list of completed records.

- **Writes the crosswalked metadata and local filepath for each item to a CSV.** The "completed_entries" list is written as a CSV. 

The jbsd_wikimedia_upload.csv can be used to perform a bulk upload to Wikimedi with [Pattypan](https://commons.wikimedia.org/wiki/Commons:Pattypan), an open-source Java tool. Pattypan has two final requirements for spreadsheets:

- An additional sheet with the following information in cell 1A:

        '=={{int:filedesc}}==
        {{Artwork
        |artist =
        |author = ${author}
        |title = ${title}
        |description = ${description}
        |date = ${date}
        |medium = ${medium}
        |dimensions = ${dimensions}
        |institution = ${institution}
        |department = ${department}
        |place of discovery =
        |object history =
        |exhibition history =
        |credit line =
        |inscriptions = ${inscriptions}
        |notes = ${notes}
        |accession number = ${accession_number}
        |place of creation =
        |source = ${source}
        |permission = ${permission}
        |other_versions =
        |references =
        |wikidata =
        }}

        =={{int:license-header}}==
        {{PD-US}}


        <#if categories ? has_content>
        <#list categories ? split(";") as category>
        [[Category:${category?trim}]]
        </#list>
        <#else>{{subst:unc}}
        </#if>

- Exported to a .xls file.

This final .xls final can be validated and uploaded with Pattypan. Can also auto-generate an upload-ready spreadsheet with its Generate feature, but this spreadsheet will lack user-defined metadata.

[The Jacques Burkhardt Scientific Drawings Wikimedia category is available now.](https://commons.wikimedia.org/wiki/Category:Jacques_Burkhardt_Scientific_Drawings)

---

This project was modeled after a pilot project conducted by the 2020 UX and Discovery intern cohort. [Documentation for their project is available on GitLab.](https://gitlab.com/hldsi/WikiMedia_Currency_Collection)
