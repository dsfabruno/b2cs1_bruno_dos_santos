import argparse, os, requests
from settings import BASE_URL, DEFAULT_DELAY
from utils import get, download, ensure_dir, slugify
from parsers import parse_category_links, parse_list_page, parse_product_page
import csv

FIELDS = ["title","price","availability","rating","product_url","image_url","upc","category"]

def write_csv(path: str, rows: list[dict]):
    ensure_dir(os.path.dirname(path))
    write_header = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            w.writeheader()
        w.writerows(rows)

def scrape_category(session, name: str, url: str, outdir: str, max_pages: int | None,
                    delay: float, download_images: bool):
    cat_slug = slugify(name)
    csv_path = os.path.join(outdir, "csv", f"category_{cat_slug}.csv")
    img_dir  = os.path.join(outdir, "images", cat_slug)

    print(f"[{name}] -> {url}")
    page_url = url
    page_idx = 0

    while page_url and (max_pages is None or page_idx < max_pages):
        r = get(page_url, delay=delay, session=session)
        links, next_url = parse_list_page(r.text, page_url)

        rows = []
        for link in links:
            pr = get(link, delay=delay, session=session)
            item = parse_product_page(pr.text, link, name)
            rows.append(item)
            if download_images and item["image_url"] and item["upc"]:
                img_name = f"{item['upc']}_{slugify(item['title'])}.jpg"
                img_path = os.path.join(img_dir, img_name)
                try:
                    download(item["image_url"], img_path, delay=delay, session=session)
                except Exception as e:
                    print(f"   (image) {e}")

        if rows:
            write_csv(csv_path, rows)
            print(f"  + {len(rows)} livres (page {page_idx+1})")

        page_url = next_url
        page_idx += 1

def main():
    ap = argparse.ArgumentParser(description="Books to Scrape")
    ap.add_argument("--categories", nargs="*", help="Noms EXACTS des catégories")
    ap.add_argument("--max-pages", type=int, default=None)
    ap.add_argument("--delay", type=float, default=DEFAULT_DELAY)
    ap.add_argument("--outdir", default="outputs")
    ap.add_argument("--no-images", action="store_true")
    args = ap.parse_args()

    ensure_dir(args.outdir)
    s = requests.Session()

    home = get(BASE_URL, session=s)
    cats = parse_category_links(home.text)
    print(f"Nombre de catégories trouvées: {len(cats)}")

    if args.categories:
        wanted = {c.lower() for c in args.categories}
        cats = [c for c in cats if c["name"].lower() in wanted]

    if not cats:
        print("Aucune catégorie à scraper.")
        return

    for c in cats:
        scrape_category(
            session=s,
            name=c["name"],
            url=c["url"],
            outdir=args.outdir,
            max_pages=args.max_pages,
            delay=args.delay,
            download_images=not args.no_images,
        )

if __name__ == "__main__":
    main()
