import requests
from bs4 import BeautifulSoup
import csv
import datetime

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
    """Récupère la liste de chaque livre pour une catégorie donnée"""
    categorie_request = requests.get(categorie_url)
    categorie_soup = BeautifulSoup(categorie_request.text, "html.parser")
    links = categorie_soup.findAll("div", { "class" : "image_container" })

    for link in links:
        #On ajoute l'url de chaque livre contenue sur la page dans un tableau
        book_list.append("https://books.toscrape.com/catalogue" + link.find("a")["href"][8:])

    #Vérifie la présence d'une page supplémentaire s'il y a plus de 20 livres restants
    if categorie_soup.find("li", { "class" : "next"}) != None:
        next = categorie_url[:categorie_url.rfind("/")] + "/" + categorie_soup.find("li", { "class" : "next"}).find("a")["href"]
        get_book_list(next)


def get_book_data(url):
    """Récupère les données demandées pour un livre donné"""
    book_request = requests.get(url)
    book_soup = BeautifulSoup(book_request.text, "html.parser")
    book_data = []
    book_data.append(url)

    #Récupère l'upc du livre
    book_data.append(book_soup.find("th", text="UPC").findNext("td").text)

    #Récupère le titre du livre
    book_data.append(book_soup.find("h1").text)

    #Récupère les prix HT et TTC du livre
    book_data.append(book_soup.find("th", text="Price (excl. tax)").findNext("td").text.strip("Â"))
    book_data.append(book_soup.find("th", text="Price (incl. tax)").findNext("td").text.strip("Â"))

    #Récupère combien de livres il reste en stock
    book_data.append(book_soup.find("th", text="Availability").findNext("td").text.strip("In stock ( available)"))

    #Vérifie qu'il y a bien une description au livre
    try:
        book_data.append(book_soup.find("div", { "id" : "product_description" }).findNext("p").text)
    except:
        book_data.append("Pas de description")

    #On cherche la catégorie sur la page du livre
    book_categorie = book_soup.find("ul", { "class" : "breadcrumb"}).findAll("li")
    book_data.append(book_categorie[2].find("a").text)

    #On cherche la note du livre
    book_data.append(book_soup.find("p", { "class" : "star-rating"})["class"][1])

    #On cherche le lien de la miniature du livre
    book_image = book_soup.find("div", { "class" : "item active"}).findNext("img")["src"]
    book_data.append("http://books.toscrape.com" + book_image[5:])
    
    #Print pour suivre l'avancement du programme et pouvoir débugguer en cas de problème
    print(book_request)
    print(book_data)
    print("\n")

    return book_data


def main():
    #On nomme le fichier avec la date du jour pour pouvoir comparer avec des données futures
    file_name = str(datetime.date.today()) + ".csv"

    with open(file_name, "w", encoding="UTF-8") as csvfile:
        line_writer = csv.writer(csvfile, delimiter=",")
        line_writer.writerow(header)
        get_categories()
        #On parcourt chaque catégorie
        for categorie in categories:
            #Pour chaque catégorie, on ajoute le lien des livres trouvés
            get_book_list(categories[categorie])
        #Pour chaque livre trouvé, on écrit ses données dans le fichier csv
        for book in book_list:               
            line_writer.writerow(get_book_data(book))          

    
if __name__ == "__main__":
    main()