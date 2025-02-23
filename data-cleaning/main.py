import pandas as pd
import urllib.parse
import os
import ast
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to load and clean the dataset
def load_and_clean_dataset(file_path):
    try:
        # Load dataset
        dataset = pd.read_csv(file_path)

        def clean_text(text):
            """Safely attempts to convert a string to a list and join its elements."""
            if isinstance(text, str):
                try:
                    #Attempt to parse the string as a literal
                    parsed_data = ast.literal_eval(text)

                    #check if the parsed data is a list
                    if isinstance(parsed_data, list):
                        return ' '.join(parsed_data)
                    else:
                         logging.warning(f"String {text} parsed as a non-list type: {type(parsed_data)}. Returning original string.")
                         return text #return the original string if not a list.

                except (SyntaxError, ValueError) as e:
                    logging.error(f"Could not parse text as a literal: {text}. Error: {e}")
                    return text # return original string on error
            return text #return if not a string

        # Apply the cleaning function
        dataset['summary'] = dataset['summary'].apply(clean_text)
        dataset['content'] = dataset['content'].apply(clean_text)
        

        # Replace 'nan' or empty lists with None or an empty string
        dataset['summary'] = dataset['summary'].apply(lambda x: None if pd.isna(x) or str(x).lower() == 'nan' or str(x) == '[]' else x)
        dataset['content'] = dataset['content'].apply(lambda x: None if pd.isna(x) or str(x).lower() == 'nan' or str(x) == '[]' else x)


        # Remove leading zeros in all numeric columns
        for column in dataset.select_dtypes(include=['object']).columns:
            dataset[column] = dataset[column].apply(lambda x: str(x).lstrip('0') if isinstance(x, str) else x)

        # Function to check if the url is valid
        def is_valid_url(url):
            try:
                result = urllib.parse.urlparse(url)
                return all([result.scheme, result.netloc])
            except ValueError:
                return False

        # Apply the URL Validation
        dataset['url_valid'] = dataset['url'].apply(is_valid_url)

        # Structure the dataset
        structured_dataset = dataset[['title', 'summary', 'content', 'url', 'url_valid']]

        # Format the column names
        structured_dataset.columns = ['Title', 'Summary', 'Content', 'URL', 'Is URL Valid']

        return structured_dataset

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Get the current directory (Where the script is running)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Use the full path to the file (in the same directory as the script)
file_path = os.path.join(current_directory, 'cleaned_relationship_data.csv')  
cleaned_dataset = load_and_clean_dataset(file_path)

# Main processing function
def process_data_directory(data_directory):
    # Create the cleaned_data directory if it doesn't exist
    cleaned_data_directory = os.path.join(data_directory, 'structured_data')
    os.makedirs(cleaned_data_directory, exist_ok=True)

    # Find all files in the data directory
    all_files = glob.glob(os.path.join(data_directory, '*'))

    for file_path in all_files:
        if os.path.isfile(file_path): #make sure file is an actual file.
            logging.info(f"Processing file: {file_path}")

            structured_dataset = load_and_clean_dataset(file_path)

            if structured_dataset is not None:
                # Create the output file path in the cleaned_data directory
                file_name = os.path.basename(file_path)
                name, ext = os.path.splitext(file_name)
                output_file_name = f'structured_{name}.csv'
                output_file_path = os.path.join(cleaned_data_directory, output_file_name)

                # Save the cleaned dataset to a new CSV file
                structured_dataset.to_csv(output_file_path, index=False)
                logging.info(f"Dataset saved to {output_file_path}")
            else:
                logging.warning(f"Skipping {file_path} due to invalid data.")
        else:
            logging.info(f"Skipping {file_path} as it is not a file.")

# Get the current directory (Where the script is running)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Define the data directory
data_directory = os.path.join(current_directory, 'data')
os.makedirs(data_directory, exist_ok=True) #create if doesn't exist

# Process all files in the data directory
process_data_directory(data_directory)

print("Processing complete.")
