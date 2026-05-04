import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import os
import joblib
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score

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

def train_models():
    os.makedirs('trained_model', exist_ok=True)
    os.makedirs('results', exist_ok=True)

    print("Loading data...")
    with open('data/recruitment_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Splitting dataset for HuggingFace...")
    train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)
    
    with open('data/train.json', 'w', encoding='utf-8') as f:
        json.dump(train_data, f, ensure_ascii=False, indent=4)
    with open('data/test.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=4)

    label_map = {"Rejected": 0, "Accepted": 1}
    
    cvs_train = [item['cv'] for item in train_data]
    y_train = np.array([label_map[item['result']] for item in train_data])
    
    cvs_test = [item['cv'] for item in test_data]
    y_test = np.array([label_map[item['result']] for item in test_data])

    print("Generating embeddings using sentence-transformers/all-MiniLM-L6-v2...")
    # This is chosen because it's fast and highly efficient for sentence/paragraph-level embeddings.
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Encoding train set...")
    X_train = embedder.encode(cvs_train, show_progress_bar=True)
    print("Encoding test set...")
    X_test = embedder.encode(cvs_test, show_progress_bar=True)
    
    # Save embeddings for semantic search in Gradio app
    print("Saving combined embeddings for semantic search...")
    X_all = np.vstack((X_train, X_test))
    data_all = train_data + test_data
    torch.save(torch.tensor(X_all), 'trained_model/cv_embeddings.pt')
    with open('trained_model/cv_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(data_all, f, ensure_ascii=False, indent=4)
        
    metrics = {}

    print("\n--- Training Random Forest ---")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_preds)
    rf_f1 = f1_score(y_test, rf_preds)
    print(f"Random Forest Accuracy: {rf_acc:.4f}, F1: {rf_f1:.4f}")
    joblib.dump(rf, 'trained_model/rf_model.pkl')
    metrics['RandomForest'] = {"accuracy": rf_acc, "f1": rf_f1}

    print("\n--- Training SVM ---")
    svm = SVC(kernel='linear', probability=True, random_state=42)
    svm.fit(X_train, y_train)
    svm_preds = svm.predict(X_test)
    svm_acc = accuracy_score(y_test, svm_preds)
    svm_f1 = f1_score(y_test, svm_preds)
    print(f"SVM Accuracy: {svm_acc:.4f}, F1: {svm_f1:.4f}")
    joblib.dump(svm, 'trained_model/svm_model.pkl')
    metrics['SVM'] = {"accuracy": svm_acc, "f1": svm_f1}

    print("\n--- Training PyTorch Neural Network ---")
    X_train_t = torch.FloatTensor(X_train)
    y_train_t = torch.LongTensor(y_train)
    X_test_t = torch.FloatTensor(X_test)
    y_test_t = torch.LongTensor(y_test)

    train_dataset = TensorDataset(X_train_t, y_train_t)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    nn_model = CVClassifierNN(input_dim=X_train.shape[1])
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(nn_model.parameters(), lr=0.001)

    epochs = 20
    nn_model.train()
    for epoch in range(epochs):
        epoch_loss = 0
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = nn_model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

    nn_model.eval()
    with torch.no_grad():
        test_outputs = nn_model(X_test_t)
        _, nn_preds = torch.max(test_outputs, 1)
        nn_preds = nn_preds.numpy()

    nn_acc = accuracy_score(y_test, nn_preds)
    nn_f1 = f1_score(y_test, nn_preds)
    print(f"NN Accuracy: {nn_acc:.4f}, F1: {nn_f1:.4f}")
    torch.save(nn_model.state_dict(), 'trained_model/nn_model.pt')
    metrics['PyTorchNN'] = {"accuracy": nn_acc, "f1": nn_f1}

    # Save evaluation results
    with open('results/evaluation.json', 'w') as f:
        json.dump(metrics, f, indent=4)

    # Determine best model based on F1
    best_model_name = max(metrics, key=lambda k: metrics[k]['f1'])
    print(f"\nBest model based on F1-score: {best_model_name}")

    with open('trained_model/best_model_info.json', 'w') as f:
        json.dump({"best_model": best_model_name}, f)

if __name__ == "__main__":
    train_models()
