# GQA Visual Question Answering Project

**Authors:** Pearl Liu, Olivia Maltz, Hanson Siu, King Long Tang

This repository contains the code and resources for a Visual Question Answering (VQA) project on the GQA dataset, focusing on improving LLaVA's performance through subquestion generation using Gemma and fine-tuning with LoRA.

## Project Overview
This project, detailed in our report *Improving Compositional Visual Question-Answering with Chain-of-Thought Reasoning and a Specialized Language Model*, explores enhancing VQA performance by leveraging an LLM for subquestion generation and fine-tuning a VLM for improved reasoning. Our best-performing method improved exact accuracy from 26.79% to 51.56%.

## Files in This Repository:

### 1. `simple-baseline.py`
- Implements a baseline VQA system using LLaVA without intermediate reasoning.

### 2. `Extension1.py`
- Uses Google’s Gemma model to generate subquestions and combines responses for final predictions.

### 3. `Extension2.py`
- Fine-tunes LLaVA with LoRA for multi-step reasoning and context integration.

### 4. `evaluate.py`
- Evaluates model predictions using exact and substring accuracy.

### 5. `error_analysis/`
- Contains scripts for analyzing errors across different question types and improving model performance.

## Dependencies
- Python 3.8+
- Hugging Face `transformers`, `bitsandbytes`, `peft`, `trl`
- PyTorch, torchvision
- PIL, numpy, scikit-learn

## How to Run
- Install dependencies and run `simple-baseline.py`, `Extension1.py`, or `Extension2.py`.
- Evaluate results using `evaluate.py`.

## Acknowledgments
- Built upon open-source Hugging Face models.
- Acknowledgment to Manu Romero for code used in Extension 2 fine-tuning.

## License
MIT License
