from decimal import Decimal
from fastapi.encoders import jsonable_encoder

def decimal_encoder(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def serialize_payload(data):
    """
    Serializes a payload for Supabase, handling special types like Decimal.
    Uses jsonable_encoder first, then converts Decimal values to float.
    """
    serialized_data = jsonable_encoder(data)
    
    # Further handle any Decimal values not caught by jsonable_encoder
    for key, value in serialized_data.items():
        if isinstance(value, Decimal):
            serialized_data[key] = float(value)
    
    return serialized_data
