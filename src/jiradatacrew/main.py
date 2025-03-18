#!/usr/bin/env python
import sys
import warnings


from jiradatacrew.crew import Jiradatacrew

from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        "board_id": "3413",
        "team_name": "EASA Modern Data Platform Board"
    }
    
    try:
        Jiradatacrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations, allowing human feedback.
    """
    inputs = {
        "board_id": "3413",
        "team_name": "EASA Modern Data Platform Board"
    }
    try:
        iterations = int(sys.argv[1])
        filename = sys.argv[2]

        for i in range(iterations):
            print(f"\n===== TRAINING ITERATION {i+1}/{iterations} =====\n")
            # Kickoff the crew and capture insights
            result = Jiradatacrew().crew().train_filename(filename, inputs=inputs)
            
            # Present output for human feedback and adjustment
            print("\n=== Current Results ===\n")
            print(result)

            feedback = input("\nProvide feedback for this iteration (leave blank to continue): ").strip()
            if feedback:
                result['feedback'] = feedback  # Store feedback for logging/improvement
                Jiradatacrew().crew().log_feedback(task_id=i+1, feedback=feedback)
            print("\nHuman feedback recorded. Proceeding...\n")

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Jiradatacrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew functionality, allowing human feedback for validation.
    """
    inputs = {
        "board_id": "3413",
        "team_name": "EASA Modern Data Platform"
    }
    try:
        iterations = int(sys.argv[1])
        model_name = sys.argv[2]

        for i in range(iterations):
            print(f"\n===== TESTING ITERATION {i+1}/{iterations} =====\n")
            # Execute the test and capture results
            result = Jiradatacrew().crew().test(n_iterations=i+1, openai_model_name=model_name, inputs=inputs)
            
            # Present test results for human verification
            print("\n=== Current Test Results ===\n")
            print(result)

            # Record Human Feedback
            feedback = input("\nProvide feedback for this test iteration (leave blank to continue): ").strip()
            if feedback:
                Jiradatacrew().crew().log_feedback(task_id=i+1, feedback=feedback)
                print("\nHuman feedback recorded. Proceeding...\n")

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")