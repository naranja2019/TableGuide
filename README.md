# TableGuide

**TableGuide: A Stepwise-Guided Retrieval and Reasoning Framework for Large-Scale Table QA**
For reproduction of Large-Scale Table QA results in our paper, see instructions below.

## Overview

This repository provides the code implementation for TableGuide, a stepwise-guided retrieval and reasoning framework designed for large-scale Table-based Question Answering (QA). TableGuide aims to improve table-based QA tasks by combining table retrieval and reasoning steps in a structured manner. The framework leverages state-of-the-art models and methods to efficiently process tabular data and answer complex questions that require deep reasoning across tables.

## Requirements

+ openai == 1.52.2
+ tiktoken == 0.8.0
+ scikit-learn == 1.5.2
+ scipy == 1.13.1

## Running the Code

### Data

In ./data file, you can find the well-preprocessed data in `jsonl` format.

Data information in ./data:

+ `WikiTQ-4k`：
+ `WikiTQ+`:

### TableGuide Framework

