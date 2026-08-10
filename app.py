from chatbot import (
    generate_ai_response,
    generate_business_plan,
    generate_business_comparison,
    search_business_ideas
)
import streamlit as st

# Page configuration    
st.set_page_config(
    page_title="Business Idea Generator",
    page_icon="💡",
    layout="centered"
)

st.title("💡 Business Idea Generator")
st.write("Turn your interests into profitable business ideas!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input is not None and user_input.strip():
    # Store user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

     # Search dataset
    results = search_business_ideas(user_input)

        # Check if user wants a comparison
    if any(word in user_input.lower() for word in [
        "compare",
        "comparison",
        "compare the first",
        "compare first",
        "compare the second"
    ]):

        bot_reply = generate_business_comparison(
            user_input,
            st.session_state.messages
        )

    # Check if user wants a business plan
    elif any(word in user_input.lower() for word in [
        "business plan",
        "business model",
        "startup plan",
        "complete plan",
        "how to start"
    ]):

        bot_reply = generate_business_plan(
            user_input,
            results,
            st.session_state.messages
        )

    else:

        bot_reply = generate_ai_response(
            user_input,
            results,
            st.session_state.messages
        )
    # Store assistant response
    st.session_state.messages.append(
        {"role": "assistant", "content": bot_reply}
    )

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
        