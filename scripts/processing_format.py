import random
import json
import sys
import re
from utils.request_gpt import request_gpt_chat, request_gpt_embedding
from utils.processing import sample_table_rows


def get_row_template(table, prompt):
    # 随机sample表格
    header, sampled_rows = sample_table_rows(table)
    markdown_header = "| " + " | ".join(header) + " |\n"
    markdown_rows = ""
    for row in sampled_rows:
        markdown_rows += "| " + " | ".join(row) + " |\n"

    # 生成行模板的prompt
    prompt = prompt.format(header = markdown_header, sampled_rows = markdown_rows)
    # print(prompt)

    max_attempts = 10  # 限制重试次数
    for attempt in range(max_attempts):
        row_template = request_gpt_chat(prompt=prompt)
        
        # 验证生成是否符合格式
        if validate_row_template(row_template, header):
            return row_template
        else:
            print(f"Attempt {attempt + 1}: Generated row template does not match the expected format, retrying...")
            # print("Wrong row template:", row_template)
    raise ValueError("Failed to generate row template in the expected format after multiple attempts.")


def get_col_template(table, prompt):
    # 随机sample表格
    header, sampled_rows = sample_table_rows(table)
    markdown_header = "| " + " | ".join(header) + " |\n"
    markdown_rows = ""
    for row in sampled_rows:
        markdown_rows += "| " + " | ".join(row) + " |\n"

    # 生成列模板的prompt
    prompt = prompt.format(header = markdown_header, sampled_rows = markdown_rows)
    # print(prompt)

    max_attempts = 10  # 限制重试次数
    for attempt in range(max_attempts):
         
        col_template = request_gpt_chat(prompt=prompt)
        # 验证生成是否符合格式
        if validate_col_template(col_template, header):
            return col_template
        else:
            print(f"Attempt {attempt + 1}: Generated template does not match the expected format, retrying...")
            # print("Wrong col template:", col_template)
    raise ValueError("Failed to generate column template in the expected format after multiple attempts.")


def validate_col_template(col_template, header):
    """验证生成的列描述是否符合每列一行且按指定格式生成的要求。"""
    # 定义格式匹配的正则表达式
    pattern = r"^Col\d+ ## .+: .+(\n|$)"
    
    # 分割生成的描述并验证
    col_template_lines = col_template.strip().splitlines()
    
    # 检查是否为每列生成了一行描述，且每行符合格式
    if len(col_template_lines) == len(header) and all(re.match(pattern, line) for line in col_template_lines):
        return True
    return False


def validate_row_template(row_template, header):
    """验证生成的行描述模板是否符合指定格式，并确保每个占位符与表格的列名匹配。"""

    # 提取模板中的列名并与 header 比较
    placeholders = re.findall(r"\{(.*?)\}", row_template)
    return all(placeholder in header for placeholder in placeholders)


def get_row_description(table, row_prompt):
    """
    为表格中的每一行数据生成自然语言描述。
    """

    row_template = get_row_template(table, row_prompt)
    # print("Ture Template:", row_template)

    header, *rows = table

    descriptions = []
    for row in rows:
        row_data = dict(zip(header, row))  
        description = row_template.format(**row_data) 
        descriptions.append(description)

    # for desc in descriptions:
    #     print(desc)
    return descriptions


def get_col_description(table, col_prompt):
    """
    为表格中的每一列数据生成自然语言描述。
    """

    col_template = get_col_template(table, col_prompt)
    column_descriptions = col_template.split('\n')
    # print("True column_descriptions:", column_descriptions)

    header, *rows = table

    column_texts = []

    for i, col_name in enumerate(header):
        description = column_descriptions[i] if i < len(column_descriptions) else "No description available."
        
        # column_values = "|".join(row[i] for row in rows)
        # column_text = f"{description} The values in this column are: {column_values}"

        column_text = description
        column_texts.append(column_text)

    # for column_text in column_texts:
    #     print(column_text)

    return column_texts


def get_row_flattened(table):
    """
    把表格中的每一行数据展平。
    """
    # 初始化一个列表来存储展平后的每一行
    flattened_rows = []

    # 从第二行开始处理（跳过第一行列名）
    for row in table[1:]:
        # 将行中的所有元素拼接成一个字符串
        flattened_row = ''.join(row)
        # 添加到展平后的列表中
        flattened_rows.append(flattened_row)
    
    return flattened_rows


# if __name__ == "__main__":

#     with open("dataset/4096_test.jsonl", 'r') as f:
#         data = f.readlines()
#     for d in data:
#         item = json.loads(d)
#         table = item["table_text"]
   
#     with open("prompt/get_row_template.md", "r") as f:
#         row_prompt = f.read()

#     with open("prompt/get_col_template.md", "r") as f:
#         col_prompt = f.read()

#     # row_template = get_row_template(table, row_prompt)
#     # col_template = get_col_template(table, col_prompt)

#     # print(row_template)
#     # print(col_template)

#     row_descriptions = get_row_description(table, row_prompt)
#     col_descriptions = get_col_description(table, col_prompt)

#     print(row_descriptions)
#     print(col_descriptions)

#     embedding = request_gpt_embedding(row_descriptions[0])
#     print(embedding)
#     print(len(embedding))