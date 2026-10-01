# Hệ thống tìm kiếm đa phương thức cho thương mại điện tử

Prototype của Assignment 06 hỗ trợ tìm sản phẩm bằng **văn bản, giọng nói mô phỏng và hình ảnh**, đồng thời tra cứu đơn hàng theo khách hàng. Có hai cách sử dụng: giao diện Web trên trình duyệt và dòng lệnh (CLI).

Dự án chạy cục bộ với dữ liệu JSON và ảnh mẫu đi kèm. Không cần API key, máy chủ cơ sở dữ liệu, micro hoặc tải mô hình AI. Sau khi cài đặt các thư viện, giao diện Web có thể hoạt động ngoại tuyến.

## 1. Phiên bản Python và thư viện cần thiết

Sử dụng **Python 3.10 trở lên**. Kiểm tra phiên bản trước khi cài đặt:

```bash
python --version
```

Nếu máy sử dụng lệnh `python3`, thay `python` bằng `python3` trong các hướng dẫn bên dưới.

Các thư viện ngoài được khai báo trong `requirements.txt`:

| Thư viện | Phiên bản | Mục đích |
|---|---|---|
| NumPy | `>=2.0,<3` | Xử lý vector ảnh và tính độ tương đồng cosine |
| Pillow | `>=10,<13` | Đọc ảnh, chuyển RGB và thay đổi kích thước |

Máy chủ HTTP, xử lý JSON, tham số dòng lệnh và kiểm thử sử dụng thư viện chuẩn Python. Bootstrap, CSS, JavaScript và ảnh trang Web được lưu sẵn trong `presentation/static/`.

## 2. Cài đặt

Mở terminal tại thư mục gốc dự án, nơi chứa `main.py` và `requirements.txt`.

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

Nếu sử dụng Command Prompt (cmd), kích hoạt môi trường bằng `.venv\Scripts\activate.bat`.

Việc cài thư viện cần Internet nếu máy chưa có các gói cần thiết. Những lần chạy sau chỉ cần kích hoạt lại môi trường ảo.

## 3. Chạy chương trình

### Giao diện Web (mặc định)

```bash
python main.py
```

Mở **http://127.0.0.1:8000** trong trình duyệt. Chương trình in địa chỉ truy cập ra terminal; dừng máy chủ bằng **Ctrl+C**.

Có thể chỉ định chế độ Web và đổi cổng nếu cổng 8000 đang được sử dụng:

```bash
python main.py --web --port 8080
```

Sau đó mở **http://127.0.0.1:8080**.

Cách sử dụng:

1. Chọn **Text**, **Voice** hoặc **Image**.
2. Với Text/Voice, nhập truy vấn tiếng Anh. Voice nhận văn bản đã phiên âm, không nhận bản ghi âm.
3. Với Image, chọn ảnh từ máy (giao diện giới hạn tệp tối đa 5 MB). Có thể thử `data/images/p01.png`.
4. Chọn mã khách hàng và số lượng kết quả, rồi nhấn **Search collection**.
5. Xem thông tin sản phẩm, giá, tồn kho, điểm tìm kiếm và **View details**. Có thể sắp xếp kết quả theo giá hoặc chọn **View all products** để xem lại danh mục.

Danh mục ban đầu có 12 sản phẩm. Tra cứu đơn hàng dùng mã khách hàng đang chọn: `O001` thuộc `C001`, còn `O002` thuộc `C002`.

### Giao diện dòng lệnh (CLI)

Chạy bộ ví dụ mặc định gồm tìm kiếm văn bản, giọng nói mô phỏng, ảnh và đơn hàng:

```bash
python main.py --cli
```

Chạy một truy vấn cụ thể bằng `--mode` và `--query`. Khi có `--mode` hoặc `--json`, chương trình tự chọn CLI nếu không chỉ định `--web`.

| Tham số | Ý nghĩa | Mặc định |
|---|---|---|
| `--web` | Khởi động giao diện Web | Được chọn khi không có tham số CLI |
| `--cli` | Chạy bộ ví dụ CLI | Không |
| `--port` | Cổng máy chủ Web | `8000` |
| `--mode` | Loại truy vấn: `text`, `voice`, `image` | Không chỉ định |
| `--query` | Văn bản truy vấn hoặc đường dẫn ảnh; bắt buộc khi có `--mode` | Không chỉ định |
| `--customer` | Mã khách hàng để tra cứu đơn hàng | `C001` |
| `--top-k` | Số kết quả sản phẩm tối đa; phải là số nguyên dương | `5` |
| `--json` | Xuất kết quả CLI dưới dạng JSON | Không |

`--web` và `--cli` không được dùng đồng thời. Giao diện Web cho phép chọn từ 1 đến 12 kết quả; CLI nhận mọi giá trị `--top-k` nguyên dương.

## 4. Các lệnh ví dụ

Chạy các lệnh từ thư mục gốc dự án.

```bash
# Xem hướng dẫn tham số
python main.py --help

# Tìm sản phẩm theo từ khóa
python main.py --mode text --query "black shoes"

# Tìm giày Nike giá dưới 100, lấy tối đa 3 kết quả
python main.py --mode text --query "find Nike shoes under 100 dollars" --top-k 3

# Giọng nói mô phỏng: đầu vào là bản phiên âm dạng văn bản
python main.py --mode voice --query "find running shoes"

# Tìm bằng ảnh mẫu
python main.py --mode image --query data/images/p01.png

# Tìm bằng ảnh truy vấn riêng, không nằm trong danh mục sản phẩm
python main.py --mode image --query data/images/query_blue_shoe.png --top-k 3

# Tra cứu đơn hàng của khách hàng C001
python main.py --mode text --query "find order O001" --customer C001

# Tra cứu đơn hàng của khách hàng C002
python main.py --mode text --query "find order O002" --customer C002

# Tra cứu đơn hàng gần nhất của khách hàng mặc định C001
python main.py --mode voice --query "where is my latest order"

# Xuất kết quả một truy vấn thành JSON
python main.py --mode text --query "blue shoes" --json

# Xuất toàn bộ bộ ví dụ mặc định thành JSON
python main.py --json
```

Đường dẫn ảnh truy vấn tương đối được tính từ thư mục terminal hiện tại. Nếu ảnh nằm ở nơi khác, dùng đường dẫn tuyệt đối và đặt trong dấu ngoặc kép nếu có khoảng trắng. Dữ liệu danh mục được nạp theo vị trí module của dự án.

Bộ lọc `under`/`below` là giới hạn giá **nhỏ hơn** giá đã nhập, không bao gồm giá bằng giới hạn. Truy vấn đơn hàng của khách hàng khác sẽ không trả về thông tin đơn hàng đó.

## 5. Cấu trúc thư mục

```text
multimodel-search-system/
├── README.md
├── requirements.txt               # Các thư viện Python cần cài
├── main.py                        # Khởi tạo dịch vụ, chạy Web hoặc CLI
├── evaluate.py                    # Đánh giá với 17 trường hợp cố định
├── application/                   # Xử lý nghiệp vụ
│   ├── query_service.py           # Chuẩn hóa truy vấn, nhận diện ý định, lọc giá
│   ├── speech_service.py          # Mô phỏng chuyển giọng nói thành văn bản
│   ├── image_service.py           # Chuyển ảnh thành vector đặc trưng
│   ├── search_service.py          # Tìm sản phẩm và tra cứu đơn hàng
│   └── ranking_service.py         # Xếp hạng và chọn top-k
├── data/                          # Dữ liệu và lớp truy cập dữ liệu
│   ├── products.json              # Danh mục 12 sản phẩm
│   ├── orders.json                # Đơn hàng mẫu
│   ├── product_repository.py      # Đọc sản phẩm và ảnh
│   ├── order_repository.py        # Đọc đơn hàng theo khách hàng
│   ├── vector_index.py            # Chỉ mục vector trong bộ nhớ
│   └── images/                    # 12 ảnh sản phẩm và một ảnh truy vấn riêng
├── presentation/                  # Giao diện người dùng
│   ├── search_ui.py               # Tiếp nhận đầu vào và trình bày kết quả CLI
│   ├── web_server.py              # Máy chủ HTTP cục bộ
│   ├── web_ui.html                # Giao diện Web
│   ├── demo_window.py             # Cửa sổ xem kết quả demo CLI (tùy chọn)
│   └── static/                    # CSS, JavaScript, Bootstrap và ảnh giao diện
│       └── ASSETS.md              # Nguồn và giấy phép tài nguyên
├── tests/
│   ├── test_search.py             # Kiểm thử tìm kiếm
│   └── test_web.py                # Kiểm thử giao diện HTTP
└── uml/
    ├── Assignment06.vpp           # Dự án UML của Visual Paradigm
    └── README.md                  # Hướng dẫn mở mô hình UML
```

Luồng xử lý chính: **giao diện → chuẩn hóa văn bản / mô phỏng phiên âm / trích xuất đặc trưng ảnh → tìm kiếm → xếp hạng → hiển thị kết quả**. Dữ liệu lưu bằng JSON; chỉ mục ảnh được tạo lại trong bộ nhớ khi khởi động.

## 6. Kiểm thử và đánh giá

Chạy bộ kiểm thử:

```bash
python -m unittest discover -s tests -v
```

Chạy đánh giá 17 trường hợp truy vấn cố định:

```bash
python evaluate.py
```

Lệnh đánh giá in kết quả ra terminal và tạo thư mục `results/` với hai tệp:

- `results/evaluation.json`: đầu vào, kết quả kỳ vọng/thực tế, trạng thái đạt và thời gian xử lý.
- `results/evaluation.md`: bảng kết quả và tỷ lệ đạt.

Tiêu chí đánh giá là ID sản phẩm/đơn hàng ở vị trí đầu tiên, hoặc không có kết quả. Bộ đánh giá có các trường hợp cố ý kiểm tra giới hạn của prototype; không nên hiểu tỷ lệ đạt là độ chính xác trên ảnh sản phẩm thực tế.

Cửa sổ xem demo tùy chọn:

```bash
python presentation/demo_window.py
```

Cửa sổ này cần **Tkinter**. Một số bản phân phối Linux cung cấp Tkinter qua gói hệ điều hành `python3-tk`; Web, CLI và đánh giá không cần Tkinter.

## 7. Giới hạn của prototype

- **Giọng nói chỉ được mô phỏng:** người dùng nhập bản phiên âm. Chưa có ghi âm từ micro, đọc tệp âm thanh hoặc nhận dạng tiếng nói thực tế.
- **Tìm kiếm văn bản dựa trên từ khóa:** đếm các token trùng khớp trong thông tin sản phẩm. Bộ xử lý thiết kế cho truy vấn tiếng Anh, chưa hỗ trợ hiểu ngữ nghĩa, từ đồng nghĩa hoặc tiếng Việt. Ví dụ `dark sneakers` có thể không tìm được sản phẩm phù hợp như `black shoes`.
- **Đặc trưng ảnh đơn giản:** ảnh được chuyển RGB, thu nhỏ xuống 16 × 16 và lấy vùng giữa 11 × 11, tạo vector 363 chiều. Đây là đặc trưng pixel thủ công, chưa sử dụng mô hình học sâu; thay đổi màu, góc chụp hoặc nền có thể ảnh hưởng kết quả.
- **Ảnh giống nhau khó phân biệt:** ảnh mẫu là các hình tổng hợp đơn giản; sản phẩm khác nhau có thể có ảnh giống hệt. Khi điểm bằng nhau, hệ thống ưu tiên ID sản phẩm nhỏ hơn.
- **Không có ngưỡng từ chối ảnh:** tìm kiếm ảnh trả về các hàng xóm gần nhất theo top-k, kể cả khi ảnh không liên quan đến danh mục. Điểm tương đồng không phải xác suất sản phẩm đúng.
- **Bộ lọc và xếp hạng còn hạn chế:** hỗ trợ giá tối đa qua `under`/`below`, nhưng chưa suy luận sở thích hay ngân sách không được nêu trong truy vấn. Sắp xếp giá trên Web chỉ sắp xếp các kết quả đã hiển thị.
- **Dữ liệu và đánh giá nhỏ:** chỉ có 12 sản phẩm mẫu. Bộ đánh giá có cả ảnh truy vấn trùng ảnh trong danh mục và một ảnh biến đổi; chưa chứng minh khả năng tổng quát trên dữ liệu thực tế.
- **Chưa có xác thực người dùng:** `--customer` và bộ chọn khách hàng là tham số mô phỏng danh tính. Việc kiểm tra chủ đơn hàng không thay thế cơ chế đăng nhập và phân quyền thực tế.
- **Hạ tầng dành cho demo cục bộ:** dùng tệp JSON và chỉ mục trong RAM, chưa có cơ sở dữ liệu sản xuất hoặc chỉ mục vector quy mô lớn. Máy chủ chỉ lắng nghe tại `127.0.0.1`; prototype chưa cung cấp quy trình đặt hàng, thanh toán hay quản trị sản phẩm.
