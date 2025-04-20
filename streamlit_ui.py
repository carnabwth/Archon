from __future__ import annotations
from dotenv import load_dotenv
import streamlit as st
import logfire
import asyncio
import os

# Set page config - must be the first Streamlit command
st.set_page_config(
    page_title="Archon - Agent Builder",
    page_icon="🤖",
    layout="wide",
)

# Utilities and styles
from utils.utils import get_clients
from streamlit_pages.styles import load_css

# Streamlit pages
from streamlit_pages.intro import intro_tab
from streamlit_pages.chat import chat_tab
from streamlit_pages.environment import environment_tab
from streamlit_pages.database import database_tab
from streamlit_pages.documentation import documentation_tab
from streamlit_pages.agent_service import agent_service_tab
from streamlit_pages.mcp import mcp_tab
from streamlit_pages.future_enhancements import future_enhancements_tab

# Load environment variables from .env file
load_dotenv()

# Initialize clients
openai_client, supabase = get_clients()

# Load custom CSS styles
load_css()

# Configure logfire to suppress warnings (optional)
logfire.configure(send_to_logfire='never')

# Debug function to check environment variables
def debug_env_vars():
    st.write("### Environment Variables Debug")
    st.write("Checking environment variables from both .env and Streamlit secrets...")
    
    # Check if we can access st.secrets
    try:
        st.write("Streamlit secrets available:", bool(st.secrets))
        if st.secrets:
            st.write("Keys in st.secrets:", list(st.secrets.keys()))
            
            # Try to access each secret directly
            st.write("### Direct Secret Access")
            for key in ["EMBEDDING_BASE_URL", "EMBEDDING_API_KEY", "EMBEDDING_PROVIDER", 
                       "SUPABASE_URL", "SUPABASE_SERVICE_KEY", "REASONER_MODEL", 
                       "PRIMARY_MODEL", "EMBEDDING_MODEL"]:
                try:
                    # Try both uppercase and lowercase
                    value = getattr(st.secrets, key, None) or getattr(st.secrets, key.lower(), None)
                    if value:
                        st.write(f"{key}: Set (value length: {len(str(value))})")
                    else:
                        st.write(f"{key}: Not Set")
                except Exception as e:
                    st.write(f"{key}: Error accessing - {str(e)}")
    except Exception as e:
        st.write("Error accessing st.secrets:", str(e))
    
    # Check environment variables
    env_vars = {
        "EMBEDDING_BASE_URL": os.getenv("EMBEDDING_BASE_URL"),
        "EMBEDDING_API_KEY": "***" if os.getenv("EMBEDDING_API_KEY") else None,
        "EMBEDDING_PROVIDER": os.getenv("EMBEDDING_PROVIDER"),
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_SERVICE_KEY": "***" if os.getenv("SUPABASE_SERVICE_KEY") else None,
        "REASONER_MODEL": os.getenv("REASONER_MODEL"),
        "PRIMARY_MODEL": os.getenv("PRIMARY_MODEL"),
        "EMBEDDING_MODEL": os.getenv("EMBEDDING_MODEL")
    }
    
    st.write("### Environment Variables Status (from os.getenv)")
    for key, value in env_vars.items():
        st.write(f"{key}: {'Set' if value else 'Not Set'}")
        if value:
            st.write(f"  Value length: {len(str(value))}")
    
    # Try to access variables through st.secrets dictionary style
    st.write("### Trying to access through st.secrets dictionary style")
    try:
        for key in env_vars.keys():
            # Try both uppercase and lowercase
            value = st.secrets.get(key, None) or st.secrets.get(key.lower(), None)
            if value:
                st.write(f"{key}: Set (from st.secrets)")
            else:
                st.write(f"{key}: Not Set (in st.secrets)")
    except Exception as e:
        st.write("Error accessing st.secrets:", str(e))

async def main():
    # Check for tab query parameter
    query_params = st.query_params
    if "tab" in query_params:
        tab_name = query_params["tab"]
        if tab_name in ["Intro", "Chat", "Environment", "Database", "Documentation", "Agent Service", "MCP", "Future Enhancements"]:
            st.session_state.selected_tab = tab_name

    # Add sidebar navigation
    with st.sidebar:
        st.image("public/ArchonLightGrey.png", width=1000)
        
        # Navigation options with vertical buttons
        st.write("### Navigation")
        
        # Initialize session state for selected tab if not present
        if "selected_tab" not in st.session_state:
            st.session_state.selected_tab = "Intro"
        
        # Vertical navigation buttons
        intro_button = st.button("Intro", use_container_width=True, key="intro_button")
        chat_button = st.button("Chat", use_container_width=True, key="chat_button")
        env_button = st.button("Environment", use_container_width=True, key="env_button")
        db_button = st.button("Database", use_container_width=True, key="db_button")
        docs_button = st.button("Documentation", use_container_width=True, key="docs_button")
        service_button = st.button("Agent Service", use_container_width=True, key="service_button")
        mcp_button = st.button("MCP", use_container_width=True, key="mcp_button")
        future_enhancements_button = st.button("Future Enhancements", use_container_width=True, key="future_enhancements_button")
        
        # Update selected tab based on button clicks
        if intro_button:
            st.session_state.selected_tab = "Intro"
        elif chat_button:
            st.session_state.selected_tab = "Chat"
        elif mcp_button:
            st.session_state.selected_tab = "MCP"
        elif env_button:
            st.session_state.selected_tab = "Environment"
        elif service_button:
            st.session_state.selected_tab = "Agent Service"
        elif db_button:
            st.session_state.selected_tab = "Database"
        elif docs_button:
            st.session_state.selected_tab = "Documentation"
        elif future_enhancements_button:
            st.session_state.selected_tab = "Future Enhancements"
    
    # Display the selected tab
    if st.session_state.selected_tab == "Intro":
        st.title("Archon - Introduction")
        intro_tab()
    elif st.session_state.selected_tab == "Chat":
        st.title("Archon - Agent Builder")
        await chat_tab()
    elif st.session_state.selected_tab == "MCP":
        st.title("Archon - MCP Configuration")
        mcp_tab()
    elif st.session_state.selected_tab == "Environment":
        st.title("Archon - Environment Configuration")
        environment_tab()
        debug_env_vars()  # Add debug section
    elif st.session_state.selected_tab == "Agent Service":
        st.title("Archon - Agent Service")
        agent_service_tab()
    elif st.session_state.selected_tab == "Database":
        st.title("Archon - Database Configuration")
        database_tab(supabase)
    elif st.session_state.selected_tab == "Documentation":
        st.title("Archon - Documentation")
        documentation_tab(supabase)
    elif st.session_state.selected_tab == "Future Enhancements":
        st.title("Archon - Future Enhancements")
        future_enhancements_tab()

if __name__ == "__main__":
    asyncio.run(main())
