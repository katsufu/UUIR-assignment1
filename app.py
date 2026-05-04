import os
import json
import torch
import torch.nn as nn
import gradio as gr
from sentence_transformers import SentenceTransformer

# Define the NN model class (must match training script)
class CVClassifierNN(nn.Module):
    def __init__(self, input_dim=384, hidden_dim=128):
        super(CVClassifierNN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 2)
        )

    def forward(self, x):
        return self.network(x)

MODEL_PATH = "./trained_model"

print("Loading Embedding Model...")
try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Error loading embedder: {e}")

print("Loading Neural Network Classifier...")
try:
    nn_model = CVClassifierNN(input_dim=384)
    nn_model.load_state_dict(torch.load(os.path.join(MODEL_PATH, "nn_model.pt")))
    nn_model.eval()
except Exception as e:
    print(f"Error loading NN model: {e}")
    nn_model = None

print("Loading historical embeddings for semantic search...")
try:
    historical_embeddings = torch.load(os.path.join(MODEL_PATH, "cv_embeddings.pt"))
    with open(os.path.join(MODEL_PATH, "cv_metadata.json"), "r", encoding="utf-8") as f:
        historical_metadata = json.load(f)
except Exception as e:
    print(f"Error loading semantic search data: {e}")
    historical_embeddings = None
    historical_metadata = []

def predict(cv_text):
    if not cv_text.strip():
        return {"Please enter a CV": 1.0}, "Please enter a CV"
        
    # Generate embedding
    embedding = embedder.encode([cv_text])
    embedding_tensor = torch.FloatTensor(embedding)
    
    # Predict with NN
    results = {}
    if nn_model:
        with torch.no_grad():
            outputs = nn_model(embedding_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
            
            results["Rejected"] = float(probabilities[0])
            results["Accepted"] = float(probabilities[1])
    else:
        results = {"Model Not Loaded": 1.0}
        
    # Sort results
    sorted_results = {k: v for k, v in sorted(results.items(), key=lambda item: item[1], reverse=True)}
    
    # Semantic Search
    similar_candidates_text = "No historical data found."
    if historical_embeddings is not None and len(historical_metadata) > 0:
        # Normalize embeddings for cosine similarity
        query_norm = torch.nn.functional.normalize(embedding_tensor, p=2, dim=1)
        hist_norm = torch.nn.functional.normalize(historical_embeddings, p=2, dim=1)
        
        # Compute Cosine Similarity
        cos_scores = torch.mm(query_norm, hist_norm.transpose(0, 1))[0]
        
        # Get top 3
        k = min(3, len(historical_metadata))
        top_results = torch.topk(cos_scores, k=k)
        
        top_candidates = []
        for score, idx in zip(top_results[0], top_results[1]):
            meta = historical_metadata[idx.item()]
            pos = meta.get("opening_position", "Unknown Position")
            res = meta.get("result", "Unknown Result")
            reason = meta.get("reason_for_result", "No reason provided")
            exp = meta.get("experience_years", "Unknown")
            
            # Format candidate info
            cand_info = f"### Position: {pos} (Score: {score.item():.2f})\n"
            cand_info += f"- **Outcome**: {res}\n"
            cand_info += f"- **Reason**: {reason}\n"
            cand_info += f"- **Experience**: {exp} years\n"
            cand_info += f"- **Excerpt**: \"{meta.get('cv', '')[:150]}...\"\n"
            top_candidates.append(cand_info)
            
        similar_candidates_text = "\n\n".join(top_candidates)

    return sorted_results, similar_candidates_text

custom_css = """
body { font-family: 'Inter', sans-serif; }
"""

with gr.Blocks() as demo:
    gr.Markdown(
        """
        # 📄 Candidate CV Evaluator & Semantic Search
        
        Paste a candidate's CV below. The system will predict whether the candidate is likely to be **Accepted** or **Rejected** based on our Neural Network model, and simultaneously perform a **Semantic Search** to find the top 3 most similar past applicants to provide context for the decision.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            input_text = gr.Textbox(
                lines=8, 
                placeholder="Paste the candidate's CV here...",
                label="Candidate CV"
            )
            submit_btn = gr.Button("Evaluate Candidate", variant="primary")
            
            gr.Examples(
                examples=[
                    ["Highly motivated professional seeking the Software Engineer position. I bring 5 years of hands-on experience in the field. My core competencies include: Python, Java, Docker, AWS. I have successfully led projects and delivered results that align with your requirements."],
                    ["Dedicated HR Manager with 2 years of experience. Skilled in Recruitment, Communication. Looking to leverage my background to contribute effectively to your team. While I am building my experience, my passion and dedication will drive my success."],
                    ["Results-driven individual targeting a Data Scientist role. I have 6 years of relevant industry experience and strong expertise in Python, Machine Learning, TensorFlow, SQL, Statistics. My past achievements demonstrate my ability to exceed expectations."]
                ],
                inputs=input_text
            )
            
        with gr.Column(scale=1):
            output_labels = gr.Label(label="Predicted Outcome Probability")
            
            gr.Markdown("### 🔍 Top 3 Similar Historical Candidates")
            output_articles = gr.Markdown()
            
    submit_btn.click(fn=predict, inputs=input_text, outputs=[output_labels, output_articles])

if __name__ == "__main__":
    demo.launch(share=False, theme=gr.themes.Soft(primary_hue="blue", neutral_hue="slate"), css=custom_css)
