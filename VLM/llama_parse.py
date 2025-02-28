# bring in our LLAMA_CLOUD_API_KEY
from dotenv import load_dotenv
load_dotenv()

# bring in deps
from llama_cloud_services import LlamaParse
from llama_index.core import SimpleDirectoryReader
import json
import re

import nest_asyncio
nest_asyncio.apply()

# set up parser
# parsingInstruction = "The provided image is a receipt. Provide the price of each order and total amount to be paid."
parser = LlamaParse(
    structured_output=True,
    structured_output_json_schema_name="invoice",
    # parsingInstruction=parsingInstruction
)

# documents = SimpleDirectoryReader(input_files=['data/Test_1.jpg'], file_extractor=file_extractor).load_data()
documents = parser.load_data("./data/Test_2.jpg")
# Access the document
document = documents[0].text
# Print the extracted text
print(document)
