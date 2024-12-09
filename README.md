# TableGuide

**TableGuide: A Stepwise-Guided Retrieval and Reasoning Framework for Large-Scale Table QA**

For reproduction of Large-Scale Table QA results in our paper, see instructions below.

## Overview

This repository provides the code implementation for TableGuide, a stepwise-guided retrieval and reasoning framework designed for large-scale Table-based Question Answering (QA). TableGuide aims to improve table-based QA tasks by combining table retrieval and reasoning steps in a structured manner. The framework leverages state-of-the-art models and methods to efficiently process tabular data and answer complex questions that require deep reasoning across tables.

## Data Format

All data is stored in `jsonl` format, where each entry contains the following fields:

```json
{
    "statement": "", 
    "table_text": [[]], 
    "answer": [], 
    "ids": ""
}
```

### Field Descriptions:

- **statement**: The question to be answered based on the provided table.
- **table_text**: The tabular data (in text format) associated with the question.
- **answer**: A list containing the answer(s) to the question.
- **ids**: A unique identifier for the data entry.

## Benchmark Dataset

+ Our dataset is publicly available in our repository.

  ### Datasets:
  
1. **WikiTQ-4k**:
     - **WikiTableQuestions (WikiTQ)** is a well-known benchmark dataset for question answering over structured tabular data. For our experiments, we filter the dataset to include only tables with more than 4k tokens, resulting in a subset of 488 entries.
2. **WikiTQ+**:
     - To augment the WikiTQ dataset, we extend medium-sized tables (containing 2k to 4k tokens) by adding additional rows generated using GPT-4o with prompt-based table generation techniques. These expanded tables now contain at least 4k tokens. The WikiTQ+ dataset includes 1023 entries.

## Baseline Method

| Method         | Reference                                                    |
| -------------- | ------------------------------------------------------------ |
| Tapas          | [TAPAS](https://huggingface.co/docs/transformers/model_doc/tapas) |
| Text-to-SQL    | [Text-to-SQL](https://arxiv.org/pdf/2204.00498)              |
| Binder         | [Binder](https://github.com/zsong96wisc/Binder-TableQA)      |
| ReAcTable      | [ReAcTable](https://github.com/yunjiazhang/reactable)        |
| Few-Shot QA    | N/A                                                          |
| Dater          | [Dater](https://arxiv.org/pdf/2301.13808)                    |
| Chain-of-Table | [Chain-of-Table](https://github.com/google-research/chain-of-table) |

## Requirements

+ `openai == 1.52.2`
+ `tiktoken == 0.8.0`
+ `scikit-learn == 1.5.2`
+ `scipy == 1.13.1`

## Running the Code

### Data

The data is preprocessed and stored in the `./data` directory in `jsonl` format.

Data files in `./data` include:

- **WikiTQ-4k**
- **WikiTQ+**

### Prompt

The prompt contains the templates used to call LLMs. The key prompts in TableGuide include:

- **`final_reasoning`**: The final reasoning step, where the model synthesizes information from the retrieved data to answer the question.
- **`get_col_template`**: Generates a column summary template based on the table schema.
- **`get_row_template`**: Generates a row summary template based on the table schema.
- **`get_solution_plan`**: Generates a solution plan for answering the table-based question.
- **`noplan_reasoning`**: Used for ablation studies, this prompt handles reasoning without a solution plan.
- **`prompt_schema_linking`**: Links the schema of the table with the question to ensure proper alignment between the data and the query.

In TableGuide, the prompts are dynamically generated based on the input data and task requirements. This stepwise-guided approach ensures that the model receives all the necessary information in a structured format, allowing it to retrieve relevant information from the table and reason through the data to answer complex questions effectively.

### Setting Your OpenAI Key:

Before running the code, you need to set your `api_key` and `base_url` in `utils/request_gpt.py`.

```python
client = OpenAI(
    api_key="",  # Set your API key here
    base_url=""  # Set the base URL for the API here
)
```

### Run

You can run the code by executing the following command in your terminal:

```bash
bash run.sh
```