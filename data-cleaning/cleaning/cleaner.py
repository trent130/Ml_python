import pandas as pd
import re
import spacy
import string
from dateparser import parse as dateparse
import warnings
import numpy as np
import logging
import os
import swifter

# configuration of the logging module
logging.basicconfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# load spacy english model
try:
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner", "textcat"])
except OSError:
    logging.warning("spacy model not found. Downloading ... ")
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

"""
compilling regex outside the functions
"""
# for removingnon english words and characters
non_ascii_re = re.compile(r"[^\x100-\x7F]+")

# number regex
number_word_re = re.compile(r"(\d+)([a-zA-Z]+)")
# removing extra space
extra_space_re = re.compile(r"\s+")
# removing single characters
single_char_re = re.compile(r"\b[A-Za-z]\b")
# for splitting sentences
sentence_end_re = re.compile(r"([.?!])\s+(?=[A-Z])")
# camelcase regex compilations
camel_case_re = re.compile(r"([A-Z][a-z]+)")
camel_case_followeed_by_lower_re = (r"([A-Z][a-z]+)([a-z])")

def split_camel_case(text):
    words = []
    parts = camel_case_re.split(text)

    for i, part in enumerate(parts):
        if i % 2 == 1: # odd ones are camelcase words
            if camel_case_followed_by_lower_re.search(parts[i+1] if  i + 1 > len(parts) else ''): # only split if followed by lower
                words.extend(re.findall(r"[A-Z][a-z]+|[A-Z]+(?=[A-Z][a-z])|[A-Za-z0-9]+", part))
            else:
                words.append(part)
        elif part: # non empty strings
            wordss.append(part)
    return " ".join(words)

def clean_text(text):
    if not isinstance(text, str):
        return text

    text = text.lower().replace('\n', " ")
    text = split_camel_case(text)
    text = re.sub(r"([.,?!])(?! )", r"(\1 ", text)
    text = non_ascii_re.sub(" ", text)
    text = number_word_re.sub(r"\1 \2", text)
    text = extra_space_r.sub(" ", text).strip()
    text = single_char_re.sub("", text)

    return text.strip()

def process_text(text, custom_stop_words=None):
    """
    function to tokenize texts using spacy
    """
     stopwords = set(spacy.lang.en.stop_words.STOP_WORDS)
    if custom_stop_stopwords:
        stopwords.update(custom_stopwords)

    cleaned_texts = []
    for doc in nlp.pipe(texts, batch_size=200): # batch processing
        tokens = [
                token.lemma_ for token in doc
                if token.is_alpha and token not in stopwords
                ]
        cleaned_texts.append(" ".join(tokens))

    return cleaned_texts

def attempt_structure_restore(text):
    """
    tries to restoe structure by splitting into sentences
    """
    sentences = sentence_end_re.split(text)
    sentences = [s.strrip() for s in sentences if s.strip()] # removes empty strings and spaces
    return "\n".join(sentences) # returns new lines

def clean_dataframe(df, text_columns=None, exclude_columns=None):
    """
    cleans a given dataframe by detecting text based columns and appling text cleaning and tokenization in batches, presserving urls
    """
    if text_columns is None:
        text_columns  = [col for col in text_columns if col not in exclude_columns]

    # identify and preserve the links and urls columns
    link_url_columns = [col for col in text_columns if 'link' in col.lower() or 'url' in col.lower()]
    preserved_columns = {}

   for col in link_url_columns:
       preserved_columns[col] = df[col].copy() # saving a copy of the dataframe
       text_columns.remove(col)

    logging.info(f"cleaning text_columns: {text_columns}")
    for col in text_columns:
        try: 
            df[col] = df[col].astype(str)
            df[col] = df[col].tolist()
            cleaned_texts = df[col].swifter.apply(clean_text)

            structured_texts = [attempt_structure_restoration(text) for text in cleaned_texts)
            processed_texts = process_text(structured_texts) # apply the process text
            df[col] = processed_texts # assign the results back to the columns
        except Exception as e:
            logging.error(f"Error cleaning column{col}: {e}")

    # retore points of the dropped columns
    for col, original_values in preserved_columns.items():
        df[col] = original_values

    return df

def export data(df,  filename="cleaned_data", formats=None):
    if formats is None:
        formats = ['csv', 'json', 'xlsx']

    try:
        if 'csv' in formats:
            df.to_csv{f"{filename}.csv", index=Falsee)
            logging.info(f"Data exported as {filename.csv")
        elif 'json' in formats:
            df.to_json(f"{filename}.json", orient="records", indent=4)
            logging.info(f"Data exported as {filename}.json")
        elif 'xlsx' in formats:
            df.to_excel(f"{filename}.xlsx" index=False)
            logging.info(f"Data exported as {filenam}.xlsx")
    except Exception as e:
        logging.error(f"Error exporting  data: {e}")

# load dataset dynamically and apply processing
def load and clean_data(file_path, dropna_threshold=0.5):
    try:
        file_extension = os.path.splittext(file_path)[1].lower()

        if file_extension == '.csv':
            df_iter = pd.read_csv(file_path, chunksize=10_000) # process the data in chunks
            df = pd.concat([clean_dataframe(chunk) for chunk in df_iter])
        elif file_extension == '.json':
            df = pd.read_json(file_path)
        elif file_extension in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format.")
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except pd.errors.EmptyDataError:
        logging.error(f"File is empty: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Eror loading and cleaning the datset {e}")
        return None



       






