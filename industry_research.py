import json
from tavily import TavilyClient

class IndustryResearchAgent:

    def __init__(self, company_name, api_key):
        self.company_name = company_name
        self.api_key = api_key
        self.results_data = []

    def perform_research(self):
        tavily_client = TavilyClient(api_key=self.api_key)

        query = (
            f"What industry does {self.company_name} operate in, and what segment the company is working in(e.g., Automotive, Manufacturing, Finance, Retail, Healthcare, etc.)?"
            "What are the company's key offerings and strategic focus areas(e.g., operations, supply chain, customer experience, etc.)?"
            "What are its recent products and its technological advancements?"
            "How has it made use of AI?"
        )

        response = tavily_client.search(query=query, search_depth="advanced", max_results=5)

        results_data = []
        for result in response['results']:
            structured_result = {
                "title": result['title'],
                "url": result['url'],
                "content": result['content']
            }
            results_data.append(structured_result)

        # Save to JSON file
        with open("search_results.json", "w") as file:
            json.dump(results_data, file, indent=2)

        return results_data