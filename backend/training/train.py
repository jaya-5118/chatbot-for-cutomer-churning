"""
ML Training Pipeline for Intent Classification.

Steps:
  1. Load dataset
  2. Clean & normalize text
  3. Handle missing values
  4. Train/test split (stratified)
  5. TF-IDF feature extraction
  6. Train multiple classifiers (Logistic Regression, Naive Bayes, Linear SVM)
  7. Evaluate and compare
  8. Save best model + vectorizer

Usage:
  python training/train.py
"""

import os
import re
import sys
import json
import warnings

import numpy as np
import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────
RANDOM_SEED = 42
TEST_SIZE = 0.2
DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset.csv")
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "training_results.json")


# ──────────────────────────────────────────────────────────────────────────────
# Text Preprocessing
# ──────────────────────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    """Clean and normalize a single text string."""
    if not isinstance(text, str):
        return ""
    # Lowercase
    text = text.lower().strip()
    # Remove special characters but keep spaces and basic punctuation
    text = re.sub(r"[^a-zA-Z0-9\s\'\-]", " ", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ──────────────────────────────────────────────────────────────────────────────
# Main Training Pipeline
# ──────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("  INTENT CLASSIFICATION – MODEL TRAINING PIPELINE")
    print("=" * 70)

    # ── 1. Load dataset ──────────────────────────────────────────────────
    print("\n[1/8] Loading dataset...")
    if not os.path.exists(DATASET_PATH):
        print(f"  ERROR: Dataset not found at {DATASET_PATH}")
        print("  Run 'python training/generate_dataset.py' first.")
        sys.exit(1)

    df = pd.read_csv(DATASET_PATH)
    print(f"  Loaded {len(df)} rows, {df['intent'].nunique()} intents")

    # ── 2. Handle missing values ─────────────────────────────────────────
    print("\n[2/8] Handling missing values...")
    missing_before = df.isnull().sum().sum()
    df = df.dropna(subset=["text", "intent"])
    df = df[df["text"].str.strip() != ""]
    print(f"  Missing values found: {missing_before}")
    print(f"  Rows after cleaning: {len(df)}")

    # ── 3. Clean text ────────────────────────────────────────────────────
    print("\n[3/8] Cleaning and normalizing text...")
    df["text_clean"] = df["text"].apply(clean_text)
    print(f"  Sample: '{df['text'].iloc[0]}' -> '{df['text_clean'].iloc[0]}'")

    # ── 4. Train/test split ──────────────────────────────────────────────
    print("\n[4/8] Splitting into train/test sets...")
    X = df["text_clean"]
    y = df["intent"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y
    )
    print(f"  Train set: {len(X_train)} samples")
    print(f"  Test set:  {len(X_test)} samples")

    # ── 5. TF-IDF Feature Extraction ─────────────────────────────────────
    print("\n[5/8] Extracting TF-IDF features...")
    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True,
    )
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)
    print(f"  Vocabulary size: {len(tfidf.vocabulary_)}")
    print(f"  Feature matrix shape: {X_train_tfidf.shape}")

    # ── 6. Train multiple classifiers ────────────────────────────────────
    print("\n[6/8] Training classifiers...")

    classifiers = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, random_state=RANDOM_SEED, C=10.0, solver="lbfgs",
            multi_class="multinomial",
        ),
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.1),
        "Linear SVM": CalibratedClassifierCV(
            LinearSVC(max_iter=2000, random_state=RANDOM_SEED, C=1.0),
            cv=3,
        ),
    }

    results = {}
    for name, clf in classifiers.items():
        print(f"\n  Training {name}...")
        clf.fit(X_train_tfidf, y_train)

        # Predictions
        y_pred = clf.predict(X_test_tfidf)

        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        # Cross-validation
        cv_scores = cross_val_score(clf, X_train_tfidf, y_train, cv=5, scoring="accuracy")

        results[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "cv_mean": round(cv_scores.mean(), 4),
            "cv_std": round(cv_scores.std(), 4),
            "classifier": clf,
            "predictions": y_pred,
        }

        print(f"    Accuracy:   {acc:.4f}")
        print(f"    Precision:  {prec:.4f}")
        print(f"    Recall:     {rec:.4f}")
        print(f"    F1-Score:   {f1:.4f}")
        print(f"    CV Acc:     {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # ── 7. Select best model ─────────────────────────────────────────────
    print("\n[7/8] Selecting best model...")
    best_name = max(results, key=lambda k: results[k]["f1_score"])
    best = results[best_name]
    best_clf = best["classifier"]

    print(f"\n  *** Best Model: {best_name} ***")
    print(f"      F1-Score: {best['f1_score']:.4f}")
    print(f"      Accuracy: {best['accuracy']:.4f}")

    # Detailed classification report for best model
    print(f"\n  Classification Report ({best_name}):")
    print("  " + "-" * 66)
    report = classification_report(y_test, best["predictions"])
    for line in report.split("\n"):
        print(f"  {line}")

    # ── 8. Save model and vectorizer ─────────────────────────────────────
    print(f"\n[8/8] Saving model artifacts to {MODEL_DIR}...")
    os.makedirs(MODEL_DIR, exist_ok=True)

    model_path = os.path.join(MODEL_DIR, "intent_model.pkl")
    vectorizer_path = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
    label_path = os.path.join(MODEL_DIR, "label_classes.pkl")

    joblib.dump(best_clf, model_path)
    joblib.dump(tfidf, vectorizer_path)
    joblib.dump(list(y.unique()), label_path)

    print(f"  Saved: {model_path}")
    print(f"  Saved: {vectorizer_path}")
    print(f"  Saved: {label_path}")

    # Save training results as JSON (for README and evaluation)
    results_json = {}
    for name, r in results.items():
        results_json[name] = {
            "accuracy": r["accuracy"],
            "precision": r["precision"],
            "recall": r["recall"],
            "f1_score": r["f1_score"],
            "cv_mean": r["cv_mean"],
            "cv_std": r["cv_std"],
        }
    results_json["best_model"] = best_name
    results_json["dataset_size"] = len(df)
    results_json["num_intents"] = int(df["intent"].nunique())
    results_json["train_size"] = len(X_train)
    results_json["test_size"] = len(X_test)
    results_json["test_split"] = TEST_SIZE
    results_json["random_seed"] = RANDOM_SEED
    results_json["feature_extraction"] = "TF-IDF (max_features=5000, ngram_range=(1,2))"

    with open(RESULTS_PATH, "w") as f:
        json.dump(results_json, f, indent=2)
    print(f"  Saved: {RESULTS_PATH}")

    print("\n" + "=" * 70)
    print("  TRAINING COMPLETE")
    print("=" * 70)

    return results_json


if __name__ == "__main__":
    main()
