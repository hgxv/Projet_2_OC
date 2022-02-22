import requests
from bs4 import BeautifulSoup

url = requests.get("http://books.toscrape.com/")
soup = BeautifulSoup(url.text, "html.parser")
header = ["product_page_url", "universal_ product_code", "title", "price_including_tax",
            "price_excluding_tax", "number_available", "product_description", "category",
            "review_rating", "image_url"]
categories = []

livre_test = requests.get("https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")
livre_actuel = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"


def get_categories():
    """Récupère le lien de toutes les catégories"""
    find_categories = soup.find("ul", { "class" : "nav-list"}).li.ul

    for found_categorie in find_categories.findAll("a"):
        categories.append("http://books.toscrape.com/" + found_categorie["href"])


def get_book_data():
    """Récupère les données demandées pour un livre donné"""
    book_soup = BeautifulSoup(livre_test.text, "html.parser")
    book_data = []
    book_data.append(livre_actuel)
    #Le titre sera passé en argument dans un prochain commit.
    book_data.append(book_soup.find("th", text="UPC").findNext("td").text)
    book_data.append(book_soup.find("h1").text)
    book_data.append(book_soup.find("th", text="Price (excl. tax)").findNext("td").text.strip("Â"))
    book_data.append(book_soup.find("th", text="Price (incl. tax)").findNext("td").text.strip("Â"))
    book_data.append(book_soup.find("th", text="Availability").findNext("td").text.strip("In stock ( available)"))
    book_data.append(book_soup.find("div", { "id" : "product_description" }).findNext("p").text)
    book_data.append("catégorie")
    #La catégorie sera passée en argument dans un prochain commit.
    book_data.append(book_soup.find("p", { "class" : "star-rating"})["class"][1])
    book_image = book_soup.find("div", { "class" : "item active"}).findNext("img")["src"]
    book_data.append("http://books.toscrape.com/" + book_image[5:])
    print(book_data)


def main():
    get_categories()
    get_book_data()
    
if __name__ == "__main__":
    main()