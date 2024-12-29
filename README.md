# 🌟 Smart Travel Planner ✈️

**Smart Travel Planner** is a powerful, AI-driven travel planning tool designed to assist travelers in organizing their trips effortlessly. Whether you're planning a luxurious vacation, a mid-range getaway, or a budget-friendly trip, this app has you covered! It helps you find transportation options, book hotels, and discover exciting activities at your destination, all within your set budget.

## 🚀 Features

- **🗺️ Plan Your Trip**: Choose your origin, destination, budget, travel dates, and the type of trip (luxury, middle, or low). 
- **🚍 Transportation Recommendations**: Get real-time transportation options (flight, train, bus) that match your travel requirements.
- **🏨 Hotel & Activity Suggestions**: Receive recommendations for hotels and activities in your destination, all within your budget.
- **💰 Automatic Budget Allocation**: Select your preferred trip style (luxury, middle, or low), and the app will automatically allocate your budget between transportation, accommodation, and activities.
- **🧳 Real-Time Travel Data**: The backend integrates with third-party APIs to pull live information about transportation, hotels, and activities to give you the most up-to-date options.
- **🌍 Personalized Travel Plans**: Whether you're traveling solo or with a group, the app customizes your travel plan based on your inputs and preferences.

## 🛠️ Technologies Used

- **Streamlit**: Built the interactive and intuitive frontend of the app where users input their travel details and view the plan. 🌐
- **Google Colab**: Powers the backend of the app, running AI models and fetching real-time data from APIs like Tavily and Gemini 2.0. 🤖
- **Tavily API**: Retrieves transportation, hotel, and activity options based on user preferences. 🚗🏨🎡
- **LangChain**: Handles the integration of AI models and decision-making processes for personalized recommendations. 🧠
- **Gemini 2.0**: A powerful AI model used to process user inputs and generate relevant travel recommendations. 💬

## 🌍 Project Structure

This project is divided into two main components:

### 1. **Frontend** (Streamlit App)
The **frontend** is built with **Streamlit**, providing an interactive user interface where users can input their trip details. It seamlessly guides them through the process of selecting transportation, hotels, and activities, and displays the results in an easy-to-understand format.

- **Frontend Link**: [Smart Travel Planner Streamlit App](https://smart-travel-planner.streamlit.app/)

### 2. **Backend** (Google Colab)
The **backend** runs on **Google Colab** and handles the processing of user inputs. It uses advanced AI techniques to interact with APIs and return personalized recommendations for transportation, hotels, and activities. The backend integrates multiple tools, such as **LangChain** and **Gemini 2.0**, to provide the best recommendations based on user preferences.

- **Backend Link**: [Smart Travel Planner Backend on Google Colab](https://colab.research.google.com/drive/190lUlANW4wzy0Gqb38AkMPy_tyATHerB#scrollTo=dMqPdJ2uzyr_)

## 💡 How It Works

1. **User Input**: The user selects their travel details, such as origin, destination, budget, and preferred trip style (luxury, middle, or low).
2. **AI-Powered Recommendations**: Based on the inputs, the backend fetches real-time transportation options, hotels, and activities from third-party APIs like **Tavily** and **Gemini 2.0**.
3. **Personalized Travel Plan**: The system generates a personalized travel plan for the user, showing options for flights, trains, buses, hotels, and activities within the allocated budget.
4. **Budget Allocation**: Depending on the selected trip type, the app automatically allocates the budget between transportation, accommodation, and activities.

## 🌐 Frontend & Backend

- **Frontend (Streamlit App)**: The user interface is deployed on Streamlit and provides an interactive experience to input travel details and view the generated travel plan.
  
- **Backend (Google Colab)**: The backend handles the AI processing and makes real-time API calls to fetch transportation, hotel, and activity options based on the user's requirements.

---

Enjoy planning your next adventure with **Smart Travel Planner**! 🌟✈️🧳

Let us help you create the perfect travel plan in just a few clicks! 😊
