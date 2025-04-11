import os
import sys
sys.path.append("../app/")

import time
import pandas as pd
from langchain_core.messages import HumanMessage, AIMessage
from  agent_setup import get_compiled_graph_app
import traceback

DATASET_CSV_PATH = "evaluation_dataset.csv"
RESULTS_CSV_PATH = "evaluation_results.csv"

def load_dataset(filepath: str):
    try:
        df = pd.read_csv(filepath)
        return df
    except Exception as e:
        print(f"Error loading dataset CSV: {e}")
        return None

def run_evaluation(df_dataset: pd.DataFrame):
    agent_app = get_compiled_graph_app()

    results = []
    current_chat_history = []

    for index, test_case in df_dataset.iterrows():
        question_id = test_case.get("id", f"Row_{index}")
        question = test_case.get("Input Question", "")

        print(f"\nProcessing Question {index + 1}/{len(df_dataset)}")

        formatted_history_for_agent = current_chat_history

        inputs = {
            "question": question,
            "chat_history": formatted_history_for_agent
        }

        start_time = time.time()
        final_answer = "Error during invocation."
        response_state = None

        try:
            response_state = agent_app.invoke(inputs)
            final_answer = response_state.get('final_answer', 'Agent did not return a final_answer.')

        except Exception as e:
            print(f"ERROR invoking agent for question ID {question_id}: {e}")
            traceback.print_exc()
            final_answer = f"ERROR: {e}"
        end_time = time.time()
        latency = end_time - start_time

        result_data = {
            "id": question_id,
            "question": question,
            "expected_classification": test_case.get("Expected Classification", ""),
            "ideal_answer_info": test_case.get("Ideal Answer / Key Info", ""),
            "notes": test_case.get("Notes", ""),
            "actual_answer": final_answer,
            "latency_seconds": latency
        }

        if response_state:
             result_data["actual_classification"] = response_state.get("question_type")
             result_data['actual_answer'] = final_answer
            #  result_data["error"] = response_state.get("error")


        results.append(result_data)

        current_chat_history.append(HumanMessage(content=question))
        current_chat_history.append(AIMessage(content=final_answer if final_answer else ""))

    return results

def save_results(results_list, filepath):
    try:
        df_results = pd.DataFrame(results_list)

        column_order = [
            "id", "question", "expected_classification", "actual_classification",
            "ideal_answer_info", "actual_answer",
            "latency_seconds", "notes"
        ]

        final_columns = [col for col in column_order if col in df_results.columns]

        df_results = df_results[final_columns]
        df_results.to_csv(filepath, index=False, encoding='utf-8')
        print(f"Results saved successfully to {filepath}")

    except Exception as e:
        print(f"Error saving results to CSV: {e}")

if __name__ == "__main__":
    df_eval_data = load_dataset(DATASET_CSV_PATH)
    if df_eval_data is not None:
        evaluation_results = run_evaluation(df_eval_data)
        if evaluation_results:
            save_results(evaluation_results, RESULTS_CSV_PATH)
    else:
        print("Could not run evaluation due to dataset loading error.")