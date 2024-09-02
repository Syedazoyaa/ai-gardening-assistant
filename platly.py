import streamlit as st
import numpy as np
from PIL import Image
import requests
import base64
import google.generativeai as genai

# Google Gemini API setup
genai.configure(api_key="AIzaSyDODWuZj0Xd8RK4QFPqP4Wttze7Zoyyx6g")
model = genai.GenerativeModel("gemini-1.0-pro")
chat = model.start_chat(history=[])

# Unsplash API setup
UNSPLASH_ACCESS_KEY = 'sedpZQEtU0fdAPlHZqIjucHGjFj4JDbaLgYajhPWNqY'
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

# Function to fetch plant images from Unsplash API
def fetch_plant_image(plant_name):
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    params = {
        "query": f"{plant_name} plant",
        "per_page": 1
    }
    response = requests.get(UNSPLASH_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['regular']
    return None

# Function to generate plant care guide using Gemini model
def generate_plant_guide(plant_name):
    msg = f"Generate a care guide for the plant '{plant_name}' including the following features: " \
          f"1. Watering needs, " \
          f"2. Fertilizer needs (if required, specify what kind), " \
          f"3. Type of soil required and its pH, no need of hardy zone and all, " \
          f"4. Optimal temperature range, " \
          f"5. Pruning requirements, " \
          f"6. Various parts of the plant which are useful, and " \
          f"7. Any extra care."
    response = chat.send_message(msg, stream=True)
    return ''.join([chunk.text for chunk in response])  # Extract the text content from the response

# Function to recommend plants based on user preferences using the Gemini model
def recommend_plants(plant_type, growth_habit, growth_place, maintenance_level, sunlight):
    msg = f"Recommend 3 home gardening plants based on the following preferences and also give only the names of three plants as output without any extra information and try to recommend the most common or known type of plants in India and also the main name of plant not its wide category do not number it just give the names of them: " \
          f"Plant Type: {plant_type}, " \
          f"Growth Habit: {growth_habit}, " \
          f"Growth Place: {growth_place}, " \
          f"Maintenance Level: {maintenance_level}, " \
          f"Sunlight Requirement: {sunlight}."
    response = chat.send_message(msg, stream=True)
    
    # Extract plant names from the response
    recommendations = ''.join([chunk.text for chunk in response]).split('\n')[:3]  # Extract the text content and split by line
    plant_names = [plant.strip() for plant in recommendations if plant.strip()]
    
    return plant_names

# Function to set background image
def set_background_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Initialize session state variables
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'selected_plant' not in st.session_state:
    st.session_state.selected_plant = None
if 'query_response' not in st.session_state:
    st.session_state.query_response = None

# Streamlit UI
set_background_image("bg (1).png")

st.markdown("<h1 style='text-align: center; color: white; font-weight: bold;'>🌿 Home Gardening AI Assistant 🌼</h1>", unsafe_allow_html=True)

# Sidebar for chatbot
with st.sidebar:
    st.markdown("<h2 style='font-weight: bold;'>Ask Me Anything About Plants 🌻</h2>", unsafe_allow_html=True)
    user_query = st.text_input("Enter your query here:")
    if st.button("Ask"):
        st.session_state.query_response = ''.join([chunk.text for chunk in chat.send_message(user_query, stream=True)])
    if st.session_state.query_response:
        st.markdown("<b>🤖 Chatbot Response:</b>", unsafe_allow_html=True)
        st.markdown(f"<b>{st.session_state.query_response}</b>", unsafe_allow_html=True)

# Main content for plant recommendations
st.markdown("<h2 style='font-weight: bold;'>Discover Your Perfect Plant 🌱</h2>", unsafe_allow_html=True)
plant_type = st.selectbox("Select Plant Type", ["Ornamental", "Vegetable", "Fruit", "Flower", "Medicinal"])
growth_habit = st.selectbox("Select Growth Habit", ["Bushy", "Herb", "Upright", "Climber"])
growth_place = st.selectbox("Select Growth Place", ["Pot", "Ground"])
maintenance_level = st.selectbox("Select Maintenance Level", ["Low", "Moderate", "High"])
sunlight = st.selectbox("Select Sunlight Requirement", ["Low", "Moderate", "High"])

if st.button("Find Your Green Companions 🌳"):
    st.session_state.recommendations = recommend_plants(plant_type, growth_habit, growth_place, maintenance_level, sunlight)
    st.session_state.selected_plant = None

if st.session_state.recommendations:
    st.markdown("<b>🌟 Here are some green gems for you! 🌟</b>", unsafe_allow_html=True)
    for plant in st.session_state.recommendations:
        st.markdown(f"<b>{plant}</b>", unsafe_allow_html=True)
    
    selected_plant = st.selectbox("Select a Plant for Care Guide", st.session_state.recommendations)
    
    if st.button("Generate Care Guide 🌿"):
        st.session_state.selected_plant = selected_plant

if st.session_state.selected_plant:
    image_url = fetch_plant_image(st.session_state.selected_plant)
    if image_url:
        st.image(image_url, caption=st.session_state.selected_plant)

    care_guide = generate_plant_guide(st.session_state.selected_plant)
    st.markdown(f"<h3 style='font-weight: bold;'>🌱 Care Guide for {st.session_state.selected_plant}:</h3>", unsafe_allow_html=True)
    st.markdown(f"<b>{care_guide}</b>", unsafe_allow_html=True)

# Garden Placement Planning Tool
st.markdown("<h2 style='font-weight: bold;'>Garden Placement Planning Tool 🌼</h2>", unsafe_allow_html=True)

def generate_recommendations_and_placements(soil_patch_size, sunlight_exposure):
    msg = f"Recommend 3 plants and their placements based on the following garden conditions: " \
          f"Largest Soil Patch Size: {soil_patch_size} pixels, " \
          f"Sunlight Exposure: {sunlight_exposure}. " \
          f"Provide the recommendations in the format: Plant Name - Placement - Reason for Placement."
    response = chatbot.chat(msg)
    
    recommendations = response['text'].split('\n')
    return [rec.strip() for rec in recommendations if rec.strip()]

# Image upload or capture
uploaded_image = st.file_uploader("Upload an image of your garden space", type=['jpg', 'jpeg', 'png'])

if uploaded_image is not None:
    # Convert the uploaded image to a format suitable for OpenCV
    image = Image.open(uploaded_image).convert('RGB')
    image_np = np.array(image)

    # Analyze the image and extract features
    soil_patch_size, sunlight_exposure = analyze_image(image_np)
    
    # Generate recommendations and placements
    recommendations = generate_recommendations_and_placements(soil_patch_size, sunlight_exposure)
    
    # Display the original image
    st.image(image, caption='Uploaded Image', use_column_width=True)
    
    # Display recommendations and placements
    st.subheader("Plant Recommendations and Placements")
    st.write(f"**Sunlight Exposure:** {sunlight_exposure}")
    st.write(f"**Largest Soil Patch Size:** {soil_patch_size} pixels")
    st.write("**Recommended Plants and Their Placements:**")
    for recommendation in recommendations:
        st.write(f"- {recommendation}")
