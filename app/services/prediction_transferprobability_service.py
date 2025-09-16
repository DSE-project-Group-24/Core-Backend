import joblib
import pandas as pd
import numpy as np
import os
from typing import Dict, Any

# Get the directory containing this script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up two levels to reach the project root (from services/ to app/ to project root)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
# Print the paths for debugging
print(f"Current directory: {current_dir}")
print(f"Project root: {project_root}")
# Construct the absolute path to the model file
model_path = os.path.join(project_root, "Core-Backend", "trained_models", "Transfer_Probablity_model.pkl")

try:
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        print(f"Model loaded successfully from {model_path}")
    else:
        print(f"Model file not found. Searched at: {model_path}")
        # Try alternative path
        alt_model_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "trained_models", "Transfer_Probablity_model.pkl")
        if os.path.exists(alt_model_path):
            model = joblib.load(alt_model_path)
            print(f"Model loaded successfully from alternative path: {alt_model_path}")
        else:
            raise FileNotFoundError(f"Model file not found at {model_path} or {alt_model_path}")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    raise

# Rest of your code remains the same...
# Rest of your code remains the same...

# Expected columns (same as X_train during training)
expected_columns = [
    'Bystander Expenditure per day', 'Traveling Expenditure per day',
    'Family Current Status', 'Hospital Distance From Home', 'Gender',
    'Any Other Hospital Admission Expenditure', 'Ethnicity_Moor',
    'Ethnicity_Sinhalese', 'Ethnicity_Tamil', 'Person Age (as of 2023-01-01)',
    'LifeStyle_Living alone', 'LifeStyle_Living with care givers',
    'LifeStyle_Living with children', 'Alcohol_Consumption_Encoded',
    'Illicit_Drugs_Encoded', 'Severity', 'First Hospital Name_BH, Tellipalai(Type A)',
    'First Hospital Name_BH,Chavakachcheri(TypeB)', 'First Hospital Name_BH,Mallavi(TypeB)',
    'First Hospital Name_BH,Mankulam(TypeA)', 'First Hospital Name_BH,Murungan (TypeB)',
    'First Hospital Name_BH,Puthukudijiruppu(TypeB)',
    'First Hospital Name_Base Hospital (A) - Mankulam',
    'First Hospital Name_Base Hospital (A) - Point Pedro',
    'First Hospital Name_Base Hospital (A) -Tellipalai',
    'First Hospital Name_Base Hospital (B) - Chavakachcheri',
    'First Hospital Name_Base Hospital (B) - Cheddikulam',
    'First Hospital Name_Base Hospital (B) - Kayts',
    'First Hospital Name_Base Hospital (B) - Mallavi',
    'First Hospital Name_Base Hospital (B) - Mulankavil',
    'First Hospital Name_Base Hospital (B) - Murunkan',
    'First Hospital Name_Base Hospital (B) - Puthukudiyiruppu',
    'First Hospital Name_DGH – Kilinochchi', 'First Hospital Name_DGH – Mannar',
    'First Hospital Name_DGH – Mullaithivu', 'First Hospital Name_DGH – Vavuniya',
    'First Hospital Name_DGH, Mannar', 'First Hospital Name_DGH,Kilinochchi',
    'First Hospital Name_DH, Nerijakulam', 'First Hospital Name_DH, Poovarasankulam',
    'First Hospital Name_DH, Puliyankulam', 'First Hospital Name_DH, Sithamparapuram',
    'First Hospital Name_DH, Ulukulam', 'First Hospital Name_DH,Adampan',
    'First Hospital Name_DH,Akkarayankulam', 'First Hospital Name_DH,Alampil',
    'First Hospital Name_DH,Alavedddy', 'First Hospital Name_DH,Atchuveli',
    'First Hospital Name_DH,Chankanai', 'First Hospital Name_DH,Chilawaththurai',
    'First Hospital Name_DH,Delft', 'First Hospital Name_DH,Erukalampitti',
    'First Hospital Name_DH,Karainagar', 'First Hospital Name_DH,Kodikamam',
    'First Hospital Name_DH,Kokulai', 'First Hospital Name_DH,Kopay',
    'First Hospital Name_DH,Moonkilaru', 'First Hospital Name_DH,Nainativu',
    'First Hospital Name_DH,Nanattan', 'First Hospital Name_DH,Nedunkerny',
    'First Hospital Name_DH,Oddusuddan', 'First Hospital Name_DH,Palai',
    'First Hospital Name_DH,Periyapandivirichchan', 'First Hospital Name_DH,Pesalai',
    'First Hospital Name_DH,Poonakary', 'First Hospital Name_DH,Pungudutivu',
    'First Hospital Name_DH,Sampathnuwara', 'First Hospital Name_DH,Talaimannar',
    'First Hospital Name_DH,Tharmapuram', 'First Hospital Name_DH,Uruthirapuram',
    'First Hospital Name_DH,Vaddakachchi', 'First Hospital Name_DH,Vaddukoddai',
    'First Hospital Name_DH,Valvettithurai', 'First Hospital Name_DH,Vankalai',
    'First Hospital Name_DH,Velanai', 'First Hospital Name_DH,Veravil',
    'First Hospital Name_DH,Vidathaltivu', 'First Hospital Name_PMCU, Bogeswewa',
    'First Hospital Name_PMCU, Omanthai', 'First Hospital Name_PMCU, Tharapuram',
    'First Hospital Name_PMCU, Velankulam', 'First Hospital Name_Teaching hospital - Jaffna (THJ)'
]

def make_prediction(input_data: dict):
    # Create a DataFrame with expected columns, filled with 0
    df = pd.DataFrame(columns=expected_columns, data=[[0] * len(expected_columns)])

    # Update DataFrame with input values
    for key, value in input_data.items():
        if key in expected_columns:
            df[key] = value if not pd.isna(value) else np.nan

    # Keep correct order + type
    df = df[expected_columns].astype(float, errors="ignore")

    # Replace NaNs
    df.fillna(-1, inplace=True)

    # Predict
    prediction = int(model.predict(df)[0])
    probabilities = model.predict_proba(df)[0]
    transfer_probability = float(probabilities[1])

    return {
        "prediction": prediction,
        "transfer_probability": transfer_probability
    }
