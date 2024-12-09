import json
import random
import sys
import re
import argparse
from tqdm import tqdm
from utils.request_gpt import request_gpt_chat
from utils.processing import list_to_markdown, sample_table_rows
from concurrent.futures import ThreadPoolExecutor, as_completed


def clean_header(header):
    """
    Cleans column names to ensure they contain only letters, numbers, and underscores.
    If a column name is empty, it is replaced with 'null'.

    Args:
        header: A list of column names to be cleaned.

    Returns:
        A list of cleaned column names.
    """
    cleaned_header = []
    for column_name in header:
        if not column_name.strip():
            cleaned_name = 'null'
        else:
            cleaned_name = re.sub(r'\W+', '_', column_name)
            cleaned_name = re.sub(r'_+', '_', cleaned_name).strip('_')
        
        cleaned_header.append(cleaned_name)
    
    return cleaned_header


def get_solution_plan(table, question, plan_prompt):
    """
    Generates a solution plan based on the table and question.

    Args:
        table: The input table containing data.
        question: The question to be answered.
        plan_prompt: The prompt template used to generate the solution plan.

    Returns:
        A dictionary representing the solution plan.
    """
    header, sampled_rows = sample_table_rows(table)

    markdown_table = list_to_markdown(header, sampled_rows)
    input_plan = plan_prompt.format(question=question, table=markdown_table)

    max_attempts = 10
    for attempt in range(max_attempts):
        solution_plan = request_gpt_chat(input_plan)
        
        plan_dict = validate_solution_plan(solution_plan)
        if plan_dict:
            return plan_dict
        else:
            print(f"Attempt {attempt + 1}: Generated solution plan does not match the expected format, retrying...")

    raise ValueError("Failed to generate solution plan in the expected format after multiple attempts.")



def validate_solution_plan(solution_plan):
    """
    Validates whether the generated solution plan meets the required format and parses it into a list of dictionaries.

    Args:
        solution_plan: The generated solution plan in JSON format.

    Returns:
        A list of dictionaries representing the solution plan if valid, or None if invalid.
    """
    try:
        plan_dict = json.loads(solution_plan)
        
        if isinstance(plan_dict, list) and all(
            isinstance(stage, dict) and 
            'Stage' in stage and 
            'Sub-Level-Question' in stage and 
            'Action' in stage and
            'Top k' in stage for stage in plan_dict
        ):
            if len(plan_dict) == 1:
                return plan_dict if plan_dict[0]['Action'] == 'Reasoning' else None
            
            for stage in plan_dict[:-1]:
                if stage['Action'] != 'Retrieval':
                    return None

            if plan_dict[-1]['Action'] == 'Reasoning':
                return plan_dict

    except json.JSONDecodeError:
        pass 
    
    return None


def process_single_table(index, d, plan_prompt):
    """
    Processes a single table and returns the result data including the question, solution plan, and cleaned table.

    Args:
        index: The index of the current iteration.
        d: A JSON string containing the table and associated question.
        plan_prompt: The prompt template used to generate the solution plan.

    Returns:
        A dictionary containing the question, solution plan, and cleaned table, or a default record in case of an error.
    """
    item = json.loads(d)
    table = item["table_text"]
    question = item["statement"]

    header = table[0]
    cleaned_header = clean_header(header)
    cleaned_table = [cleaned_header] + table[1:]

    try:
        solution_plan = get_solution_plan(cleaned_table, question, plan_prompt)
        record_data = {
            "question": question,
            "solution_plan": solution_plan,
            "table": cleaned_table,
        }
    except Exception as e:
        print(f"Error encountered {index}: {e}. Skipping this iteration.")
        record_data = {
            "question": question,
            "solution_plan": "null",
            "table": cleaned_table,
        }

    return record_data



def main():
    parser = argparse.ArgumentParser(description="Process dataset for solution plan generation.")
    parser.add_argument(
        '--dataset_path', 
        type=str, 
        help="Path to the dataset file"
    )
    parser.add_argument(
        '--plan_prompt', 
        type=str, 
        default="prompt/get_solution_plan.md", 
        help="Path to the plan prompt file"
    )
    parser.add_argument(
        '--output_path', 
        type=str, 
        help="Path to the output result file"
    )
    args = parser.parse_args()

    with open(args.dataset_path, 'r') as f:
        data = f.readlines()

    with open(args.plan_prompt, "r") as f:
        plan_prompt = f.read()

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(process_single_table, index, d, plan_prompt)
            for index, d in enumerate(data)
        ]

        with open(args.output_path, 'a', encoding='utf-8') as f: 
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing data"):
                result = future.result()
                
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
                f.flush()


if __name__ == "__main__":
    main()
