#!/bin/bash

# Set path variables
DATASET_PATH="data/WikiTQ-4k/valid.jsonl"
ROW_PROMPT_PATH="prompt/get_row_template.md"
COL_PROMPT_PATH="prompt/get_col_template.md"
PLAN_PROMPT_PATH="prompt/get_solution_plan.md"
FINAL_REASONING_PROMPT_PATH="prompt/final_reasoning.md"
NOPLAN_REASONING_PROMPT_PATH="prompt/noplan_reasoning.md"
RESULT_FILE_PATH="result/final_reasoning_result.jsonl"
MAX_WORKERS=5

# Check if the dataset file exists
if [ ! -f "$DATASET_PATH" ]; then
  echo "Dataset file does not exist at $DATASET_PATH"
  exit 1
fi

# Check if the row prompt file exists
if [ ! -f "$ROW_PROMPT_PATH" ]; then
  echo "Row prompt file does not exist at $ROW_PROMPT_PATH"
  exit 1
fi

# Check if the column prompt file exists
if [ ! -f "$COL_PROMPT_PATH" ]; then
  echo "Column prompt file does not exist at $COL_PROMPT_PATH"
  exit 1
fi

# Check if the plan prompt file exists
if [ ! -f "$PLAN_PROMPT_PATH" ]; then
  echo "Plan prompt file does not exist at $PLAN_PROMPT_PATH"
  exit 1
fi

# Check if the final reasoning prompt file exists
if [ ! -f "$FINAL_REASONING_PROMPT_PATH" ]; then
  echo "Final reasoning prompt file does not exist at $FINAL_REASONING_PROMPT_PATH"
  exit 1
fi

# Check if the no-plan reasoning prompt file exists
if [ ! -f "$NOPLAN_REASONING_PROMPT_PATH" ]; then
  echo "No-plan reasoning prompt file does not exist at $NOPLAN_REASONING_PROMPT_PATH"
  exit 1
fi

# Run the Python script with the provided arguments
python3 scripts/final_reasoning.py \
  --dataset_path "$DATASET_PATH" \
  --row_prompt_path "$ROW_PROMPT_PATH" \
  --col_prompt_path "$COL_PROMPT_PATH" \
  --plan_prompt_path "$PLAN_PROMPT_PATH" \
  --final_reasoning_prompt_path "$FINAL_REASONING_PROMPT_PATH" \
  --noplan_reasoning_prompt_path "$NOPLAN_REASONING_PROMPT_PATH" \
  --result_file_path "$RESULT_FILE_PATH" \
  --max_workers "$MAX_WORKERS"

# Print completion message
echo "Processing complete. Results saved to $RESULT_FILE_PATH"
