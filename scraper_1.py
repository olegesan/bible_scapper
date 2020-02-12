import requests
import re
import json
from bs4 import BeautifulSoup as bs
import time



version_code=59
link = f'https://www.bible.com/bible/{version_code}/'
version = "ESV"



#  getting all the books and their shortcut name from bible.com
def getBibleBooks():
    bible_books = {}
    with open('names.txt', 'r') as names:                                   # names.txt scraped from bible.com
        books_names_raw = names.readline()
        names.close()
    matched_books = re.findall(r'-label="(.*?)".*?>(.*?)<', books_names_raw)
    for book in matched_books:
        bible_books[book[0]]={
            'name' : book[1],
            'code' : book[0]
        }
    return bible_books




#  getting number of chapters in books
def addNumberOfChapters(bible):                     #Accepts a fictionary that has bible books names as keys
    for book in bible.keys():
        current_chapter = 1
        last_chapter = 0
        bible[book]["chapters"]["total"]=0
        while not current_chapter < last_chapter:
            current_chapter=last_chapter+1                  #at bible.com if chapter number overflows it sends it back to number 1
            req = requests.get(f'{link}{book}.{current_chapter}.{version}')
            chapter = re.search(r'\.([0-9]{1,3})\.', req.url).group(1)
            
            current_chapter = int(chapter)
            if(current_chapter<=last_chapter):         #if last chapter == current chapter -> there is only one chapter in the book
                break
            bible[book]["chapters"]["total"]+=1
            last_chapter = current_chapter

#  returns the number of chaters in the provided book
def getNumberOfChapters(book):                     
    current_chapter = 1
    last_chapter = 0
    
    while not current_chapter < last_chapter:
        current_chapter=last_chapter+1                  #at bible.com if chapter number overflows it sends a user back to number 1
        req = requests.get(f'{link}{book}.{current_chapter}.{version}')
        chapter = re.search(r'\.([0-9]{1,3})\.', req.url).group(1)
        current_chapter = int(chapter)
        if(current_chapter<=last_chapter):         #if last chapter == current chapter -> there is only one chapter in the book
            break
        last_chapter = current_chapter 
        print(current_chapter)
    return last_chapter  


#  scraping all the verse for one chapter # 


# *********************************
# getting the number of verses from a chapter
def getNumberOfVerses(book,chapter):                        #helps to get number of verses in one chapter
    req = requests.get(f'{link}{book}.{chapter}.{version}')
    verses = re.findall(r'class="verse v(\d{1,3})', req.text)
    return int(verses[-1])
# *********************************


# *********************************
# grabbing all the verses in the chapter
def getAllVersesInChapter(book,chapter):
        chapter_counter = time.perf_counter()                       #starting a timer for chapter
        page = requests.get(f'{link}{book}.{chapter}.{version}')    # getting html source of the chapter
        page_soup = bs(page.text,'html.parser') 
        verses = page_soup.find_all(attrs={"class":"verse"})            # finding all divs that have "verse" class
        verse_counter = 1                                           #keeping track of current verse
        allVerses = {}
        for verse in verses:
            verse_text = verse.get_text()
            if verse_text[0:len(str(verse_counter+1))]==str(verse_counter+1): #checking the beginning of the verse piece to for a number, if 
                verse_counter+=1                                              #number matches the next next verse counter, then we are on
            if verse_text[0:len(str(verse_counter))]==str(verse_counter): # a new verse, otherwise it is the another piece of the same 
                allVerses[f'verse_{verse_counter}'] = verse_text.lstrip('0123456789').replace('\u2014','-')
            else:
                allVerses[f'verse_{verse_counter}'] += verse_text.replace('\u2014','-')
        chapter_over = time.perf_counter() - chapter_counter
        print(f'{book} {chapter} done in {chapter_over}')
        return allVerses

def getBook(book):                     
    current_chapter = 1
    last_chapter = 0
    bible_book = {}
    while not current_chapter < last_chapter:
        current_chapter=last_chapter+1                  #at bible.com if chapter number overflows it sends a user back to number 1
        req = requests.get(f'{link}{book}.{current_chapter}.{version}')
        chapter = re.search(r'\.([0-9]{1,3})\.', req.url).group(1)
        current_chapter = int(chapter)
        if(current_chapter<=last_chapter):         #if last chapter == current chapter -> there is only one chapter in the book
            break
        last_chapter = current_chapter 
        verses = getAllVersesInChapter(book,current_chapter)
        bible_book[str(current_chapter)] = verses
        

    return bible_book

def getBible():
    bible_counter = time.perf_counter()
    print("Let's first get all the Bible books, start a stopwatch")
    books_counter = time.perf_counter()
    bible = getBibleBooks() #getting the names of bible books
    books_over = time.perf_counter() - books_counter
    print(f"Got all the books in {books_over}")
    for book in bible.keys():   
        print(f"Now let's get every chapter in {book}")
        book_counter = time.perf_counter() 
        book_chapters = getBook(book) #getting total number of chapters in the book
        book_over = time.perf_counter() - book_counter
        print(f"It wasn't so bad, was it? Only {book_over}")
        bible[book]={
            'chapters':{
                'total': len(book_chapters.keys())
            }
        }
        bible[book]['chapters'].update(book_chapters)
    bible_over = time.perf_counter() - bible_counter
    print(f"We are almost done, all verses have been scrapped.\nTime:{bible_over}\nLet's save out bible as Bible{version}.json")
    open(f'Bible{version}.json', 'x').write(json.dumps(bible))

    
getBible()
