import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
import os
from dotenv import load_dotenv
load_dotenv()

class MarketStandardsAgent:
    def __init__(self, filename, openai_api_key, company_name):
        self.filename = filename
        self.openai_api_key = openai_api_key
        self.company_name = company_name
        self.use_cases = []
        self.additional_resources = []

    def load_search_results(self):
        with open(self.filename, "r") as file:
            data = json.load(file)
        return data

    def analyze_results(self, data):
        combined_content = "\n".join(result['content'] for result in data)
        
        # Modify the query to generate an array of objects
        query = (
            f"Analyze the following content and generate at least 20 relevant use cases in the format of a JSON array of objects, "
            f"where each object contains the keys 'UseCase', 'Objective', 'AI application', and 'Cross-Functional Benefits'. "
            f"Make sure to provide a clear structure and avoid any markdown or code block formatting. "
            f"Focus on how {self.company_name} can leverage GenAI, LLMs, and ML technologies to improve their processes, enhance customer satisfaction, and boost operational efficiency."
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ('system', query),
            ('user', '{content}')
        ])

        llm = ChatOpenAI(model="gpt-4o-mini", api_key=self.openai_api_key)
        parser = StrOutputParser()
        chain = prompt | llm | parser

        # Generate the use cases
        use_case_json = chain.invoke({'content': combined_content})

        '''print the use_cases_json'''; print(use_case_json)

        try:
            # Parse the JSON response to a Python list (array of objects)
            parsed_use_cases = json.loads(use_case_json)

            '''print the parsed_use_cases'''; print(parsed_use_cases)

            # Check if the parsed result is a list
            if isinstance(parsed_use_cases, list):
                # Update the use_cases attribute with the array of objects
                self.use_cases.extend(parsed_use_cases)  # Extend the list with new use cases

                # Save to JSON file
                with open("use_cases.json", "w") as json_file:
                    json.dump(self.use_cases, json_file, indent=2)
            else:
                print("Expected an array of use cases, but got:", type(parsed_use_cases))
        except json.JSONDecodeError:
            print("Failed to decode JSON from the LLM output:", use_case_json)


    def recommend_additional_resources(self):
        reports_queries = [
            "AI and digital transformation insights McKinsey",
            "Deloitte AI applications in business",
            "Nexocode digital transformation trends",
            "How is the retail industry leveraging AI and ML",
            "AI applications in automotive manufacturing"
        ]

        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        for query in reports_queries:
            response = tavily_client.search(query=query, search_depth="advanced", max_results=3)
            self.additional_resources.extend(response['results'])


    def collect_resource_assets(self):
        dataset_queries = [
            "AI datasets site:kaggle.com",
            "machine learning datasets site:huggingface.co",
            "AI datasets site:github.com"
        ]
        
        dataset_links = []
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        for use_case in self.use_cases:
            use_case_datasets = []
            useCase = use_case.get('UseCase')

            for query in dataset_queries:
                # Tailor the query to reflect the new use case structure
                full_query = (
                    f"{query} for use case {useCase}"
                )
                
                response = tavily_client.search(query=full_query, search_depth="advanced", max_results=2)
                for result in response['results']:
                    use_case_datasets.append({"title": result['title'], "url": result['url']})

                # Check if we have found at least 2 datasets for this use case
                if len(use_case_datasets) >= 2:
                    break
            
            # If fewer than 2 datasets were found, add "None found" message
            if len(use_case_datasets) < 2:
                use_case_datasets.append({"title": "None found", "url": ""})

            dataset_links.append({
                "use_case": use_case,
                "datasets": use_case_datasets
            })

        with open("datasets.md", "w") as file:
            for entry in dataset_links:
                # Check if the entry contains a use_case dictionary
                if isinstance(entry['use_case'], dict):
                    use_case_title = entry['use_case'].get('UseCase', 'No Use Case Found')
                    file.write(f"### Use Case: {use_case_title}\n")
                else:
                    file.write("### Use Case: None found\n")

                for link in entry['datasets']:
                    if link['url']:  # If there is a URL, create a link
                        file.write(f"- [{link['title']}]({link['url']})\n")
                    else:  # Otherwise, indicate that none were found
                        file.write(f"- {link['title']}\n")  # This will show "None found"


        return dataset_links


    def propose_genai_solutions(self):
        prompt = ChatPromptTemplate.from_messages([
            ('system', 'Propose GenAI solutions, for the following use cases generated'),
            ('user', '{use_cases}')
        ])

        llm = ChatOpenAI(model="gpt-4o-mini", api_key=self.openai_api_key)
        parser = StrOutputParser()
        chain = prompt | llm | parser

        use_cases_text = "\n".join(
            f"UseCase: {use_case['UseCase']}, Objective: {use_case['Objective']}"
            for use_case in self.use_cases
        )
        solutions = chain.invoke({"use_cases": use_cases_text})

        if isinstance(solutions, list):
            solutions = " ".join(solutions)

        return solutions

    def generate_use_cases(self):
        search_results = self.load_search_results()
        self.analyze_results(search_results)
        self.recommend_additional_resources()  # Fetch additional resources
        dataset_links = self.collect_resource_assets()  # Collect dataset links
        return self.use_cases, self.additional_resources, dataset_links
