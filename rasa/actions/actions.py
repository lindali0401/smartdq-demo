# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
from rasa_sdk.events import SlotSet

class ActionRecommendMethod(Action):
    def name(self) -> Text:
        return "action_recommend_method"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            # response = requests.get("http://localhost:5000/summary")
            response = requests.get("http://127.0.0.1:5000/summary")
            if response.status_code != 200:
                dispatcher.utter_message(text="Sorry, I couldn't retrieve your data summary.")
                return []

            result = response.json()
            low_dims = result.get("low_dimensions", [])
            summary = result.get("summary", {})

            relevant_dimensions = [
                "Completeness", "Consistency", "Traceability",
                "Understandability", "Currentness"
            ]

            method_requirements = {
                "ANOVA":         ["Accuracy", "Completeness", "Consistency", "Precision", "Understandability"],
                "Correlation":   ["Accuracy", "Completeness", "Consistency", "Understandability"],
                "NB":            ["Accuracy", "Completeness", "Understandability", "Consistency", "Credibility"],
                "DT":            ["Accuracy", "Completeness", "Consistency", "Understandability", "Traceability"],
                "Logistic":      ["Accuracy", "Completeness", "Consistency", "Understandability", "Traceability"],
                "KNN":           ["Accuracy", "Completeness", "Consistency", "Precision"],
                "Stepwise":      ["Accuracy", "Completeness", "Consistency", "Precision"],
                "BN":            ["Accuracy", "Completeness", "Consistency", "Credibility", "Traceability"],
                "K-Means":       ["Accuracy", "Completeness", "Consistency", "Precision"],
                "PCA":           ["Accuracy", "Completeness", "Consistency", "Precision"],
                "AE":            ["Accuracy", "Completeness", "Consistency", "Precision"],
                "RBM":           ["Accuracy", "Completeness", "Consistency", "Precision"],
                "DBM":           ["Accuracy", "Completeness", "Consistency", "Precision"],
                "AR":            ["Accuracy", "Completeness", "Consistency", "Currentness"],
                "MA":            ["Accuracy", "Completeness", "Consistency", "Currentness"],
                "ARIMA":         ["Accuracy", "Completeness", "Consistency", "Currentness"],
                "ARMA":          ["Accuracy", "Completeness", "Consistency", "Currentness"],
                "LR":            ["Accuracy", "Completeness", "Consistency", "Traceability", "Understandability"],
                "GLM":           ["Accuracy", "Completeness", "Consistency", "Traceability", "Understandability"],
                "Lasso":         ["Accuracy", "Completeness", "Precision", "Traceability", "Understandability"],
                "Ridge":         ["Accuracy", "Completeness", "Precision", "Traceability", "Understandability"],
                "Robust":        ["Accuracy", "Completeness", "Precision", "Traceability", "Understandability"],
                "RF":            ["Accuracy", "Completeness", "Consistency", "Traceability"],
                "RF Regression": ["Accuracy", "Completeness", "Consistency", "Traceability"],
                "GBM":           ["Accuracy", "Completeness", "Consistency", "Efficiency", "Traceability"],
                "SVM":           ["Accuracy", "Completeness", "Consistency", "Precision", "Traceability"],
                "SVR":           ["Accuracy", "Completeness", "Precision", "Consistency"],
                "MLP":           ["Accuracy", "Completeness", "Precision", "Consistency"],
                "DNN":           ["Accuracy", "Completeness", "Consistency", "Efficiency", "Precision"],
                "BPNN":          ["Accuracy", "Completeness", "Precision", "Consistency"],
                "CNN":           ["Accuracy", "Completeness", "Precision", "Consistency", "Efficiency"],
                "RNN":           ["Accuracy", "Completeness", "Precision", "Consistency"],
                "LSTM":          ["Accuracy", "Completeness", "Consistency", "Currentness", "Efficiency", "Precision"],
                "GRU":           ["Accuracy", "Completeness", "Consistency", "Precision", "Currentness"]
            }

            recommended = []
            for method, dims in method_requirements.items():
                if not any(dim in low_dims for dim in dims if dim in relevant_dimensions):
                    recommended.append(method)

            if recommended:
                dispatcher.utter_message(text=(
                    f"📊 I analyzed your uploaded data.\n"
                    f"⚠️ Detected quality issues in: {', '.join(low_dims) or 'None'}\n\n"
                    f"✅ Based on that, I recommend the following methods:\n" +
                    "\n".join(f"- {m}" for m in recommended)
                ))
                
                good_dims = [dim for dim in relevant_dimensions if dim not in low_dims]

                return [
                    SlotSet("recommended_methods", recommended),
                    SlotSet("user_quality_strengths", good_dims)
                ]
                
            else:
                dispatcher.utter_message(text=(
                    f"⚠️ Your data has quality issues in: {', '.join(low_dims)}.\n"
                    f"Unfortunately, none of the available methods are a good fit. Please consider improving your dataset."
                ))

        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred while recommending methods: {e}")
            return []

        return []

