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
    """Clean column names to ensure they contain only letters, numbers, and underscores. If a column name is empty, return 'null'."""
    cleaned_header = []
    for column_name in header:
        if not column_name.strip():  # Check if the column is empty or only contains whitespace
            cleaned_name = 'null'
        else:
            # Replace non-letter, non-number, and non-underscore characters
            cleaned_name = re.sub(r'\W+', '_', column_name)
            # Ensure no consecutive underscores and remove leading/trailing underscores
            cleaned_name = re.sub(r'_+', '_', cleaned_name).strip('_')
        
        cleaned_header.append(cleaned_name)
    return cleaned_header 


def get_solution_plan(table, question, plan_prompt):
    header, sampled_rows = sample_table_rows(table)

    markdown_table = list_to_markdown(header, sampled_rows)
    input = plan_prompt.format(question=question, table=markdown_table)
    # print(input)
    # print("****************")

    # Set maximum number of retry attempts
    max_attempts = 10
    for attempt in range(max_attempts):
        solution_plan = request_gpt_chat(input)
        
        # Use validate_solution_plan function to check solution_plan
        plan_dict = validate_solution_plan(solution_plan)
        if plan_dict:
            return plan_dict
        else:
            print(f"Attempt {attempt + 1}: Generated solution plan does not match the expected format, retrying...")

    raise ValueError("Failed to generate solution plan in the expected format after multiple attempts.")


def validate_solution_plan(solution_plan):
    """Validate whether the generated solution_plan meets the requirements and parse it into a list of dictionaries."""
    try:
        plan_dict = json.loads(solution_plan)
        
        # Check if the parsed plan is a list and contains Stage, Sub-Level-Question, Action, and Top k fields for each stage
        if isinstance(plan_dict, list) and all(
            isinstance(stage, dict) and 
            'Stage' in stage and 
            'Sub-Level-Question' in stage and 
            'Action' in stage and
            'Top k' in stage for stage in plan_dict
        ):
            # If the plan contains only one stage
            if len(plan_dict) == 1:
                return plan_dict if plan_dict[0]['Action'] == 'Reasoning' else None
            
            # For plans with multiple stages, check the previous stages
            for stage in plan_dict[:-1]:  # Check all stages except the last
                if stage['Action'] != 'Retrieval':
                    return None
            
            # Ensure the last stage is 'Reasoning'
            if plan_dict[-1]['Action'] == 'Reasoning':
                return plan_dict

    except json.JSONDecodeError:
        pass 
    return None


def process_single_table(index, d, plan_prompt):
    """Process a single table and return the result data"""
    item = json.loads(d)
    table = item["table_text"]
    question = item["statement"]

    # Clean the header
    header = table[0]
    cleaned_header = clean_header(header)
    cleaned_table = [cleaned_header] + table[1:]

    try:
        # Generate solution plan
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
    # Set up argument parser
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

    # Load the dataset
    with open(args.dataset_path, 'r') as f:
        data = f.readlines()

    # Load the plan prompt
    with open(args.plan_prompt, "r") as f:
        plan_prompt = f.read()

    # Thread pool to process each table data concurrently
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(process_single_table, index, d, plan_prompt)
            for index, d in enumerate(data)
        ]

        # Write the results to the output file
        with open(args.output_path, 'a', encoding='utf-8') as f: 
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing data"):
                result = future.result()
                
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
                f.flush()


if __name__ == "__main__":
    main()
