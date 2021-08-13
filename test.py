import requests
import cloudscraper
from bs4 import BeautifulSoup
import re
from PIL import Image
import io
import csv

class Album:
    def __init__(self, album_id, artist, title, year, genre, tracklist, imageLink):
        self.album_id = album_id
        self.artist = artist
        self.title = title
        self.year = year
        self.genre = genre
        self.tracklist = tracklist
        self.imageLink = imageLink

    def printInfo(self):
        print(self.album_id, "-", self.artist, "-", self.title, "-", self.year, "-", self.genre, "-", self.tracklist)
        r = requests.get(self.imageLink)
        image_bytes = io.BytesIO(r.content)

        img = Image.open(image_bytes)
        img.show()

class Song:
    def __init__(self, position, title, duration=None):
        self.position = position
        self.title = title
        self.duration = duration

class Tracklist:
    def __init__(self, songs):
        self.songs = songs

def get_album(search):
    url = "https://www.discogs.com/search/?q=" + str(search) + "&type=master"
    scraper = cloudscraper.create_scraper()
    r = scraper.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    albums = soup.findAll("div", {"data-object-type": "master release"})[0:5]
    album_links = [album.find("a", {"class": "search_result_title"})['href'] for album in albums]
    print(album_links)
    return album_links

def get_album_info(search):
    search = search.replace(" ", "+")
    album_links = get_album(search)
    urls = ["https://www.discogs.com/" + str(link) for link in album_links]

    scraper = cloudscraper.create_scraper()
    full_album_list = []
    for url in urls:
        r = scraper.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        info = soup.find("div", {"class": "profile"})
        header = [i.text.strip() for i in info.find("h1", {"id": "profile_title"}).findAll("span")][-2:]
        tracklist_header = soup.find("table", {"class": "playlist"})

        positions = [i["data-track-position"] for i in tracklist_header.findAll("tr", {"class": "track"})]
        titles = [i.text.strip("\n") for i in tracklist_header.findAll("td", {"class": "tracklist_track_title"})]
        durations = [i.text.strip("\n") for i in tracklist_header.findAll("td", {"class": "tracklist_track_duration"})]

        album_id = str(url.rsplit('/', 1)[1])
        artist = header[0]
        title = header[1]
        year = info.find("a", {"href": re.compile("/search.*")}).text
        style = [i.text for i in info.findAll("a", {"href": re.compile("/style.*")})]
        tracklist = Tracklist([Song(positions[i], titles[i], durations[i]) for i in range(len(positions))])

        imageLink = soup.find("span", {"class": "thumbnail_center"}).find("img")["src"]
        
        full_album_list.append(Album(album_id, artist, title, year, style, tracklist, imageLink))
    return full_album_list
def write_to_collection(album):
    with open('collection.csv', "a") as collection:
        writer = csv.writer(collection, delimiter=",")
        writer.writerow([album.album_id, album.artist, album.title, album.year, album.genre, album.tracklist, album.imageLink])

#album = get_album_info("david+bowie+ziggy+stardust")
# write_to_collection(album)