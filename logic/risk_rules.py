def calculate_risk(product_info, user_profile):
    """
    Calculates a numerical risk score based on product data and a user's profile.

    Args:
        product_info (dict): A dictionary containing product details, including 'risk_label'.
        user_profile (dict): A dictionary with user's health information.
                             Expected keys: 'weight_kg', 'height_cm', 'age',
                             'liver_disease', 'consumes_alcohol'.

    Returns:
        tuple: A tuple containing the final score (int) and a list of strings
               explaining each identified risk factor.
    """
    score = 0
    risk_factors = []

    # 1. Base Score from product's risk_label
    risk_label_map = {"High": 3, "Moderate": 2, "Low": 1}
    base_score = risk_label_map.get(product_info.get("risk_label", "Low"), 1)
    score += base_score
    if base_score > 1:
        risk_factors.append(f"Base Risk ({product_info.get('risk_label', 'Low')})")

    # 2. BMI Calculation and Modifier
    weight_kg = user_profile.get("weight_kg")
    height_cm = user_profile.get("height_cm")

    if height_cm and weight_kg and height_cm > 0:
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        if bmi < 18.5:
            score += 1
            risk_factors.append("Low BMI (<18.5) may increase sensitivity.")

    # 3. Other User Profile Modifiers
    if user_profile.get("age", 0) >= 65:
        score += 1
        risk_factors.append("Age (>=65 years) increases sensitivity.")

    if user_profile.get("liver_disease", False):
        score += 2
        risk_factors.append("Existing liver conditions significantly increase risk.")

    if user_profile.get("consumes_alcohol", False):
        score += 1
        risk_factors.append("Regular alcohol use can increase liver strain.")

    return score, risk_factors

def map_score_to_level(score):
    """
    Converts a numerical score into a human-readable level and color.

    Args:
        score (int): The numerical risk score.

    Returns:
        tuple: A tuple containing the risk level (str) and a color code (str).
    """
    if score >= 5:
        return ("High", "red")
    elif score >= 3: # Covers 3 and 4
        return ("Moderate", "orange")
    else: # Covers scores less than 3
        return ("Low", "green")
