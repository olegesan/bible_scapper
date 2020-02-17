# bible_scapper
>made for learning purposes only
## Descritption
It is a python script scrapes any version of bible from bible.com. It was made due to inability to find various verisions of Bible online in JSON format.
So the script requires the version code like "NIV" for 'New International Version' and as a result gives back json file with the version.
It follows the following structure:
1. Bible_ESV.json
    2. Book Codes like 'GEN'
        1. 'Chapters'
            1. Chapters by number like '1'
                1. Verses by numbe like 'verse_1'
            2.  'Total' : contains total number of chapters in the book
## Usage
launch scraper_1.py and follow the instructions:
- Provide a standard code of a Bible version just like 'ESV' or 'KJV'
- Wait until it finishes and prompts you for the next action.
## Used Libraries
- BeautifulSoup
- Requests
- re, json

