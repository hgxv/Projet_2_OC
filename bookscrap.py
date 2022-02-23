import requests
from bs4 import BeautifulSoup

url = requests.get("http://books.toscrape.com/")
soup = BeautifulSoup(url.text, "html.parser")
header = ["product_page_url", "universal_ product_code", "title", "price_including_tax",
            "price_excluding_tax", "number_available", "product_description", "category",
            "review_rating", "image_url"]
categories = {}
book_list = []

def get_categories():
    """Récupère le lien de toutes les catégories"""
    find_categories = soup.find("ul", { "class" : "nav-list"}).li.ul

    for found_categorie in find_categories.findAll("a"):
        #On ajoute l'url de chaque catégorie dans un tableau.
        categories[found_categorie.text.strip()] = "http://books.toscrape.com/" + found_categorie["href"]


def get_book_list(categorie_url):
    categorie_request = requests.get(categorie_url)
    categorie_soup = BeautifulSoup(categorie_request.text, "html.parser")
    links = categorie_soup.findAll("div", { "class" : "image_container" })

    for link in links:
        #On ajoute l'url de chaque livre contenue sur la page dans un tableau
        book_list.append("https://books.toscrape.com/catalogue" + link.find("a")["href"][8:])

    if categorie_soup.find("li", { "class" : "next"}) != None:
        next = categorie_url[:categorie_url.rfind("/")] + "/" + categorie_soup.find("li", { "class" : "next"}).find("a")["href"]
        print(next + "\n")
        get_book_list(next)


def get_book_data(url, categorie):
    """Récupère les données demandées pour un livre donné"""
    book_request = requests.get(url)
    book_soup = BeautifulSoup(book_request.text, "html.parser")
    book_data = []
    book_data.append(url)
    #Le titre sera passé en argument dans un prochain commit.
    book_data.append(book_soup.find("th", text="UPC").findNext("td").text)
    book_data.append(book_soup.find("h1").text)
    book_data.append(book_soup.find("th", text="Price (excl. tax)").findNext("td").text.strip("Â"))
    book_data.append(book_soup.find("th", text="Price (incl. tax)").findNext("td").text.strip("Â"))
    book_data.append(book_soup.find("th", text="Availability").findNext("td").text.strip("In stock ( available)"))
    book_data.append(book_soup.find("div", { "id" : "product_description" }).findNext("p").text)
    book_data.append(categorie)
    #La catégorie sera passée en argument dans un prochain commit.
    book_data.append(book_soup.find("p", { "class" : "star-rating"})["class"][1])
    book_image = book_soup.find("div", { "class" : "item active"}).findNext("img")["src"]
    book_data.append("http://books.toscrape.com" + book_image[5:])
    print(book_data)


def main():
    get_categories()
    for categorie in categories:
        get_book_list(categories[categorie])
        for book in book_list:
            get_book_data(book, categorie)
            print("\n")


    
if __name__ == "__main__":
    main()