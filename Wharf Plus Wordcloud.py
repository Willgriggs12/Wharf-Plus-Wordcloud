import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import numpy as np

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
    fig, ax = plt.subplots(figsize=(12, 6)); ax.imshow(wordcloud, interpolation='bilinear'); ax.axis("off")
    return fig

# --- STREAMLIT APPLICATION ---
if check_password():
    st.set_page_config(layout="wide")
    
    # --- UI Enhancement: Custom CSS Injection ---
    st.markdown("""
    <style>
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #F8F9FA; /* A light, clean grey */
        }

        /* Leaderboard Button Styling - THIS IS THE KEY PART */
        .stButton>button {
            background-color: #FFFFFF;      /* White background */
            color: #4A4A4A;                 /* Professional dark grey text */
            border: 1px solid #E0E0E0;      /* Subtle light grey border */
            border-radius: 8px;             /* Rounded corners */
            padding-top: 10px;              /* Vertical padding */
            padding-bottom: 10px;           /* Vertical padding */
            width: 100%;                    /* Make all buttons the same width */
            text-align: left;               /* Align company name to the left */
            font-weight: 500;               /* Slightly bolder font */
            transition: all 0.2s ease-in-out; /* Smooth hover effect */
        }
        .stButton>button:hover {
            border-color: #6200EE;          /* A professional purple for hover */
            color: #6200EE;                 /* Text color changes on hover */
            box-shadow: 0 2px 5px rgba(0,0,0,0.1); /* Add a subtle shadow on hover */
        }
        .stButton>button:focus {
            outline: none !important;
            box-shadow: 0 0 0 2px #D6BFFF !important; /* Focus ring for accessibility */
        }

        /* Styling for the response count number */
        .leaderboard-count {
            font-size: 1.1em;
            font-weight: bold;
            color: #2E2E2E;
            text-align: right;
            padding-top: 10px; /* Align number with button text */
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("Word Cloud Generator")
    uploaded_file = st.file_uploader("Upload your Excel file to begin", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file, na_values=['None'])
        df['display_response'] = df['Response'].astype(str).str.replace('â€™', "'").str.replace('â€œ', '"').str.replace('â€', '"')
        df['Sector'] = df['Company'].map(SECTOR_MAPPING).fillna('Other')
        df['cleaned_response'] = df['Response'].apply(clean_text)

        st.sidebar.title("Filters")
        st.sidebar.markdown("---")

        # --- Sidebar: Multi-Select Filters ---
        sector_list = sorted([s for s in df['Sector'].unique() if s != 'Other']) + ['Other']
        selected_sectors = st.multoselect("Filter by Sector:", sector_list, key='sector_filter')

        if selected_sectors: company_df = df[df['Sector'].isin(selected_sectors)]
        else: company_df = df
        
        company_list = sorted(company_df['Company'].dropna().unique().tolist())
        selected_companies = st.multoselect("Filter by Company:", company_list, key='company_filter')
        st.sidebar.markdown("---")
        
        # --- Sidebar: Interactive Leaderboard (with new UI) ---
        st.sidebar.subheader("Response Leaderboard")
        st.sidebar.caption("Click a company name to filter the dashboard.")
        leaderboard_df = df[~df['Company'].isin(['1. Company not listed', 'Visitor', None, np.nan])]
        if not leaderboard_df.empty:
            company_counts = leaderboard_df['Company'].value_counts().reset_index()
            company_counts.columns = ['Company', 'Responses']
            
            for row in company_counts.itertuples():
                cols = st.sidebar.columns([4, 1])
                button_clicked = cols[0].button(row.Company, key=f"btn_{row.Company}")
                # Use markdown with custom class for the count
                cols[1].markdown(f"<div class='leaderboard-count'>{row.Responses}</div>", unsafe_allow_html=True)
                
                if button_clicked:
                    st.session_state.sector_filter = [df.loc[df['Company'] == row.Company, 'Sector'].iloc[0]]
                    st.session_state.company_filter = [row.Company]
                    st.rerun()

        # --- Main Panel: Filtering & Display (No changes here) ---
        filtered_df = df.copy()
        title_parts = []
        if selected_sectors:
            filtered_df = filtered_df[filtered_df['Sector'].isin(selected_sectors)]
            title_parts.append(f"Sector(s): {', '.join(selected_sectors)}")
        
        if selected_companies:
            filtered_df = filtered_df[filtered_df['Company'].isin(selected_companies)]
            title_parts.append(f"Company(s): {', '.join(selected_companies)}")

        if not title_parts: title = "Word Cloud for All Responses"
        else: title = "Word Cloud for " + " & ".join(title_parts)
        st.header(title)
        
        if not filtered_df.empty:
            full_text = " ".join(response for response in filtered_df['cleaned_response'].dropna())
            wordcloud_fig = generate_wordcloud_image(full_text)
            if wordcloud_fig: st.pyplot(wordcloud_fig)
            else: st.warning("No text available to generate a word cloud for the selected filter.")
            
            with st.expander(f"View the {len(filtered_df)} Raw Response(s)"):
                display_df = filtered_df[['display_response', 'Company']].rename(columns={'display_response': 'Original Response', 'Company': 'Company Name'})
                st.dataframe(display_df, hide_index=True, use_container_width=True)
        else:
            st.warning("No responses found for the selected filters.")
