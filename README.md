# ScholarSense Analytics Platform

**Big Data Student Performance Analytics Dashboard**  
Built with **Streamlit + Pandas + Plotly**

---

## 🎯 Project Objective

To provide an **interactive and easy-to-use dashboard** for educators to analyze student performance, identify weak students, and predict final scores using data-driven insights.

---

## ✨ Key Features

- Interactive filters (School Type, Risk Score, High/Low Score Thresholds)
- Real-time Top Performers and Weak Students lists
- Risk vs Score analysis with dynamic thresholds
- Student performance prediction using trained ML model
- Multiple visualizations (Bar, Histogram, Pie, Scatter)
- CSV download option for all tables
- Clean and user-friendly interface suitable for school staff

---

## 🛠️ Tech Stack

- **Frontend/Dashboard**: Streamlit
- **Data Processing**: Pandas
- **Visualizations**: Plotly Express
- **Machine Learning**: scikit-learn (Linear Regression)
- **Big Data Foundation**: Apache Spark (PySpark) used in backend processing (Colab)
- **Model**: Saved `performance_model.pkl`

---

## 📁 Project Structure

```bash
ScholarSense-Analytics-Dashboard/
├── data/
│   └── Student_Performance.csv
├── processed/
│   ├── processed_students.csv
│   └── performance_model.pkl
├── frontend/
│   └── app.py
├── notebooks/
│   └── Colab_Backend.ipynb
├── requirements.txt
├── .gitignore
└── README.md
