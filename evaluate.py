import json
import argparse

def normalize_text(text):
    """Normalize text by converting to lowercase and stripping spaces."""
    return text.strip().lower() if isinstance(text, str) else text

def load_file(filepath):
    """Load JSON data from a file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error loading file {filepath}: {e}")

def compute_exact_accuracy(predictions, questions):
    """
    Compute exact accuracy.
    - Metric: Percentage of predictions that match the short `answer` exactly.
    """
    correct = 0
    total = 0

    for qid, question in questions.items():
        if qid in predictions:
            predicted = normalize_text(predictions[qid])
            short_answer = normalize_text(question.get("answer", ""))

            if predicted == short_answer:  # Exact match
                correct += 1

            total += 1

    return correct / total if total > 0 else 0.0

def compute_substring_accuracy(predictions, questions):
    """
    Compute substring accuracy.
    - Metric: Percentage of predictions where the `answer` is a substring of the prediction.
    """
    substring_count = 0
    total = 0

    for qid, question in questions.items():
        if qid in predictions:
            predicted = normalize_text(predictions[qid])
            short_answer = normalize_text(question.get("answer", ""))

            if short_answer in predicted:  # Substring match
                substring_count += 1

            total += 1

    return substring_count / total if total > 0 else 0.0

def evaluate(predictions_file, questions_file):
    """
    Main evaluation logic.
    - Metrics Calculated:
        1. Exact Accuracy: Percentage of predictions matching the `answer` exactly.
        2. Substring Accuracy: Percentage of predictions containing the `answer` as a substring.
    """
    predictions = {p['questionId']: p['prediction'] for p in load_file(predictions_file)}
    questions = load_file(questions_file)

    # Compute metrics
    exact_accuracy = compute_exact_accuracy(predictions, questions)
    substring_accuracy = compute_substring_accuracy(predictions, questions)

    # Print results
    print("Evaluation Results:")
    print(f"Exact Accuracy: {exact_accuracy * 100:.2f}%")
    print(f"Substring Accuracy: {substring_accuracy * 100:.2f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simplified Evaluation for GQA predictions with essential metrics.")
    parser.add_argument("--predictions", type=str, required=True, help="Path to the predictions JSON file.")
    parser.add_argument("--questions", type=str, required=True, help="Path to the questions JSON file.")

    args = parser.parse_args()

    evaluate(args.predictions, args.questions)
