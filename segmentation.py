import streamlit as st
import numpy as np
import pandas as pd
import joblib

kmeans_model = joblib.load('kmeans_model.pkl')
scaler = joblib.load('scaler.pkl')

# Define feature columns and segment names
feature_columns = ['Gender', 'Age', 'City', 'Membership Type', 'Total Spend', 
                   'Items Purchased', 'Average Rating', 'Discount Applied', 
                   'Days Since Last Purchase', 'Satisfaction Level']
segment_names = ['VIP Loyalists', 'Big Spenders At Risk', 'Sleeping Mid-Tier', 'Dissatisfied & Churned']

# st.set_page_config(page_title("Customer Segmentation")
st.image("images/logo.png", width=150)  # replace with your real logo URL or local file
st.markdown("<h1 style='text-align: center; color: white;'>Customer Segmentation Predictor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaaaaa; font-size:18px;'>Powered by K-means + PCA • Built by Brightman</p>", unsafe_allow_html=True)
st.set_page_config(page_title="Customer Segmentation", layout="centered")
st.markdown("### Enter customer details to instantly see which segment they belong to:")

st.sidebar.header("Customer Input Features")

def user_input_features():
    # --- All 10 features in nice order ---
    gender = st.sidebar.selectbox('Gender', ['Female', 'Male'])
    age = st.sidebar.slider('Age', 18, 80, 35)
    city = st.sidebar.selectbox('City', 
        ['New York', 'Los Angeles', 'Chicago', 'San Francisco', 'Miami', 'Houston', 'Boston', 'Seattle'])
    
    membership = st.sidebar.selectbox('Membership Type', ['Bronze', 'Silver', 'Gold'])
    total_spend = st.sidebar.number_input('Total Spend ($)', min_value=0.0, value=850.0, step=10.0)
    items_purchased = st.sidebar.slider('Items Purchased', 1, 50, 12)
    average_rating = st.sidebar.slider('Average Rating', 1.0, 5.0, 4.2, step=0.1)
    discount_applied = st.sidebar.selectbox('Discount Applied?', ['No', 'Yes'])
    days_since_last = st.sidebar.slider('Days Since Last Purchase', 0, 365, 20)
    satisfaction = st.sidebar.selectbox('Satisfaction Level', 
        ['Unsatisfied', 'Neutral', 'Satisfied'])

    data = {
        'Gender': gender,
        'Age': age,
        'City': city,
        'Membership Type': membership,
        'Total Spend': total_spend,
        'Items Purchased': items_purchased,
        'Average Rating': average_rating,
        'Discount Applied': discount_applied,
        'Days Since Last Purchase': days_since_last,
        'Satisfaction Level': satisfaction
    }
    return pd.DataFrame(data, index=[0])

df_input = user_input_features()

def preprocess_input(df):
    df_processed = df.copy()
    
    # Same encoding as during training
    df_processed['Gender'] = df_processed['Gender'].map({'Female': 0, 'Male': 1})
    df_processed['City'] = df_processed['City'].astype('category').cat.codes
    df_processed['Membership Type'] = df_processed['Membership Type'].map({'Bronze': 0, 'Silver': 1, 'Gold': 2})
    df_processed['Discount Applied'] = df_processed['Discount Applied'].map({'No': 0, 'Yes': 1})
    df_processed['Satisfaction Level'] = df_processed['Satisfaction Level'].map({
        'Unsatisfied': 0, 'Neutral': 1, 'Satisfied': 2
    })
    
    df_processed = df_processed[feature_columns]           # exact column order
    scaled = scaler.transform(df_processed.values.reshape(1, -1))  # ← THIS LINE FIXES EVERYTHING
    
    return scaled

if st.button("Predict Customer Segment"):
    try:
        X = preprocess_input(df_input)
        cluster_id = kmeans_model.predict(X)[0]
        segment = segment_names[cluster_id]
        
        # Color mapping for nice display
        color_map = {
            'VIP Loyalists': '🟦',
            'Big Spenders At Risk': '🟠',
            'Sleeping Mid-Tier': '🟢',
            'Dissatisfied & Churned': '🔴'
        }
        
        st.markdown(f"""
        ## {color_map.get(segment, '⚪')} **{segment}**
        """)
        
        if segment == 'VIP Loyalists':
            st.success("This is your BEST customer! Reward them heavily.")
        elif segment == 'Big Spenders At Risk':
            st.warning("High spender but unhappy — act fast to retain!")
        elif segment == 'Sleeping Mid-Tier':
            st.info("Good potential — wake them up with targeted offers.")
        elif segment == 'Dissatisfied & Churned':
            st.error("High churn risk — consider win-back campaign or let go.")
            
        st.balloons()
        
    except Exception as e:
        st.error(f"Error: {e}")

# Show raw input table
st.write("### Input Data Preview")
st.dataframe(df_input.T.rename(columns={0: "Value"}), width=700)