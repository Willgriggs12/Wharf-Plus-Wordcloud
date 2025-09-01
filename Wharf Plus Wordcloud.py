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
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', "can't", 'cannot', 'com', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', 'don', "don't", 'down', 'during', 'each', 'else', 'ever', 'etc', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'http', 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', 'just', 'k', "let's", 'like', 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ourselves', 'out', 'over', 'own', 'r', 'same', 'shall', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'whats', 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'www', 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves', 'helps', 'feel', 'canary', 'wharf', 'plus', 'know', 'also', 'keeps', 'make', 'let'
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
    fig, ax = plt.subplots(figsize=(12, 6)); ax.imshow(wordcloud, interpolation='bilinear'); ax.axis("off"); fig.patch.set_facecolor('white')
    return fig

# --- STREAMLIT APPLICATION ---
if check_password():
    st.set_page_config(layout="wide", page_title="Response Dashboard")

    # --- Custom CSS for Professional UI ---
    st.markdown("""
    <style>
        /* Reduce top padding of the main page */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #F8F9FA;
            padding-top: 1rem;
        }
        /* Leaderboard Button Styling */
        .stButton>button {
            background-color: #FFFFFF; color: #4A4A4A; border: 1px solid #E0E0E0;
            border-radius: 8px; padding-top: 10px; padding-bottom: 10px;
            width: 100%; text-align: left; font-weight: 500;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            border-color: #6200EE; color: #6200EE; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        /* Styling for the response count number */
        .leaderboard-count {
            font-size: 1.1em; font-weight: bold; color: #2E2E2E;
            text-align: right; padding-top: 10px;
        }
        /* Sector Legend Styling */
        .legend-container {
            display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px;
        }
        .legend-item {
            display: flex; align-items: center; font-size: 0.9em;
        }
        .legend-color-box {
            width: 12px; height: 12px; border-radius: 3px; margin-right: 6px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state for filter defaults
    if 'default_sectors' not in st.session_state: st.session_state['default_sectors'] = []
    if 'default_companies' not in st.session_state: st.session_state['default_companies'] = []

    # --- Sidebar Controls ---
    with st.sidebar:
        st.title("Controls")
        st.markdown("---")
        uploaded_file = st.file_uploader("Upload Response File", type=["xlsx"])
        
        if st.button("Clear All Filters"):
            st.session_state['default_sectors'] = []
            st.session_state['default_companies'] = []
            st.rerun()

        st.markdown("---")
        st.subheader("Response Leaderboard")
        st.caption("Click a company name to filter.")
    
    # --- Main Page ---
    st.title("Interactive Response Word Cloud")
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file, na_values=['None'])
        df['display_response'] = df['Response'].astype(str).str.replace('â€™', "'").str.replace('â€œ', '"').str.replace('â€', '"')
        df['Sector'] = df['Company'].map(SECTOR_MAPPING).fillna('Other')
        df['cleaned_response'] = df['Response'].apply(clean_text)

        # --- Display Color Legend ---
        legend_html = '<div class="legend-container">'
        for sector, color in SECTOR_COLORS.items():
            legend_html += f'<div class="legend-item"><div class="legend-color-box" style="background-color:{color};"></div>{sector}</div>'
        legend_html += '</div>'
        st.markdown(legend_html, unsafe_allow_html=True)

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

        # --- Filtering Logic and Word Cloud Display ---
        filtered_df = df.copy()
        title_parts = []
        if selected_sectors:
            filtered_df = filtered_df[filtered_df['Sector'].isin(selected_sectors)]
            title_parts.append(f"Sectors: {', '.join(selected_sectors)}")
        if selected_companies:
            filtered_df = filtered_df[filtered_df['Company'].isin(selected_companies)]
            title_parts.append(f"Companies: {', '.join(selected_companies)}")
        
        full_text = " ".join(response for response in filtered_df['cleaned_response'].dropna())
        wordcloud_fig = generate_wordcloud_image(full_text)
        
        if wordcloud_fig:
            st.pyplot(wordcloud_fig, use_container_width=True)
            
            # --- Download Button Logic ---
            buf = io.BytesIO()
            wordcloud_fig.savefig(buf, format="png", bbox_inches="tight")
            
            # Create dynamic filename
            filename_parts = []
            if selected_sectors: filename_parts.append(f"Sectors_{'-'.join(selected_sectors)}")
            if selected_companies: filename_parts.append(f"Companies_{'-'.join(selected_companies)}")
            if not filename_parts: download_filename = "WordCloud_All-Responses.png"
            else: download_filename = f"WordCloud_{'_'.join(filename_parts)}.png"
            
            # Sanitize filename
            download_filename = re.sub(r'[\s/&]', '-', download_filename)

            st.download_button(
                label="📥 Download Visual",
                data=buf,
                file_name=download_filename,
                mime="image/png"
            )
        else:
            st.warning("No text available to generate a word cloud for the selected filter.")
        
        # --- Raw Data Expander ---
        with st.expander(f"View the {len(filtered_df)} Raw Response(s)"):
            display_df = filtered_df[['display_response', 'Company']].rename(columns={'display_response': 'Original Response', 'Company': 'Company Name'})
            st.dataframe(display_df, hide_index=True, use_container_width=True)
    
    else:
        st.info("Please upload an Excel file using the control panel on the left to begin analysis.")
