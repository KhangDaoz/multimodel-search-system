# V02 sample catalog and photographs

15 entries (5 shoes, 5 shirts, 5 bags) adapted from the public DummyJSON sample
catalog: https://github.com/Ovi/DummyJSON/blob/master/database/products.json .
Downloaded 2026-10-07. Original IDs are retained in `source_id`; original image
URLs are retained in `image_source`. This is sample e-commerce data, not live
inventory or verified customer reviews. Names/prices/descriptions/ratings come
from that source. Color labels were checked against the actual photographs;
product 7 is marked out of stock to exercise availability filtering.

The product WebP cutouts were composited onto white PNG backgrounds for local
serving and image retrieval. They are actual product photographs, replacing V01
synthetic shapes. Source attribution is provided; DummyJSON's repository license
is MIT, but this does not establish separate commercial rights to branded photos.
The catalog is used here for this educational assignment.

`query_blue_trainers.png` is a resized, rotated copy of product 3 and is excluded
from the index. This is a transformation robustness check, not an independent
real-world image dataset. `query_blue_shoe.png` is a historical V01 synthetic query.

Order totals/line prices were updated to match the current sample product prices.
C001 owns O001 and 20261001; C002 owns O002. Customer IDs are demo identities.
