# Frontend Design - House Price Predictor

## 🎯 Thiết Kế Giao Diện

### Nguyên Tắc Thiết Kế

1. **Đơn giản & Trực quan**: Không làm người dùng bối rối với quá nhiều fields
2. **All Fields Optional**: Tất cả fields đều optional - API sẽ impute các giá trị thiếu
3. **Tổ chức theo nhóm**: Chia inputs thành các tabs theo chủ đề
4. **Progressive Disclosure**: Basic info trước, advanced features trong expander

## 📋 Cấu Trúc Giao Diện

### Tab 1: Basic (Cơ bản)
Các thông tin quan trọng nhất cho prediction:
- **Neighborhood**: Khu vực (quan trọng nhất cho model)
- **MS Zoning**: Phân loại zoning
- **Lot Area**: Diện tích lô đất
- **Lot Frontage**: Mặt tiền

### Tab 2: Structure (Cấu trúc)
Các thông tin về cấu trúc nhà (đã đơn giản hóa, thân thiện, kèm mô tả):
- **Above‑ground Living Area (sq ft)**: Diện tích ở trên mặt đất (GrLivArea)
- **1st Floor Area (sq ft)**: Diện tích tầng 1 (`1stFlrSF`)
- **2nd Floor Area (sq ft)**: Diện tích tầng 2 (`2ndFlrSF`)
- **Total Basement Area (sq ft)**: Tổng diện tích tầng hầm (hoàn thiện + chưa hoàn thiện)
- **Bedrooms (above ground)**: Số phòng ngủ trên mặt đất (`BedroomAbvGr`)
- **Full bathrooms (above ground)**: Số phòng tắm đầy đủ (`FullBath`)
- **Half bathrooms (above ground)**: Số phòng tắm 1/2 (`HalfBath`)
- **House Style**: Kiểu nhà (1Story, 2Story, 1.5Fin, ...)


### Tab 3: Garage & Basement
Thông tin về garage và basement:
- **Garage**: Cars, Area, Type
- **Basement Baths**: Full/ Half baths

### Tab 4: Quality
Chất lượng và điều kiện:
- **Overall Qual/Cond**: Xếp hạng tổng thể (1-10)
- **Kitchen Quality**: Chất lượng bếp
- **Exterior Quality**: Chất lượng ngoại thất
- **Year Built/Sold**: Năm xây/ năm bán

### Advanced Features (Expander)
Các features phụ:
- MS SubClass, Lot Shape, Land Contour
- Building Type, Foundation

## 🔄 Flow Người Dùng

```
1. User mở app → Thấy giao diện sạch sẽ với tabs
2. Chọn tab "Basic" → Điền thông tin cơ bản (Neighborhood, Lot Area, etc.)
3. (Optional) Chọn tab "Structure" → Thêm thông tin về cấu trúc
4. (Optional) Chọn tab "Quality" → Chỉ định chất lượng
5. Click "Predict" → API được gọi với tất cả features đã nhập
6. Hiển thị kết quả → Price + Confidence Interval
```

## 💡 Lợi Ích Thiết Kế Này

### 1. **Không Overwhelm Users**
- Không có 80+ fields hiển thị cùng lúc
- Chia thành tabs → người dùng chỉ thấy những gì cần thiết
- Basic info đủ để có prediction đơn giản

### 2. **Progressive Enhancement**
- User có thể chỉ nhập basic info → vẫn có prediction
- Càng nhập nhiều thông tin → prediction càng chính xác
- Advanced features trong expander → không làm rối

### 3. **Trải Nghiệm Tốt**
- Tabs giúp navigation dễ dàng
- Clear categorization (Basic, Structure, Garage, Quality)
- Visual feedback khi predict
- Error handling rõ ràng

## 🎨 UI/UX Features

### Visual Design
- **Gradient header**: Eye-catching, modern
- **Card-based layout**: Clean, organized
- **Tabs**: Easy navigation
- **Icons**: Visual guidance (🏢, 🏛️, 🚗, 🎨)

### Interactive Elements
- **Number inputs**: Với validation (min/max)
- **Selectboxes**: Danh sách có sẵn cho categorical features
- **Help tooltips**: Giải thích từng field
- **Loading spinner**: Feedback khi predict

### Results Display
- **Large prediction value**: Dễ đọc
- **Confidence interval**: Giá trị range
- **Metric cards**: Hiển thị thông tin rõ ràng

## 🔧 Technical Details

### API Contract
```python
# Request
{
    "Neighborhood": "NAmes",  # Optional
    "LotArea": 7000,         # Optional
    "GrLivArea": 1500,        # Optional
    # ... tất cả fields đều optional
}

# Response
{
    "predicted_price": 187000,
    "confidence_interval": {
        "lower": 168300,
        "upper": 205700
    }
}
```

### Error Handling
- **Connection Error**: Clear message + suggestion
- **Timeout**: Retry suggestion
- **HTTP Error**: Show error details
- **Empty Input**: Warning + tip

## 📊 Model Info Integration

Khi không có prediction, hiển thị model info:
- R² Score: Model performance
- RMSE: Error metric
- Features count: Số lượng features model sử dụng

## 🚀 Usage

### Run Frontend
```bash
cd src/frontend
streamlit run app.py
```

### Set API URL
```bash
export API_URL=http://localhost:8000
streamlit run app.py
```

## 📝 Notes

### Why This Design Works

1. **Psychological Load**: User chỉ thấy một phần fields mỗi lúc → không overwhelmed
2. **Progressive Disclosure**: Basic → Advanced → Advanced+
3. **Default Values**: Empty values → API imputes (user không cần nhập tất cả)
4. **Quick Wins**: Có thể predict chỉ với vài fields quan trọng

### Comparison với 80+ Fields Design

❌ **Bad**: Hiển thị tất cả 80+ fields
- Quá nhiều scroll
- User không biết field nào quan trọng
- Mất thời gian điền

✅ **Good**: Tabs + Progressive Disclosure
- Organized theo nhóm
- User biết field nào quan trọng (Basic tab)
- Có thể predict với minimal info
