import json
import sys
import re
from utils.request_gpt import request_gpt_chat, request_gpt_embedding
from scripts.processing_format import get_row_description, get_col_description
from scripts.generate_solution_plan import get_solution_plan
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from tqdm import tqdm
from scripts.schema_linking import rewrite_question


def get_embeddings(descriptions, request_gpt_embedding):

    embeddings = [request_gpt_embedding(desc) for desc in tqdm(descriptions, desc="Generating Embeddings")]
    return embeddings


def retrieve_rows_by_string_match(table, question):

    # Remove trailing punctuation from the question and convert to lowercase
    question_cleaned = re.sub(r'[^\w\s]$', '', question.strip()).lower()
    # Split the question into words, keeping only letters, numbers, and spaces
    question_words = set(word for word in re.split(r'\W+', question_cleaned) if word)

    matching_rows = set()

    # Iterate over the table rows in reverse order (excluding the header)
    for row_index, row in enumerate(reversed(table[1:])):
        # Calculate the actual index of the row in the original table
        actual_row_index = len(table) - row_index - 2  # -2 accounts for zero-based index and header row
        for cell in row:
            # Convert cell content to lowercase and split into words based on non-alphanumeric characters
            cell_words = set(
                word for word in re.split(r'\W+', str(cell).lower())
                if (len(word) > 3 or word.isdigit()) and word
            )

            # Check if there is any intersection between cell words and question words
            if question_words.intersection(cell_words):
                # Uncomment the following line for debugging purposes
                # print(f"Matched row index: {actual_row_index}, cell content: '{cell}', in question: '{question}'")
                matching_rows.add(actual_row_index)

    return list(matching_rows)


def retrieve_top_relevant_rows_cols(stage, row_embeddings, col_embeddings, request_gpt_embedding, header, topk):

    # Determine the number of rows to select
    if topk == 'all':
        topk = len(row_embeddings)
    else:
        topk = int(topk)

    # Rewrite the sub-level question using schema linking
    sub_level_question = stage['Sub-Level-Question']
    rewrited_sub_level_question = rewrite_question(sub_level_question, header)
    # Get the embedding of the rewritten question
    question_embedding = request_gpt_embedding(rewrited_sub_level_question)

    # Compute similarities with row descriptions and sort them
    row_similarities = cosine_similarity([question_embedding], row_embeddings)[0]
    sorted_row_indices = np.argsort(-row_similarities)  # Sort in descending order of similarity

    # Select the top-k row indices
    num_rows_to_select = min(topk, len(sorted_row_indices))
    top_sorted_rows = sorted_row_indices[:num_rows_to_select]

    # Compute similarities with column descriptions and sort them
    col_similarities = cosine_similarity([question_embedding], col_embeddings)[0]
    sorted_col_indices = np.argsort(-col_similarities)  # Sort in descending order of similarity

    # Select the top-5 column indices
    num_cols_to_select = min(5, len(sorted_col_indices))
    top_sorted_cols = sorted_col_indices[:num_cols_to_select]

    return top_sorted_rows, top_sorted_cols


def retrieve_top_relevant_rows_cols_notopk(question, row_embeddings, col_embeddings, request_gpt_embedding, header):

    # Rewrite the sub-level question using schema linking
    rewrited_sub_level_question = rewrite_question(question, header)
    # Generate the embedding for the rewritten question
    question_embedding = request_gpt_embedding(rewrited_sub_level_question)

    # Calculate cosine similarities with row descriptions and sort them
    row_similarities = cosine_similarity([question_embedding], row_embeddings)[0]
    sorted_row_indices = np.argsort(-row_similarities)  # Sort in descending order of similarity

    # Select up to 60 rows based on similarity
    num_rows_to_select = min(60, len(sorted_row_indices))  
    top_sorted_rows = sorted_row_indices[:num_rows_to_select]

    # Calculate cosine similarities with column descriptions and sort them
    col_similarities = cosine_similarity([question_embedding], col_embeddings)[0]
    sorted_col_indices = np.argsort(-col_similarities)  # Sort in descending order of similarity

    # Select top 5 columns based on similarity
    num_cols_to_select = min(5, len(sorted_col_indices))
    top_sorted_cols = sorted_col_indices[:num_cols_to_select]

    return top_sorted_rows, top_sorted_cols


def retrieve_final_subtable(solution_plan, indexed_table, row_descriptions, col_descriptions, request_gpt_embedding, question):

    # Extract header information from the indexed table
    header_with_index = indexed_table[0]
    header = header_with_index[1:]  # Skip the row index column

    # Get embeddings for row and column descriptions
    row_embeddings = get_embeddings(row_descriptions, request_gpt_embedding)
    col_embeddings = get_embeddings(col_descriptions, request_gpt_embedding)

    # Initialize lists to store indices for rows and columns
    final_row_indices = list()
    final_col_indices = list()
    match_row_indices = list()
    embedding_row_indices = list()
    embedding_col_indices = list()

    # Iterate through each stage in the solution plan and gather relevant rows and columns
    for stage in solution_plan:
        topk = stage['Top k']
        # Retrieve the top rows and columns based on embeddings and the sub-level question
        top_rows, top_cols = retrieve_top_relevant_rows_cols(
            stage, row_embeddings, col_embeddings, request_gpt_embedding, header, topk
        )

        # Update row and column indices based on embedding retrieval
        embedding_row_indices.extend(top_rows)
        embedding_col_indices.extend(top_cols)

    # Perform string matching to find relevant rows for the main question
    matching_rows_question = retrieve_rows_by_string_match(indexed_table, question)
    match_row_indices.extend(matching_rows_question)

    # Combine the embedding-based and matching row indices, ensuring uniqueness
    combined_rows = embedding_row_indices + match_row_indices
    combined_rows = list(dict.fromkeys(combined_rows))  # Remove duplicates while preserving order

    # Add header and row index column to final column indices
    final_col_indices.extend(embedding_col_indices)
    final_row_indices = [-1] + final_row_indices  # Add header row
    final_col_indices = [-1] + final_col_indices  # Add row index column

    # Remove duplicates from final row and column indices
    final_row_indices = list(dict.fromkeys(final_row_indices))
    final_col_indices = list(dict.fromkeys(final_col_indices))

    # Construct the final subtable based on selected rows and columns
    final_subtable = []
    for i in final_row_indices:
        subtable_row = [indexed_table[i + 1][j + 1] for j in final_col_indices]  # i+1 and j+1 to account for index adjustments
        final_subtable.append(subtable_row)

    return final_subtable, final_row_indices, final_col_indices


def retrieve_final_subtable_add(solution_plan, indexed_table, row_descriptions, col_descriptions, request_gpt_embedding, question):
    
    """Retrieve top k row and column indices for all retrieval stages, add the previous and next rows, and generate the final subtable."""
    
    header_with_index = indexed_table[0]
    header = header_with_index[1:]  # Extract column headers (excluding the row index column)

    # Get embeddings for row and column descriptions
    row_embeddings = get_embeddings(row_descriptions, request_gpt_embedding)
    col_embeddings = get_embeddings(col_descriptions, request_gpt_embedding)

    # Initialize lists to store final row and column indices
    final_row_indices = list()
    final_col_indices = list()
    match_row_indices = list()
    embedding_row_indices = list()
    embedding_col_indices = list()

    # Perform string matching for the main question to retrieve relevant rows
    matching_rows_question = retrieve_rows_by_string_match(indexed_table, question)
    match_row_indices.extend(matching_rows_question)

    # For each stage in the solution plan, get the top k rows and columns based on embeddings
    for stage in solution_plan:
        topk = stage['Top k']
        top_rows, top_cols = retrieve_top_relevant_rows_cols(
            stage, row_embeddings, col_embeddings, request_gpt_embedding, header, topk
        )

        # Update the list of rows and columns based on embedding-based retrieval
        embedding_row_indices.extend(top_rows)
        embedding_col_indices.extend(top_cols)

    # Sort the embedding-based row indices
    embedding_row_indices = sorted(embedding_row_indices, key=int)

    # Combine embedding-based and string-matching row indices, ensuring no duplicates
    combined_rows = embedding_row_indices + match_row_indices
    combined_rows = list(dict.fromkeys(combined_rows))  # Remove duplicates while preserving order

    # Add the previous and next rows for each selected row (if they exist)
    for row_index in combined_rows:
        if row_index > 0:  # Add the previous row if it exists
            final_row_indices.append(row_index - 1)

        final_row_indices.append(row_index)  # Add the current row

        if row_index < len(indexed_table) - 2:  # Add the next row if it exists
            final_row_indices.append(row_index + 1)

    # Include columns based on embedding-based retrieval
    final_col_indices.extend(embedding_col_indices)

    # Add the header row (-1) and row index column (-1, 0) to the final row and column indices
    final_row_indices = [-1] + final_row_indices  # Add header row
    final_col_indices = [-1, 0] + final_col_indices  # Add row index column and first column

    # Remove duplicates from the final row and column indices, keeping the last occurrence
    final_row_indices = list(dict.fromkeys(final_row_indices[::-1]))[::-1]
    final_col_indices = list(dict.fromkeys(final_col_indices[::-1]))[::-1]

    # Generate the final subtable based on the selected rows and columns
    final_subtable = []
    for i in final_row_indices:
        subtable_row = [indexed_table[i+1][j+1] for j in final_col_indices]  # i+1 and j+1 account for index offsets
        final_subtable.append(subtable_row)

    return final_subtable, final_row_indices, final_col_indices


def retrieve_final_subtable_add_noplan(indexed_table, row_descriptions, col_descriptions, request_gpt_embedding, question):
    
    """Retrieve top k row and column indices, add the previous and next rows, and generate the final subtable without using a solution plan."""
    
    header_with_index = indexed_table[0]
    header = header_with_index[1:]  # Extract column headers (excluding the row index column)

    # Get embeddings for row and column descriptions
    row_embeddings = get_embeddings(row_descriptions, request_gpt_embedding)
    col_embeddings = get_embeddings(col_descriptions, request_gpt_embedding)

    # Initialize lists to store final row and column indices
    final_row_indices = list()
    final_col_indices = list()
    match_row_indices = list()
    embedding_row_indices = list()
    embedding_col_indices = list()

    # Perform string matching for the main question to retrieve relevant rows
    matching_rows_question = retrieve_rows_by_string_match(indexed_table, question)
    match_row_indices.extend(matching_rows_question)

    # Retrieve top k rows and columns based on embeddings (without a solution plan)
    top_rows, top_cols = retrieve_top_relevant_rows_cols_notopk(
        question, row_embeddings, col_embeddings, request_gpt_embedding, header
    )

    # Update the list of rows and columns based on embedding-based retrieval
    embedding_row_indices.extend(top_rows)
    embedding_col_indices.extend(top_cols)

    # Sort the embedding-based row indices
    embedding_row_indices = sorted(embedding_row_indices, key=int)

    # Combine embedding-based and string-matching row indices, ensuring no duplicates
    combined_rows = embedding_row_indices + match_row_indices
    combined_rows = list(dict.fromkeys(combined_rows))  # Remove duplicates while preserving order

    # Add the previous and next rows for each selected row (if they exist)
    for row_index in combined_rows:
        if row_index > 0:  # Add the previous row if it exists
            final_row_indices.append(row_index - 1)

        final_row_indices.append(row_index)  # Add the current row

        if row_index < len(indexed_table) - 2:  # Add the next row if it exists
            final_row_indices.append(row_index + 1)

    # Include columns based on embedding-based retrieval
    final_col_indices.extend(embedding_col_indices)

    # Add the header row (-1) and row index column (-1, 0) to the final row and column indices
    final_row_indices = [-1] + final_row_indices  # Add header row
    final_col_indices = [-1, 0] + final_col_indices  # Add row index column and first column

    # Remove duplicates from the final row and column indices, keeping the last occurrence
    final_row_indices = list(dict.fromkeys(final_row_indices[::-1]))[::-1]
    final_col_indices = list(dict.fromkeys(final_col_indices[::-1]))[::-1]

    # Generate the final subtable based on the selected rows and columns
    final_subtable = []
    for i in final_row_indices:
        subtable_row = [indexed_table[i+1][j+1] for j in final_col_indices]  # i+1 and j+1 account for index offsets
        final_subtable.append(subtable_row)

    return final_subtable, final_row_indices, final_col_indices



    





