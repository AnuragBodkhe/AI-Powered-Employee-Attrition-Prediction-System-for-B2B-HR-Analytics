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


def _load_meta(filename, default=None):
    """Safely load a pickle metadata file from models/ directory."""
    import joblib
    path = os.path.join(PROJECT_ROOT, 'models', filename)
    try:
        return joblib.load(path) if os.path.exists(path) else default
    except Exception:
        return default

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
        from utils.model_loader import predict_batch, load_thresholds

        df_feat    = preprocess_uploaded_csv(df_raw)
        df_results = predict_batch(df_feat, model_name)

        # Use the user-supplied threshold if different from optimal, else use model's optimal
        saved_thresholds = load_thresholds()
        optimal_thresh   = saved_thresholds.get(model_name, 0.5)
        # If user passed threshold explicitly (not default 0.5), honour it; else use optimal
        effective_thresh = threshold if threshold != 0.5 else optimal_thresh
        df_results['Risk_Level'] = df_results['Probability'].apply(
            lambda p: 'HIGH' if p >= 0.70 else ('MEDIUM' if p >= 0.40 else 'LOW'))

        # Save to latest batch results for dashboard
        df_export = df_raw.copy()
        df_export['Prediction']  = df_results['Prediction'].values
        df_export['Probability'] = df_results['Probability'].values
        df_export['Risk_Level']  = df_results['Risk_Level'].values
        latest_path = os.path.join(PROJECT_ROOT, 'data', 'latest_batch_results.csv')
        df_export.to_csv(latest_path, index=False)

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
            'total':         total,
            'leavers':       int(leavers),
            'high_risk':     int(high_r),
            'avg_prob':      avg_p,
            'threshold_used': round(effective_thresh, 4),
            'optimal_threshold': round(optimal_thresh, 4),
            'risk_counts':   df_results['Risk_Level'].value_counts().to_dict(),
            'high_risk_table': high_risk.to_dict(orient='records'),
            'csv_b64':       csv_b64,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── API: Dashboard chart data ──────────────────────────────────────────────────
@app.route('/api/chart-data')
def api_chart_data():
    try:
        data_dir  = os.path.join(PROJECT_ROOT, 'data')
        latest_path = os.path.join(data_dir, 'latest_batch_results.csv')

        if not os.path.exists(latest_path):
            return jsonify({'error': 'No batch prediction results found. Please run a <a href="/batch" style="text-decoration:underline">Batch Prediction</a> first to populate the dashboard.'}), 404

        df = pd.read_csv(latest_path)
        
        # Normalize column names so raw aliases like 'Job_Role' become 'JobRole'
        try:
            from utils.preprocess import COLUMN_ALIASES
            df.rename(columns=COLUMN_ALIASES, inplace=True)
            # Add some missing ones just in case the raw CSV uses slightly different casings
            df.rename(columns={
                'Years_at_Company': 'YearsAtCompany',
                'Years_in_Current_Role': 'YearsInCurrentRole',
                'Work_Environment_Satisfaction': 'EnvironmentSatisfaction',
                'Relationship_with_Manager': 'RelationshipSatisfaction',
                'Job_Involvement': 'JobInvolvement',
                'Job_Level': 'JobLevel'
            }, inplace=True)
        except ImportError:
            pass

        if 'Prediction' not in df.columns:
            return jsonify({'error': 'Invalid batch results format. Expected Prediction column.'}), 400

        # Map Prediction output ('Leave', 'Stay') back to Attrition format for legacy dashboard charts
        df['Attrition'] = df['Prediction'].map({'Leave': 'Yes', 'Stay': 'No'})
        df['Attrition_Num'] = df['Prediction'].map({'Leave': 1, 'Stay': 0})
        charts = {}

        # 1. Department attrition (Stacked)
        if 'Department' in df.columns:
            d_grp = df.groupby(['Department', 'Prediction']).size().unstack(fill_value=0)
            charts['department'] = {
                'labels': d_grp.index.tolist(),
                'stay': d_grp.get('Stay', pd.Series(0, index=d_grp.index)).tolist(),
                'leave': d_grp.get('Leave', pd.Series(0, index=d_grp.index)).tolist(),
            }

        # 2. JobRole attrition (Stacked)
        if 'JobRole' in df.columns:
            # Sort by total people in role or by leave count
            j_grp = df.groupby(['JobRole', 'Prediction']).size().unstack(fill_value=0)
            # Sort by highest leave count descending
            if 'Leave' in j_grp.columns:
                j_grp = j_grp.sort_values(by='Leave', ascending=True)
            charts['jobrole'] = {
                'labels': j_grp.index.tolist(),
                'stay': j_grp.get('Stay', pd.Series(0, index=j_grp.index)).tolist(),
                'leave': j_grp.get('Leave', pd.Series(0, index=j_grp.index)).tolist(),
            }

        # 3. Age histogram
        if 'Age' in df.columns:
            stay   = df[df['Attrition'] == 'No']['Age'].tolist()
            leave  = df[df['Attrition'] == 'Yes']['Age'].tolist()
            charts['age'] = {'stay': stay, 'leave': leave}

        # 4. Income box
        if 'MonthlyIncome' in df.columns:
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

        # 6. Radar Chart Analytics
        radar_cols = ['JobSatisfaction', 'EnvironmentSatisfaction', 'RelationshipSatisfaction', 'WorkLifeBalance', 'JobInvolvement']
        if all(c in df.columns for c in radar_cols):
            radar = df.groupby('Prediction')[radar_cols].mean().round(2)
            charts['radar'] = {
                'metrics': radar_cols,
                'stay': radar.loc['Stay'].tolist() if 'Stay' in radar.index else [0]*len(radar_cols),
                'leave': radar.loc['Leave'].tolist() if 'Leave' in radar.index else [0]*len(radar_cols),
            }

        # 7. Heatmap (Department vs JobLevel)
        if 'Department' in df.columns and 'JobLevel' in df.columns:
            val_col = 'Probability' if 'Probability' in df.columns else 'Attrition_Num'
            hm = df.groupby(['Department', 'JobLevel'])[val_col].mean().unstack(fill_value=0)
            charts['heatmap'] = {
                'y': hm.index.tolist(),
                'x': [f'Level {c}' for c in hm.columns],
                'z': (hm.values * (100 if val_col == 'Probability' else 1)).tolist(),
            }

        # 8. Leaderboard (Department + JobRole)
        if 'Department' in df.columns and 'JobRole' in df.columns:
            val_col = 'Probability' if 'Probability' in df.columns else 'Attrition_Num'
            df['Segment'] = df['Department'] + " — " + df['JobRole']
            lb = df.groupby('Segment')[val_col].mean().sort_values(ascending=False).head(5)
            lb = lb.iloc[::-1]
            charts['leaderboard'] = {
                'y': lb.index.tolist(),
                'x': (lb.values * (100 if val_col == 'Probability' else 1)).round(1).tolist(),
            }

        # 9. Grouped Bar (Tenure Metrics)
        tenure_cols = ['YearsAtCompany', 'YearsInCurrentRole', 'YearsSinceLastPromotion']
        if all(c in df.columns for c in tenure_cols):
            tb = df.groupby('Prediction')[tenure_cols].mean().round(1)
            charts['tenure'] = {
                'metrics': ['Company Tenure', 'Current Role Tenure', 'Years Since Promo'],
                'stay': tb.loc['Stay'].tolist() if 'Stay' in tb.index else [0]*3,
                'leave': tb.loc['Leave'].tolist() if 'Leave' in tb.index else [0]*3,
            }

        # 10. KPIs
        total    = len(df)
        attrited = (df['Attrition'] == 'Yes').sum()
        charts['kpis'] = {
            'total':   total,
            'attrited': int(attrited),
            'rate':    round(attrited / total * 100, 1) if total > 0 else 0,
            'avg_income': round(float(df['MonthlyIncome'].mean()), 0) if 'MonthlyIncome' in df.columns else None,
            'avg_age':    round(float(df['Age'].mean()), 1) if 'Age' in df.columns else None,
        }

        return jsonify(charts)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── API: Compare — run all models on one employee ─────────────────────────────
@app.route('/api/compare-predict', methods=['POST'])
def api_compare_predict():
    try:
        data = request.get_json()

        from utils.model_loader import predict_single, load_feature_names
        from utils.preprocess   import encode_input

        X_enc      = encode_input(data)
        feat_names = load_feature_names()
        emp_dict   = X_enc.iloc[0].to_dict()

        model_names = ['Random Forest', 'XGBoost', 'SVM', 'Logistic Regression']
        results     = {}

        for mname in model_names:
            res = predict_single(emp_dict, mname)
            if 'error' not in res:
                results[mname] = res
            else:
                results[mname] = {'prediction': 'N/A', 'probability': 0.0,
                                  'risk_level': 'N/A', 'error': res['error']}

        # SHAP for tree models only
        shap_all = {}
        try:
            import joblib, shap as shap_lib
            import numpy as np
            model_dir = os.path.join(PROJECT_ROOT, 'models')
            fname_map = {'Random Forest': 'random_forest.pkl',
                         'XGBoost': 'xgboost.pkl'}
            row_df = X_enc.reindex(columns=feat_names, fill_value=0)
            for mname, fname in fname_map.items():
                try:
                    clf       = joblib.load(os.path.join(model_dir, fname))
                    explainer = shap_lib.TreeExplainer(clf)
                    sv        = explainer.shap_values(row_df)
                    sv        = sv[1][0] if isinstance(sv, list) else sv[0]
                    pairs     = sorted(zip(feat_names, sv.tolist()),
                                       key=lambda x: abs(x[1]), reverse=True)[:8]
                    shap_all[mname] = [{'feature': f, 'shap': round(v, 5)} for f, v in pairs]
                except Exception:
                    pass
        except Exception:
            pass

        return jsonify({'results': results, 'shap': shap_all})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── API: Compare — run all models on batch CSV ─────────────────────────────────
@app.route('/api/compare-batch', methods=['POST'])
def api_compare_batch():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file      = request.files['file']
        threshold = float(request.form.get('threshold', 0.5))
        df_raw    = pd.read_csv(file)

        from utils.preprocess   import preprocess_uploaded_csv
        from utils.model_loader import predict_batch

        df_feat     = preprocess_uploaded_csv(df_raw)
        model_names = ['Random Forest', 'XGBoost', 'SVM', 'Logistic Regression']
        summary     = {}

        for mname in model_names:
            try:
                df_res = predict_batch(df_feat, mname)
                df_res['Risk_Level'] = df_res['Probability'].apply(
                    lambda p: 'HIGH' if p >= threshold else ('MEDIUM' if p >= 0.4 else 'LOW'))
                total   = len(df_res)
                leavers = int((df_res['Prediction'] == 'Leave').sum())
                high_r  = int((df_res['Risk_Level'] == 'HIGH').sum())
                avg_p   = round(float(df_res['Probability'].mean() * 100), 2)
                # Probability histogram buckets (0-10%, 10-20%, ... 90-100%)
                buckets = [0] * 10
                for p in df_res['Probability']:
                    idx = min(int(p * 10), 9)
                    buckets[idx] += 1
                summary[mname] = {
                    'total':   total,
                    'leavers': leavers,
                    'attrition_rate': round(leavers / total * 100, 2) if total else 0,
                    'high_risk':  high_r,
                    'medium_risk': int((df_res['Risk_Level'] == 'MEDIUM').sum()),
                    'low_risk':   int((df_res['Risk_Level'] == 'LOW').sum()),
                    'avg_prob': avg_p,
                    'risk_counts': df_res['Risk_Level'].value_counts().to_dict(),
                    'prob_buckets': buckets,
                }
            except Exception as me:
                summary[mname] = {'error': str(me)}

        saved_thresholds = {}
        try:
            from utils.model_loader import load_thresholds
            saved_thresholds = load_thresholds()
        except Exception:
            pass

        return jsonify({
            'total':    len(df_raw),
            'summary':  summary,
            'thresholds': saved_thresholds,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── API: Model Diagnostics ────────────────────────────────────────────────────
@app.route('/api/model-diagnostics')
def api_model_diagnostics():
    """
    Returns per-model metadata:
      - optimal thresholds saved during training
      - class ratio (imbalance)
      - whether calibration is active
      - feature count
    """
    try:
        import joblib
        thresholds   = _load_meta('threshold.pkl',      default={})
        class_ratio  = _load_meta('class_ratio.pkl',    default=None)
        best_model   = _load_meta('best_model_name.pkl', default='Random Forest')
        feature_names = _load_meta('feature_names.pkl',  default=[])

        model_names = ['Random Forest', 'XGBoost', 'Logistic Regression', 'SVM']
        model_files = {
            'Random Forest':       'random_forest.pkl',
            'XGBoost':             'xgboost.pkl',
            'Logistic Regression': 'logistic_regression.pkl',
            'SVM':                 'svm.pkl',
        }
        models_info = {}
        for name, fname in model_files.items():
            path = os.path.join(PROJECT_ROOT, 'models', fname)
            exists = os.path.exists(path)
            models_info[name] = {
                'exists':      exists,
                'threshold':   thresholds.get(name, 0.5),
                'calibrated':  name in ('Random Forest', 'XGBoost'),
                'scaled_input': name in ('Logistic Regression', 'SVM'),
                'is_best':     name == best_model,
            }

        return jsonify({
            'models':       models_info,
            'class_ratio':  round(class_ratio, 2) if class_ratio else None,
            'best_model':   best_model,
            'feature_count': len(feature_names),
            'feature_names': feature_names,
            'debiased':     os.path.exists(os.path.join(PROJECT_ROOT, 'models', 'threshold.pkl')),
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 55)
    print("  EAPS Flask App — Employee Attrition Prediction")
    print("  [Debiased Version — Optimal Thresholds Active]")
    print("  http://localhost:5000")
    print("=" * 55)
    app.run(debug=True, host='0.0.0.0', port=5000)

