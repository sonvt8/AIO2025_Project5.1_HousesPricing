"""Streamlit UI for House Price Prediction API - Simplified version."""

import os
import socket
import requests
import streamlit as st

# Friendly label mappings for categorical features
NEIGHBORHOOD_OPTIONS = {
    "Bắc Ames (NAmes)": "NAmes",
    "College Creek (CollgCr)": "CollgCr",
    "Old Town (OldTown)": "OldTown",
    "Edwards (Edwards)": "Edwards",
}

MSZONING_OPTIONS = {
    "Nhà ở mật độ thấp (RL)": "RL",
    "Nhà ở mật độ trung bình (RM)": "RM",
    "Khu làng nổi/ngoại lệ (FV)": "FV",
}

QUALITY_SIMPLE = {
    "Xuất sắc (Ex)": "Ex",
    "Tốt (Gd)": "Gd",
    "Trung bình (TA)": "TA",
}

HOUSE_STYLE_OPTIONS = {
    "1 tầng (1Story)": "1Story",
    "2 tầng (2Story)": "2Story",
    "1.5 tầng hoàn thiện (1.5Fin)": "1.5Fin",
    "1.5 tầng chưa hoàn thiện (1.5Unf)": "1.5Unf",
    "2.5 tầng hoàn thiện (2.5Fin)": "2.5Fin",
    "2.5 tầng chưa hoàn thiện (2.5Unf)": "2.5Unf",
    "Gác lửng cầu thang (SFoyer)": "SFoyer",
    "Bán hầm/bán tầng (SLvl)": "SLvl",
}

# Page configuration
st.set_page_config(
    page_title="Dự đoán giá nhà",
    page_icon="🏠",
    layout="wide",
)

# Initialize session state
if "prediction" not in st.session_state:
    st.session_state.prediction = None

API_URL = os.getenv("API_URL", "http://localhost:8000")

# Styles
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-title { font-size: 32px; font-weight: 800; margin: 0; }
    .main-subtitle { font-size: 14px; margin: 8px 0 0; opacity: 0.9; }
    .prediction-box {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2px solid #e5e7eb;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .prediction-label {
        font-size: 14px;
        color: #6b7280;
        margin: 0 0 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .prediction-value {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def call_api(features):
    """Call the prediction API."""
    try:
        response = requests.post(f"{API_URL}/predict", json=features, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


def apply_preset():
    preset = st.session_state.get("preset", "")
    if not preset:
        return
    if preset == "Nhà gia đình 1 tầng, khu RL":
        st.session_state["neighborhood"] = "Bắc Ames (NAmes)"
        st.session_state["ms_zoning"] = "Nhà ở mật độ thấp (RL)"
        st.session_state["gr_liv_area"] = 1500
        st.session_state["first_flr"] = 1200
        st.session_state["second_flr"] = 0
        st.session_state["bedrooms"] = 3
        st.session_state["full_bath"] = 2
        st.session_state["half_bath"] = 1
        st.session_state["total_bsmt"] = 800
        st.session_state["house_style"] = "1 tầng (1Story)"
        st.session_state["year_built"] = 2005
        st.session_state["yr_sold"] = 2010
    elif preset == "Nhà 2 tầng, trung tâm RM":
        st.session_state["neighborhood"] = "College Creek (CollgCr)"
        st.session_state["ms_zoning"] = "Nhà ở mật độ trung bình (RM)"
        st.session_state["gr_liv_area"] = 2000
        st.session_state["first_flr"] = 1000
        st.session_state["second_flr"] = 900
        st.session_state["bedrooms"] = 4
        st.session_state["full_bath"] = 2
        st.session_state["half_bath"] = 1
        st.session_state["total_bsmt"] = 900
        st.session_state["house_style"] = "2 tầng (2Story)"
        st.session_state["year_built"] = 2012
        st.session_state["yr_sold"] = 2014
    elif preset == "Nhà nhỏ OldTown":
        st.session_state["neighborhood"] = "Old Town (OldTown)"
        st.session_state["ms_zoning"] = "Nhà ở mật độ thấp (RL)"
        st.session_state["gr_liv_area"] = 900
        st.session_state["first_flr"] = 800
        st.session_state["second_flr"] = 0
        st.session_state["bedrooms"] = 2
        st.session_state["full_bath"] = 1
        st.session_state["half_bath"] = 0
        st.session_state["total_bsmt"] = 600
        st.session_state["house_style"] = "1 tầng (1Story)"
        st.session_state["year_built"] = 1950
        st.session_state["yr_sold"] = 2008


# Main UI
st.markdown(
    """
    <div class="main-header">
        <h1 class="main-title">🏠 Dự đoán giá nhà</h1>
        <p class="main-subtitle">Máy học dự đoán giá theo đặc trưng bạn nhập • Tất cả trường là tùy chọn</p>
    </div>
""",
    unsafe_allow_html=True,
)

col_left, col_right = st.columns([1.2, 1], gap="large")

with col_left:
    st.markdown("### 📝 Thông tin căn nhà")
    features = {}

    # -------- Quick presets (auto-fill widgets) --------
    st.markdown("#### 🎯 Gợi ý nhanh")
    st.selectbox(
        "Chọn mẫu tham khảo",
        [
            "",
            "Nhà gia đình 1 tầng, khu RL",
            "Nhà 2 tầng, trung tâm RM",
            "Nhà nhỏ OldTown",
        ],
        key="preset",
        on_change=apply_preset,
        help="Tự động điền các trường bên dưới để thao tác nhanh",
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🏢 Cơ bản", "🏛️ Cấu trúc & Bố cục", "🚗 Gara", "🎨 Chất lượng"]
    )

    with tab1:
        st.markdown("**Khu vực & Diện tích**")
        col1, col2 = st.columns(2)
        with col1:
            neighborhood_label = st.selectbox(
                "Khu phố (Neighborhood)",
                [""] + list(NEIGHBORHOOD_OPTIONS.keys()),
                index=0,
                key="neighborhood",
                help="Vị trí khu phố theo tập dữ liệu Ames",
            )
            if neighborhood_label:
                features["Neighborhood"] = NEIGHBORHOOD_OPTIONS[neighborhood_label]
            lot_area = st.number_input(
                "Diện tích lô đất (ft²)",
                min_value=0,
                value=0,
                step=100,
                help="Tổng diện tích lô đất",
            )
            if lot_area > 0:
                features["LotArea"] = int(lot_area)

        with col2:
            ms_zoning_label = st.selectbox(
                "Phân vùng quy hoạch (MS Zoning)",
                [""] + list(MSZONING_OPTIONS.keys()),
                index=0,
                key="ms_zoning",
                help="Loại phân vùng quy hoạch sử dụng đất",
            )
            if ms_zoning_label:
                features["MSZoning"] = MSZONING_OPTIONS[ms_zoning_label]
            lot_frontage = st.number_input(
                "Mặt tiền lô đất (ft)",
                min_value=0,
                value=0,
                step=1,
                help="Chiều dài tiếp giáp đường",
            )
            if lot_frontage > 0:
                features["LotFrontage"] = float(lot_frontage)

    with tab2:
        st.markdown("**Cấu trúc & Bố cục**")
        # Above-grade living area
        gr_liv_area = st.number_input(
            "Diện tích sử dụng trên mặt đất (ft²)",
            min_value=0,
            value=0,
            step=50,
            help="Diện tích ở có thể sử dụng nằm trên mặt đất",
            key="gr_liv_area",
        )
        if gr_liv_area > 0:
            features["GrLivArea"] = int(gr_liv_area)

        col1, col2 = st.columns(2)
        with col1:
            first_flr = st.number_input(
                "Diện tích tầng 1 (ft²)",
                min_value=0,
                value=0,
                step=50,
                help="Diện tích sàn đã hoàn thiện của tầng 1",
                key="first_flr",
            )
            if first_flr > 0:
                features["1stFlrSF"] = int(first_flr)

            bedrooms = st.number_input(
                "Số phòng ngủ (trên mặt đất)",
                min_value=0,
                value=0,
                step=1,
                format="%d",
                help="Số phòng ngủ nằm trên mặt đất",
                key="bedrooms",
            )
            if bedrooms > 0:
                features["BedroomAbvGr"] = int(bedrooms)

            full_bath = st.number_input(
                "Phòng tắm đầy đủ (trên mặt đất)",
                min_value=0,
                value=0,
                step=1,
                format="%d",
                help="Phòng tắm có đủ bồn/tắm đứng, bồn rửa, bồn cầu",
                key="full_bath",
            )
            if full_bath > 0:
                features["FullBath"] = int(full_bath)

        with col2:
            second_flr = st.number_input(
                "Diện tích tầng 2 (ft²)",
                min_value=0,
                value=0,
                step=50,
                help="Diện tích sàn đã hoàn thiện của tầng 2",
                key="second_flr",
            )
            if second_flr > 0:
                features["2ndFlrSF"] = int(second_flr)

            half_bath = st.number_input(
                "Phòng tắm 1/2 (trên mặt đất)",
                min_value=0,
                value=0,
                step=1,
                format="%d",
                help="Phòng tắm không có bồn/tắm đứng (chỉ bồn rửa + bồn cầu)",
                key="half_bath",
            )
            if half_bath > 0:
                features["HalfBath"] = int(half_bath)

        # Advanced options in Structure
        with st.expander("Tùy chọn nâng cao (Cấu trúc)"):
            total_bsmt = st.number_input(
                "Tổng diện tích tầng hầm (ft²)",
                min_value=0,
                value=0,
                step=50,
                help="Tổng diện tích tầng hầm (bao gồm phần hoàn thiện và chưa hoàn thiện)",
                key="total_bsmt",
            )
            if total_bsmt > 0:
                features["TotalBsmtSF"] = int(total_bsmt)

        # House style
        house_style_label = st.selectbox(
            "Kiểu nhà",
            [""] + list(HOUSE_STYLE_OPTIONS.keys()),
            index=0,
            help="Kiểu kiến trúc/thiết kế tổng thể của căn nhà",
            key="house_style",
        )
        if house_style_label:
            features["HouseStyle"] = HOUSE_STYLE_OPTIONS[house_style_label]

    with tab3:
        st.markdown("**Gara & Tầng hầm**")
        garage_cars = st.number_input(
            "Số chỗ đậu xe trong gara",
            min_value=0,
            value=0,
            step=1,
            format="%d",
            help="Sức chứa theo số xe ô tô",
        )
        if garage_cars > 0:
            features["GarageCars"] = int(garage_cars)
        garage_area = st.number_input(
            "Diện tích gara (ft²)",
            min_value=0,
            value=0,
            step=20,
            help="Tổng diện tích sàn của gara",
        )
        if garage_area > 0:
            features["GarageArea"] = float(garage_area)

    with tab4:
        st.markdown("**Chất lượng & Tình trạng**")
        col1, col2 = st.columns(2)

        with col1:
            overall_qual = st.selectbox(
                "Chất lượng tổng thể",
                ["", "10", "9", "8", "7", "6", "5"],
                index=0,
                help="Chất lượng vật liệu và mức độ hoàn thiện",
            )
            if overall_qual:
                features["OverallQual"] = int(overall_qual)
            kitchen_qual_label = st.selectbox(
                "Chất lượng bếp",
                [""] + list(QUALITY_SIMPLE.keys()),
                index=0,
                help="Đánh giá chất lượng khu bếp",
                key="kitchen_qual",
            )
            if kitchen_qual_label:
                features["KitchenQual"] = QUALITY_SIMPLE[kitchen_qual_label]

        with col2:
            overall_cond = st.selectbox(
                "Tình trạng tổng thể",
                ["", "10", "9", "8", "7", "6", "5"],
                index=0,
                help="Đánh giá tình trạng hiện tại của căn nhà",
            )
            if overall_cond:
                features["OverallCond"] = int(overall_cond)
            exter_qual_label = st.selectbox(
                "Chất lượng ngoại thất",
                [""] + list(QUALITY_SIMPLE.keys()),
                index=0,
                help="Chất lượng vật liệu và hoàn thiện bên ngoài",
                key="exter_qual",
            )
            if exter_qual_label:
                features["ExterQual"] = QUALITY_SIMPLE[exter_qual_label]

        year_built = st.number_input(
            "Năm xây dựng",
            min_value=1800,
            max_value=2025,
            value=2000,
            step=1,
            help="Năm hoàn thành xây dựng ban đầu",
            key="year_built",
        )
        features["YearBuilt"] = int(year_built)

        yr_sold = st.number_input(
            "Năm bán",
            min_value=2000,
            max_value=2025,
            value=2024,
            step=1,
            help="Năm giao dịch bán diễn ra",
            key="yr_sold",
        )
        features["YrSold"] = int(yr_sold)

    st.markdown("---")
    # (đã bỏ block gợi ý nhanh thứ hai để tránh trùng lặp)

    predict_btn = st.button("🚀 Dự đoán giá", type="primary", use_container_width=True)

with col_right:
    st.markdown("### 💰 Kết quả dự đoán")

    if predict_btn:
        if not features:
            st.warning("⚠️ Vui lòng nhập ít nhất một đặc trưng.")
        else:
            with st.spinner("🤔 Đang tính toán..."):
                result = call_api(features)
                if result:
                    st.session_state.prediction = result
                    st.rerun()

    if st.session_state.prediction:
        pred = st.session_state.prediction
        price = pred.get("predicted_price", 0)

        st.markdown(
            f"""
            <div class="prediction-box">
                <p class="prediction-label">Giá dự đoán</p>
                <p class="prediction-value">${price:,.0f}</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

        if "confidence_interval" in pred:
            ci = pred["confidence_interval"]
            st.markdown("#### 📈 Khoảng giá")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Thấp", f"${ci.get('lower', price*0.9):,.0f}")
            with col_b:
                st.metric("Cao", f"${ci.get('upper', price*1.1):,.0f}")

        if st.button("🔄 Dự đoán căn khác", use_container_width=True):
            st.session_state.prediction = None
            st.rerun()
    else:
        st.markdown(
            """
            <div style="display: flex; height: 400px; align-items: center; justify-content: center;
                        text-align: center; color: #6b7280;">
                <div>
                    <p style="font-size: 24px; margin: 0;">👈 Nhập thông tin căn nhà</p>
                    <p style="font-size: 14px;">Điền form để nhận kết quả dự đoán</p>
                </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="text-align: center; color: #9ca3af; margin-top: 20px;">
        <p><strong>🏠 Dự đoán giá nhà v1.0.0</strong></p>
        <p style="font-size: 12px;">Máy chủ: {socket.gethostname()} | API: {API_URL}</p>
    </div>
""",
    unsafe_allow_html=True,
)

if __name__ == "__main__":
    pass
