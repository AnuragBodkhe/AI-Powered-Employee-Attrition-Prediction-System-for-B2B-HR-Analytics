import pandas as pd, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
for fname in ['data/employee_attrition_dataset.csv', 'data/employee_attrition_dataset_10000.csv']:
    try:
        df = pd.read_csv(fname)
        print(f"\n=== {fname} ===")
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Dtypes:\n{df.dtypes.to_string()}")
        print(f"Head:\n{df.head(2).to_string()}")
    except Exception as e:
        print(f"Error reading {fname}: {e}")
