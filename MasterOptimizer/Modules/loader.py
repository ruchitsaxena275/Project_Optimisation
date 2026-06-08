import pandas as pd

def load_data(file_path):

    nodes_df = pd.read_excel(
        file_path,
        sheet_name="Node coordinate"
    )

    masters_df = pd.read_excel(
        file_path,
        sheet_name="Master coordinates"
    )

    nodes_df.columns = (
        nodes_df.columns
        .str.strip()
        .str.lower()
    )

    masters_df.columns = (
        masters_df.columns
        .str.strip()
        .str.lower()
    )

    return nodes_df, masters_df