import re
import autopep8
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_code_from_csv(file_path, column_name):
    """Loads code from a CSV file, handling potential errors."""
    try:
        df = pd.read_csv(file_path)
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in CSV file.")
        return df[column_name].tolist(), df
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return [], None
    except pd.errors.EmptyDataError:
        logging.error(f"CSV file is empty: {file_path}")
        return [], None
    except Exception as e:
        logging.error(f"An error occurred while loading CSV: {e}")
        return [], None

def clean_code(code):
    """Cleans JavaScript code by removing comments, logs, and empty lines, then formats it."""
    try:
        # Remove console logs
        code = re.sub(r'console\.log\(.*?\);?', '', code)

        # Remove single-line comments
        code = re.sub(r'//.*', '', code)

        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

        # Remove empty lines
        code = re.sub(r'\n\s*\n', '\n', code)

        # Format code using autopep8 (alternative for prettier in Python)
        formatted_code = autopep8.fix_code(code)

        return formatted_code
    except Exception as e:
        logging.error(f"An error occurred while cleaning code: {e}")
        return code

# Save cleaned JavaScript code to a CSV file
def save_code_to_csv(file_path, df, column_name, cleaned_codes):
    try:
        if df is None:
            raise ValueError("DataFrame is None. Cannot save.")
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in DataFrame.")
        df[column_name] = cleaned_codes  # Assign the cleaned code list
        df.to_csv(file_path, index=False)
        logging.info(f"Cleaned code saved to {file_path}")
    except ValueError as ve:
        logging.error(str(ve))
    except Exception as e:
        logging.error(f"An error occurred while saving CSV: {e}")

input_csv_path = 'input.csv'
output_csv_path = 'cleaned_output.csv'
column_name = 'code' 

raw_codes, df = load_code_from_csv(input_csv_path, column_name)

if df is not None:
    cleaned_codes = [clean_code(code) for code in raw_codes]
    save_code_to_csv(output_csv_path, df, column_name, cleaned_codes)
    print('JavaScript tutorial code cleaned successfully and saved to CSV!')
else:
    print("Failed to load data.  See the logs for more detail")
