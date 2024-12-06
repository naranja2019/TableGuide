### Instruction
You are given a sample from a large table and a question related to the data in that large table. Your task is to create a step-by-step plan to answer the question. Each step in the plan should contain:

1. A Sub-Level-Question that specifies what needs to be resolved at this step. Ensure the wording in the Sub-Level-Question closely align with the phrasing in the table's rows and columns.

2. An Action that indicates the operation the model should perform:
    a. Retrieval: This action directs the model to search the entire large table using the current Sub-Level-Question to retrieve a relevant subset of rows or columns in order to answer the question.
    b. Reasoning: Use the Sub-Level-Question and the retrieved tables from the previous stage to infer or calculate the answer.
    - Calculations Across All Rows: For questions containing terms like “-est” , “most” or “last” (e.g., “What is the highest revenue?”) or involving calculations like finding a maximum, average, total count which need to analyze all rows, set Top k to "all".
3. An top k value that specifies the number of rows needed for answering the current Sub-Level-Question. Generally, questions fall into three categories:  
    - Specific Value Retrieval: Requires finding a specific value and extracting other attributes from its row (e.g., "What is the name of the company that has profit of 93823?"). In this example, since the task is to find the row where the profit equals 93,823, set Top k to "1".
    - Relative Position Retrieval: For questions that require finding a specific row along with the row immediately before or after it (e.g., retrieving values from a target row and its neighboring rows), set Top k to "1".


### Important Rule
The Plan must satisfy the following constraints:

1. If answering the question requires only one step that needs analyzing the whole table (For example, the question includes superlative terms like “highest,” counting phrases like "how many," or requires calculating an average), then skip any Retrieval steps and create a single-stage plan only has "Reasoning" as the action.


The output format should be:
Plan:
Stage 1:
Sub-Level-Question: xxxxx
Action: Retrieval/Reasoning
Top k: xxx

Stage 2:
Sub-Level-Question: xxxxx
Action: Retrieval/Reasoning
Top k: xxx

………………

Stage n:
Sub-Level-Question: xxxxx
Action: Reasoning
Top k: xxx


### Example 1 
- Question: What is the difference between the highest and lowest profit companies in the oil and gas industry?
- Sampled Table:
| Rank | Company Name       | Industry      | Revenue ($ Million) | Profit ($ Million) | Employees | Headquarters  |
| 1    | Walmart            | Retail        | $559,151            | $13,510           | 2,300,000 | United States  |
| 3    | Amazon             | Retail        | $386,064            | $21,331           | 1,298,000 | United States  |
| 4    | National Petroleum | Oil and gas   | $283,958            | $4,575            | 1,242,245 | China          |
| 9    | Toyota             | Automotive    | $256,722            | $21,180           | 366,283   | Japan          |
| 10   | Volkswagen         | Automotive    | $253,965            | $10,104           | 662,575   | Germany        |

- Plan:
[
{{
    "Stage": 1,
    "Sub-Level-Question": "What is the profit of the highest profit company in the oil and gas industry?",
    "Action": "Retrieval",
    "Top k": "1"
}},
{{
    "Stage": 2,
    "Sub-Level-Question": "What is the profit of the lowest profit company in the oil and gas industry?",
    "Action": "Retrieval",
    "Top k": "1"
}},
{{
    "Stage": 3,
    "Sub-Level-Question": "What is the difference between the highest and the lowest profit?",
    "Action": "Reasoning",
    "Top k": "2"
}}
]

### Example 2
- Question: Which company has the revenue of 559151 million and has 2300000 employees?
- Sampled Table:
| Rank | Company Name       | Industry      | Revenue ($ Million) | Profit ($ Million) | Employees | Headquarters  |
| 1    | Walmart            | Retail        | $559,151            | $13,510           | 2,300,000 | United States  |
| 3    | Amazon             | Retail        | $386,064            | $21,331           | 1,298,000 | United States  |
| 4    | National Petroleum | Oil and gas   | $283,958            | $4,575            | 1,242,245 | China          |
| 9    | Toyota             | Automotive    | $256,722            | $21,180           | 366,283   | Japan          |
| 10   | Volkswagen         | Automotive    | $253,965            | $10,104           | 662,575   | Germany        |

- Plan:
[
{{
    "Stage": 1,
    "Sub-Level-Question": "Which company has the revenue of 559151 million?",
    "Action": "Retrieval",
    "Top k": "1"
}},
{{
    "Stage": 2,
    "Sub-Level-Question": "Which company has the revenue of 559151 million?",
    "Action": "Reasoning",
    "Top k": "1"
}}
]

### Example 3
- Question: What is the highest revenue in the automotive industry?
- Sampled Table:
| Rank | Company Name       | Industry      | Revenue ($ Million) | Profit ($ Million) | Employees | Headquarters   |
| 1    | Walmart            | Retail        | $559,151            | $13,510            | 2,300,000 | United States  |
| 3    | Amazon             | Retail        | $386,064            | $21,331            | 1,298,000 | United States  |
| 4    | National Petroleum | Oil and gas   | $283,958            | $4,575             | 1,242,245 | China          |
| 9    | Toyota             | Automotive    | $256,722            | $21,180            | 366,283   | Japan          |
| 10   | Volkswagen         | Automotive    | $253,965            | $10,104            | 662,575   | Germany        |

- Plan:
[
{{
    "Stage": 1,
    "Sub-Level-Question": "What is the highest revenue in the automotive industry?",
    "Action": "Reasoning",
    "Top k": "all"
}}
]

### Example 4
- Question: What is the total number of companys listed?
- Sampled Table:
| Rank | Company Name       | Industry      | Revenue ($ Million) | Profit ($ Million) | Employees | Headquarters   |
| 1    | Walmart            | Retail        | $559,151            | $13,510            | 2,300,000 | United States  |
| 3    | Amazon             | Retail        | $386,064            | $21,331            | 1,298,000 | United States  |
| 4    | National Petroleum | Oil and gas   | $283,958            | $4,575             | 1,242,245 | China          |
| 9    | Toyota             | Automotive    | $256,722            | $21,180            | 366,283   | Japan          |
| 10   | Volkswagen         | Automotive    | $253,965            | $10,104            | 662,575   | Germany        |

- Plan:
[
{{
    "Stage": 1,
    "Sub-Level-Question": "What is the total number of companys listed?",
    "Action": "Reasoning",
    "Top k": "all"
}}
]


### Attention
1. The action of the last stage of the plan must be reasoning.
2. Generate a plan instead of directly providing the answer to the question.
3. The output content only includes a Plan that conforms to the specified format, without any other content or explanations.

Generate a structured plan for the following question using the same approach:

Question: {question}
Sampled Table:
{table}

Plan: