import pandas as pd
import os
from fastapi.testclient import TestClient
import json
import wandb
from langchain.evaluation import load_evaluator
import time

with open("./configs/testing_config.json") as f:
    config = json.load(f)

USE_WANDB = config["use_wandb"]

class CommonTests():
    @classmethod
    def tearDownClass(cls):
        if USE_WANDB:
            df = cls.table.get_dataframe()
            q_types = list(df["Question Type"].unique())
            for q_type in q_types:
                filtered_df = df[df["Question Type"] == q_type]
                unique_datasets = list(df["Dataset"].unique())
                for dataset in unique_datasets:
                    cls.config = {
                        "llm_service": cls.llm_service,
                        "question_type": q_type,
                        "dataset": dataset
                    }
                    cls.wandbLogger = wandb.init(project="llm-eval-sweep", config=cls.config)
                    final_df = filtered_df[filtered_df["Dataset"] == dataset]
                    acc = (final_df["Answer Correct"].sum())/final_df["Answer Correct"].shape[0]
                    avg_resp_time = final_df["Response Time (seconds)"].mean()
                    cls.wandbLogger.log({"LLM Service": cls.llm_service,
                                        "Question Type": q_type,
                                        "Dataset": dataset,
                                        "Accuracy": acc,
                                        "Average Response Time (seconds)": avg_resp_time,
                                        "Number of Questions": final_df["Answer Correct"].shape[0]}, commit=True)
                    tmp_table = wandb.Table(dataframe=final_df)
                    cls.wandbLogger.log({"qa_results": tmp_table})
                    wandb.finish()

def test_generator(dataset, row, username, password):
    
    # Need to extract q/a pairs before test is generated,
    # as otherwise we look at the last question/answer pair is used
    question = row["Question"]
    true_answer = str(row["Answer"])
    function_call = row["Function Call"]
    question_theme = row["Question Theme"]
    question_type = row["Question Type"]

    test_name = "test_"+dataset+"_"+str(row.name)+question_theme.replace(" ", "_")

    def test(self):
        t1 = time.time()
        resp = self.client.post("/"+dataset+"/query", json={"query": question}, auth=(username, password))
        t2 = time.time()
        self.assertEqual(resp.status_code, 200)
        evaluator = load_evaluator("string_distance")
        answer = list(resp.json()["query_sources"][0].values())[-1]
        correct = False
        if isinstance(answer, str):
            string_dist = evaluator.evaluate_strings(prediction=answer, reference=true_answer)["score"]
            if string_dist <= .2:
                correct = True
        elif isinstance(answer, list):
            json_form = json.loads(true_answer)
            for i in range(len(json_form)):
                if json_form[i] == answer[i]:
                    correct = True
                else:
                    correct = False
                    break
        elif isinstance(answer, dict):
            json_form = json.loads(true_answer)
            if sorted(answer.items()) == sorted(json_form.items()):
                correct = True
        else:
            if str(answer) == true_answer:
                correct = True

        if USE_WANDB:
            self.table.add_data(
                    self.llm_service,
                    dataset,
                    question_type,
                    question_theme,
                    question,
                    true_answer,
                    function_call,
                    resp.json()["natural_language_response"], 
                    str(answer),
                    list(resp.json()["query_sources"][0].keys())[-1],
                    correct,
                    t2-t1
            )

        if isinstance(answer, str):
            self.assertLessEqual(string_dist, .5)
        else:
            self.assertEqual(str(answer), true_answer)
    return test_name, test

with open("./configs/db_config.json", "r") as config_file:
    config = json.load(config_file)

for suite in ["OGB_MAG"]:
    questions = "./test_questions/"+suite+"/"+suite+"Questions.tsv"
    questions = pd.read_csv(questions, delimiter="\t")
    
    tests = list(questions.apply(lambda x: test_generator(suite, x, config["username"], config["password"]), axis = 1))
    for test in tests:
        setattr(CommonTests, test[0], test[1])