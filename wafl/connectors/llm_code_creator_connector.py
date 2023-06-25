from wafl.connectors.base_llm_connector import BaseLLMConnector


class LLMCodeCreatorConnector(BaseLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)

    async def _get_answer_prompt(self, text: str, task: str, function_name: str = None):
        function_name = function_name.split("=")[-1]
        prompt = f"""
The code needs to accomplish the following task: Return the nth Fibonacci number

The function with arguments and output needs to be exactly as in the following. Keep the same names and argument number:
n_th_number = fibonacci(2)

Create a python code that returns the user's request. Import within the function the relevant modules:
def fibonacci(number_to_return):
    if number_to_return == 0:
        return 0
        
    return number_to_return * fibonacci(number_to_return - 1)<|EOS|>
        

The code needs to accomplish the following task: list all files in a folder

The function with arguments and output needs to be exactly as in the following. Keep the same names and argument number:
files = list_all_files("./")

Create a python code that returns the user's request. Import within the function the relevant modules:
def list_all_files(folder_name):
    import os

    files_list = []
    for file in os.listdir(folder_name):
        files_list.append(file)
    return files_list<|EOS|>

        
The code needs to accomplish the following task: {task}

The function with arguments and output needs to be exactly as in the following. Keep the same names and argument number:
{function_name}

Create a python code that returns the user's request. Import within the function the relevant modules:
        """.strip()

        return prompt