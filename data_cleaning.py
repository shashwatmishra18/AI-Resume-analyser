import pandas as pd

def clean_data(input_file, output_file):
    df = pd.read_csv(input_file)

    # Remove duplicates
    df = df.drop_duplicates()

    # Fill missing values
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].fillna(df[col].mode()[0])
        else:
            df[col] = df[col].fillna(df[col].median())

    # Save cleaned data
    df.to_csv(output_file, index=False)

    return df