import traceback
from typing import List, Dict, Any

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier

# Small subset of preprocessing functions ported from your standalone script
import re


def normalize_text(x):
    if pd.isna(x):
        return np.nan
    s = str(x).strip()
    s = re.sub(r'\s+', ' ', s)
    return s.lower()


def standardize_site(raw):
    if pd.isna(raw):
        return np.nan
    s = re.sub(r'[\(\),]', ' ', str(raw))
    s = re.sub(r'[^a-z0-9\s-]', ' ', s).lower().strip()
    if s in ('no injury found', 'no secondary injury found', 'missing data'):
        return 'no_injury'
    if any(k in s for k in ['head', 'face', 'forehead', 'eye']):
        return 'head_face'
    if any(k in s for k in ['neck', 'cervical']):
        return 'neck'
    if any(k in s for k in ['shoulder', 'clavicle', 'humerus']):
        return 'shoulder'
    if any(k in s for k in ['thoracic', 'chest']):
        return 'chest'
    if 'abdomen' in s:
        return 'abdomen'
    if any(k in s for k in ['spine', 'lumbar', 'sacrum']):
        return 'spine'
    if 'pelvis' in s:
        return 'pelvis'
    if 'knee' in s:
        return 'knee'
    if any(k in s for k in ['thigh', 'femur']):
        return 'thigh'
    if 'tibia' in s and 'fibula' in s:
        return 'leg_tibia_fibula'
    if 'tibia' in s:
        return 'leg_tibia'
    if 'fibula' in s:
        return 'leg_fibula'
    if any(k in s for k in ['hand', 'finger', 'carpal']):
        return 'hand'
    if any(k in s for k in ['foot', 'toe']):
        return 'foot'
    return s.replace(' ', '_')


def standardize_injury_type(raw):
    if pd.isna(raw):
        return np.nan
    s = re.sub(r'\s+', ' ', str(raw).lower().strip())
    if 'fract' in s:
        return 'fracture'
    if 'amput' in s:
        return 'amputation'
    if 'ligament' in s:
        return 'ligament_injury'
    if 'lacer' in s:
        return 'laceration'
    if 'abr' in s:
        return 'abrasion'
    if 'contus' in s:
        return 'contusion'
    if 'nerve' in s:
        return 'nerve_lesion'
    if 'disloc' in s:
        return 'dislocation'
    if 'spinal' in s:
        return 'spinal_injury'
    return s.replace(' ', '_')


def preprocess_side_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in ['Side', 'Side.1']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
            df[col] = df[col].replace({'nan': np.nan, 'none': np.nan, '': np.nan})
    return df


def preprocess_for_catboost(df: pd.DataFrame):
    df = df.copy()
    drop_cols = [
        "Person Id", "Full Name", "Contact Number", "Hospital Reference Number",
        "Address Street", "Facilities for Daily Activity",
        "Access To Wash Room", "Type of Toilet Modification", "Age", "Employment Type Name",
        "Dress Name", "Vehicle Insurance Type", "Vehicle Type", "State of Transfer",
        "Treatment During Tranfer", "Reason for stay in first ward",
        "Reason for stay in Second ward", "Reason for stay in Third ward",
        "Number of Wards Stayed", "Management Done At First Hospital",
        "Management Name 1", "Management Name 2", "Other Injury",
        "First Aid Given At Seen", "Total Traveling Expenditure For Whole Hospital Stay",
        "Discharge Outcome"
    ]
    df = df.drop(columns=drop_cols, errors='ignore')

    df.replace('Victim not willing to share/ Unable to respond/  Early Discharge', np.nan, inplace=True)

    df = preprocess_side_columns(df)

    for site_col in ['Site of Injury No1', 'Site of injury No 2']:
        if site_col in df.columns:
            df[site_col] = df[site_col].apply(standardize_site)
    for type_col in ['Type of injury No 1', 'Type of Injury No 2']:
        if type_col in df.columns:
            df[type_col] = df[type_col].apply(standardize_injury_type)

    # Date features
    for col in ['Date Of Birth', 'Incident At Time and Date']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[f'{col}_year'] = df[col].dt.year.fillna(-999).astype(int)
            df[f'{col}_month'] = df[col].dt.month.fillna(-999).astype(int)
            df[f'{col}_day'] = df[col].dt.day.fillna(-999).astype(int)
    df.drop(['Date Of Birth', 'Incident At Time and Date'], axis=1, inplace=True, errors='ignore')

    freq_encode_cols = [
        'Ethnicity', 'Gender', 'Life Style', 'Occupation',
        'Mode Of Travel During Accident', 'Collision With ',
        'Category of Road', 'Type of Admission', 'Severity'
    ]
    for col in freq_encode_cols:
        if col in df.columns:
            freq = df[col].value_counts(normalize=True)
            df[col + '_freq'] = df[col].map(freq).fillna(-999)

    for col in df.columns:
        if df[col].dtype == 'object' or df[col].dtype == 'category':
            df[col] = df[col].astype(str).replace('nan', '-999')

    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    return df, categorical_cols


MODEL_PATH = "trained_models/catboost_stay_classifier_v2_with_feature_15.cbm"
TOP_FEATURES = [
    'Investigation Done', 'Type of injury No 1', 'Side', 'Site of Injury No1',
    'Current Hospital Name', 'Engine Capacity', 'Severity', 'Collision Force From',
    'Side.1', 'Type of Injury No 2', 'Family Current Status', 'Time Taken To Reach Hospital',
    'Mode of Transport to the Hospital', 'Category of Road', 'Time of Collision'
]


def load_model(path: str):
    m = CatBoostClassifier()
    m.load_model(path)
    return m


try:
    model = load_model(MODEL_PATH)
    load_error = None
except Exception as e:
    model = None
    load_error = str(e) + "\n" + traceback.format_exc()


def prepare_input(df_in: pd.DataFrame) -> pd.DataFrame:
    df = df_in.copy()

    for col in ["Number of days in first ward", "Number of days in Second ward", "Number of days in Third ward"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    if any(c in df.columns for c in ["Number of days in first ward", "Number of days in Second ward", "Number of days in Third ward"]):
        df["Total days stay"] = df[[c for c in ["Number of days in first ward", "Number of days in Second ward", "Number of days in Third ward"] if c in df.columns]].sum(axis=1)

    if 'Incident At Time and Date' in df.columns:
        df['Incident At Time and Date'] = pd.to_datetime(df['Incident At Time and Date'], errors='coerce')
        df['incident_weekday'] = df['Incident At Time and Date'].dt.weekday.fillna(-1).astype(int)
        df['is_weekend'] = df['incident_weekday'].isin([5,6]).astype(int)
        try:
            df['incident_hour'] = df['Incident At Time and Date'].dt.hour.fillna(-1).astype(int)
            df['is_night'] = ((df['incident_hour'] >= 20) | (df['incident_hour'] <= 5)).astype(int)
        except Exception:
            df['incident_hour'] = -1
            df['is_night'] = 0
    else:
        df['is_weekend'] = 0
        df['is_night'] = 0
        df['incident_hour'] = -1

    def severity_score_from_injury(x):
        if pd.isna(x):
            return 0
        s = str(x)
        if 'fracture' in s:
            return 3
        if 'amputation' in s:
            return 4
        if 'spinal' in s:
            return 4
        if 'dislocation' in s:
            return 2
        if 'ligament' in s:
            return 2
        if 'laceration' in s:
            return 1
        if 'abrasion' in s:
            return 0
        return 1

    df['injury1_severity'] = df.get('Type of injury No 1', pd.Series(np.nan)).apply(severity_score_from_injury).fillna(0)
    df['injury2_severity'] = df.get('Type of Injury No 2', pd.Series(np.nan)).apply(severity_score_from_injury).fillna(0)
    df['injury_severity_sum'] = df['injury1_severity'] + df['injury2_severity']

    if 'Investigation Done' in df.columns:
        df['Investigation Done'] = df['Investigation Done'].astype(str)
        df['Investigation Done_flag'] = df['Investigation Done'].str.lower().isin(['yes','true','y','1']).astype(int)
    else:
        df['Investigation Done_flag'] = 0

    df_processed, cat_cols = preprocess_for_catboost(df)

    X = df_processed.reindex(columns=TOP_FEATURES, fill_value='-999')
    X = X.fillna('-999')
    for col in X.columns:
        try:
            X[col] = X[col].astype(str).replace({'nan': '-999', 'None': '-999'})
        except Exception:
            X[col] = X[col].where(pd.notnull(X[col]), '-999')

    return X


def predict_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Take list of dicts and return predictions in the project response format."""
    if model is None:
        raise RuntimeError(f"Model not loaded: {load_error}")
    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError("Empty data")

    X = prepare_input(df)
    X = X[TOP_FEATURES]

    preds = model.predict(X)
    proba = model.predict_proba(X)

    results = []
    classes = [str(c) for c in getattr(model, 'classes_', [])]
    for p, prob in zip(preds, proba):
        # match example: prediction looks like "['2–3 days']" -> represent as str(list)
        pred_str = str([p])
        prob_map = {cls: float(pr) for cls, pr in zip(classes, prob)} if classes else {}
        results.append({'prediction': pred_str, 'probabilities': prob_map})

    return {'predictions': results}
