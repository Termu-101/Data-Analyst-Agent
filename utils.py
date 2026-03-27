import pandas as pd
import io


# Load a  CSV file and return the dataframe + any error message
# The return is (dataFrame, error message), If error message is empty, load successfull

def load_csv(file_path: str) -> tuple[pd.DataFrame, str]:
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return None, "The CSV file is empty."
        return df, ""
    except Exception as e:
        return None, f"Could not read file: {str(e)}"



# Returns a compact description of the dataFrame. This is how we send data to LLM instead of sending all rows and columns

def get_dataframe_schema(df: pd.DataFrame) -> str:
    
    schema_parts = []
    schema_parts.append(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    schema_parts.append(f"\nColumn names and types:")
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        n_unique = df[col].nunique()
        n_null = df[col].isnull().sum()
        schema_parts.append(f"  - {col} ({dtype}) | {n_unique} unique values | {n_null} nulls")
    
    schema_parts.append(f"\nFirst 3 rows as sample:")
    schema_parts.append(df.head(3).to_string())
    
    return "\n".join(schema_parts)


# Formats the number where floats and ints are converted with commas

def format_value(val) -> str:
    if isinstance(val, float):
        return f"{val:,.4f}" if val < 1 else f"{val:,.2f}"
    if isinstance(val, int):
        return f"{val:,}"
    return str(val)

