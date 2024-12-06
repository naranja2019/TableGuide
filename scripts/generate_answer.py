from utils.request_gpt import request_gpt_chat

def generate_final_answer(question, plan, final_subtable_with_header, prompt):

    # Extract column headers and subtable data
    col_headers = final_subtable_with_header[0]
    subtable = final_subtable_with_header[1:]

    # Format the subtable into a markdown-like table format
    subtable_md = "| " + " | ".join(col_headers) + " |\n"
    subtable_md += "| " + " | ".join(["---"] * len(col_headers)) + " |\n"
    for row in subtable:
        subtable_md += "| " + " | ".join(map(str, row)) + " |\n"

    # Format the solution plan into a readable text format
    plan_text = ""
    for stage in plan:
        plan_text += f"Stage {stage['Stage']}:\n"
        plan_text += f"  Sub-Level-Question: {stage['Sub-Level-Question']}\n"

    # Format the final prompt by embedding the question, table, and plan into the template
    prompt = prompt.format(question=question, table=subtable_md, plan=plan_text)

    # Get the final answer by sending the prompt to GPT
    final_answer = request_gpt_chat(prompt=prompt)

    return final_answer


def generate_noplan_answer(question, table_with_header, prompt):

    # Extract column headers and table data (excluding the header row)
    col_headers = table_with_header[0]
    table = table_with_header[1:]

    # Format the table into a markdown-like table format
    table_md = "| " + " | ".join(col_headers) + " |\n"
    table_md += "| " + " | ".join(["---"] * len(col_headers)) + " |\n"
    for row in table:
        table_md += "| " + " | ".join(map(str, row)) + " |\n"

    # Format the final prompt by embedding the question and table into the template
    prompt = prompt.format(question=question, table=table_md)

    # Get the final answer by sending the prompt to GPT
    final_answer = request_gpt_chat(prompt=prompt)

    return final_answer
