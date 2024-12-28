import streamlit as st
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

# Function to filter and format transportation options (ensuring 5 links)
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

# Function to automatically allocate budget based on the trip type
def allocate_budget(budget, trip_type):
    # Basic logic for allocating budget based on luxury, middle, low
    if trip_type == "Luxury":
        return budget * 0.5, budget * 0.3, budget * 0.2  # High transportation budget
    elif trip_type == "Middle":
        return budget * 0.4, budget * 0.4, budget * 0.2  # Balanced budget
    else:  # Low budget
        return budget * 0.3, budget * 0.5, budget * 0.2  # Lower transportation budget, more for hotels

# Function to infer transportation mode based on origin and destination
def infer_transportation_mode(origin, destination, trip_type):
    # If it's a city-to-city trip, ask the user for transportation mode
    if origin.lower() != destination.lower():
        return st.selectbox("What transportation mode do you prefer?", ["flight", "train", "bus"])
    return None  # No transportation type needed for country-to-country trips

# Define the travel planner workflow
def travel_planner(origin, destination, budget, dates, transportation_type, currency, number_of_people, trip_type):
    # Allocate budget based on trip type (luxury, middle, low)
    transportation_budget, hotel_budget, activities_budget = allocate_budget(budget, trip_type)

    # Check if transportation type is needed
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

    formatted_plan = ""

    # Only show transportation details if relevant
    if transportation_type:
        formatted_plan += "\n🚍 Transportation Options:\n"
        total_transport_price = 0
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
        trip_type = st.selectbox("Choose your trip type", ["Luxury", "Middle", "Low"])

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
        result = travel_planner(origin, destination, converted_budget, str(dates), transportation_type, currency, number_of_people, trip_type)
        st.write(result)

if __name__ == "__main__":
    main()
