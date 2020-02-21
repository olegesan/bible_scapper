# bible_scapper
>made for learning purposes only
## Descritption
It is a python script scrapes any version of bible from bible.com. It was made due to inability to find various verisions of Bible online in JSON format.
So the script requires the version code like "NIV" for 'New International Version' and as a result gives back json file with the version.
It follows the following structure:
1. Bible_ESV.json
	1. Books: 'books'
		1. Bible books: i.e. 'GEN'
			1.  Code name of the book: 'code' 
			2. Actual name of the book: 'name'
			3. Chapters: 'chapters' 
				1. Chapters by number: '1...50'
					1. Verses by number: '1...31'
				2.  Total number of chapters in the book (int): 50
	2. Translation Copyright information: "translation_copyRight"
	3. Version: 'version'
## Usage
launch scraper_1.py and follow the instructions:
- Provide a list of standard codes of a Bible versions just like 'ESV' or 'KJV': 'ESV, KJV, nasb'
- Wait until it finishes and prompts you for the next action.
## Used Libraries
- BeautifulSoup
- Requests
- re, json

