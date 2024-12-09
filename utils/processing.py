import random
import re
import copy

def sample_table_rows(table, num_samples=5):
    """
    Randomly sample a specified number (num_samples) of rows from a 2D array representing a table.

    Parameters:
    - table (list): The input table as a list of lists (rows).
    - num_samples (int): The number of rows to sample (default is 5).

    Returns:
    - tuple: A tuple containing the header and the sampled rows.
    """
    # Extract the header (first row)
    header = table[0]
    
    # Sample the specified number of rows (excluding the header)
    rows = random.sample(table[1:], num_samples)
    
    return header, rows


def list_to_markdown(header, rows):
    """
    Convert a table (header and rows) into a markdown-formatted table.

    Parameters:
    - header (list): The list of column names (header).
    - rows (list): The list of rows to include in the table.

    Returns:
    - str: A markdown-formatted string representing the table.
    """
    # Start the markdown table with the header
    markdown_table = "| " + " | ".join(header) + " |\n"
    # Add the separator row with dashes
    markdown_table += "| " + " | ".join(["---"] * len(header)) + " |\n"
    # Add each data row to the markdown table
    for row in rows:
        markdown_table += "| " + " | ".join(row) + " |\n"
    
    return markdown_table


def clean_header(header):
    """
    Clean column names to ensure they only contain letters, numbers, and underscores. 
    If a column name is empty, replace it with 'null'.

    Parameters:
    - header (list): The list of column names (header).

    Returns:
    - list: A cleaned list of column names.
    """
    cleaned_header = []
    for column_name in header:
        if not column_name.strip():  # Check if the column is empty or contains only whitespace
            cleaned_name = 'null'  # Replace empty column names with 'null'
        else:
            cleaned_name = re.sub(r'\W+', '_', column_name)
            cleaned_name = re.sub(r'_+', '_', cleaned_name).strip('_')
        
        cleaned_header.append(cleaned_name)  # Append cleaned column name to the list
    
    return cleaned_header 


def clean_table(table):
    """
    Clean the entire table by cleaning the header and ensuring column names are valid.

    Parameters:
    - table (list): The input table as a list of lists (rows).

    Returns:
    - list: A cleaned version of the input table with cleaned headers.
    """
    table_copy = copy.deepcopy(table)
    header = table_copy[0]
    cleaned_header = clean_header(header)
    cleaned_table = [cleaned_header] + table_copy[1:]
    
    return cleaned_table


def index_table(table):
    """
    Add a row index to the table, creating a new "row index" column and numbering each row.

    Parameters:
    - table (list): The input table as a list of lists (rows).

    Returns:
    - list: A new table with a "row index" column added.
    """
    table_copy = copy.deepcopy(table)
    table_copy[0].insert(0, "row index")

    for i in range(1, len(table_copy)):
        table_copy[i].insert(0, f"row {i}")
    
    return table_copy
