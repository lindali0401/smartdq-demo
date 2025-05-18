from flask import Flask, request, jsonify
from together import Together
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

# Load method requirements and summaries
with open("method_knowledge.json") as f:
    method_docs = json.load(f)

method_requirements = {doc["method"]: doc.get("dimensions", []) for doc in method_docs}
documents = [f"{doc['method']} – {doc['summary']}" for doc in method_docs]

vectorizer = TfidfVectorizer()
doc_vectors = vectorizer.fit_transform(documents)

def retrieve_top_k_docs(query, k=3):
    query_vec = vectorizer.transform([query])
    scores = cosine_similarity(query_vec, doc_vectors).flatten()
    top_indices = scores.argsort()[-k:][::-1]
    return [documents[i] for i in top_indices]

def build_prompt(question: str, context_docs: list, recommended_methods: list, user_dims: list) -> str:
    user_dims_text = ", ".join(user_dims)
    context = "\n".join(context_docs)

    method_lines = []
    for method in recommended_methods:
        dims = method_requirements.get(method, [])
        matched = [d for d in dims if d in user_dims]
        method_lines.append(f"- {method}: requires {', '.join(dims)} | matches: {', '.join(matched) or 'none'}")

    method_info = "\n".join(method_lines)

    return f"""You are a data analytics assistant focused on data quality in industrial settings.

The following methods were recommended based on the user's data strengths: {user_dims_text}

{method_info}

Please answer the question below using only data quality reasoning.

Question:
{question}

Instructions:
1. Acknowledge the user's data strengths in {user_dims_text}.
2. Explain how the method depends on those dimensions.
3. Justify its suitability based on that overlap.
4. Do NOT explain how the method works in general.
5. Answer in no more than 150 words.
6. Use second-person phrasing throughout (e.g., your data, instead of the user's data).

You may refer to the following context:
{context}
"""

def call_llama3_with_prompt(prompt: str) -> str:
    response = client.chat.completions.create(
        model="meta-llama/Llama-Vision-Free",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=256
    )
    return response.choices[0].message.content.strip()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("prompt", "")
    recommended = data.get("recommended_methods", [])
    user_dims = data.get("user_quality_strengths", [])

    try:
        context_docs = retrieve_top_k_docs(question, k=3)
        prompt = build_prompt(question, context_docs, recommended, user_dims)
        answer = call_llama3_with_prompt(prompt)
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5056)

