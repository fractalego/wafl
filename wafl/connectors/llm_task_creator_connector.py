from wafl.connectors.base_llm_connector import BaseLLMConnector


class LLMTaskCreatorConnector(BaseLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)

    async def _get_answer_prompt(self, text: str, task: str, triggers: str = None):
        prompt = f"""
The intention of the user is the following: the user wants to know to eat at a restaurant

The system has rules that are triggered by the following sentences
- the user wants to know where something is

Create a new rule to answer the user. The first line is the rule trigger. The following lines are the steps to accomplish the task. Use the least steps:
the user wants to eat at a restaurant
   food_type = what type of food do you want?
   restaurant_position = the user wants to know where a {{food_type}} restaurant is
   result = Format this restaurant position {{restaurant_position}} in a convenient way to explain where it is:
   SAY The restaurant you want could be at {{result}}


The intention of the user is the following: the user wants to know if it is going to rain

The system has rules that are triggered by the following sentences
- the user wants to know what the weather is like
- the user wants to know the time

Create a new rule to answer the user. The first line is the rule trigger. The following lines are the steps to accomplish the task. Use the least steps:
the user wants to know if it is going to rain
   weather_forecast = the user wants to know the weather today
   result = Answer the following question given this forecast: {{weather_forecast}} Q: is it going to rain? A:
   SAY {{result}}<|EOS|>


The intention of the user is the following: the user wants to repeat the first thing that they said

The system has rules that are triggered by the following sentences
- The user needs to go

Create a new rule to answer the user. The first line is the rule trigger. The following lines are the steps to accomplish the task. Use the least steps:
the user wants to repeat the first thing that they said 
   first_sentence = What did the user say first?
   SAY {{first_sentence}}<|EOS|>


The intention of the user is the following: the user wants to know where to buy legos

The system has rules that are triggered by the following sentences
- The user wants to know the road to somewhere
- the user wants to add something to the shopping list

Create a new rule to answer the user. The first line is the rule trigger. The following lines are the steps to accomplish the task. Use the least steps:
the user wants to know where to buy legos
   road_to_lego_shop = the user wants to know the road to the nearest lego shop
   result = Answer the following question given this road: {{road_to_lego_shop}} Q: How to get to the lego shop? A:
   SAY {{result}}<|EOS|>


The intention of the user is the following: {task}

The system has rules that are triggered by the following sentences
{triggers}

Create a new rule to answer the user. The first line is the rule trigger. The following lines are the steps to accomplish the task. Use the least steps:
        """.strip()

        return prompt
