# import requests
# from typing import Any, Text, Dict, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher

# class ActionQueryHaystack(Action):
#     def name(self) -> Text:
#         return "action_query_rag"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         user_message = tracker.latest_message.get("text")
#         haystack_api_url = "http://localhost:5056/chat"  # 调你的 Flask server

#         try:
#             response = requests.post(
#                 haystack_api_url,
#                 json={"prompt": user_message},
#                 timeout=10
#             )
#             response.raise_for_status()
#             reply = response.json().get("response", "LLM didn't respond.")
#         except Exception as e:
#             reply = f"Error in actions: {str(e)}"

#         dispatcher.utter_message(text=reply)
#         return []

import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionQueryHaystack(Action):
    def name(self) -> Text:
        return "action_query_rag"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get("text")
        # llm_api_url = "http://localhost:5056/chat"  # 你的 Flask server 地址
        llm_api_url = "http://rag_server:5056/chat"

        # 读取之前推荐的算法和用户维度
        recommended_methods = tracker.get_slot("recommended_methods") or []
        user_quality_strengths = tracker.get_slot("user_quality_strengths") or []

        try:
            response = requests.post(
                llm_api_url,
                json={
                    "prompt": user_message,
                    "recommended_methods": recommended_methods,
                    "user_quality_strengths": user_quality_strengths
                },
                timeout=10
            )
            response.raise_for_status()
            reply = response.json().get("response", "LLM didn't respond.")
        except Exception as e:
            reply = f"Error in actions: {str(e)}"

        dispatcher.utter_message(text=reply)
        return []

