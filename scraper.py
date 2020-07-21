import requests
from bs4 import BeautifulSoup
import os
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse
import pandas as pd
from pathlib import Path


# https://www.thepythoncode.com/article/download-web-page-images-python
def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_images(url):
    """
    Returns all image URLs on a single `url`
    """
    soup = bs(requests.get(url).content, "html.parser")
    urls = []
    for img in tqdm(soup.find_all("img",attrs={"class":"product-retina"}), "Extracting images"):
        img_url = img.attrs.get("src")
        if not img_url:
            # if img does not contain src attribute, just skip
            continue

        # make the URL absolute by joining domain with the URL that is just extracted
        img_url = urljoin(url, img_url)

        try:
            pos = img_url.index("?")
            img_url = img_url[:pos]
        except ValueError:
            pass
        # finally, if the url is valid
        if is_valid(img_url):
            urls.append(img_url)
    return urls


def download(url, pathname):
    """
    Downloads a file given an URL and puts it in the folder `pathname`
    """
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)
    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))
    # get the file name

    filename = os.path.join(pathname, url.split("/")[-1])

    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "ab") as f:
        for data in progress:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))

def main(url, path):
    # get all images
    imgs = get_all_images(url)
    content = requests.get(url)
    soup = BeautifulSoup(content.text , 'html.parser')

    id = []
    products =[] #List to store name of the product
    prices = [] #List to store price of the product
    category = []


    for img in imgs:
        # for each image, download it
        download(img, path)

    counter = 1
    # https://www.pluralsight.com/guides/web-scraping-with-selenium
    for a in soup.findAll('div',attrs={'class':'span2 product'}):
        subPage = a.find('h3', attrs={'class':'product-name'})
        li = subPage.find('a', href = True)
        li = li.get('href')
        subContent = requests.get(li)
        subSoup = BeautifulSoup(subContent.text , 'html.parser')

        name=subSoup.find('div', attrs={'class':'product-name'})
        pro_name = name.find('h1')

        price=subSoup.find('span', attrs={'class':'price'})

        catg = subSoup.find('div', attrs={'class':'cat-tree'})

        products.append(pro_name.text)
        prices.append(price.text)
        id.append(counter)
        category.append(catg.text)
        counter = counter + 1

    df = pd.DataFrame({'Id':id,'Product_Name':products,'Price':prices,'Category':category,})
    my_file = Path("products.csv")
    if my_file.exists():
        df.to_csv('products.csv', index=False,mode = 'a', encoding='utf-8')
    else:
        df.to_csv('products.csv', index=False, encoding='utf-8')



main("link-is-here", "folder-for-pictures")
