# Multimodal Search System for E-Commerce

This Assignment 06 prototype lets users search for products using **text, simulated voice, or images**. It also supports order lookup by customer ID. You can use it in a web browser or from the command line (CLI).

The program runs locally with the included JSON data and sample images. It needs no API key, database server, microphone, or AI model download. After installing the Python packages, you can use it offline.

## 1. Python Version and Required Packages

Use **Python 3.10 or later**. Check your version:

```bash
python --version
```

If your computer uses `python3`, replace `python` with `python3` in the commands below.

The required packages are listed in `requirements.txt`:

| Package | Version | Purpose |
|---|---|---|
| NumPy | `>=2.0,<3` | Work with image vectors and calculate cosine similarity |
| Pillow | `>=10,<13` | Open images, convert them to RGB, and resize them |

The web server, JSON handling, command-line options, and tests use Python's standard library. Bootstrap, CSS, JavaScript, and website images are included in `presentation/static/`.

## 2. Installation

Open a terminal in the project root folder, which contains `main.py` and `requirements.txt`.

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

In Windows Command Prompt (cmd), activate the environment with `.venv\Scripts\activate.bat`.

Installing packages normally requires an Internet connection. For later runs, activate the virtual environment again; you do not need to reinstall the packages.

## 3. How to Run the Program

### Web Interface (Default)

```bash
python main.py
```

Open **http://127.0.0.1:8000** in your browser. The terminal also shows the address. Press **Ctrl+C** in that terminal to stop the server.

If you get `OSError: [Errno 98] Address already in use`, another program is using the port. Stop the previous server with Ctrl+C, or choose a different port:

```bash
python main.py --web --port 8080
```

Then open **http://127.0.0.1:8080**.

To search in the browser:

1. Choose **Text**, **Voice**, or **Image**.
2. For Text or Voice, enter an English query. Voice uses a typed transcript instead of an audio recording.
3. For Image, upload an image from your computer. The page allows files up to 5 MB. Try `data/images/p01.png`.
4. Choose a customer ID and a result limit, then click **Search collection**.
5. View product names, prices, stock, and search scores. Click **View details** for more information. You can sort the shown results by price or use **View all products** to return to the full catalog.

The catalog contains 12 products. Order lookup uses the selected customer ID: order `O001` belongs to `C001`, and order `O002` belongs to `C002`.

### Command-Line Interface (CLI)

Run the default examples for text, simulated voice, images, and orders:

```bash
python main.py --cli
```

For a single search, use `--mode` and `--query`. Using `--mode` or `--json` selects CLI mode unless you also specify `--web`.

| Option | Meaning | Default |
|---|---|---|
| `--web` | Start the web interface | Used when no CLI option is given |
| `--cli` | Run the default CLI examples | Off |
| `--port` | Set the web server port | `8000` |
| `--mode` | Search type: `text`, `voice`, or `image` | Not set |
| `--query` | Query text or image path; required with `--mode` | Not set |
| `--customer` | Customer ID for order lookup | `C001` |
| `--top-k` | Maximum number of product results; must be a positive integer | `5` |
| `--json` | Print CLI results as JSON | Off |

You cannot use `--web` and `--cli` together. The web interface allows 1 to 12 results. The CLI accepts any positive integer for `--top-k`.

## 4. Example Commands

Run these commands from the project root folder.

```bash
# Show all command-line options
python main.py --help

# Search by keywords
python main.py --mode text --query "black shoes"

# Search for Nike shoes under $100 and return up to 3 results
python main.py --mode text --query "find Nike shoes under 100 dollars" --top-k 3

# Simulate voice input using a typed transcript
python main.py --mode voice --query "find running shoes"

# Search using a sample product image
python main.py --mode image --query data/images/p01.png

# Search using a separate image that is not in the product catalog
python main.py --mode image --query data/images/query_blue_shoe.png --top-k 3

# Look up an order for customer C001
python main.py --mode text --query "find order O001" --customer C001

# Look up an order for customer C002
python main.py --mode text --query "find order O002" --customer C002

# Find the latest order for the default customer, C001
python main.py --mode voice --query "where is my latest order"

# Print one search result as JSON
python main.py --mode text --query "blue shoes" --json

# Print all default examples as JSON
python main.py --json
```

Relative image paths start from your terminal's current folder. For an image elsewhere, use an absolute path. Put the path in quotes if it contains spaces. The program loads catalog data from its own module folder.

The `under` and `below` price filters mean **less than** the given price. Products with exactly that price are excluded. An order lookup does not return an order owned by another customer.

## 5. Project Directory Structure

```text
multimodel-search-system/
├── README.md
├── requirements.txt               # Required Python packages
├── main.py                        # Set up services and start Web or CLI
├── evaluate.py                    # Run 17 fixed evaluation cases
├── application/                   # Search logic
│   ├── query_service.py           # Process queries and read price filters
│   ├── speech_service.py          # Simulate speech transcription
│   ├── image_service.py           # Convert images into feature vectors
│   ├── search_service.py          # Search products and look up orders
│   └── ranking_service.py         # Rank results and select top-k
├── data/                          # Sample data and data access
│   ├── products.json              # Catalog of 12 products
│   ├── orders.json                # Sample orders
│   ├── product_repository.py      # Read products and their images
│   ├── order_repository.py        # Read orders by customer
│   ├── vector_index.py            # Image vector index stored in memory
│   └── images/                    # 12 product images and a separate query image
├── presentation/                  # User interfaces
│   ├── search_ui.py               # Handle input and display CLI results
│   ├── web_server.py              # Local HTTP server
│   ├── web_ui.html                # Web page
│   ├── demo_window.py             # Optional window showing CLI demo output
│   └── static/                    # CSS, JavaScript, Bootstrap, and website images
│       └── ASSETS.md              # Asset sources and licenses
├── tests/
│   ├── test_search.py             # Search tests
│   └── test_web.py                # HTTP interface tests
└── uml/
    ├── Assignment06.vpp           # Visual Paradigm UML project
    └── README.md                  # Instructions for opening the UML model
```

The main flow is: **user input → process text or image → search → rank → display results**. Data is stored in JSON files. The image index is built in memory each time the program starts.

## 6. Tests and Evaluation

Run the tests:

```bash
python -m unittest discover -s tests -v
```

Run the 17 fixed evaluation cases:

```bash
python evaluate.py
```

The evaluation prints results in the terminal and creates a `results/` folder with:

- `results/evaluation.json`: inputs, expected and actual results, pass/fail status, and processing time.
- `results/evaluation.md`: a results table and the pass rate.

Each case checks the first product or order ID, or checks that there is no result. Some cases are designed to show the prototype's limits. The pass rate does not measure accuracy on real product photos.

To open the optional CLI demo viewer:

```bash
python presentation/demo_window.py
```

This viewer needs **Tkinter**. Some Linux distributions provide it through the `python3-tk` system package. The Web, CLI, and evaluation do not need Tkinter.

## 7. Prototype Limitations

- **Voice input is simulated.** Users type a transcript. The program does not record a microphone, read audio files, or perform real speech recognition.
- **Text search matches keywords.** It counts matching words in product information. It is designed for English queries and does not understand synonyms, meaning, or Vietnamese queries. For example, `dark sneakers` may not find the same products as `black shoes`.
- **Image search uses simple pixel features.** Images are converted to RGB and resized to 16 × 16 pixels. An 11 × 11 center area produces a vector of 363 values. There is no deep learning model. Changes in color, camera angle, or background can affect results.
- **Identical images can give incorrect product matches.** The sample images are simple generated shapes. Different products may use identical images. When scores are equal, the smaller product ID comes first.
- **Image search has no minimum similarity score.** It returns the closest top-k images even when the query image is unrelated to the catalog. A similarity score is not a probability that the match is correct.
- **Filters and ranking are basic.** The program supports maximum prices through `under` or `below`. It does not infer preferences or a budget that the user has not stated. Price sorting on the web page only sorts the results already shown.
- **The dataset and evaluation are small.** There are only 12 sample products. Evaluation includes catalog images and one changed image, so it does not show how well the system works on real-world data.
- **There is no user authentication.** The customer option is a test identity value. Checking order ownership does not replace a real login and access control system.
- **The system is for local demonstrations.** It uses JSON files and an in-memory index rather than a production database or a large vector index. The server listens only on `127.0.0.1`. Checkout, payments, and product management are not included.
