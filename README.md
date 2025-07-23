## Mục tiêu tổng thể
Viết một hàm thu thập thông tin chi tiết về một app/module/package bất kỳ (ví dụ: "numpy") từ các nguồn phổ biến như PyPI và GitHub, phục vụ phát triển chatbot kỹ thuật.

---

## Chức năng chính

| Yêu cầu                | Diễn giải cụ thể                                                                 |
|------------------------|----------------------------------------------------------------------------------|
| Truy cập PyPI          | Dùng API https://pypi.org/pypi/<package>/json để lấy metadata                    |
| Lấy mô tả              | Lấy summary hoặc description của package từ PyPI                                 |
| Lấy version            | Lấy danh sách version (sắp xếp giảm dần)                                         |
| Xác định version phổ biến | Lấy 3 version mới nhất làm "popular versions"                                 |
| Lấy dependencies       | Từ metadata từng version hoặc từ requires_dist                                   |
| Xác định GitHub repo   | Nếu có, trích GitHub URL từ metadata PyPI (home_page, project_urls, ...)         |
| Crawl GitHub (nếu có)  | Lấy nội dung README.md và requirements.txt từ repo GitHub (nhánh master/main)    |
| Trả về object chuẩn    | Bao gồm tất cả thông tin trên trong một dict hoặc JSON object                    |

---

## Input

```python
fetch_package_metadata(app_name: str)
# app_name: Tên một package từ PyPI (ví dụ "flask", "numpy", "langchain", ...)
```

---

## Output

```python
{
    "description": str,
    "latest_version": str,
    "popular_versions": List[str],
    "dependencies": Dict[str, List[str]],
    "github_url": str or None,
    "readme_content": str or None,
    "requirements": str or None
}
```

---

## Yêu cầu chi tiết & Kỳ vọng

| Hạng mục                | Chi tiết                                                                                 |
|-------------------------|-----------------------------------------------------------------------------------------|
| Mục tiêu sử dụng        | Tích hợp vào chatbot kỹ thuật, giúp chatbot trả lời user về package                     |
| Tính năng mở rộng sau   | Có thể mở rộng để trả lời: "package này dùng để làm gì?", "nên dùng version nào?", ...  |
| Nguồn dữ liệu           | PyPI (metadata, version, dependency), GitHub (readme, requirements)                     |
| Robustness              | Nếu không có GitHub/file không tồn tại → trả về None, không raise lỗi                   |
| Kỹ năng cần luyện        | Làm việc với API, ghép dữ liệu nhiều nguồn, làm sạch & chuẩn hóa dữ liệu, code mở rộng  |

---

## Checklist 

- [x] Lấy mô tả và version từ PyPI
- [x] Lấy dependency của các version chính
- [x] Xác định GitHub repo nếu có
- [x] Lấy README.md và requirements.txt nếu repo tồn tại
- [x] Xử lý fallback nếu không có file hoặc link
- [x] Có thể chạy thử hàm `fetch_package_metadata("numpy")` và thấy kết quả
- [x] Code rõ ràng, chia nhỏ hàm, dễ debug/mở rộng

--- 
