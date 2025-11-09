"""
SHL Assessment Recommendation System - Streamlit Frontend
Beautiful, product-quality UI for the GenAI-powered recommendation engine
"""

import streamlit as st
import requests
from typing import List, Dict, Any

# ============================================================================
# Configuration
# ============================================================================

# API endpoint configuration
API_URL = "https://shl-api-p9xh.onrender.com/recommend"

# Page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="SHL Recommendation Engine",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# Custom CSS for Enhanced Styling
# ============================================================================

st.markdown("""
    <style>
    /* Main title styling */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(120deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    /* Subtitle styling */
    .subtitle {
        font-size: 1.2rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    
    /* Card-like containers */
    .assessment-card {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(120deg, #1e3a8a, #3b82f6);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        font-size: 1rem;
    }
    
    .stTextArea textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# Header Section
# ============================================================================

st.markdown('<h1 class="main-title">🤖 SHL GenAI Assessment Recommender</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Enter a job description or query to find the perfect SHL assessments, powered by AI.</p>',
    unsafe_allow_html=True
)

# Add a visual separator
st.divider()

# ============================================================================
# Main Input Section
# ============================================================================

# Create a clean input area
st.markdown("### 📝 Your Query")
query = st.text_area(
    "Enter your query:",
    height=150,
    placeholder="e.g., I need a Java developer who is also a good collaborator...",
    help="Describe the candidate profile you're looking for. Be specific about both technical skills and behavioral traits.",
    label_visibility="collapsed"
)

# Example queries for user guidance
with st.expander("💡 Need inspiration? Try these example queries"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Technical + Behavioral:**")
        st.code("I need a Python developer with strong leadership skills")
    
    with col2:
        st.markdown("**Behavioral Focus:**")
        st.code("Looking for someone with excellent communication and teamwork abilities")
    
    with col3:
        st.markdown("**Technical Focus:**")
        st.code("Need a full-stack developer proficient in React and Node.js")

st.markdown("")  # Add spacing

# Center the button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    search_button = st.button("🔍 Get Recommendations", use_container_width=True)

# ============================================================================
# API Call and Results Display
# ============================================================================

if search_button:
    # Validate input
    if not query or query.strip() == "":
        st.warning("⚠️ Please enter a query to get recommendations.")
    else:
        # Show loading spinner
        with st.spinner("🧠 AI is analyzing your query and finding the best assessments..."):
            try:
                # Prepare API request
                payload = {"query": query.strip()}
                
                # Make API call
                response = requests.post(API_URL, json=payload, timeout=30)
                
                # Handle successful response
                if response.status_code == 200:
                    # Parse response
                    data = response.json()
                    recommendations = data.get("recommended_assessments", [])
                    
                    # Display success message
                    st.success(f"✅ Found {len(recommendations)} recommendations!")
                    
                    # Check if we have results
                    if len(recommendations) == 0:
                        st.info("🔍 No assessments found matching your query. Try rephrasing or broadening your search.")
                    else:
                        st.markdown("---")
                        st.markdown("### 📊 Recommended Assessments")
                        st.markdown("")
                        
                        # Display each recommendation as a card
                        for idx, product in enumerate(recommendations, 1):
                            # Create a visual card using columns and styling
                            st.markdown(f"#### {idx}. {product['name']}")
                            
                            # Main info columns
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                # Display description
                                st.markdown(f"**Description:**")
                                st.write(product.get('description', 'No description available'))
                                
                                # Display test types as colored badges
                                st.markdown("**Test Types:**")
                                test_types = product.get('test_type', [])
                                if test_types:
                                    # Create inline badges
                                    badges_html = " ".join([
                                        f'<span style="background-color: #dbeafe; color: #1e40af; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 500; margin-right: 0.5rem;">{test_type}</span>'
                                        for test_type in test_types
                                    ])
                                    st.markdown(badges_html, unsafe_allow_html=True)
                                else:
                                    st.write("Not specified")
                                
                                st.markdown("")  # Spacing
                                
                                # Link button
                                url = product.get('url', '')
                                if url:
                                    st.link_button("🔗 View Assessment Details", url, use_container_width=False)
                            
                            with col2:
                                # Key metrics
                                duration = product.get('duration', 0)
                                st.metric(
                                    label="Duration",
                                    value=f"{duration} min",
                                    help="Time required to complete the assessment"
                                )
                                
                                remote = product.get('remote_support', 'Unknown')
                                st.metric(
                                    label="Remote Support",
                                    value=remote,
                                    help="Whether remote proctoring is available"
                                )
                            
                            with col3:
                                # Additional metrics
                                adaptive = product.get('adaptive_support', 'Unknown')
                                st.metric(
                                    label="Adaptive Support",
                                    value=adaptive,
                                    help="Whether the test adapts to candidate's skill level"
                                )
                            
                            # Visual separator between cards
                            st.divider()
                        
                        # Summary statistics at the bottom
                        st.markdown("---")
                        st.markdown("### 📈 Summary")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Assessments", len(recommendations))
                        
                        with col2:
                            avg_duration = sum(p.get('duration', 0) for p in recommendations) / len(recommendations) if recommendations else 0
                            st.metric("Avg Duration", f"{avg_duration:.0f} min")
                        
                        with col3:
                            remote_count = sum(1 for p in recommendations if p.get('remote_support', '').lower() == 'yes')
                            st.metric("Remote Supported", remote_count)
                        
                        with col4:
                            adaptive_count = sum(1 for p in recommendations if p.get('adaptive_support', '').lower() == 'yes')
                            st.metric("Adaptive Tests", adaptive_count)
                
                # Handle API errors
                else:
                    st.error(f"❌ Error: Could not connect to the API. (Status Code: {response.status_code})")
                    st.markdown(f"**Response:** {response.text}")
                    
                    # Troubleshooting tips
                    with st.expander("🔧 Troubleshooting"):
                        st.markdown("""
                        **Common issues:**
                        1. Make sure the backend API is running (`python main.py`)
                        2. Check that the API is accessible at `http://127.0.0.1:8000`
                        3. Verify your OpenAI API key is set in the `.env` file
                        4. Check the backend terminal for error messages
                        """)
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Connection Error: Could not reach the API server.")
                st.markdown("""
                **Please ensure:**
                - The backend server is running (`python main.py`)
                - The API is accessible at `http://127.0.0.1:8000`
                """)
            
            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout Error: The API took too long to respond.")
                st.markdown("Try again with a simpler query or check your internet connection.")
            
            except Exception as e:
                st.error(f"❌ Unexpected Error: {str(e)}")
                with st.expander("🐛 Error Details"):
                    st.code(str(e))

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.9rem; padding: 2rem 0;">
        <p>🚀 Powered by GenAI & RAG Technology | Built with Streamlit & FastAPI</p>
        <p>💡 Using OpenAI Embeddings + ChromaDB Vector Search</p>
    </div>
    """,
    unsafe_allow_html=True
)
