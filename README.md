# MetadataFetcher

**MetadataFetcher** là công cụ thu thập thông tin chi tiết về bất kỳ package, module, app hoặc tool nào (bao gồm cả ngoài PyPI) từ nhiều nguồn như PyPI, GitHub, Google Search, trang chủ chính thức, v.v. Kết quả trả về bao gồm hướng dẫn cài đặt, link tài liệu, README, dependency, v.v. – sẵn sàng tích hợp cho chatbot kỹ thuật hoặc các hệ thống tự động hóa.

---

## 🚀 Tính năng nổi bật
- **Tự động lấy metadata từ PyPI, GitHub, Google Search**
- **Hỗ trợ cả tool ngoài PyPI** (ví dụ: milvus, postgresql, redis, elastic, nats...)
- **Trích xuất hướng dẫn cài đặt** (pip, docker, docker compose, build from source, package manager...)
- **Tìm và lưu link tài liệu, hướng dẫn setup**
- **Lưu dữ liệu thô (HTML/text) để phân tích sâu hơn**
- **Lưu output mẫu dạng JSON tóm tắt, ngắn gọn**

---

## 🛠️ Cài đặt & Chuẩn bị
1. **Clone repo về máy**
2. **Cài đặt Python >= 3.8**
3. **Cài đặt thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Tạo file `.env`** (không commit lên git!) với nội dung:
   ```
   GOOGLE_CSE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_cse_id
   ```
   > Đăng ký Google Custom Search API và CSE ID theo hướng dẫn bên dưới.

### 🔑 Hướng dẫn lấy Google Custom Search API Key & CSE ID

1. **Lấy Google API Key:**
   - Vào [Google Cloud Console](https://console.cloud.google.com/).
   - Tạo project mới (nếu chưa có).
   - Vào **APIs & Services > Library**.
   - Tìm **Custom Search API** và bật nó.
   - Vào **APIs & Services > Credentials**.
   - Chọn **Create Credentials > API key**. Sao chép key này.

2. **Lấy Google CSE ID:**
   - Vào [Google Custom Search Engine](https://cse.google.com/cse/all).
   - Nhấn **Add** để tạo search engine mới.
   - Ở “Sites to search”, nhập `*.io` hoặc domain bất kỳ (có thể sửa sau).
   - Nhấn **Create**.
   - Trong control panel, nhấn tên search engine, vào **Setup**.
   - Sao chép **Search engine ID**.
   - Để tìm toàn bộ web, vào control panel, chỉnh “Sites to search” thành “Search the entire web”.

3. **Thêm vào file `.env`**
   ```
   GOOGLE_CSE_API_KEY=your_api_key_here
   GOOGLE_CSE_ID=your_cse_id_here
   ```

---

## 💡 Cách sử dụng nhanh

> **Lưu ý:**
> - Với **package PyPI** (ví dụ: flask, numpy), nên dùng API Python để lấy metadata đầy đủ nhất. API hiện đã lấy link tài liệu (documentation) và hướng dẫn cài đặt chính xác hơn cho các package PyPI.
> - CLI phù hợp nhất cho **tool ngoài PyPI** (ví dụ: milvus, postgresql, redis). Nếu dùng CLI cho package PyPI, kết quả có thể không đầy đủ và sẽ có cảnh báo nên dùng API.

### 1. Lấy metadata cho package PyPI (khuyến nghị)
```python
from metadata_fetcher import fetch_package_metadata
metadata = fetch_package_metadata("flask")
print(metadata)
# Trường 'documentation' và hướng dẫn cài đặt sẽ được điền nếu có trong metadata của PyPI.
```

### 2. Lấy metadata cho tool ngoài PyPI hoặc bất kỳ tool nào (CLI)
```bash
python -m metadata_fetcher.generic_fetcher
# Nhập tên tool hoặc package khi được hỏi (ví dụ: flask, milvus, postgresql)
# Có thể nhập link homepage thủ công nếu Google trả về sai
```
> ⚠️ Nếu nhập tên package PyPI vào CLI, bạn có thể thấy cảnh báo nên dùng API Python để có metadata đầy đủ hơn.

### 3. Lưu output mẫu ra file JSON
Sau khi chạy, chọn lưu output khi được hỏi. File sẽ nằm trong thư mục `SampleOutputs/metadata/PyPI/` hoặc `SampleOutputs/metadata/Non-PyPI/`. Output là JSON tóm tắt ngắn gọn (xem bên dưới).

---

## 📦 Output Schema (Chuẩn hóa)
```python
{
  "name": str,
  "description": str | None,
  "latest_version": str | None,
  "popular_versions": List[str],
  "dependencies": Dict[str, List[str]],
  "github_url": str | None,
  "readme_content": str | None,
  "requirements": str | None,
  "installation": {
    "pip": List[dict],
    "from_source": List[dict],
    "docker": List[dict],
    "docker_compose": List[dict],
    "other": List[dict],
    "platforms": Dict[str, List[dict]]
  },
  "homepage": str | None,
  "documentation": str | None,
  "documentation_links": List[str],
  "installation_links": List[str],
  "homepage_html": str | None,
  "documentation_html": str | None,
  "source": "pypi" | "manual + google"
}
```
- **Lưu ý:** File JSON tóm tắt chỉ hiển thị các trường quan trọng và link liên quan, không phải toàn bộ chi tiết dài dòng.

---

## 📋 Ví dụ output mẫu (milvus)
```json
{
  "Name": "milvus",
  "Homepage": "https://milvus.io/",
  "Documentation": "https://milvus.io/docs",
  "Source": "manual + google",
  "Documentation Links": ["https://milvus.io/docs", ...],
  "Installation Summary": {
    "pip": {
      "command": "pip install -U pymilvus",
      "explanation": "Install a Python package using pip.",
      "note": "Run in your terminal or command prompt."
    },
    ...
  }
}
```

---

## 📖 Kiến trúc & Mở rộng
- **Modular:** Tách riêng fetcher cho PyPI, GitHub, Google, parser cài đặt...
- **Dễ mở rộng:** Thêm nguồn mới, parser mới dễ dàng
- **Có thể tích hợp chatbot, API, UI...**
- **Parser cài đặt:** Nhận diện pip, docker, docker compose, conda, npm, các trình quản lý gói hệ điều hành, v.v., kèm giải thích và gợi ý nền tảng.
- **Google Search:** Yêu cầu `.env` với API key và CSE ID; sẽ báo lỗi nếu thiếu.
- **Phụ thuộc:** `requests`, `packaging`, `beautifulsoup4`, `python-dotenv`.

