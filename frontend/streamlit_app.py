"""Streamlit frontend for the SuperKart sales-revenue prediction service."""

import os

import pandas as pd
import requests
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:7860")
PREDICT_URL = f"{BACKEND_URL}/v1/predict"
PREDICT_BATCH_URL = f"{BACKEND_URL}/v1/predictbatch"

st.set_page_config(page_title="SuperKart Sales Predictor", page_icon="🛒")
st.title("🛒 SuperKart Sales Revenue Predictor")
st.write(
    "Predict the quarterly sales revenue of a product at a SuperKart outlet, "
    "either one product at a time or as a batch upload."
)

tab_online, tab_batch = st.tabs(["Online Prediction", "Batch Prediction"])

with tab_online:
    st.subheader("Single Prediction")
    col1, col2 = st.columns(2)

    with col1:
        product_weight = st.number_input("Product Weight", min_value=0.0, value=12.66)
        product_sugar_content = st.selectbox(
            "Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"]
        )
        product_allocated_area = st.number_input(
            "Product Allocated Area", min_value=0.0, max_value=1.0, value=0.027, format="%.3f"
        )
        product_mrp = st.number_input("Product MRP", min_value=0.0, value=117.08)
        product_id_char = st.selectbox("Product Id Prefix", ["FD", "DR", "NC"])

    with col2:
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        store_location_city_type = st.selectbox(
            "Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"]
        )
        store_type = st.selectbox(
            "Store Type",
            ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"],
        )
        store_age_years = st.number_input("Store Age (Years)", min_value=0, value=16, step=1)
        product_type_category = st.selectbox(
            "Product Type Category", ["Perishables", "Non Perishables"]
        )

    if st.button("Predict Sales", type="primary"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": store_age_years,
            "Product_Type_Category": product_type_category,
        }
        try:
            response = requests.post(PREDICT_URL, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            st.success(f"Predicted Sales Revenue: {result['Product_Store_Sales_Total']:.2f}")
        except requests.exceptions.RequestException as exc:
            st.error(f"Prediction request failed: {exc}")

with tab_batch:
    st.subheader("Batch Prediction")
    st.caption(
        "Upload a CSV with columns: Product_Weight, Product_Sugar_Content, "
        "Product_Allocated_Area, Product_MRP, Store_Size, Store_Location_City_Type, "
        "Store_Type, Product_Id_char, Store_Age_Years, Product_Type_Category"
    )
    uploaded_file = st.file_uploader("Upload batch CSV", type=["csv"])

    if uploaded_file is not None:
        st.dataframe(pd.read_csv(uploaded_file).head())
        uploaded_file.seek(0)

        if st.button("Run Batch Prediction", type="primary"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
                response = requests.post(PREDICT_BATCH_URL, files=files, timeout=30)
                response.raise_for_status()
                predictions = response.json()
                result_df = pd.DataFrame(
                    {
                        "Row": list(predictions.keys()),
                        "Predicted_Sales": list(predictions.values()),
                    }
                )
                st.dataframe(result_df)
                st.download_button(
                    "Download predictions as CSV",
                    result_df.to_csv(index=False).encode("utf-8"),
                    "superkart_predictions.csv",
                    "text/csv",
                )
            except requests.exceptions.RequestException as exc:
                st.error(f"Batch prediction request failed: {exc}")
