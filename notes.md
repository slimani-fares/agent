# JUST NOTES
-system prompt (always)  

-The confidence field we added to the json  exposed a interesting thing-the LLM does not have introspective knowledge if its confidence level in an answer so if i want that in the future i should use the `logprobs` from the API or bigger temperature and see on average how much i have the answer  

-got to know about reasoning and chain of thoughts and how it helps to solve complex tasks

-also got to know there are ways to assure a strucutred outputs which can be useful later for tool cals or evals or anything that must fit a certain format

-also learned a bit about prompt injections and the so many ways they can be passed (in files..in code ...etc)

-while implementing the embedding i read in the docs that the task type might change the embedding so for now i am doing a basic retrieval-document and query and then later i will do specefic ones depending on the downstream task 
 
-tools are wired in correctly but there is certainly work to be done on them because most of them are not used untill the llm is exlicilty asked to do so i have to fix this so he knows how to use them just by insinuating

-also things like logging are now as simple as possible later they will be improved and customised 

-memory managament also i will probably add options to clear and browse specefic documents
