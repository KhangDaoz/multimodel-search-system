# Bundled storefront assets

Bootstrap **5.3.8** CSS and JavaScript bundle are distributed under MIT.
Official documentation: https://getbootstrap.com/docs/5.3/getting-started/introduction/
The license is retained in `vendor/BOOTSTRAP_LICENSE.txt`.
Downloads: https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/

Category and hero photographs from Unsplash (illustrative editorial images,
not images of specific products in the prototype dataset):

- `images/hero-sneaker.jpg`: https://images.unsplash.com/photo-1542291026-7eec264c27ff
- `images/bags.jpg`: https://images.unsplash.com/photo-1553062407-98eeb64c6a62
- `images/shirts.jpg`: https://images.unsplash.com/photo-1521572163474-6864f9cf17ab

Unsplash license: https://unsplash.com/license
Product cards use the locally bundled V02 catalog photographs, served through
application services. These same photographs are used by image retrieval.
All runtime assets are local; the storefront makes no CDN requests.

## V02 catalog

Product cards now use 15 downloaded product photographs from DummyJSON, bundled
in `data/images/`. Full source URLs are stored per product in `data/products.json`.
See `data/README.md` for provenance and the sample-data scope. Transparent source
cutouts are composited onto white, rather than flattened onto black.
