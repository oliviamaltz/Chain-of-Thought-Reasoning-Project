# -*- coding: utf-8 -*-
"""Copy of gemma_and_llava.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Tb51SvQvg1PIcGAgbjAPZYQxgnPesChm
"""

import os
from google.colab import userdata


!pip install -U transformers bitsandbytes accelerate

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(load_in_4bit=True)

tokenizer = AutoTokenizer.from_pretrained("google/gemma-1.1-7b-it")
tokenizer.padding_side = 'left'
model = AutoModelForCausalLM.from_pretrained(
    "google/gemma-1.1-7b-it",
    device_map="auto",
    quantization_config=quantization_config
)

input_text = "Write me a poem about Machine Learning."
input_ids = tokenizer(input_text, return_tensors="pt").to("cuda")

outputs = model.generate(**input_ids)
print(tokenizer.decode(outputs[0]))

import json
from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# Path to the JSON file in your Google Drive
json_file_path = "/content/drive/MyDrive/NLP_Final_Project/Data/selected_test_questions.json"

# Load questions from the JSON file
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Prompt template
prompt_template = (
    "Question: What piece of furniture is to the right of the pink blanket? "
    "Sub-questions: Where in the image is the pink blanket? Describe what is to the right of the pink blanket. Where to the right of the pink blanket is the piece of furniture? Describe the piece of furniture. What piece of furniture is it?\n"
    "Question: {question}"
)

# Prepare prompts and associate them with ImageIDs
image_question_mapping = {entry["imageId"]: entry["question"] for entry in data}

subquestion_outputs = {}
for idx, (image_id, question) in enumerate(image_question_mapping.items(), start=1):
    print(f"Processing question {idx}/{len(image_question_mapping)}: ImageID {image_id}, Question: {question}")

    chat = [{'role': 'user', 'content': prompt_template.replace('{question}', question)}]
    formatted_prompt = tokenizer.apply_chat_template(chat, tokenize=False)

    input_ids = tokenizer(formatted_prompt, return_tensors="pt", padding=True, truncation=True).to(model.device)

    generated_ids = model.generate(**input_ids)

    output = tokenizer.decode(generated_ids[:, input_ids.input_ids.shape[1]:][0], skip_special_tokens=True)

    # Save the subquestions for this ImageID
    subquestion_outputs[image_id] = output.strip().split('\n')

# Save subquestions by ImageID
output_file_path = "/content/drive/My Drive/NLP_Final_Project/Milestone_3/gemma_subquestions08.json"
with open(output_file_path, 'w') as file:
    json.dump(subquestion_outputs, file, indent=4)

print(f"Subquestions saved to: {output_file_path}")

!pip install transformers
!pip install transformers torch torchvision accelerate sentencepiece

import torch
print(torch.__version__)
print(torch.cuda.is_available())

# Ensure necessary imports
import torch
from transformers import AutoProcessor, LlavaForConditionalGeneration

# Specify the model identifier
model_id = "llava-hf/llava-1.5-7b-hf"

# Load the processor and model
processor = AutoProcessor.from_pretrained(model_id)
model = LlavaForConditionalGeneration.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto"
)

import json
from PIL import Image
import torch
import random
import numpy as np
import re


SEED = 42
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

# Paths
subquestions_path = "/content/drive/MyDrive/NLP_Final_Project/Milestone_3/gemma_subquestions/gemma_subquestions08.json"
questions_path = "/content/drive/MyDrive/NLP_Final_Project/Data/selected_test_questions.json"
images_dir = "/content/drive/MyDrive/NLP_Final_Project/Data/test_images/"
output_path = "/content/drive/MyDrive/NLP_Final_Project/Milestone_3/prediction/subquestion_predictions08.json"

# Load data
with open(subquestions_path, 'r') as f:
    subquestions_data = json.load(f)

with open(questions_path, 'r') as f:
    official_questions_data = {entry["imageId"]: entry["question"] for entry in json.load(f)}

# Results storage
results = {}

# Helper function to clean subquestions
def extract_valid_subquestions(subquestion_text):
    # Find all indices of '.' or '?' in the text
    delimiters = [m.start() for m in re.finditer(r'[.?]', subquestion_text)]
    valid_subquestions = []

    start = 0
    for end in delimiters:
        subquestion = subquestion_text[start:end + 1].strip()
        if subquestion:
            valid_subquestions.append(subquestion)
        start = end + 1
    return valid_subquestions

# Process each ImageID
for idx, (image_id, subquestions) in enumerate(subquestions_data.items(), start=1):
    print(f"Processing question {idx}/{len(subquestions_data)}: ImageID {image_id}")
    image_path = f"{images_dir}/{image_id}.jpg"

    # Load the image
    try:
        image = Image.open(image_path)
        print(f"Image loaded for ImageID: {image_id}")
    except FileNotFoundError:
        print(f"Image not found for ImageID: {image_id}")
        results[image_id] = {"error": "Image not found"}
        continue

    # Extract valid subquestions
    valid_subquestions = extract_valid_subquestions(subquestions[0])
    if not valid_subquestions:
        print(f"No valid subquestions for ImageID: {image_id}")
        results[image_id] = {"error": "No valid subquestions"}
        continue

    # Initialize context
    context = ""

    subquestion_responses = []
    for sub_idx, subquestion in enumerate(valid_subquestions, start=1):
        # First prompt: Ask subquestion with the image
        prompt = f"USER: <image>\nQuestion: {subquestion}\nASSISTANT:"
        inputs = processor(images=image, text=prompt, return_tensors="pt").to("cuda")
        outputs = model.generate(**inputs, max_new_tokens=256, do_sample=True, temperature=0.7, top_p=0.9)
        response = processor.decode(outputs[0], skip_special_tokens=True).split("ASSISTANT:")[-1].strip()
        subquestion_responses.append({"subquestion": subquestion, "response": response})
        print(f"Subquestion {sub_idx}: {subquestion}")
        print(f"LLaVA Response: {response}\n")

        # Update context text
        context += f" {subquestion} {response}"

    # Get the official question
    official_question = official_questions_data.get(image_id, None)
    if not official_question:
        print(f"Official question not found for ImageID: {image_id}")
        results[image_id] = {
            "subquestions": subquestion_responses,
            "error": "Official question not found"
        }
        continue

    # Final prompt: Ask the official question with context and image
    final_prompt = f"USER: <image>\nQuestion: Use the context: {context}. Answer the following question: {official_question} Provide a short answer.\nASSISTANT:"
    inputs = processor(images=image, text=final_prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=50, do_sample=False)
    final_answer = processor.decode(outputs[0], skip_special_tokens=True).split("ASSISTANT:")[-1].strip()

    print(f"Official Question: {official_question}")
    print(f"LLaVA Prediction: {final_answer}\n")

    # Store results for this ImageID
    results[image_id] = {
        "subquestions": subquestion_responses,
        "official_question": official_question,
        "prediction": final_answer
    }

with open(output_path, 'w') as f:
    formatted_results = {}
    for image_id, result in results.items():
        if "error" in result:
            # Include the error if it exists
            formatted_results[image_id] = {"error": result["error"]}
        else:
            # Structure the output with separated subquestions and answers
            formatted_results[image_id] = {
                "subquestions": [entry["subquestion"] for entry in result["subquestions"]],
                "responses": [entry["response"] for entry in result["subquestions"]],
                "official_question": result["official_question"],
                "prediction": result["prediction"]
            }
    json.dump(formatted_results, f, indent=4)

print(f"Formatted LLaVA responses saved to: {output_path}")

import json
import os


# Define the paths
input_path = "/content/drive/MyDrive/NLP_Final_Project/Milestone_3/prediction/subquestion_predictions08.json"
output_path = "/content/drive/MyDrive/NLP_Final_Project/Milestone_3/prediction/official_prediction08.json"

if os.path.exists(input_path):
    print(f"File found at {input_path}, processing...")

    # Read the subquestion_predictionsXX.json
    with open(input_path, "r") as f:
        data = json.load(f)

    formatted_data = [
        {"questionId": qid, "prediction": details["prediction"]}
        for qid, details in data.items()
        if "prediction" in details
    ]

    with open(output_path, "w") as f:
        json.dump(formatted_data, f, indent=4)

    print(f"File successfully created at {output_path}")
else:
    print(f"File not found at {input_path}. Please check the path and try again.")