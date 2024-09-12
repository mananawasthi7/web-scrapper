import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
import time
import io
import xlsxwriter

# Set up Streamlit
st.title('Web Scraper for Google Search Results')
st.write('Enter the data you want to search, and the results will be saved in an Excel file.')

# Input for search query
search_query = st.text_input('Enter search query (e.g., "real estate agent in Jasola")')

# Button to start the scraping process
if st.button('Run Scraper'):
    if search_query:
        # Generate a fake user agent
        user_agent = UserAgent().random
        headers = {'User-Agent': user_agent, 'Accept-Language': 'en-US,en;q=0.5'}
        
        all_company_names = []
        all_company_links = []
        all_company_name1 = []
        
        # Loop through each page (assuming 12 pages)
        for page in range(1, 13):
            url = f"https://www.google.com/search?sca_esv=585445638&tbs=lf:1,lf_ui:2&tbm=lcl&q={search_query}&rflfq=1&num=20&start={20 * (page - 1)}"
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract company names and links
            company_divs = soup.find_all('div', class_='VkpGBb')
            for company_div in company_divs:
                company_name = company_div.text.strip()
                all_company_names.append(company_name)

                link_tag = company_div.find('a', href=True)
                if link_tag:
                    company_link = link_tag['href']
                    all_company_links.append(company_link)
                else:
                    all_company_links.append(None)

            # Additional company name extraction
            company_divs1 = soup.find_all("div", class_='dbg0pd')
            for company_div1 in company_divs1:
                company_name1 = company_div1.text.strip()
                all_company_name1.append(company_name1)

            # Adding delay to avoid being blocked
            time.sleep(5)

        # Create DataFrame and save to Excel
        data = {'Company Name': all_company_names, 'Company Link': all_company_links, 'Company Name1': all_company_name1}
        df = pd.DataFrame(data)

        # Split the 'Company Name' column based on '·' delimiter
        df['Company Name'] = df['Company Name'].astype(str)
        df[['col1', 'col2', 'col3', 'col4', 'col5']] = df['Company Name'].str.split('·', expand=True)

        # Cleaning up columns with numeric values
        columns_to_clean = ['col3', 'col4', 'col5']

        def extract_numeric(value):
            try:
                return float(''.join(filter(str.isdigit, str(value))))
            except ValueError:
                return float('nan')

        for column in columns_to_clean:
            df[column] = df[column].apply(extract_numeric)

        df = df[(df['col3'].astype(str).apply(len) >= 10) | (df['col4'].astype(str).apply(len) >= 10)]
        df = df.reset_index(drop=True)

        # Replace values with less than 10 digits with '0'
        df['col3'] = df['col3'].astype(str).apply(lambda x: '0' if len(x) < 10 else x)
        df['col3'] = pd.to_numeric(df['col3'])

        # Extract last 10 digits for 'col3' and 'col4'
        def extract_last_10_digits(value):
            return str(value)[-12:]

        df['col3'] = df['col3'].apply(extract_last_10_digits)
        df['col4'] = df['col4'].apply(extract_last_10_digits)

        # Handling 'nan' replacement
        df['col4'] = df['col4'].replace('nan', 0)

        # Calculate final column 'col5'
        df['col5'] = df['col3'].astype(float) + df['col4'].astype(float)

        # Drop unnecessary columns
        df.drop(columns=['col2', 'col3', 'col4'], inplace=True)

        # Match words between 'Company Name' and 'Company Name1'
        for index, row in df.iterrows():
            for word in df['Company Name1']:
                if word in df['Company Name'].iloc[index]:
                    df.at[index, 'Company Name1'] = word
                    break

        # Save DataFrame to an in-memory buffer (BytesIO)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        # Notify user of completion and provide download link
        st.success('Scraping complete! You can download the results below:')
        st.download_button(label="Download Excel File", data=output, file_name='final_output.xlsx')
    else:
        st.error('Please enter a search query.')






        
