from textwrap import dedent
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
import streamlit as st
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
import json
from config import (
    BUDGET_RANGES, TRAVEL_STYLES, INTERESTS, 
    EMERGENCY_SERVICES, ITINERARY_SECTIONS
)
from utils import (
    RateLimiter, get_cached_data, set_cached_data,
    get_weather_forecast, format_currency, calculate_total_cost,
    generate_packing_list
)

# Load environment variables
load_dotenv()

# Set up the Streamlit app
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

st.title("AI Travel Planner ✈️")
st.caption("Plan your next adventure with AI Travel Planner by researching and planning a personalized itinerary on autopilot using GPT-4o")

# Get API keys from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
serp_api_key = os.getenv("SERP_AI_API_KEY")

if not openai_api_key or not serp_api_key:
    st.error("Please set OPENAI_API_KEY and SERP_AI_API_KEY in your .env file")
    st.stop()

# Initialize rate limiter
rate_limiter = RateLimiter(10)  # 10 calls per minute

if openai_api_key and serp_api_key:
    researcher = Agent(
        name="Researcher",
        role="Searches for travel destinations, activities, and accommodations based on user preferences",
        model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),
        description=dedent(
            """\
        You are a world-class travel researcher. Given a travel destination and the number of days the user wants to travel for,
        generate a list of search terms for finding relevant travel activities and accommodations.
        Then search the web for each term, analyze the results, and return the 10 most relevant results.
        """
        ),
        instructions=[
            "Given a travel destination and the number of days the user wants to travel for, first generate a list of 3 search terms related to that destination and the number of days.",
            "For each search term, `search_google` and analyze the results."
            "From the results of all searches, return the 10 most relevant results to the user's preferences.",
            "Remember: the quality of the results is important.",
        ],
        tools=[SerpApiTools(api_key=serp_api_key)],
        add_datetime_to_instructions=True,
    )
    planner = Agent(
        name="Planner",
        role="Generates a draft itinerary based on user preferences and research results",
        model=OpenAIChat(id="gpt-4o", api_key=openai_api_key),
        description=dedent(
            """\
        You are a senior travel planner. Given a travel destination, the number of days the user wants to travel for, and a list of research results,
        your goal is to generate a draft itinerary that meets the user's needs and preferences.
        """
        ),
        instructions=[
            "Given a travel destination, the number of days the user wants to travel for, and a list of research results, generate a draft itinerary that includes suggested activities and accommodations.",
            "Ensure the itinerary is well-structured, informative, and engaging.",
            "Ensure you provide a nuanced and balanced itinerary, quoting facts where possible.",
            "Remember: the quality of the itinerary is important.",
            "Focus on clarity, coherence, and overall quality.",
            "Never make up facts or plagiarize. Always provide proper attribution.",
        ],
        add_datetime_to_instructions=True,
    )

    # Create three columns for input fields
    col1, col2, col3 = st.columns(3)

    with col1:
        # Basic travel information
        destination = st.text_input("Where do you want to go?")
        num_days = st.number_input("How many days do you want to travel for?", min_value=1, max_value=30, value=7)
        start_date = st.date_input("When do you want to start?", value=datetime.now() + timedelta(days=1))

    with col2:
        # Additional preferences
        budget = st.selectbox("What's your budget range?", BUDGET_RANGES)
        travel_style = st.selectbox("What's your travel style?", TRAVEL_STYLES)
        interests = st.multiselect("What are your interests?", INTERESTS)

    with col3:
        # Additional options
        group_size = st.number_input("How many people are traveling?", min_value=1, max_value=20, value=2)
        preferred_language = st.selectbox("Preferred language for information", ["English", "Spanish", "French", "German", "Italian"])
        dietary_restrictions = st.multiselect("Any dietary restrictions?", ["None", "Vegetarian", "Vegan", "Gluten-Free", "Halal", "Kosher"])

    # Create action buttons
    col1, col2 = st.columns(2)
    with col1:
        generate_button = st.button("Generate Itinerary", type="primary")
    with col2:
        clear_button = st.button("Clear All")

    if clear_button:
        st.session_state.clear()
        st.experimental_rerun()

    if generate_button:
        if not destination:
            st.error("Please enter a destination")
            st.stop()
            
        try:
            # Create progress bar
            progress_bar = st.progress(0)
            
            # Research phase
            with st.spinner("Researching your destination..."):
                rate_limiter.wait_if_needed()
                research_prompt = f"""
                Research {destination} for a {num_days} day trip.
                Budget: {budget}
                Travel Style: {travel_style}
                Interests: {', '.join(interests)}
                Start Date: {start_date}
                Group Size: {group_size}
                Language: {preferred_language}
                Dietary Restrictions: {', '.join(dietary_restrictions)}
                """
                research_results = researcher.run(research_prompt, stream=False)
                progress_bar.progress(33)
                
            # Get weather forecast
            with st.spinner("Getting weather forecast..."):
                weather_data = get_weather_forecast(destination, start_date, num_days)
                progress_bar.progress(66)
                
            # Planning phase
            with st.spinner("Creating your personalized itinerary..."):
                rate_limiter.wait_if_needed()
                prompt = f"""
                Destination: {destination}
                Duration: {num_days} days
                Start Date: {start_date}
                Budget: {budget}
                Travel Style: {travel_style}
                Interests: {', '.join(interests)}
                Group Size: {group_size}
                Language: {preferred_language}
                Dietary Restrictions: {', '.join(dietary_restrictions)}
                Weather Forecast: {json.dumps(weather_data)}
                Research Results: {research_results.content}
                
                Please create a detailed itinerary based on this research. Format the output with:
                - A brief introduction
                - Day-by-day breakdown with estimated times
                - Estimated costs for each activity
                - Transportation options between locations
                - Local tips and recommendations
                - Emergency contacts
                - Weather considerations
                - Packing suggestions
                """
                response = planner.run(prompt, stream=False)
                progress_bar.progress(100)
                
                # Generate packing list
                packing_list = generate_packing_list(weather_data, travel_style, num_days)
                
                # Display the itinerary with better formatting
                st.markdown("## Your Personalized Itinerary")
                
                # Create tabs for different sections
                tab1, tab2, tab3, tab4 = st.tabs(["Itinerary", "Map", "Weather", "Packing List"])
                
                with tab1:
                    st.markdown(response.content)
                    
                    # Add download buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="Download Itinerary (Markdown)",
                            data=response.content,
                            file_name=f"{destination}_itinerary.md",
                            mime="text/markdown"
                        )
                    with col2:
                        st.download_button(
                            label="Download Itinerary (JSON)",
                            data=json.dumps({
                                "destination": destination,
                                "duration": num_days,
                                "start_date": start_date.strftime("%Y-%m-%d"),
                                "itinerary": response.content,
                                "weather": weather_data,
                                "packing_list": packing_list
                            }, indent=2),
                            file_name=f"{destination}_itinerary.json",
                            mime="application/json"
                        )
                
                with tab2:
                    # Create a map centered on the destination
                    m = folium.Map(location=[0, 0], zoom_start=2)
                    st_folium(m, returned_objects=[])
                
                with tab3:
                    st.markdown("### Weather Forecast")
                    for day in weather_data["forecast"]:
                        st.write(f"**{day['date']}**: {day['temperature']}, {day['conditions']}")
                
                with tab4:
                    st.markdown("### Packing List")
                    for item in packing_list:
                        st.write(f"- {item}")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.stop()