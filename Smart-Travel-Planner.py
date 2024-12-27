import streamlit as st
import speech_recognition as sr
import pyttsx3
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient
import json
from datetime import datetime
from dotenv import load_dotenv
import os
from langgraph.graph import Graph

# Load environment variables from the .env file
load_dotenv()

# Initialize Gemini 2.0 using the API key from the .env file
api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    api_key=api_key
)

# Initialize Tavily Client using the API key from the .env file
tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

# Initialize LangGraph
graph = Graph()

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to handle invalid input
def handle_invalid_input():
    st.error("❌ I am a travel planner. I can only assist with travel planning. Please provide a valid query.")

# Function to validate and retrieve structured input
def get_input(prompt):
    user_input = st.text_input(prompt)
    return user_input

# Function to validate if the entered input is a valid number
def get_float_input(prompt):
    user_input = st.text_input(prompt)
    if user_input.strip() == "":
        st.error("❌ Please enter a valid number.")
        return None
    try:
        return float(user_input)
    except ValueError:
        st.error("❌ Invalid number. Please enter a valid number.")
        return None

# Function to check if the entered date is valid
def validate_date(travel_date):
    today = datetime.now().date()
    try:
        user_date = datetime.strptime(travel_date, "%Y-%m-%d").date()
        if user_date < today:
            return False, "❌ The travel date has already passed. Please enter a valid future date."
        return True, user_date
    except ValueError:
        return False, "❌ Invalid date format. Please use YYYY-MM-DD."

# Function to convert budget and prices based on currency
def convert_currency(amount, currency):
    conversion_rates = {"usd": 1, "pkr": 275}  # Example conversion rates
    if currency.lower() not in conversion_rates:
        return None, "❌ Unsupported currency. Please use USD or PKR."
    converted_amount = float(amount) * conversion_rates[currency.lower()]
    return converted_amount, None

# Function to filter and format transportation options
def filter_transportation_options(results):
    filtered_results = []
    for result in results:
        if "ticket" in result.get('title', '').lower() or "booking" in result.get('url', '').lower():
            price = result.get('price', 'N/A')
            if price != 'N/A' and price != "":
                try:
                    # Try to convert the price to float, if valid
                    price = float(price.replace('$', '').replace('₹', '').replace(currency.upper(), "").strip())
                except ValueError:
                    price = 'N/A'
            filtered_results.append({
                "title": result.get('title', 'Unknown Option'),
                "url": result.get('url', 'N/A'),
                "price": price
            })
    # Ensure exactly 5 options, even if the data is incomplete
    while len(filtered_results) < 5:
        filtered_results.append({
            "title": "No More Options Available",
            "url": "N/A",
            "price": "N/A"
        })
    return filtered_results

# Function to save the travel plan
def save_travel_plan(travel_plan):
    with open('saved_travel_plans.json', 'a') as f:
        json.dump(travel_plan, f)
        f.write("\n")

# Function to load saved travel plans
def load_saved_travel_plans():
    try:
        with open('saved_travel_plans.json', 'r') as f:
            saved_plans = f.readlines()
            return [json.loads(plan) for plan in saved_plans]
    except FileNotFoundError:
        return []

# Function to allow the user to customize their budget allocation
def customize_budget_allocation(total_budget):
    st.write("\n🌟 Customize your Budget Allocation:")
    
    # Sliders to adjust percentage allocation
    transportation_percentage = st.slider("Transportation Budget (%)", 0, 100, 40)
    hotel_percentage = st.slider("Hotel Budget (%)", 0, 100, 40)
    activities_percentage = st.slider("Activities Budget (%)", 0, 100, 20)
    
    # Check if the total percentage adds up to 100
    if transportation_percentage + hotel_percentage + activities_percentage == 100:
        # Calculate the actual amounts based on the user's input
        transportation_budget = (transportation_percentage / 100) * total_budget
        hotel_budget = (hotel_percentage / 100) * total_budget
        activities_budget = (activities_percentage / 100) * total_budget
    else:
        st.error("❌ Total percentage must add up to 100%. Please try again.")
        transportation_budget, hotel_budget, activities_budget = 0, 0, 0
    
    return transportation_budget, hotel_budget, activities_budget

# Function to infer transportation mode based on origin and destination
def infer_transportation_mode(origin, destination, trip_type):
    # Determine if the trip is a city-to-city or country-to-country
    if origin.lower() == destination.lower():
        return None  # Same city, no need for transportation options
    elif trip_type == "One-Way":
        return "flight"  # One-Way trip assumed as flight
    elif trip_type == "Round Trip":
        return "flight"  # Round trip, assume flight both ways
    elif trip_type == "Multi-City":
        return "flight"  # Multi-city, assume flights for simplicity

# Function to use speech recognition to get voice input
def listen_for_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        st.write(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        st.error("Sorry, I could not understand the audio.")
        return ""
    except sr.RequestError:
        st.error("Sorry, I'm having trouble with the speech recognition service.")
        return ""

# Function to speak the output
def speak_output(output_text):
    engine.say(output_text)
    engine.runAndWait()

# Define the travel planner workflow
def travel_planner(origin, destination, budget, dates, transportation_type, currency, number_of_people):
    st.write("🚍 Retrieving transportation options...")

    # Determine if transportation is needed based on trip type
    if transportation_type:
        transport_query = (
            f"Find {transportation_type} ticket booking options from {origin} to {destination} "
            f"on {dates} within a budget of {budget}. Provide direct booking links."
        )
        try:
            transport_options = tavily_client.search(transport_query)
            transport_options = filter_transportation_options(transport_options.get('results', []))
        except Exception as e:
            return f"❌ Error retrieving transportation details: {str(e)}"

    st.write("🏨 Retrieving hotel details...")
    hotel_query = f"Find hotels in {destination} within budget {budget}. Provide booking links."
    try:
        hotels = tavily_client.search(hotel_query).get('results', [])
    except Exception as e:
        return f"❌ Error retrieving hotel details: {str(e)}"

    st.write("🎡 Retrieving activities...")
    activities_query = f"Suggest activities in {destination} for a traveler. Provide booking links if available."
    try:
        activities = tavily_client.search(activities_query).get('results', [])
    except Exception as e:
        return f"❌ Error retrieving activities: {str(e)}"

    st.write("📋 Formatting the final travel plan...")

    # Get customized budget allocation
    transportation_budget, hotel_budget, activities_budget = customize_budget_allocation(budget)

    formatted_plan = "\n🌟 Your Travel Plan:\n"
    formatted_plan += f"👥 Number of Travelers: {number_of_people}\n"
    formatted_plan += f"💰 Total Budget: {budget} {currency.upper()}\n"
    formatted_plan += f"🚍 Transportation Budget: {transportation_budget} {currency.upper()}\n"
    formatted_plan += f"🏨 Hotels Budget: {hotel_budget} {currency.upper()}\n"
    formatted_plan += f"🎡 Activities Budget: {activities_budget} {currency.upper()}\n"

    formatted_plan += "\n🚍 Transportation Options:\n"
    total_transport_price = 0
    if transport_options:
        for idx, option in enumerate(transport_options, start=1):
            if option['price'] != 'N/A' and option['price'] != "":
                try:
                    total_transport_price += float(option['price'].replace(currency.upper(), "").strip())
                except ValueError:
                    option['price'] = "N/A"
            formatted_plan += f"{idx}. {option['title']}\n"
            formatted_plan += f"   Link: {option['url']}\n"
            formatted_plan += f"   Price: {option['price']}\n"
    formatted_plan += f"🚍 Total Transportation Cost: {total_transport_price} {currency.upper()}\n"

    formatted_plan += "\n🏨 Hotels:\n"
    total_hotel_price = 0
    for idx, hotel in enumerate(hotels[:5], start=1):
        formatted_plan += f"{idx}. {hotel.get('title', 'Unknown Hotel')}\n"
        formatted_plan += f"   Link: {hotel.get('url', 'N/A')}\n"
        formatted_plan += f"   Price: {hotel.get('price', 'N/A')}\n"
        if hotel.get('price', 'N/A') != "N/A":
            total_hotel_price += float(hotel['price'].replace(currency.upper(), "").strip())
    formatted_plan += f"🏨 Total Hotel Cost: {total_hotel_price} {currency.upper()}\n"

    formatted_plan += "\n🎡 Activities:\n"
    total_activities_price = 0
    for idx, activity in enumerate(activities[:5], start=1):
        formatted_plan += f"{idx}. {activity.get('title', 'Unknown Activity')}\n"
        formatted_plan += f"   Link: {activity.get('url', 'N/A')}\n"
        formatted_plan += f"   Price: {activity.get('price', 'N/A')}\n"
        if activity.get('price', 'N/A') != "N/A":
            total_activities_price += float(activity['price'].replace(currency.upper(), "").strip())
    formatted_plan += f"🎡 Total Activities Cost: {total_activities_price} {currency.upper()}\n"

    # Save the plan
    save_travel_plan({
        'origin': origin,
        'destination': destination,
        'budget': budget,
        'dates': dates,
        'transportation_type': transportation_type,
        'currency': currency,
        'number_of_people': number_of_people,
        'transportation_budget': transportation_budget,
        'hotel_budget': hotel_budget,
        'activities_budget': activities_budget,
        'plan_details': formatted_plan
    })

    return formatted_plan

# Main function for user interaction
def main():
    st.title("🌟 Welcome to the Smart Travel Planner!")

    # Display user options to start planning
    query = st.selectbox("What would you like to do?", ["Select an option", "Plan a Trip", "View Saved Plans"])

    if query == "Plan a Trip":
        origin = get_input("📍 Where are you currently located?")
        destination = get_input("🌍 Where do you want to travel?")

        # Select the trip type
        trip_type = st.selectbox("Choose your trip type", ["One-Way", "Round Trip", "Multi-City"])

        # Handle transportation mode depending on city-to-city or country-to-country
        transportation_type = infer_transportation_mode(origin, destination, trip_type)

        budget = get_float_input("💰 What is your budget? (e.g., 30000): ")
        if budget is None:
            return  # Stop execution if the budget is invalid

        currency = get_input("💱 What is your budget currency? (USD or PKR): ")

        # Convert currency
        converted_budget, error_message = convert_currency(budget, currency)
        if error_message:
            st.error(error_message)
            return

        # Date input with calendar
        dates = st.date_input("📅 When are you planning to travel?")
        if not dates:
            st.error("Please select a valid travel date.")
            return

        number_of_people = get_input("👥 How many people are traveling? (e.g., 1 for solo, 2 for pair): ")

        # Process travel query
        result = travel_planner(origin, destination, converted_budget, str(dates), transportation_type, currency, number_of_people)
        st.write(result)

        # Voice Output (read out the travel plan)
        speak_output(result)

if __name__ == "__main__":
    main()
