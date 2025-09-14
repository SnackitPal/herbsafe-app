import streamlit as st
import json
from logic.risk_rules import calculate_risk, map_score_to_level
from logic.pubmed_util import fetch_pubmed_summary

# --- Page Setup ---
st.set_page_config(page_title="HerbSafe", layout="wide")
st.title("🌱 HerbSafe")
st.header("Herbal Product Safety Checker")
st.info("Disclaimer: This is a prototype for awareness only. Not medical advice. Always consult a physician.")

# --- Data Loading ---
@st.cache_data
def load_data():
    try:
        with open("data/brands.json", "r") as f:
            product_data = json.load(f)
        return product_data
    except FileNotFoundError:
        return None

PRODUCT_DATA = load_data()
if PRODUCT_DATA is None:
    st.error("The product database (data/brands.json) was not found.")
    st.stop()

PRODUCT_NAMES = ["--- Select a Product ---"] + list(PRODUCT_DATA.keys())


# --- Function to perform assessment and save to state ---
def perform_assessment():
    if st.session_state.selected_product != "--- Select a Product ---":
        product_info = PRODUCT_DATA[st.session_state.selected_product]
        user_profile = {
            "age": st.session_state.age,
            "weight_kg": st.session_state.weight_kg,
            "height_cm": st.session_state.height_cm,
            "liver_disease": st.session_state.liver_disease,
            "consumes_alcohol": st.session_state.consumes_alcohol,
        }
        score, risk_factors = calculate_risk(product_info, user_profile)
        level, color = map_score_to_level(score)

        # Save all results into session state
        st.session_state.results = {
            "level": level,
            "product_info": product_info,
            "risk_factors": risk_factors
        }
    else:
        st.warning("Please select a product from the dropdown menu.")
        # Clear previous results if any
        if 'results' in st.session_state:
            del st.session_state.results

# --- Input Sidebar ---
with st.sidebar:
    st.header("Enter Information")
    st.selectbox("Product Name", options=PRODUCT_NAMES, key="selected_product", help="Select the herbal product you are using.")
    st.header("Personalization (Optional)")
    st.number_input("Age", min_value=1, max_value=120, value=30, key="age")
    st.number_input("Weight (kg)", min_value=1.0, value=70.0, step=0.5, key="weight_kg")
    st.number_input("Height (cm)", min_value=50.0, value=170.0, step=0.5, key="height_cm")
    st.checkbox("Do you have a known liver condition?", key="liver_disease")
    st.checkbox("Do you regularly consume alcohol?", key="consumes_alcohol")

# --- Main Panel ---
st.subheader("For a Quick Demo")
col1, col2 = st.columns(2)
# Demo buttons now just provide guidance
with col1:
    if st.button("Test High-Risk Case (Giloy)"):
        st.info("Demo: Please select 'Zandu Giloy Tablets' from the sidebar and click 'Assess Risk'.")
with col2:
    if st.button("Test Low-Risk Case (Turmeric)"):
        st.info("Demo: Please select 'Himalaya Turmeric 95' from the sidebar and click 'Assess Risk'.")

st.divider()

# Assessment Button now uses a callback function
st.button("Assess Risk", on_click=perform_assessment, use_container_width=True)

# --- Results Display Section ---
# This part now checks session_state, not the button click
if 'results' in st.session_state:
    results = st.session_state.results
    level = results['level']
    product_info = results['product_info']
    risk_factors = results['risk_factors']
    
    st.subheader("Risk Assessment Results")
    res_col1, res_col2 = st.columns([1, 2])

    with res_col1:
        if level == "High":
            st.error(f"**Risk Level: {level}**")
        elif level == "Moderate":
            st.warning(f"**Risk Level: {level}**")
        else:
            st.success(f"**Risk Level: {level}**")

    with res_col2:
        ingredients = ", ".join(product_info.get("ingredients", ["N/A"]))
        st.write(f"**Primary Ingredient(s):** {ingredients}")
        evidence_text = product_info.get("evidence", "No evidence provided.")
        evidence_link = product_info.get("evidence_link", "")
        if evidence_link:
            st.markdown(f"**Evidence:** {evidence_text} [Read More]({evidence_link})")
        else:
            st.markdown(f"**Evidence:** {evidence_text}")

    st.divider()

    if risk_factors:
        st.subheader("Personalized Cautions")
        for factor in risk_factors:
            st.write(f"- {factor}")
    
    st.subheader("General Precautions & Alternatives")
    if level == "High":
        st.error("⚠️ ...") # Abridged for clarity
    elif level == "Moderate":
        st.warning("🟡 ...")
    else:
        st.success("✅ ...")

    st.divider()

    if level in ["High", "Moderate"]:
        primary_ingredient = product_info.get("ingredients", [])[0]
        if primary_ingredient:
            with st.spinner(f"Searching PubMed..."):
                pubmed_result = fetch_pubmed_summary(primary_ingredient)
            if pubmed_result:
                with st.expander("Live Evidence from PubMed"):
                    st.markdown(f"#### [{pubmed_result['title']}]({pubmed_result['url']})")
                    st.write(pubmed_result['snippet'])
            else:
                st.info(f"No specific liver risk studies found on PubMed...")
