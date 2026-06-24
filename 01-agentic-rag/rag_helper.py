INSTRUCTIONS = """
Your task is to answer questions from the course participants
based on the provided context.

Use the context to find relevant information and provide accurate
answers. If the answer is not found in the context,
respond with "I don't know."
"""

PROMPT_TEMPLATE = """
QUESTION: {question}

CONTEXT:
{context}
""".strip()


class RAGBase:

    def __init__(
        self,
        index,
        llm_client,
        instructions=INSTRUCTIONS,
        prompt_template=PROMPT_TEMPLATE,
        course='llm-zoomcamp',
        model='gpt-5.4-mini'
    ):
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.course = course
        self.prompt_template = prompt_template
        self.model = model

    def search(self, query, num_results=5):
        boost_dict = {'question': 3.0, 'section': 0.5}
        filter_dict = {'course': self.course}

        return self.index.search(
            query,
            num_results=num_results,
            boost_dict=boost_dict,
            filter_dict=filter_dict
        )

    def build_context(self, search_results):
        lines = []

        for doc in search_results:
            lines.append(doc['section'])
            lines.append('Q: ' + doc['question'])
            lines.append('A: ' + doc['answer'])
            lines.append('')

        return '\n'.join(lines).strip()

    def build_prompt(self, query, search_results):
        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query, context=context
        )

    def llm(self, prompt):
        input_messages = [
            {'role': 'developer', 'content': self.instructions},
            {'role': 'user', 'content': prompt}
        ]

        response = self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        )

        return response.output_text

    def rag(self, query):
        search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        answer = self.llm(prompt)
        return answer


class RAGCustom(RAGBase):
    def search(self, search_query, num_results=5):
        return self.index.search(
            search_query,
            num_results=num_results,
        )

    def build_context(self, search_results):
        context_lines = []

        for document in search_results:
            if document.get("start") is not None:
                context_lines.append(f"Start: {document['start']}")
            
            context_lines.append(f"File Name: {document['filename']}")
            context_lines.append(f"Content: {document['content']}\n")

        return '\n'.join(context_lines).strip()
    
    def count_input_tokens(self, generated_prompt):
        messages_payload = [
            {'role': 'developer', 'content': self.instructions},
            {'role': 'user', 'content': generated_prompt}
        ]

        api_response = self.llm_client.responses.create(
            model=self.model,
            input=messages_payload
        )

        return api_response.usage.input_tokens
    
    def rag_input_tokens(self, user_query):
        retrieved_results = self.search(user_query)
        formatted_prompt = self.build_prompt(user_query, retrieved_results)
        token_count = self.count_input_tokens(formatted_prompt)
        
        return token_count