import requests
import re
import json
from bs4 import BeautifulSoup as bs
import time
import os
from bible_scraper_supplement import bible_versions_eng, bible_books


def main():
    print(f"{stars}\nWelcome to bible_scraper shell interface\n{stars}")
    while True:
        versions = list(input("\nType the codes of desired version, i.e. ESV, KJV for English Standard Version\nand King \
James Version :").upper().replace(' ', '').split(','))
        # print(versions)
        for idx, version in enumerate(versions):
            while True:
                if version in bible_versions_eng:
                    break
                else:
                    print(f'The code "{version}" is incorrect, cannot find such version, try again.')
                    version = input("\nType the code of desired version, i.e. ESV for English Standard Version :\n").upper()
                    versions[idx]=version
            # versions_info = getVersions()
        print(versions)
        global versions_needed
        versions_needed = versions
        multipleVersions()
        again = input("Do you want to get another version? y/n \n")
        if again.lower() == 'n':
            print("Pleasure to have business with you! Have a good day.")
            break
        elif again.lower() != 'y':
            print('Wrong input\nExiting pogram')


global version_code
global version
global link
stars = '*************************************'
global versions_needed


def getVersions():  # fetches all the codes and versions avaliable for english at bible.com
    versions = []
    with open('src/versions.html', 'r') as file:
        soup = bs(file.read(), 'html.parser')
    versions_raw = soup.find_all('a')
    for version in versions_raw:
        text = version.attrs['data-vars-event-label']
        version_code = re.search(r'1\.(.*)', version.attrs['href']).group(1)
        code_number, version_name = re.findall(r'^(\d{1,4}):(.*)', text, re.DOTALL)[0]
        versions.append(
            [version_code, code_number, version_name])  # returns a list like ['ESV',59,'English Standard Vesion']
    return versions


#  getting all the books and their shortcut name from bible.com
def getBibleBooks():
    bible_books = {}
    with open('src/names.txt', 'r') as names:  # names.txt scraped from bible.com
        books_names_raw = names.readline()
        names.close()
    matched_books = re.findall(r'-label="(.*?)".*?>(.*?)<', books_names_raw)
    for book in matched_books:
        bible_books[book[0]] = {
            'name': book[1],
            'code': book[0]
        }
    print(bible_books)


#  getting number of chapters in books
def addNumberOfChapters(bible):  # Accepts a fictionary that has bible books names as keys
    for book in bible.keys():
        current_chapter = 1
        last_chapter = 0
        bible['books'][book]["chapters"]["total"] = 0
        while not current_chapter < last_chapter:
            current_chapter = last_chapter + 1  # at bible.com if chapter number overflows it sends it back to number 1
            req = requests.get(f'{link}{book}.{current_chapter}.{version}')
            chapter = re.search(r'\.([0-9]{1,3})\.', req.url).group(1)

            current_chapter = int(chapter)
            if (
                    current_chapter <= last_chapter):  # if last chapter == current chapter -> there is only one chapter in the book
                break
            bible['books'][book]["chapters"]["total"] += 1
            last_chapter = current_chapter


#  returns the number of chaters in the provided book
def getNumberOfChapters(book):
    current_chapter = 1
    last_chapter = 0

    while not current_chapter < last_chapter:
        current_chapter = last_chapter + 1  # at bible.com if chapter number overflows it sends a user back to number 1
        req = requests.get(f'{link}{book}.{current_chapter}.{version}')
        chapter = re.search(r'\.([0-9]{1,3})\.', req.url).group(1)
        current_chapter = int(chapter)
        if (
                current_chapter <= last_chapter):  # if last chapter == current chapter -> there is only one chapter in the book
            break
        last_chapter = current_chapter
        print(current_chapter)
    return last_chapter


#  scraping all the verse for one chapter # 


# *********************************
# getting the number of verses from a chapter
def getNumberOfVerses(book, chapter):  # helps to get number of verses in one chapter
    req = requests.get(f'{link}{book}.{chapter}.{version}')
    verses = re.findall(r'class="verse v(\d{1,3})', req.text)
    return int(verses[-1])


# *********************************


# *********************************
# grabbing all the verses in the chapter
def getAllVersesInChapter(book, chapter):
    chapter_counter = time.perf_counter()  # starting a timer for chapter
    page = requests.get(f'{link}{book}.{chapter}.{version}')  # getting html source of the chapter
    page_soup = bs(page.text, 'html.parser')
    verses = page_soup.find_all(attrs={"class": "verse"})  # finding all divs that have "verse" class
    verse_counter = 1  # keeping track of current verse
    allVerses = {}
    for verse in verses:
        content = verse.find_all(attrs={"class":["content","label"]})
        for text in content:
            verse_text = text.get_text()

            if verse_text[0:len(str(verse_counter + 1))] == str(
                    verse_counter + 1):  # checking the beginning of the verse piece to for a number, if
                verse_counter += 1  # number matches the next next verse counter, then we are on
            if verse_text=="#":
                allVerses[f'{verse_counter}'] += " "
            elif verse_text[0:len(str(verse_counter))] == str(
                    verse_counter):  # a new verse, otherwise it is the another piece of the same
                allVerses[f'{verse_counter}'] = verse_text.lstrip('0123456789').replace('\u2014', '-')
            else:
                allVerses[f'{verse_counter}'] += verse_text.replace('\u2014', '-')
    chapter_over = time.perf_counter() - chapter_counter
    print(f'{book} {chapter} done in {chapter_over}')
    return allVerses


def getBook(book):
    current_chapter = 1
    last_chapter = 0
    bible_book = {}
    while not current_chapter < last_chapter:
        current_chapter = last_chapter + 1  # at bible.com if chapter number overflows it sends a user back to number 1
        req = requests.get(f'{link}{book}.{current_chapter}.{version}')
        chapter = re.search(r'\.([0-9]{1,3})\.', req.url).group(1)
        current_chapter = int(chapter)
        if (
                current_chapter <= last_chapter):  # if last chapter == current chapter -> there is only one chapter in the book
            break
        last_chapter = current_chapter
        verses = getAllVersesInChapter(book, current_chapter)
        bible_book[str(current_chapter)] = verses

    return bible_book


def getCopyRight():
    page = requests.get(f'{link}Gen.1.{version}')
    page_soup = bs(page.text, 'html.parser')
    return page_soup.find_all('div', class_="lh-copy")[0].find('p').get_text()


def getBible():
    bible_counter = time.perf_counter()
    print("Let's first get all the Bible books, start a stopwatch")
    books_counter = time.perf_counter()
    bible = {
        "books": bible_books.copy()
    }  # used to be getBibleBooks() #getting the names of bible books

    books_over = time.perf_counter() - books_counter
    print(f"Got all the books in {books_over}")
    for book in bible['books'].keys():
        print(f"Now let's get every chapter in {book}")
        book_counter = time.perf_counter()
        book_chapters = getBook(book)  # getting total number of chapters in the book
        book_over = time.perf_counter() - book_counter
        print(f"It wasn't so bad, was it? Only {book_over}")
        bible['books'][book].update({
            'chapters': {
                'total': len(book_chapters.keys())
            }
        })
        bible['books'][book]['chapters'].update(book_chapters)
        # break #delete this one
    try:
        bible['translation_copyRight'] = getCopyRight()
    except:
        print('No copyright info for this eversion')
    bible['version'] = version
    bible_over = time.perf_counter() - bible_counter
    print(
        f"We are almost done, all verses have been scrapped.\nTime:{bible_over}\nLet's save our bible as Bible{version}.json")
    try:
        try:
            os.mkdir('bibles')
        except:
            print("bibles directory already exists")
        open(f'bibles/Bible_{version}.json', 'x').write(json.dumps(bible))
        print(f'Success, you Bible_{version}.json has been successfully created\n{stars}')
    except FileExistsError:
        print(f'oops, seems like you already have a file named Bible_{version}.json in this folder\ncannot create it')
    except:
        print('there was an error, something went wrong')


def multipleVersions():  # function that get's all the version specified by the version code
    all_versions = getVersions()
    for version_name in versions_needed:
        for version_list in all_versions:
            if version_name in version_list:
                global version
                global link
                global version_code
                version = version_list[0]
                version_code = version_list[1]
                link = f'https://www.bible.com/bible/{version_code}/'
                getBible()


main()
