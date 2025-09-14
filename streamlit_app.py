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
try:
    with open("data/brands.json", "r") as f:
        PRODUCT_DATA = json.load(f)
    PRODUCT_NAMES = ["--- Select a Product ---"] + list(PRODUCT_DATA.keys())
except FileNotFoundError:
    st.error("The product database (data/brands.json) was not found.")
    PRODUCT_DATA = {}
    PRODUCT_NAMES = ["--- Select a Product ---"]


# --- Input Sidebar ---
with st.sidebar:
    st.header("Enter Information")

    # Product Selection
    selected_product = st.selectbox(
        "Product Name",
        options=PRODUCT_NAMES,
        help="Select the herbal product you are using."
    )

    # User Profile Inputs
    st.header("Personalization (Optional)")

    age = st.number_input("Age", min_value=1, max_value=120, value=30)
    weight_kg = st.number_input("Weight (kg)", min_value=1.0, value=70.0, step=0.5)
    height_cm = st.number_input("Height (cm)", min_value=50.0, value=170.0, step=0.5)
    liver_disease = st.checkbox("Do you have a known liver condition?")
    consumes_alcohol = st.checkbox("Do you regularly consume alcohol?")

# --- Main Panel ---

# Quick Demo Buttons
st.subheader("For a Quick Demo")
col1, col2 = st.columns(2)
with col1:
    if st.button("Test High-Risk Case (Giloy)"):
        st.info("Demo: Please select 'Zandu Giloy Tablets' from the sidebar and click 'Assess Risk'.")
with col2:
    if st.button("Test Low-Risk Case (Turmeric)"):
        st.info("Demo: Please select 'Himalaya Turmeric 95' from the sidebar and click 'Assess Risk'.")

st.divider()

# Assessment Button and Results
if st.button("Assess Risk", use_container_width=True):
    if selected_product != "--- Select a Product ---":
        # A. Get Product Info
        product_info = PRODUCT_DATA[selected_product]

        # B. Create User Profile
        user_profile = {
            "age": age, "weight_kg": weight_kg, "height_cm": height_cm,
            "liver_disease": liver_disease, "consumes_alcohol": consumes_alcohol,
        }

        # C. Run Assessment
        score, risk_factors = calculate_risk(product_info, user_profile)
        level, color = map_score_to_level(score)

        # D. Display Results in a polished layout
        st.subheader("Risk Assessment Results")
        res_col1, res_col2 = st.columns([1, 2]) # Ratio of column sizes

        # Column 1: The colored metric box
        with res_col1:
            if level == "High":
                with st.error():
                    st.metric("Risk Level", level) # REMOVED label_visibility
            elif level == "Moderate":
                with st.warning():
                    st.metric("Risk Level", level) # REMOVED label_visibility
            else: # Low
                with st.success():
                    st.metric("Risk Level", level) # REMOVED label_visibility

        # Column 2: The evidence and details
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

        # E. Display Personalized Cautions
        if risk_factors:
            st.subheader("Personalized Cautions")
            for factor in risk_factors:
                st.write(f"- {factor}")
        
        # F. Add Actionable Advice
        st.subheader("General Precautions & Alternatives")
        if level == "High":
            st.error("⚠️ Action Recommended: Consider stopping this product and consulting a physician. Monitor for any symptoms of liver injury (e.g., jaundice, dark urine, abdominal pain). Avoid concurrent use of alcohol or other potentially liver-toxic substances.")
        elif level == "Moderate":
            st.warning("🟡 Caution Advised: Use this product with care, preferably under the guidance of a healthcare professional. Be aware of the potential risks and consider periodic liver function tests (LFTs) if using for an extended period.")
        else: # Low
            st.success("✅ Generally Safe: This product is considered safe for most people at standard doses. However, always discontinue use if you experience any adverse effects.")

        st.divider()

        # G. Fetch and display live PubMed evidence
        if level in ["High", "Moderate"]:
            primary_ingredient = product_info.get("ingredients", [])[0]
            if primary_ingredient:
                with st.spinner(f"Searching PubMed for live evidence on {primary_ingredient}..."):
                    pubmed_result = fetch_pubmed_summary(primary_ingredient)
                
                if pubmed_result:
                    with st.expander("Live Evidence from PubMed"):
                        st.markdown(f"#### [{pubmed_result['title']}]({pubmed_result['url']})")
                        st.write(pubmed_result['snippet'])
                        st.caption(f"Full article available at: {pubmed_result['url']}")
                else:
                    st.info(f"No specific liver risk studies found on PubMed for '{primary_ingredient}'. This does not guarantee safety.")

    else:
        st.warning("Please select a product from the dropdown menu.")
