from unicodedata import category
import requests
from bs4 import BeautifulSoup
import csv
import os

url = requests.get("http://books.toscrape.com/")
soup = BeautifulSoup(url.text, "html.parser")
header = ["product_page_url", "universal_ product_code", "title", "price_including_tax",
            "price_excluding_tax", "number_available", "product_description", "category",
            "review_rating", "image_url"]
categories = {}
book_list = []

def get_categories():
    """Get the link for every categories"""
    find_categories = soup.find("ul", { "class" : "nav-list"}).li.ul

    for found_categorie in find_categories.findAll("a"):
        #Add the cagerory's url to an array.
        categories[found_categorie.text.strip()] = "http://books.toscrape.com/" + found_categorie["href"]


def get_book_list(categorie_url):
    """Get the book list for a given category"""
    categorie_request = requests.get(categorie_url)
    categorie_soup = BeautifulSoup(categorie_request.text, "html.parser")
    links = categorie_soup.findAll("div", { "class" : "image_container" })

    for link in links:
        #Add every book's link to an array
        book_list.append("https://books.toscrape.com/catalogue" + link.find("a")["href"][8:])

    #Check if there is a "next" page
    if categorie_soup.find("li", { "class" : "next"}) != None:
        next = categorie_url[:categorie_url.rfind("/")] + "/" + categorie_soup.find("li", { "class" : "next"}).find("a")["href"]
        get_book_list(next)


def get_book_data(url):
    """Get the data from a given book"""
    book_request = requests.get(url)
    book_soup = BeautifulSoup(book_request.text, "html.parser")
    book_data = []
    book_data.append(url)

    #Get the book's upc
    book_upc = book_soup.find("th", text="UPC").findNext("td").text
    book_data.append(book_upc)

    #Get the book's title
    book_title = book_soup.find("h1").text
    book_data.append(book_title)

    #Get the book's different prices
    book_data.append(book_soup.find("th", text="Price (excl. tax)").findNext("td").text.strip("Â"))
    book_data.append(book_soup.find("th", text="Price (incl. tax)").findNext("td").text.strip("Â"))

    #Get how many books are left
    book_data.append(book_soup.find("th", text="Availability").findNext("td").text.strip("In stock ( available)"))

    #Check if the book has a description
    try:
        book_data.append(book_soup.find("div", { "id" : "product_description" }).findNext("p").text)
    except:
        book_data.append("Pas de description")

    #Look for the book's category
    book_category_container = book_soup.find("ul", { "class" : "breadcrumb"}).findAll("li")
    book_category = book_category_container[2].find("a").text
    book_data.append(book_category)

    #Get the book's rating
    book_data.append(book_soup.find("p", { "class" : "star-rating"})["class"][1])

    #Get the book's image
    book_image_container = book_soup.find("div", { "class" : "item active"}).findNext("img")["src"]
    book_image_link = "http://books.toscrape.com" + book_image_container[5:]
    book_data.append(book_image_link)
    #Request the book's image
    book_image = requests.get(book_image_link)
    image_directory = "images/" + book_category + "/" + book_upc + ".jpg"
    #Create folders if they doesn't exist yet
    if not os.path.isdir("images/"):
        os.mkdir("images/")
    if not os.path.isdir("images/" + book_category):
        os.mkdir("images/" + book_category)
    #Save the image at the asked location
    with open(image_directory, "wb") as file:
        file.write(book_image.content)
    
    #Prints to follow program's progression to debug
    print(book_request)
    print(book_data)
    print("\n")

    return book_data

def main():
    get_categories()
    #Get through every category
    for category in categories:
        file_name = category + ".csv"
        with open(file_name, "w", encoding="UTF-8") as csvfile:
            line_writer = csv.writer(csvfile, delimiter=",")
            line_writer.writerow(header)

            #For every category, add found book's url
            get_book_list(categories[category])
            #For every found books, get it's data
            for book in book_list:
                line_writer.writerow(get_book_data(book))
            book_list.clear()


if __name__ == "__main__":
    main()