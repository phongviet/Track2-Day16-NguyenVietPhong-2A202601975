import time
import json
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, precision_score, recall_score

def run_benchmark():
    results = {}
    
    # 1. Đo thời gian Load Data
    print("--> 1. Loading dataset...")
    start_load = time.perf_counter()
    data_path = "creditcard.csv"
    df = pd.read_csv(data_path)
    load_time = time.perf_counter() - start_load
    results["load_time_seconds"] = round(load_time, 4)
    print(f"Data shape: {df.shape} | Load time: {load_time:.4f}s")
    
    # Tách Features & Target
    X = df.drop(columns=["Class"])
    y = df["Class"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 2. Huấn luyện mô hình LightGBM
    print("--> 2. Training LightGBM model...")
    model = lgb.LGBMClassifier(
        n_estimators=100,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    
    start_train = time.perf_counter()
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        callbacks=[lgb.early_stopping(stopping_rounds=10, verbose=False)]
    )
    train_time = time.perf_counter() - start_train
    results["train_time_seconds"] = round(train_time, 4)
    results["best_iteration"] = model.best_iteration_ if hasattr(model, "best_iteration_") else 100
    print(f"Training completed in: {train_time:.4f}s | Best iteration: {results['best_iteration']}")
    
    # 3. Đánh giá trên tập test
    print("--> 3. Evaluating test metrics...")
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    results["auc_roc"] = round(float(roc_auc_score(y_test, y_pred_proba)), 6)
    results["accuracy"] = round(float(accuracy_score(y_test, y_pred)), 6)
    results["f1_score"] = round(float(f1_score(y_test, y_pred)), 6)
    results["precision"] = round(float(precision_score(y_test, y_pred)), 6)
    results["recall"] = round(float(recall_score(y_test, y_pred)), 6)
    
    # 4. Đo Inference Latency (1 dòng)
    print("--> 4. Measuring inference latency (1 row)...")
    sample_single = X_test.iloc[[0]]
    # Warm-up
    for _ in range(10):
        _ = model.predict_proba(sample_single)
        
    latencies = []
    for _ in range(100):
        t0 = time.perf_counter()
        _ = model.predict_proba(sample_single)
        latencies.append(time.perf_counter() - t0)
        
    avg_latency_ms = (np.mean(latencies)) * 1000  # Chuyển sang ms
    results["inference_latency_single_row_ms"] = round(float(avg_latency_ms), 4)
    
    # 5. Đo Inference Throughput (1000 dòng)
    print("--> 5. Measuring inference throughput (1000 rows)...")
    sample_1k = X_test.iloc[:1000]
    
    # Warm-up
    for _ in range(5):
        _ = model.predict_proba(sample_1k)
        
    t0 = time.perf_counter()
    num_runs = 50
    for _ in range(num_runs):
        _ = model.predict_proba(sample_1k)
    total_time = time.perf_counter() - t0
    
    throughput_samples_per_sec = (1000 * num_runs) / total_time
    results["inference_throughput_samples_per_sec"] = round(float(throughput_samples_per_sec), 2)
    
    # 6. Ghi kết quả ra benchmark_result.json
    with open("benchmark_result.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print("\n" + "="*50)
    print(" BENCHMARK RESULTS")
    print("="*50)
    for k, v in results.items():
        print(f" {k:<40}: {v}")
    print("="*50)
    print("--> Saved results to benchmark_result.json successfully!")

if __name__ == "__main__":
    run_benchmark()
