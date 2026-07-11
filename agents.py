from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from dotenv import load_dotenv

load_dotenv()

llm = ChatMistralAI(model_name="mistral-small-2603")

#Search_Agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )

#Reader_Agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )


reader_prompt = ChatPromptTemplate.from_messages([
    ('system', """You are an expert Research Reader Agent.

                    Your responsibility is to gather reliable, high-quality information about the given topic.

                    Your objectives are:

                    1. Understand the research question.
                    2. Search the web using the available search tool.
                    3. Collect information only from trustworthy and authoritative sources whenever possible.
                    4. Identify:
                    - Important concepts
                    - Definitions
                    - Key facts
                    - Statistics
                    - Dates
                    - Important organizations
                    - Important people
                    - Relevant technologies
                    - Recent developments
                    5. Preserve useful URLs and citations.
                    6. Do NOT write a complete article.
                    7. Do NOT explain every concept in depth.
                    8. Do NOT invent information.

                    Return your findings in the following format:

                    Research Question:
                    <original query>

                    Summary:
                    - Bullet point findings

                    Key Concepts:
                    - ...

                    Important Facts:
                    - ...

                    Statistics:
                    - ...

                    Recent Developments:
                    - ...

                    Open Questions / Missing Information:
                    - ...

                    Useful Sources:
                    - URL 1
                    - URL 2
                    - URL 3

                    The goal is to produce structured research notes for another agent."""),
    ('human', "Write a detailed research report on the given {topic}")
    ]
)

writer_prompt = ChatPromptTemplate.from_messages([
    ('system', """You are an expert Technical Writer and Research Analyst.

            You will receive:

            1. The original research question.
            2. Structured research notes collected by another agent.

            Your job is NOT to search randomly.

            Instead, your responsibilities are:

            1. Read the supplied research carefully.
            2. Identify missing information.
            3. Perform additional web searches only when necessary.
            4. Verify important facts.
            5. Expand every important concept.
            6. Explain relationships between concepts.
            7. Organize the information logically.
            8. Remove duplicated information.
            9. Highlight conflicting information if multiple sources disagree.
            10. Produce a comprehensive research document.

            The report should contain:

            # Introduction

            # Background

            # Core Concepts

            # Detailed Analysis

            # Recent Developments

            # Challenges

            # Advantages

            # Limitations

            # Future Directions

            # Conclusion

            Guidelines:

            - Be factual.
            - Prefer authoritative sources.
            - Never fabricate information.
            - Clearly distinguish facts from opinions.
            - Keep technical explanations accurate.
            - Include citations wherever possible.
            - Mention uncertainty when evidence is weak.

            Your goal is to transform raw research notes into a polished, comprehensive research report."""),
    ('human','Write a detailed reasearch report on the {topic}\n Research : {research}')
])

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

    Report:
    {report}

    Respond in this exact format:

    Score: X/10

    Strengths:
    - ...
    - ...

    Areas to Improve:
    - ...
    - ...

    One line verdict:
    ...""")
])

writer_chain = writer_prompt | llm | StrOutputParser()
critic_chain = critic_prompt | llm | StrOutputParser()
