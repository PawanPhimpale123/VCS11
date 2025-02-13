import streamlit as st
import google.generativeai as genai
import time

# Configure Google Generative AI API
genai.configure(api_key="AIzaSyCGFuix5MqCBmJRE8oi1FzBYPjAt038dKc")
model = genai.GenerativeModel("gemini-1.5-flash")

# Set up the Streamlit page layout
st.set_page_config(page_title="Chat with AI", layout="centered")

# Function to display chat bubbles
def display_message(text, is_user=True):
    if is_user:
        # User message bubble (aligned to the right)
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; padding: 10px;">
            <div style="max-width: 70%; padding: 10px; background-color: #DCF8C6; border-radius: 15px;">
                {text}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # AI response bubble (aligned to the left)
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-start; padding: 10px;">
            <div style="max-width: 70%; padding: 10px; background-color: #E4E6EB; border-radius: 15px;">
                {text}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Streamlit Interface
st.title("Chat with AI")

# Create session state to store chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message, is_user in st.session_state.messages:
    display_message(message, is_user)

# Container for input field and send button at the bottom
st.markdown("""
    <style>
        .stTextInput {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            width: 80%;
            background-color: #f1f1f1;
            padding: 10px;
            border-radius: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .send-button {
            position: fixed;
            bottom: 20px;
            right: 10%;
            background-color: #34B7F1;
            color: white;
            border: none;
            border-radius: 20px;
            padding: 10px 20px;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .send-button:hover {
            background-color: #128C7E;
        }
    </style>
""", unsafe_allow_html=True)

# Input field for text with Enter key submission
user_input = st.text_input("Type your message:", "", key="input_field", help="Type your message here")

# Send button to submit input
send_button = st.button("Send", key="send_button", use_container_width=False)

# If the send button is clicked or Enter is pressed, process the input
if send_button or user_input:
    # Display the user's message
    display_message(user_input, is_user=True)
    
    # Add the user message to session state
    st.session_state.messages.append((user_input, True))

    # Show loading spinner while AI is thinking
    with st.spinner("AI is thinking..."):
        # Generate AI response
        try:
            response = model.generate_content(user_input)
            ai_message = response.text.strip()

            # Display the AI's response
            display_message(ai_message, is_user=False)

            # Add the AI message to session state
            st.session_state.messages.append((ai_message, False))

            time.sleep(1)  # Simulate some delay
        except Exception as e:
            st.error(f"Error: {str(e)}")
