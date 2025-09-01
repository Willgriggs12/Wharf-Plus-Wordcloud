import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import numpy as np
import io

# --- 0. PASSWORD PROTECTION FUNCTION ---
def check_password():
    """Returns `True` if the user has the correct password."""
    def password_entered():
        if st.session_state.get("password") == st.secrets.get("password"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if not st.session_state.get("password_correct", False):
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.info("Please enter the password to access the dashboard.")
        return False
    return True

# --- 1. SETUP AND CONFIGURATION ---
STOPWORDS = [
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', "can't", 'cannot', 'com', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', 'don', "don't", 'down', 'during', 'each', 'else', 'ever', 'etc', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'http', 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', 'just', 'k', "let's", 'like', 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'r', 'same', 'shall', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'whats', 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'www', 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves', 'helps', 'feel', 'canary', 'wharf', 'plus', 'know', 'also', 'keeps', 'make', 'let'
]

SECTOR_MAPPING = {
    'Barclays': 'Banking & Finance', 'Morgan Stanley': 'Banking & Finance', 'Societe Generale': 'Banking & Finance', 'JP Morgan': 'Banking & Finance', 'Citigroup': 'Banking & Finance', 'EBRD': 'Banking & Finance', 'HSBC': 'Banking & Finance', 'Deutsche Bank': 'Banking & Finance', 'Northern Trust': 'Banking & Finance', 'Revolut': 'Banking & Finance', 'State Street': 'Banking & Finance', 'Mitsubishi UF J Financial Group': 'Banking & Finance', 'Moodyâ€™s': 'Banking & Finance', 'Barclays Capital': 'Banking & Finance', 'European Bank for Construction and Redevelopment (EBRD)': 'Banking & Finance', 'BGC Brokers L.P.': 'Banking & Finance',
    'BP': 'Manufacturing, Industrial & Energy', 'TotalEnergies': 'Manufacturing, Industrial & Energy',
    'Hexaware Technologies': 'TMT', 'Infosys Consulting': 'TMT', 'Thomson Reuters': 'TMT', 'Cision': 'TMT',
    'WeWork': 'Business Services', 'JLL': 'Business Services', 'Adamson Associates (International) Ltd': 'Business Services',
    'KPMG': 'Professional', 'Ernst Young (EY)': 'Professional', 'Herbert Smith Freehills Kramer': 'Professional',
    'General Optical Council': 'Public Sector / Regulatory Body / Charity', 'WaterAid': 'Public Sector / Regulatory Body / Charity', 'UCL': 'Public Sector / Regulatory Body / Charity', 'Transport for London': 'Public Sector / Regulatory Body / Charity',
    'MDU': 'Life Sciences & Healthcare', 'Hvivo Plc': 'Life Sciences & Healthcare', 'Bupa Health and Dental Centre': 'Life Sciences & Healthcare',
    'Waitrose & Partners': 'Other', 'Canary Wharf Group': 'Other', 'Westferry Circus Property Ltd': 'Other', 'Paul Smith': 'Other', 'Ocean Network Express': 'Other', 'Blacklock': 'Other', 'Third Space': 'Other', 'Visitor': 'Other', '1. Company not listed': 'Other', 'None': 'Other', None: 'Other', np.nan: 'Other'
}

SECTOR_COLORS = {
    'Banking & Finance': '#7d3c98', 'Manufacturing, Industrial & Energy': '#2e86c1', 'TMT': '#16a085',
    'Business Services': '#f1c40f', 'Professional': '#e67e22', 'Public Sector / Regulatory Body / Charity': '#27ae60',
    'Life Sciences & Healthcare': '#c0392b', 'Other': '#7f8c8d'
}

def clean_text(text):
    if not isinstance(text, str): return ""
    text = text.replace('â€™', "'").replace('â€œ', '"').replace('â€', '"')
    text = re.sub(r'wharf plus', 'WharfPlus', text, flags=re.IGNORECASE)
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    clean_words = [word for word in words if word not in STOPWORDS and len(word) > 2]
    return " ".join(clean_words)

def generate_wordcloud_image(text):
    if not text or text.isspace(): return None
    wordcloud = WordCloud(width=1600, height=800, background_color='white', colormap='viridis', collocations=False, stopwords=STOPWORDS).generate(text)
    # Reduced figsize to make the plot shorter and fit better on screen
    fig, ax = plt.subplots(figsize=(10, 5)); ax.imshow(wordcloud, interpolation='bilinear'); ax.axis("off"); fig.patch.set_facecolor('white')
    return fig

def generate_color_css(df):
    """Dynamically generates CSS for coloring multiselect tags."""
    css = "<style>"
    for sector, color in SECTOR_COLORS.items():
        css += f''' div[data-baseweb="tag"] span[title="{sector}"] {{ background-color: {color} !important; color: white !important; }} '''
    for company, sector in SECTOR_MAPPING.items():
        if company and sector in SECTOR_COLORS:
            color = SECTOR_COLORS[sector]
            css += f''' div[data-baseweb="tag"] span[title="{company}"] {{ background-color: {color} !important; color: white !important; }} '''
    css += "</style>"
    return css

# --- STREAMLIT APPLICATION ---
if check_password():
    st.set_page_config(layout="wide", page_title="Response Dashboard")

    # --- UI Polish: Custom CSS Injection ---
    st.markdown("""
    <style>
        /* Main Layout & Whitespace Reduction */
        .block-container {
            padding-top: 1rem; /* SQUASH UP: Reduced top padding */
            padding-bottom: 1rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
        }
        [data-testid="stSidebar"] { background-color: #F8F9FA; }
        
        /* Compact File Uploader in top right */
        div[data-testid="stFileUploader"] {
            padding: 0;
        }
        div[data-testid="stFileUploader"] section {
            padding: 1rem;
            border-style: dashed;
            border-color: #d3d3d3;
        }
        div[data-testid="stFileUploader"] small {
            font-size: 0.8rem;
        }

        /* TIGHTER LEADERBOARD: Reduce vertical spacing to create a dense list */
        div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] {
            gap: 0.25rem !important; /* This is the key change for tighter spacing */
        }
        .stButton>button {
            background-color: #FFFFFF; color: #4A4A4A; border: 1px solid #E0E0E0;
            border-radius: 8px; padding: 6px 12px; /* Reduced button padding */
            width: 100%; text-align: left; font-weight: 500;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover { border-color: #6200EE; color: #6200EE; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .leaderboard-count {
            font-size: 1.0em; font-weight: 600; color: #2E2E2E;
            text-align: right; padding-top: 6px; /* Match button padding */
        }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'default_sectors' not in st.session_state: st.session_state['default_sectors'] = []
    if 'default_companies' not in st.session_state: st.session_state['default_companies'] = []

    # --- Sidebar ---
    with st.sidebar:
        st.title("Controls")
        if st.button("Clear All Filters"):
            st.session_state['default_sectors'] = []
            st.session_state['default_companies'] = []
            st.rerun()
        st.markdown("<hr style='margin-top:0.5rem; margin-bottom:0.5rem;'>", unsafe_allow_html=True)
        st.subheader("Response Leaderboard")
        st.caption("Click a company name to filter.")
        # Leaderboard content will be added later after file upload

    # --- Main Page Layout ---
    # Create an empty container at the top for the uploader
    uploader_container = st.container()
    
    # Check for uploaded file first
    uploaded_file = st.session_state.get('uploaded_file', None)
    if not uploaded_file:
        with uploader_container:
            _, uploader_col = st.columns([2, 1]) # Pushes uploader to the right
            uploaded_file = uploader_col.file_uploader("Upload Response File", type=["xlsx"], label_visibility="collapsed")
            if uploaded_file:
                st.session_state['uploaded_file'] = uploaded_file
                st.rerun()

    if 'uploaded_file' in st.session_state and st.session_state['uploaded_file'] is not None:
        df = pd.read_excel(st.session_state['uploaded_file'], na_values=['None'])
        df['display_response'] = df['Response'].astype(str).str.replace('â€™', "'").str.replace('â€œ', '"').str.replace('â€', '"')
        df['Sector'] = df['Company'].map(SECTOR_MAPPING).fillna('Other')
        df['cleaned_response'] = df['Response'].apply(clean_text)

        st.markdown(generate_color_css(df), unsafe_allow_html=True)

        # --- Main Page Filter Columns ---
        filter_col1, filter_col2 = st.columns(2)
        sector_list = sorted([s for s in df['Sector'].unique() if s != 'Other']) + ['Other']
        selected_sectors = filter_col1.multiselect("Filter by Sector:", sector_list, default=st.session_state['default_sectors'])

        if selected_sectors: company_df = df[df['Sector'].isin(selected_sectors)]
        else: company_df = df
        
        company_list = sorted(company_df['Company'].dropna().unique().tolist())
        selected_companies = filter_col2.multiselect("Filter by Company:", company_list, default=st.session_state['default_companies'])

        # --- Update Leaderboard in Sidebar ---
        with st.sidebar:
            leaderboard_df = df[~df['Company'].isin(['1. Company not listed', 'Visitor', None, np.nan])]
            if not leaderboard_df.empty:
                company_counts = leaderboard_df['Company'].value_counts().reset_index()
                company_counts.columns = ['Company', 'Responses']
                for row in company_counts.itertuples():
                    cols = st.columns([4, 1])
                    if cols[0].button(row.Company, key=f"btn_{row.Company}"):
                        st.session_state['default_sectors'] = [df.loc[df['Company'] == row.Company, 'Sector'].iloc[0]]
                        st.session_state['default_companies'] = [row.Company]
                        st.rerun()
                    cols[1].markdown(f"<div class='leaderboard-count'>{row.Responses}</div>", unsafe_allow_html=True)

        # --- Word Cloud Display ---
        filtered_df = df.copy()
        if selected_sectors: filtered_df = filtered_df[filtered_df['Sector'].isin(selected_sectors)]
        if selected_companies: filtered_df = filtered_df[filtered_df['Company'].isin(selected_companies)]
        
        full_text = " ".join(response for response in filtered_df['cleaned_response'].dropna())
        wordcloud_fig = generate_wordcloud_image(full_text)
        
        if wordcloud_fig:
            st.pyplot(wordcloud_fig, use_container_width=True)
            
            buf = io.BytesIO()
            wordcloud_fig.savefig(buf, format="png", bbox_inches="tight")
            filename_parts = []
            if selected_sectors: filename_parts.append(f"Sectors_{'-'.join(selected_sectors)}")
            if selected_companies: filename_parts.append(f"Companies_{'-'.join(selected_companies)}")
            download_filename = f"WordCloud_{'_'.join(filename_parts) or 'All-Responses'}.png"
            download_filename = re.sub(r'[\\/*?:"<>|&\s]', '-', download_filename)

            st.download_button(label="📥 Download Visual", data=buf, file_name=download_filename, mime="image/png")
        else:
            st.warning("No text available to generate a word cloud for the selected filter.")
        
        with st.expander(f"View the {len(filtered_df)} Raw Response(s)"):
            display_df = filtered_df[['display_response', 'Company']].rename(columns={'display_response': 'Original Response', 'Company': 'Company Name'})
            st.dataframe(display_df, hide_index=True, use_container_width=True)
    
    else:
        st.info("Upload an Excel file to begin analysis.")
