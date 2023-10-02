import streamlit as st
import openai
from metaphor_python import Metaphor

# Set OpenAI API key
openai.api_key = st.sidebar.text_input("OPENAI_API-KEY",type="password")

# Set Metaphor API key
metaphor = Metaphor(st.sidebar.text_input("METAPHOR_API-KEY",type="password"))

# Streamlit app title and description
st.title("Job Search Assistant")

# User input for the question
USER_QUESTION = st.text_input("Enter the job title:")

st.markdown("Sample Search: 'Job Title' Listings (e.g., New Data Scientist Positions / Data Scientist Jobs)")

# Button to perform the search and display results
if st.button("Search"):
    if USER_QUESTION:
        SYSTEM_MESSAGE = "You are a helpful assistant that generates search queries based on user questions. Only generate one search query."

        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": USER_QUESTION},
            ],
        )

        query = completion.choices[0].message.content
        search_response = metaphor.search(
            query, use_autoprompt=True, start_published_date="2023-06-01"
        )

        SYSTEM_MESSAGE = "Please provide the following details: Company Name, Job Title, Years of Experience Required"

        contents_result = search_response.get_contents()

        # Limit the number of processed links to 5
        max_links_to_process = 5

        # Iterate through each link in the search results
        for i, link in enumerate(contents_result.contents):
            # Check if we have processed the desired number of links
            if i >= max_links_to_process:
                break

            # Extract the content of the link
            link_content = link.extract

            if "linkedin.com" in link.url:
            # Skip LinkedIn job postings
                continue

            # Use the link content as user input for OpenAI API
            messages = [
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": link_content},
            ]

            # Make an API request for the current link
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
            )

            # Extract and display the response for the current link
            summary = completion.choices[0].message.content
            # st.write(f"{link.url}: {summary}")
            lines = summary.split('\n')
            
            # Extract and display URL, company, title, and experience
            url = link.url
            company = lines[0] if len(lines) > 0 else ""
            title = lines[1] if len(lines) > 1 else ""
            experience = lines[2] if len(lines) > 2 else ""
            
            # Display the information in separate lines
            job_id = i + 1
            st.write(f"**Job ID: {job_id}**")
            st.write(f"{company}")
            st.write(f"Job Posting Link: {url}")
            st.write(f"{title}")
            st.write(f"{experience}")
            if i < max_links_to_process - 1:
                st.markdown("---")
