# Streamlit Frontend

Giao diện Streamlit cho ứng dụng dự đoán giá nhà.

## 🚀 Chạy local

```bash
streamlit run src/frontend/app.py
```

Mặc định frontend gọi API ở `http://localhost:8000`. Có thể đổi bằng biến môi trường `API_URL`.

```bash
API_URL=http://localhost:8000 streamlit run src/frontend/app.py
```

## 🐳 Docker

Đã cung cấp `Dockerfile` sẵn trong thư mục này.

### Build image

Từ thư mục gốc dự án (khuyến nghị tag `house-frontend`):

```bash
docker build -f src/frontend/Dockerfile -t house-frontend .
```

### Run container

```bash
docker run --rm -p 8501:8501 \
  -e API_URL=http://host.docker.internal:8000 \
  house-frontend
```

Ghi chú: `host.docker.internal` giúp container truy cập API đang chạy trên máy host (macOS/Windows). Nếu API chạy bằng container khác trong cùng một Docker network, set `API_URL` theo tên service, ví dụ: `http://api:8000`.

### Kết hợp với API container (ví dụ)

Tạo network dùng chung:
```bash
docker network create house-net || true
```

Chạy API:
```bash
docker run -d --name api --network house-net -p 8000:8000 house-api
```

Chạy Frontend (trỏ đến service `api`):
```bash
docker run -d --name frontend --network house-net -p 8501:8501 \
  -e API_URL=http://api:8000 \
  house-frontend
```
