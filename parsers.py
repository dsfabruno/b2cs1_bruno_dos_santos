from parsel import Selector
from urllib.parse import urljoin
from settings import BASE_URL
from utils import slugify

def parse_category_links(html: str) -> list[dict]:
    sel = Selector(text=html)
    items = []
    for a in sel.css("ul.nav-list ul li a"):
        name = a.xpath("normalize-space(text())").get()
        href = a.attrib.get("href")
        if not (name and href):
            continue
        url = urljoin(BASE_URL, href)
        items.append({"name": name, "url": url, "slug": slugify(name)})
    return items

def parse_list_page(html: str, page_url: str) -> tuple[list[str], str | None]:
    sel = Selector(text=html)
    # liens produits relatifs -> url absolue par rapport à page_url
    book_links = []
    for a in sel.css("article.product_pod h3 a"):
        href = a.attrib.get("href") or ""
        book_links.append(urljoin(page_url, href))
    # pagination
    next_href = sel.css("li.next a::attr(href)").get()
    next_url = urljoin(page_url, next_href) if next_href else None
    return book_links, next_url

def parse_product_page(html: str, product_url: str, category: str) -> dict:
    sel = Selector(text=html)
    title = sel.css(".product_main h1::text").get() or ""
    price = sel.css(".product_main .price_color::text").get() or ""
    availability = " ".join(t.strip() for t in sel.css(".availability::text").getall() if t.strip())

    rating_map = {"One":1,"Two":2,"Three":3,"Four":4,"Five":5}
    rating_cls = (sel.css(".product_main .star-rating").attrib.get("class","")).split()
    rating = next((v for k,v in rating_map.items() if k in rating_cls), 0)

    upc = ""
    for tr in sel.css("table.table.table-striped tr"):
        th = tr.css("th::text").get()
        if th == "UPC":
            upc = tr.css("td::text").get() or ""
            break

    img_rel = sel.css("#product_gallery img::attr(src)").get() or ""
    img_url = urljoin(product_url, img_rel)

    return {
        "title": title,
        "price": price,
        "availability": availability,
        "rating": rating,
        "product_url": product_url,
        "image_url": img_url,
        "upc": upc,
        "category": category,
    }
