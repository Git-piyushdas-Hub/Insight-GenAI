import os
import streamlit as st
from dotenv import load_dotenv
from industry_research import IndustryResearchAgent
from market_standards_agent import MarketStandardsAgent

load_dotenv()

def main():

    st.title("AI Use Case Generator")

    company_name = st.text_input("Enter Company Name:", "Samsung")
    if st.button("Run Analysis"):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        tavily_api_key = os.getenv("TAVILY_API_KEY")

        st.write("Performing industry research...")
        industry_agent = IndustryResearchAgent(company_name, tavily_api_key)
        results = industry_agent.perform_research()

        # Display industry research results
        with st.expander("Industry Research Results", expanded=True):
            for result in results:
                st.markdown(f"**[{result['title']}]({result['url']})**")
                st.write(result['content'])

        st.write("Generating use cases...")
        market_standards_agent = MarketStandardsAgent("search_results.json", openai_api_key, company_name)
        use_cases, additional_resources, dataset_links = market_standards_agent.generate_use_cases()

        # Display the generated use cases
        st.subheader("Generated AI Use Cases")
        for case in use_cases:
            st.write("-", case)

        # Display additional resources
        st.subheader("Recommended Additional Resources")
        for resource in additional_resources:
            st.markdown(f"**[{resource['title']}]({resource['url']})**")

        # st.subheader("Dataset Links")
        # for entry in dataset_links:
        #     st.markdown(f"### Use Case: {entry['use_case']}")
        #     for link in entry['datasets']:
        #         if link['url']:  # If there is a URL, create a link
        #             st.markdown(f"- [{link['title']}]({link['url']})")
        #         else:  # Otherwise, indicate that none were found
        #             st.markdown(f"- {link['title']}")  # This will show "None found"

        st.subheader("Dataset Links")
        for entry in dataset_links:
            # Check if the entry contains a use_case dictionary
            if isinstance(entry['use_case'], dict):
                use_case_title = entry['use_case'].get('UseCase', 'No Use Case Found')
                st.markdown(f"### Use Case: {use_case_title}")
            else:
                st.markdown("### Use Case: None found")

            for link in entry['datasets']:
                if link['url']:  # If there is a URL, create a link
                    st.markdown(f"- [{link['title']}]({link['url']})")
                else:  # Otherwise, indicate that none were found
                    st.markdown(f"- {link['title']}")  # This will show "None found"



        # Propose GenAI Solutions
        st.write("Proposing GenAI Solutions...")
        genai_solutions = market_standards_agent.propose_genai_solutions()
        st.subheader("Proposed GenAI Solutions:")
        st.write(genai_solutions)

if __name__ == "__main__":
    main()
