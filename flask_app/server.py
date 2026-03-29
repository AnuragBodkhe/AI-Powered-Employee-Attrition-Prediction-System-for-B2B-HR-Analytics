"""
flask_app/server.py
===================
EAPS — Employee Attrition Prediction System
Flask Web App Entry Point (No Streamlit required)

Usage:
    pip install flask
    python flask_app/server.py

Opens at: http://localhost:5000
"""

import os, sys

# Add project root to path so utils/ is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, render_template, jsonify, request, send_file
import pandas as pd
import io

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB upload limit

# ── Helper: check if models exist ─────────────────────────────────────────────
def get_models_status():
    model_dir = os.path.join(PROJECT_ROOT, 'models')
    files = ['random_forest.pkl', 'xgboost.pkl',
             'logistic_regression.pkl', 'svm.pkl', 'scaler.pkl']
    found = [f for f in files if os.path.exists(os.path.join(model_dir, f))]
    return len(found), len(files)

# ── Page Routes ───────────────────────────────────────────────────────────────
@app.route('/')
def home():
    trained, total = get_models_status()
    return render_template('index.html', models_trained=trained, models_total=total)

@app.route('/predict')
def predict_page():
    return render_template('predict.html')

@app.route('/batch')
def batch_page():
    return render_template('batch.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/compare')
def compare_page():
    return render_template('compare.html')


# ── API: Single prediction ─────────────────────────────────────────────────────
@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data       = request.get_json()
        model_name = data.pop('model_name', 'Random Forest')

        from utils.model_loader  import predict_single, load_feature_names
        from utils.preprocess    import encode_input

        # Encode categorical → numeric
        X_enc  = encode_input(data)
        result = predict_single(X_enc.iloc[0].to_dict(), model_name)

        if 'error' in result:
            return jsonify({'error': result['error']}), 400

        # SHAP explanation (top 8 features)
        shap_data = []
        try:
            import joblib, shap as shap_lib
            import numpy as np
            model_dir  = os.path.join(PROJECT_ROOT, 'models')
            fname_map  = {'Random Forest': 'random_forest.pkl',
                          'XGBoost': 'xgboost.pkl',
                          'Logistic Regression': 'logistic_regression.pkl',
                          'SVM': 'svm.pkl'}
            clf        = joblib.load(os.path.join(model_dir, fname_map[model_name]))
            feat_names = load_feature_names()
            row_df     = X_enc[feat_names] if all(f in X_enc.columns for f in feat_names) \
                         else X_enc.reindex(columns=feat_names, fill_value=0)

            explainer  = shap_lib.TreeExplainer(clf)
            sv         = explainer.shap_values(row_df)
            sv         = sv[1][0] if isinstance(sv, list) else sv[0]

            pairs = sorted(zip(feat_names, sv.tolist()),
                           key=lambda x: abs(x[1]), reverse=True)[:8]
            shap_data = [{'feature': f, 'shap': round(v, 5)} for f, v in pairs]
        except Exception:
            pass

        result['shap'] = shap_data
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── API: Batch prediction ──────────────────────────────────────────────────────
@app.route('/api/batch', methods=['POST'])
def api_batch():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file       = request.files['file']
        model_name = request.form.get('model_name', 'Random Forest')
        threshold  = float(request.form.get('threshold', 0.5))

        df_raw     = pd.read_csv(file)

        from utils.preprocess   import preprocess_uploaded_csv
        from utils.model_loader import predict_batch

        df_feat    = preprocess_uploaded_csv(df_raw)
        df_results = predict_batch(df_feat, model_name)

        # Re-apply custom threshold
        df_results['Risk_Level'] = df_results['Probability'].apply(
            lambda p: 'HIGH' if p >= threshold else ('MEDIUM' if p >= 0.4 else 'LOW'))

        total   = len(df_results)
        leavers = (df_results['Prediction'] == 'Leave').sum()
        high_r  = (df_results['Risk_Level'] == 'HIGH').sum()
        avg_p   = round(float(df_results['Probability'].mean() * 100), 1)

        # Top 20 high-risk employees for table preview
        preview_cols = ['Prediction', 'Probability', 'Risk_Level']
        for col in ['Age', 'Department', 'JobRole', 'MonthlyIncome', 'OverTime']:
            if col in df_raw.columns:
                df_results[col] = df_raw[col].values
                preview_cols    = [col] + preview_cols

        high_risk = df_results[df_results['Risk_Level'] == 'HIGH']\
                        .sort_values('Probability', ascending=False)\
                        .head(20)[preview_cols].round({'Probability': 4})

        # Full CSV as base64 for download
        import base64
        buf = io.BytesIO()
        df_results.to_csv(buf, index=False)
        csv_b64 = base64.b64encode(buf.getvalue()).decode()

        return jsonify({
            'total':    total,
            'leavers':  int(leavers),
            'high_risk': int(high_r),
            'avg_prob': avg_p,
            'risk_counts': df_results['Risk_Level'].value_counts().to_dict(),
            'high_risk_table': high_risk.to_dict(orient='records'),
            'csv_b64': csv_b64,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── API: Dashboard chart data ──────────────────────────────────────────────────
@app.route('/api/chart-data')
def api_chart_data():
    try:
        data_dir  = os.path.join(PROJECT_ROOT, 'data')
        ibm_path  = os.path.join(data_dir, 'WA_Fn-UseC_-HR-Employee-Attrition.csv')
        cust_path = os.path.join(data_dir, 'employee_attrition_dataset.csv')

        if os.path.exists(ibm_path):
            df = pd.read_csv(ibm_path)
        elif os.path.exists(cust_path):
            df = pd.read_csv(cust_path)
            df.rename(columns={
                'Marital_Status': 'MaritalStatus', 'Job_Role': 'JobRole',
                'Monthly_Income': 'MonthlyIncome', 'Work_Life_Balance': 'WorkLifeBalance',
                'Job_Satisfaction': 'JobSatisfaction', 'Overtime': 'OverTime',
            }, inplace=True)
            df['Attrition'] = df['Attrition'].map(
                lambda x: 'Yes' if str(x).strip().lower() in ['yes','1','true'] else 'No')
        else:
            return jsonify({'error': 'No dataset found in data/'}), 404

        df['Attrition_Num'] = df['Attrition'].map({'Yes': 1, 'No': 0})
        charts = {}

        # 1. Department attrition
        dept = df.groupby('Department')['Attrition_Num'].mean().reset_index()
        charts['department'] = {
            'x': dept['Department'].tolist(),
            'y': (dept['Attrition_Num'] * 100).round(1).tolist(),
        }

        # 2. JobRole attrition (top 9)
        if 'JobRole' in df.columns:
            role = df.groupby('JobRole')['Attrition_Num'].mean().reset_index()\
                     .sort_values('Attrition_Num', ascending=True)
            charts['jobrole'] = {
                'y': role['JobRole'].tolist(),
                'x': (role['Attrition_Num'] * 100).round(1).tolist(),
            }

        # 3. Age histogram
        stay   = df[df['Attrition'] == 'No']['Age'].tolist()
        leave  = df[df['Attrition'] == 'Yes']['Age'].tolist()
        charts['age'] = {'stay': stay, 'leave': leave}

        # 4. Income box
        income_stay  = df[df['Attrition'] == 'No']['MonthlyIncome'].tolist()
        income_leave = df[df['Attrition'] == 'Yes']['MonthlyIncome'].tolist()
        charts['income'] = {'stay': income_stay, 'leave': income_leave}

        # 5. Overtime
        if 'OverTime' in df.columns:
            ot = df.groupby(['OverTime', 'Attrition']).size().unstack(fill_value=0).reset_index()
            charts['overtime'] = {
                'labels': ot['OverTime'].tolist(),
                'no':  ot.get('No', pd.Series([0]*len(ot))).tolist(),
                'yes': ot.get('Yes', pd.Series([0]*len(ot))).tolist(),
            }

        # 6. KPIs
        total    = len(df)
        attrited = (df['Attrition'] == 'Yes').sum()
        charts['kpis'] = {
            'total':   total,
            'attrited': int(attrited),
            'rate':    round(attrited / total * 100, 1),
            'avg_income': round(float(df['MonthlyIncome'].mean()), 0),
            'avg_age':    round(float(df['Age'].mean()), 1),
        }

        return jsonify(charts)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 55)
    print("  EAPS Flask App — Employee Attrition Prediction")
    print("  http://localhost:5000")
    print("=" * 55)
    app.run(debug=True, host='0.0.0.0', port=5000)
