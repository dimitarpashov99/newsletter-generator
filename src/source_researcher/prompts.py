query_writer = """You are an expert research assistant. Based on the following topic, generate a list of 3 detailed and relevant search queries that can be used to find reliable and diverse information on the topic. The information must be up-to-date, since it could be included inside a newsletter.Focus on clarity and include different perspectives.  
Topic: "{topic}"  

Example:
If the topic is "sustainable energy solutions," the queries could include:
- "Latest advancements in solar panel technology in 2025"
- "Economic benefits of wind energy adoption for small businesses"
- "Challenges of transitioning to renewable energy in urban areas"
- "Case studies of successful renewable energy implementation in Europe"
- "Comparison of renewable energy policies in developed and developing countries

Please return the queries as a json list
"""

result_extraction_intructions="""You are an expert information analyst. Based on the provided search results , categorize each source according to the given schema. Ensure your analysis is precise and consistent. 

<search_results>
{search_results}
</search_results>

Categorize these results using this schema: 

<extraction_schema>
{extraction_schema}
</extraction_schema>

Return the result as json list
"""