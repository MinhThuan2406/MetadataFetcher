# MetadataFetcher

**MetadataFetcher** là công cụ thu thập thông tin chi tiết về bất kỳ package, module, app hoặc tool nào (bao gồm cả ngoài PyPI) từ nhiều nguồn như PyPI, GitHub, Google Search, trang chủ chính thức, v.v. Kết quả trả về bao gồm hướng dẫn cài đặt, link tài liệu, README, dependency, v.v. – sẵn sàng tích hợp cho chatbot kỹ thuật hoặc các hệ thống tự động hóa.

---

## 🚀 Tính năng nổi bật
- **Tự động lấy metadata từ PyPI, GitHub, Google Search**
- **Hỗ trợ cả tool ngoài PyPI** (ví dụ: milvus, postgresql, redis, elastic, nats...)
- **Trích xuất hướng dẫn cài đặt** (pip, docker, build from source, package manager...)
- **Tìm và lưu link tài liệu, hướng dẫn setup**
- **Lưu dữ liệu thô (HTML/text) để phân tích sâu hơn**
- **Có thể lưu output mẫu ra file JSON**

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
   > Đăng ký Google Custom Search API và CSE ID theo hướng dẫn trong docs.

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
### 1. Lấy metadata cho package/tool bất kỳ
```python
from metadata_fetcher import fetch_package_metadata
metadata = fetch_package_metadata("flask")
print(metadata)
```

### 2. Lấy metadata cho tool ngoài PyPI (ví dụ: milvus)
```bash
python -m metadata_fetcher.generic_fetcher
# Nhập tên tool khi được hỏi (ví dụ: milvus)
# Có thể nhập link homepage thủ công nếu Google trả về sai
```

### 3. Lưu output mẫu ra file JSON
Sau khi chạy, chọn lưu output khi được hỏi. File sẽ nằm trong thư mục `SampleOutputs/`.

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
    "pip": str | None,
    "from_source": str | None,
    "docker": str | None,
    "other": str | None
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

---

## 📋 Ví dụ output mẫu (milvus)
```json
{
  "name": "milvus",
  "homepage": "https://milvus.io/",
  "documentation": "https://milvus.io/docs",
  "documentation_links": ["https://milvus.io/docs", ...],
  "installation_links": ["https://milvus.io/docs/quickstart.md", ...],
  "installation": {
    "pip": "pip install -U pymilvus",
    "docker": null,
    "from_source": null,
    "other": null
  },
  ...
}
```

---

## 📖 Kiến trúc & Mở rộng
- **Modular:** Tách riêng fetcher cho PyPI, GitHub, Google, parser cài đặt...
- **Dễ mở rộng:** Thêm nguồn mới, parser mới dễ dàng
- **Có thể tích hợp chatbot, API, UI...**

