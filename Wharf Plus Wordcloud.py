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
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.info("Please enter the password to access the dashboard.")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

# --- 1. SETUP AND CONFIGURATION ---
STOPWORDS = [
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', "can't", 'cannot',
    'com', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', 'don', "don't", 'down', 'during',
    'each', 'else', 'ever', 'etc', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having',
    'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's",
    'http', 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself',
    'just', 'k', "let's", 'like', 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off',
    'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'r', 'same',
    'shall', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than',
    'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they',
    "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up',
    'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'whats', 'when',
    "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't",
    'would', "wouldn't", 'www', 'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself',
    'yourselves', 'helps', 'feel', 'canary', 'wharf', 'plus', 'know', 'also', 'keeps', 'make', 'let'
]

SECTOR_MAPPING = {
    'Barclays': 'Banking & Finance', 'Morgan Stanley': 'Banking & Finance', 'Societe Generale': 'Banking & Finance',
    'JP Morgan': 'Banking & Finance', 'Citigroup': 'Banking & Finance', 'EBRD': 'Banking & Finance', 'HSBC': 'Banking & Finance',
    'Deutsche Bank': 'Banking & Finance', 'Northern Trust': 'Banking & Finance', 'Revolut': 'Banking & Finance',
    'State Street': 'Banking & Finance', 'Mitsubishi UF J Financial Group': 'Banking & Finance', 'Moodyâ€™s': 'Banking & Finance',
    'Barclays Capital': 'Banking & Finance', 'European Bank for Construction and Redevelopment (EBRD)': 'Banking & Finance',
    'BGC Brokers L.P.': 'Banking & Finance',
    'BP': 'Manufacturing, Industrial & Energy', 'TotalEnergies': 'Manufacturing, Industrial & Energy',
    'Hexaware Technologies': 'TMT', 'Infosys Consulting': 'TMT', 'Thomson Reuters': 'TMT', 'Cision': 'TMT',
    'WeWork': 'Business Services', 'JLL': 'Business Services', 'Adamson Associates (International) Ltd': 'Business Services',
    'KPMG': 'Professional', 'Ernst Young (EY)': 'Professional', 'Herbert Smith Freehills Kramer': 'Professional',
    'General Optical Council': 'Public Sector / Regulatory Body / Charity', 'WaterAid': 'Public Sector / Regulatory Body / Charity',
    'UCL': 'Public Sector / Regulatory Body / Charity', 'Transport for London': 'Public Sector / Regulatory Body / Charity',
    'MDU': 'Life Sciences & Healthcare', 'Hvivo Plc': 'Life Sciences & Healthcare',
    'Bupa Health and Dental Centre': 'Life Sciences & Healthcare',
    'Waitrose & Partners': 'Other', 'Canary Wharf Group': 'Other', 'Westferry Circus Property Ltd': 'Other',
    'Paul Smith': 'Other', 'Ocean Network Express': 'Other', 'Blacklock': 'Other', 'Third Space': 'Other',
    'Visitor': 'Other', '1. Company not listed': 'Other', 'None': 'Other', None: 'Other', np.nan: 'Other'
}

def clean_text(text):
    if not isinstance(text, str): return ""
    # Fix common encoding errors for punctuation BEFORE any other cleaning
    text = text.replace('â€™', "'")  # Fixes apostrophes and single quotes
    text = text.replace('â€œ', '"')  # Fixes opening double quotes
    text = text.replace('â€', '"')  # Fixes closing double quotes
    # This is the original cleaning logic, which should now run on the corrected text
    text = re.sub(r'wharf plus', 'WharfPlus', text, flags=re.IGNORECASE)
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text) # Remove any remaining special characters
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
    st.title("Interactive Response Word Cloud Generator")
    uploaded_file = st.file_uploader("Upload your Excel file to begin", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, na_values=['None'])
            # We apply the cleaning to the raw response text before displaying it
            df['display_response'] = df['Response'].str.replace('â€™', "'").str.replace('â€œ', '"').str.replace('â€', '"')
            st.sidebar.header("Filters")
            
            if 'Response' in df.columns and 'Company' in df.columns:
                df['Sector'] = df['Company'].map(SECTOR_MAPPING).fillna('Other')
                df['cleaned_response'] = df['Response'].apply(clean_text)

                st.sidebar.subheader("Response Leaderboard")
                leaderboard_df = df[~df['Company'].isin(['1. Company not listed', 'Visitor', None, np.nan])]
                if not leaderboard_df.empty:
                    company_counts = leaderboard_df['Company'].value_counts().reset_index()
                    company_counts.columns = ['Company', 'Responses']
                    st.sidebar.dataframe(company_counts, hide_index=True, use_container_width=True)
                
                sector_list = ['All Sectors'] + sorted([s for s in df['Sector'].unique() if s != 'Other']) + ['Other']
                selected_sector = st.sidebar.selectbox("Filter by Sector:", sector_list)

                if selected_sector == 'All Sectors': company_list = ['All Companies'] + sorted(df['Company'].dropna().unique().tolist())
                else: company_list = ['All Companies'] + sorted(df[df['Sector'] == selected_sector]['Company'].dropna().unique().tolist())
                selected_company = st.sidebar.selectbox(f"Filter by Company:", company_list)

                filtered_df = df.copy(); title = "Word Cloud for "
                if selected_sector != 'All Sectors':
                    filtered_df = filtered_df[filtered_df['Sector'] == selected_sector]; title += f"'{selected_sector}' Sector"
                    if selected_company != 'All Companies': filtered_df = filtered_df[filtered_df['Company'] == selected_company]; title = f"Word Cloud for '{selected_company}'"
                elif selected_company != 'All Companies': filtered_df = filtered_df[filtered_df['Company'] == selected_company]; title = f"Word Cloud for '{selected_company}'"
                else: title += "All Responses"
                st.header(title)
                
                if not filtered_df.empty:
                    full_text = " ".join(response for response in filtered_df['cleaned_response'].dropna())
                    wordcloud_fig = generate_wordcloud_image(full_text)
                    if wordcloud_fig: st.pyplot(wordcloud_fig)
                    else: st.warning("No text available to generate a word cloud for the selected filter.")
                    
                    with st.expander(f"View the {len(filtered_df)} Raw Response(s)"):
                        # Use the new 'display_response' column here for a clean view
                        display_df = filtered_df[['display_response', 'Company']].rename(columns={'display_response': 'Original Response', 'Company': 'Company Name'})
                        st.dataframe(display_df, hide_index=True, use_container_width=True)
                else: st.warning("No responses found for the selected filters.")
            else: st.error("The uploaded Excel file must contain 'Response' and 'Company' columns.")
        except Exception as e: st.error(f"An error occurred while processing the file: {e}")
