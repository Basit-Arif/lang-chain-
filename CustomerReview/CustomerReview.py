from typing import List, Tuple,Union
import streamlit as st
from langchain.llms import OpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.pydantic_v1 import BaseModel, Field, validator
from langchain.chat_models import ChatOpenAI
import os
import openai
import time



if 'validated' not in st.session_state:
    st.session_state.validated = False
key = st.sidebar.text_input("Enter your OpenAI API Key", placeholder="Enter your OpenAI API Key", type="password")

@st.cache_resource()
def initialize_openai():
    return openai

def validate_api_key(key):
    openai_instance = initialize_openai()
    openai_instance.api_key = key
    try:
        openai_instance.Completion.create(model="text-davinci-003", prompt="Hello", max_tokens=5)
        return True
    except :
        st.error("Invalid API Key")
        return False

if key == "":
    st.warning("Please enter your OpenAI API Key")
else:
    if not st.session_state.validated:
        st.session_state.validated = validate_api_key(key)
        if st.session_state.validated:
            st.success("API Key is valid")

st.title("Understanding Product Problems: What Customers Complain About 😞")
st.write("Review will be converted into main pain points of product")
review_text = st.text_area("Enter your review here:", height=300)

class ProductEntry(BaseModel):
    id: int 
    customer_name: str = Field(description="Name of the customer") 
    product_name: str 
    problem: Union[List[str], str] = Field(description="Problem with the product") 


class Review(BaseModel):
    Review: list[ProductEntry] 


def review_to_json(review_text):
    # review = """I recently purchased this cookingset with high hopes, but unfortunately, it failed to meet my expectations. The device's performance was inconsistent, with fluctuating heat settings that made styling my hair a bit of a challenge. Moreover, the noise level was surprisingly loud, disrupting my morning routine.\
    # The build quality left much to be desired; the handle felt fragile, I would not recommend this hair dryer based on my experience.\
    # Emily Smith \
    # """

    parser = PydanticOutputParser(pydantic_object=Review)

    prompt = PromptTemplate(
        template="List of reviews given by customers by tripple backslash. Each review starts on a new line. \
        Extract the main cause of the problem in 2-3 words,\
            along with the name and the purchased product.,\
            and if name is not text then say <<not mentioned>> and if purchase product is not text then write <<not mentioned>>\
            and if there is no problem then say <<not Mentioned>> <\
            \n{format_instructions}\n\
            ```{query}\n\
            \
             \
                "
            
            ,
        input_variables=["query"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()},
    )

    _input = prompt.format_prompt(query=review_text)

    # Replace 'model' with your actual OpenAI model instance
    output = model(_input.to_string())
    parsed_output = parser.parse(output)
    return parsed_output.json()









#### model Deployment

progress_text = "Operation in progress. Please wait."              
my_bar = st.progress(0, text=progress_text)
my_bar.empty()
# print(model.predict("how are you"))
if st.button("Convert") and st.session_state.validated:
        if review_text:
            model = OpenAI(model_name="text-davinci-003", temperature=0.0,
               openai_api_key=key)
            main_point = review_to_json(review_text)
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text=progress_text)
            
            st.success("Main Point:")
            st.json(main_point)
        else:

            st.warning("Please enter a review!")













