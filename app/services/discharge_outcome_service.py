import pandas as pd
import numpy as np
import re
import os
import importlib
from typing import Dict, Any
from fastapi import HTTPException
from app.models.discharge_outcome import DischargeOutcomePredictionRequest

# Define the exact 25 features used in training
TOP_25_FEATURES = [
    'Current Hospital Name',
    'Family Current Status',
    'Type of injury No 1',
    'Traveling Expenditure per day',
    'First Hospital Name',
    'Date Of Birth_year',
    'Site of Injury No1',
    'Approximate Speed',
    'Incident At Time and Date_month',
    'Hospital Distance From Home',
    'Date Of Birth_month',
    'Mode of Transport to the Hospital',
    'Educational Qualification',
    'Time Taken To Reach Hospital',
    'Any Other Hospital Admission Expenditure',
    'Site of injury No 2',
    'Occupation',
    'Date Of Birth_day',
    'Family Monthly Income Before Accident',
    'Collision With ',
    'Incident At Time and Date_day',
    'Life Style',
    'Collision Force From',
    'Road Type',
    'Type of Injury No 2'
]

# Define class labels (from your training output)
CLASS_LABELS = ['Complete Recovery', 'Further Interventions', 'Partial Recovery']

# Model path
MODEL_PATH = os.path.join("trained_models", "catboost_top25_model.cbm")

class DischargeOutcomePredictor:
    """Singleton class for handling discharge outcome predictions"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DischargeOutcomePredictor, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance
    
    def _load_model(self):
        """Load the CatBoost model"""
        try:
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Model file {MODEL_PATH} not found")
            
            # Import CatBoost lazily to avoid import-time errors when the package isn't installed
            try:
                catboost = importlib.import_module("catboost")
                CatBoostClassifier = getattr(catboost, "CatBoostClassifier", None)
                if CatBoostClassifier is None:
                    raise ImportError("catboost.CatBoostClassifier not found")
            except ImportError as ie:
                print(f"❌ CatBoost not available: {ie}")
                self._model = None
                return
            
            self._model = CatBoostClassifier()
            self._model.load_model(MODEL_PATH)
            print(f"✅ CatBoost discharge outcome model loaded successfully from {MODEL_PATH}")
            
        except Exception as e:
            print(f"❌ Failed to load CatBoost model: {str(e)}")
            self._model = None
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        return {
            "features": TOP_25_FEATURES,
            "total_features": len(TOP_25_FEATURES),
            "classes": CLASS_LABELS,
            "model_type": "CatBoost Classifier",
            "description": "Trained model for predicting patient discharge outcomes using top 25 features"
        }
    
    def predict(self, request_data: DischargeOutcomePredictionRequest) -> Dict[str, Any]:
        """Make prediction using the loaded model"""
        if not self.is_loaded:
            raise HTTPException(status_code=500, detail="Model not loaded. Please check server logs.")
        
        try:
            # Convert request to dictionary and preprocess
            input_data = request_data.model_dump(exclude_none=False)
            processed_df = self._preprocess_input_data(input_data)
            
            # Make prediction
            prediction_proba = self._model.predict_proba(processed_df)[0]
            prediction_class_idx = np.argmax(prediction_proba)
            prediction_class = CLASS_LABELS[prediction_class_idx]
            
            # Create probability dictionary
            probabilities = {
                class_name: float(prob) 
                for class_name, prob in zip(CLASS_LABELS, prediction_proba)
            }
            
            # Get processed features for transparency
            processed_features = processed_df.iloc[0].to_dict()
            
            return {
                "prediction": prediction_class,
                "prediction_probabilities": probabilities,
                "preprocessed_features": processed_features,
                "model_info": {
                    "model_type": "CatBoost Classifier",
                    "features_used": len(TOP_25_FEATURES),
                    "classes": CLASS_LABELS
                }
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
    
    def _preprocess_input_data(self, data: dict) -> pd.DataFrame:
        """Preprocess input data to match the training pipeline"""
        # Create DataFrame from input
        df = pd.DataFrame([data])
        
        # Map input fields to actual column names
        column_mapping = {
            'current_hospital_name': 'Current Hospital Name',
            'family_current_status': 'Family Current Status',
            'type_of_injury_no_1': 'Type of injury No 1',
            'traveling_expenditure_per_day': 'Traveling Expenditure per day',
            'first_hospital_name': 'First Hospital Name',
            'date_of_birth': 'Date Of Birth',
            'site_of_injury_no1': 'Site of Injury No1',
            'approximate_speed': 'Approximate Speed',
            'incident_at_time_and_date': 'Incident At Time and Date',
            'hospital_distance_from_home': 'Hospital Distance From Home',
            'mode_of_transport_to_the_hospital': 'Mode of Transport to the Hospital',
            'educational_qualification': 'Educational Qualification',
            'time_taken_to_reach_hospital': 'Time Taken To Reach Hospital',
            'any_other_hospital_admission_expenditure': 'Any Other Hospital Admission Expenditure',
            'site_of_injury_no_2': 'Site of injury No 2',
            'occupation': 'Occupation',
            'family_monthly_income_before_accident': 'Family Monthly Income Before Accident',
            'collision_with': 'Collision With ',
            'life_style': 'Life Style',
            'collision_force_from': 'Collision Force From',
            'road_type': 'Road Type',
            'type_of_injury_no_2': 'Type of Injury No 2'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Apply standardization to injury and site columns
        df = self._preprocess_side_columns(df)
        
        for site_col in ['Site of Injury No1', 'Site of injury No 2']:
            if site_col in df.columns:
                df[site_col] = df[site_col].apply(self._standardize_site)
        
        for type_col in ['Type of injury No 1', 'Type of Injury No 2']:
            if type_col in df.columns:
                df[type_col] = df[type_col].apply(self._standardize_injury_type)
        
        # Handle date features
        for col in ['Date Of Birth', 'Incident At Time and Date']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                df[f'{col}_year'] = df[col].dt.year
                df[f'{col}_month'] = df[col].dt.month
                df[f'{col}_day'] = df[col].dt.day
        
        # Drop original date columns
        df.drop(['Date Of Birth', 'Incident At Time and Date'], axis=1, inplace=True, errors='ignore')
        
        # Fill NaNs with -999 (as done in training)
        df = df.fillna(-999)
        
        # Ensure all required features are present
        for feature in TOP_25_FEATURES:
            if feature not in df.columns:
                df[feature] = -999
        
        # Select only the top 25 features in the correct order
        df_selected = df[TOP_25_FEATURES]
        
        return df_selected
    
    def _normalize_text(self, x):
        """Normalize text input"""
        if pd.isna(x):
            return np.nan
        s = str(x).strip()
        s = re.sub(r'\s+', ' ', s)
        return s.lower()
    
    def _standardize_site(self, raw):
        """Standardize injury site"""
        if pd.isna(raw):
            return np.nan
        s = re.sub(r'[\(\),]', ' ', str(raw))
        s = re.sub(r'[^a-z0-9\s-]', ' ', s).lower().strip()
        if s in ('no injury found', 'no secondary injury found', 'missing data'):
            return 'no_injury'
        if any(k in s for k in ['head', 'face', 'forehead', 'eye']): return 'head_face'
        if any(k in s for k in ['neck', 'cervical']): return 'neck'
        if any(k in s for k in ['shoulder', 'clavicle', 'humerus']): return 'shoulder'
        if any(k in s for k in ['thoracic', 'chest']): return 'chest'
        if 'abdomen' in s: return 'abdomen'
        if any(k in s for k in ['spine', 'lumbar', 'sacrum']): return 'spine'
        if 'pelvis' in s: return 'pelvis'
        if 'knee' in s: return 'knee'
        if any(k in s for k in ['thigh', 'femur']): return 'thigh'
        if 'tibia' in s and 'fibula' in s: return 'leg_tibia_fibula'
        if 'tibia' in s: return 'leg_tibia'
        if 'fibula' in s: return 'leg_fibula'
        if any(k in s for k in ['hand', 'finger', 'carpal']): return 'hand'
        if any(k in s for k in ['foot', 'toe']): return 'foot'
        return s.replace(' ', '_')
    
    def _standardize_injury_type(self, raw):
        """Standardize injury type"""
        if pd.isna(raw):
            return np.nan
        s = re.sub(r'\s+', ' ', str(raw).lower().strip())
        if 'fract' in s: return 'fracture'
        if 'amput' in s: return 'amputation'
        if 'ligament' in s: return 'ligament_injury'
        if 'lacer' in s: return 'laceration'
        if 'abr' in s: return 'abrasion'
        if 'contus' in s: return 'contusion'
        if 'nerve' in s: return 'nerve_lesion'
        if 'disloc' in s: return 'dislocation'
        if 'spinal' in s: return 'spinal_injury'
        return s.replace(' ', '_')
    
    def _preprocess_side_columns(self, df):
        """Preprocess side columns"""
        for col in ['Side', 'Side.1']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.lower()
                df[col] = df[col].replace({'nan': np.nan, 'none': np.nan, '': np.nan})
        return df

# Create global predictor instance
discharge_outcome_predictor = DischargeOutcomePredictor()

# Service functions
def predict_discharge_outcome_service(request: DischargeOutcomePredictionRequest) -> Dict[str, Any]:
    """Service function for predicting discharge outcome"""
    return discharge_outcome_predictor.predict(request)

def get_discharge_outcome_model_info_service() -> Dict[str, Any]:
    """Service function for getting model information"""
    return discharge_outcome_predictor.get_model_info()

def get_discharge_outcome_model_health_service() -> Dict[str, Any]:
    """Service function for model health check"""
    return {
        "status": "healthy" if discharge_outcome_predictor.is_loaded else "unhealthy",
        "model_loaded": discharge_outcome_predictor.is_loaded,
        "model_path": MODEL_PATH,
        "features_count": len(TOP_25_FEATURES),
        "classes_count": len(CLASS_LABELS)
    }