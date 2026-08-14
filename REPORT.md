# BÁO CÁO KẾT QUẢ LAB DAY 16 (TRACK 2)
## Triển khai Hạ tầng Tự động hóa với Terraform trên Google Cloud Platform (GCP) và Benchmark LightGBM

---

## 1. Thông tin Triển khai
- **Nền tảng Cloud:** Google Cloud Platform (GCP)
- **Vùng (Region / Zone):** `us-central1` / `us-central1-a`
- **Tài nguyên Compute:** `e2-medium` (2 vCPU, 4 GB RAM, Debian 12)
- **Hạ tầng Mạng:**
  - Custom VPC (`ai-vpc`) & Private Subnet (`ai-private-subnet` 10.0.0.0/24)
  - Cloud Router (`ai-router`) & Cloud NAT (`ai-nat`) cho phép Private VM truy cập internet
  - IAP TCP Forwarding (SSH an toàn qua port 22 không cần Public IP)
  - External HTTP Load Balancer & Health Check (port 8000)
- **Tập dữ liệu:** Credit Card Fraud Detection (284,807 dòng, 31 cột)
- **Mô hình ML:** LightGBM (`LGBMClassifier`)

---

## 2. Kết quả Benchmark Chi tiết

| Metric | Giá trị đo được | Đánh giá |
|---|---|---|
| **Thời gian load data** | **1.9560 s** | Load cực nhanh với Pandas cho ~285k dòng (150MB) |
| **Thời gian training** | **1.3262 s** | Thuật toán Histogram của LightGBM tối ưu đa luồng trên CPU `e2-medium` |
| **Best iteration** | **1** | Early stopping dừng sau 10 round, tối ưu loss ngay từ vòng 1 |
| **AUC-ROC** | **0.951654** | Khả năng phân biệt gian lận xuất sắc (~95.2%) |
| **Accuracy** | **0.998947 (99.89%)** | Độ chính xác tổng thể rất cao trên toàn bộ tập test |
| **F1-Score** | **0.727273** | Cân bằng tốt giữa Precision và Recall trên bài toán Imbalanced |
| **Precision** | **0.655738** | 65.6% các ca cảnh báo gian lận là chính xác |
| **Recall** | **0.816327 (81.63%)** | Bắt được hơn 81.6% tổng số các vụ gian lận thực tế |
| **Inference latency (1 row)** | **0.8508 ms** | Dưới 1ms, đáp ứng yêu cầu chấm điểm giao dịch thời gian thực (real-time scoring) |
| **Inference throughput (1000 rows)** | **991,799.37 samples/s** | Xử lý gần 1 triệu giao dịch/giây trên CPU |

---

## 3. Đánh giá Tài nguyên Hệ thống (Resource Monitoring)

Theo số liệu ghi nhận từ các công cụ giám sát trên VM (`top`, `free -h`, `ip -s link`):
- **CPU Utilization:** Mức tải CPU trung bình sau khi chạy là `0.2% us, 0.2% sy`, máy hoạt động ổn định và giải phóng tài nguyên CPU ngay sau khi train.
- **RAM Utilization:** Tổng RAM `3.8 GiB`, mức sử dụng khi chạy và lưu trữ dữ liệu chỉ khoảng `499 MiB` (chiếm ~13% RAM), còn trống `2.3 GiB free` và `3.3 GiB available`.
- **Network Traffic:** Lưu lượng mạng qua interface `ens4` nhận về `~255 MB` (chủ yếu là tải dataset Kaggle và các package pip), gửi đi `~9.9 MB`.

---

## 4. Nhận xét & Kết luận (Deliverable 6)

1. **Hiệu năng của LightGBM trên CPU Node:**
   - Thuật toán LightGBM thể hiện ưu thế vượt trội về tốc độ huấn luyện (`1.33s`) và nạp dữ liệu (`1.96s`) trên cấu hình CPU phổ thông (`e2-medium` 2 vCPU / 4GB RAM) mà không cần chi phí đắt đỏ cho phần cứng GPU.
2. **Khả năng ứng dụng thực tế:**
   - Với độ trễ dự đoán đơn lẻ chỉ **`0.85 ms`** và thông lượng **`~991,800 samples/s`**, hệ thống hoàn toàn đáp ứng các tiêu chuẩn khắt khe về thời gian phản hồi trong các hệ thống phòng chống gian lận thẻ tín dụng thời gian thực.
3. **Mô hình kiến trúc hạ tầng Cloud:**
   - Kiến trúc Private Subnet kết hợp Cloud NAT và Identity-Aware Proxy (IAP) đảm bảo máy ảo Compute Node không lộ Public IP ra ngoài Internet, ngăn ngừa tối đa nguy cơ tấn công từ bên ngoài mà vẫn đảm bảo khả năng quản trị và tải dữ liệu an toàn.

---

## 5. Danh mục Minh chứng (Evidence Files)
- `evidence/1_Benchmark.py.png`: Ảnh chụp màn hình kết quả chạy script `python3 benchmark.py`.
- `evidence/3_Resource.png`: Ảnh chụp màn hình giám sát tài nguyên CPU (`top`), RAM (`free -h`), Network (`ip -s link`).
- `evidence/benchmark_result.json`: File JSON chứa toàn bộ số liệu đo lường.
- `benchmark.py`: Mã nguồn script benchmark hoàn chỉnh.
