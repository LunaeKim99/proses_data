import pandas as pd
import os

def load_data(filepath: str) -> pd.DataFrame:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()
    df = df[df['Provinsi'] != 'Luar Negeri']
    return df
