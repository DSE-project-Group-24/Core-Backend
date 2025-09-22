from fastapi import APIRouter, HTTPException
import h2o
import pandas as pd
from h2o.frame import H2OFrame
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


h2o.init()

# Load model once
# Load model once with logging
try:
    best_model = h2o.load_model("./trained_models/StackedEnsemble_AllModels_1_AutoML_1_20250922_153204")
    if best_model:
        logger.info(f"✅ Model loaded successfully: {best_model.algo} (ID: {best_model.model_id})")
    else:
        logger.error("❌ Model loading returned None.")
except Exception as e:
    logger.error(f"❌ Failed to load model: {str(e)}")
    best_model = None

# These dtypes are from your training
train_types = {
    'Time of Collision': 'enum',
    'Discharge Outcome': 'enum',
    'Facilities for Daily Activity': 'enum',
    'Access To Wash Room': 'enum',
    'Type of Toilet Modification': 'enum',
    'Bystander Expenditure per day': 'enum',
    'Traveling Expenditure per day': 'enum',
    'Total Traveling Expenditure For Whole Hospital Stay': 'enum',
    'Family Monthly Income Before Accident': 'enum',
    'Family Monthly Income After Accident': 'enum',
    'Family Current Status': 'enum',
    'Hospital Distance From Home': 'enum',
    'Any Insurance Claim Type': 'enum',
    'Any Other Hospital Admission Expenditure': 'enum',
    'Ethnicity': 'enum',
    'Age': 'enum',
    'Gender': 'enum',
    'Life Style': 'enum',
    'Educational Qualification': 'enum',
    'Occupation': 'enum',
    'Employment Type Name': 'enum',
    'Dress Name': 'enum',
    'Mode Of Travel During Accident': 'enum',
    'Collision With ': 'enum',
    'Vehicle Insured': 'enum',
    'Vehicle Insurance Type': 'enum',
    'Category of Road': 'enum',
    'Incident At Time and Date': 'time',  # important one
    'Collision Force From': 'enum',
    'Visiblity': 'enum',
    'Road Condition': 'enum',
    'Road Type': 'enum',
    'Road Signals Exist': 'enum',
    'Approximate Speed': 'enum',
    'Alcohol Consumption': 'enum',
    'Time between Alcohol Consumption and Accident': 'enum',
    'Illicit Drugs': 'enum',
    'Vehicle Type': 'enum',
    'Helmet Worn': 'enum',
    'Engine Capacity': 'enum',
    'Passenger Type': 'enum',
    'Mode of Transport to the Hospital': 'enum',
    'Time Taken To Reach Hospital': 'enum',
    'First Aid Given At Seen': 'enum',
    'Current Hospital Name': 'enum',
    'First Hospital Name': 'enum',
    'Transfer To Next Hospital': 'enum',
    'Treatment During Tranfer': 'enum',
    'State of Transfer': 'enum',
    'Transport Time To Second Hospital': 'enum',
    'Site of Injury No1': 'enum',
    'Type of injury No 1': 'enum',
    'Side': 'enum',
    'Site of injury No 2': 'enum',
    'Type of Injury No 2': 'enum',
    'Side.1': 'enum',
    'Other Injury': 'enum',
    'Investigation Done': 'enum',
    'Management Done At First Hospital': 'enum',
    'Management Name 1': 'enum',
    'Management Name 2': 'enum',
    'Number of Wards Stayed': 'int',
    'Reason for stay in first ward': 'enum',
    'Reason for stay in Second ward': 'enum',
    'Reason for stay in Third ward': 'enum',
    'Total_Days_Stay': 'int'
}


@router.post("/predict")
async def predict(data: dict):
    try:
        logger.info("=== Starting Hospital Stay Prediction ===")
        # logger.info(f"Received input data keys: {list(data.keys())}")
        # logger.info(f"Input data values: {data}")
        
        # Convert incoming JSON to DataFrame
        df = pd.DataFrame([data])
        # logger.info(f"Initial DataFrame columns: {list(df.columns)}")
        # logger.info(f"Initial DataFrame shape: {df.shape}")

        # Track missing and present columns
        missing_columns = []
        present_columns = []
        type_conversions = []

        # Ensure types match training
        for col, dtype in train_types.items():
            if col not in df.columns:
                df[col] = None  # fill missing with None
                missing_columns.append(col)
            else:
                present_columns.append(col)

            original_value = df[col].iloc[0] if col in df.columns else None
            
            if dtype == "enum":
                df[col] = df[col].astype("category")
                type_conversions.append(f"{col}: {original_value} -> category")
            elif dtype == "int":
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                type_conversions.append(f"{col}: {original_value} -> Int64")
            elif dtype == "time":
                df[col] = pd.to_datetime(df[col], errors="coerce")
                type_conversions.append(f"{col}: {original_value} -> datetime")

        # Log debugging information
        logger.info(f"Missing columns filled with None ({len(missing_columns)}): {missing_columns[:10]}...")  # Show first 10
        # logger.info(f"Present columns from input ({len(present_columns)}): {present_columns}")
        # logger.info(f"Total expected columns: {len(train_types)}")
        # logger.info(f"Final DataFrame columns: {list(df.columns)}")
        logger.info(f"Final DataFrame shape: {df.shape}")
        
        # Log some type conversions for debugging
        # logger.info("Sample type conversions:")
        # for conversion in type_conversions[:5]:  # Show first 5 conversions
        #     logger.info(f"  {conversion}")

        # Convert to H2OFrame
        logger.info("Converting DataFrame to H2OFrame...")
        hf = H2OFrame(df)
        logger.info(f"H2OFrame shape: {hf.shape}")
        # logger.info(f"H2OFrame column names: {hf.column_names[:10]}...")  # Show first 10 columns

        # Predict
        logger.info("Making prediction with H2O model...")
        # preds = best_model.predict(hf).as_data_frame().to_dict(orient="records")
        preds = best_model.predict(hf).as_data_frame(use_multi_thread=True).to_dict(orient="records")
        logger.info(f"Prediction result: {preds}")
        logger.info("=== Hospital Stay Prediction Completed ===")

        return {"predictions": preds}

    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=str(e))
