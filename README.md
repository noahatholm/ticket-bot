# ticket-bot
A discord ticket bot that also provides helpful assistance due to finetuning to be a support bot + rag/embeding to access specific support documents

## Rag
the bot is designed to parse PDF's and split them up based on their headers into vector embeddable chunks that are then stored in a vector database waiting to be queried by the Finetuned LLM the quality of response including Rag data are much higher and it also allows for the LLM to provide things like images which have been extracted from the PDF's

for example
### User Question
`Help my router isn't working its showing a flashing red light?`

### LM's Answer without RAG
`Your router's flashing red light typically indicates a power issue. This can occur due to a dead battery, loose or damaged cables, or a faulty power adapter. To resolve this, ensure that your router is properly plugged into a working outlet and try replacing the batteries if they're old. Check the power cord and cable for any damage or wear. If none of these steps resolve the issue, consider resetting your router to its default settings to see if it resolves the problem.`

This whilst it appears helpful is a hallucination. the real answer lies within the documentation

`I would suggest resetting the router to its factory settings and then reconfiguring the network settings. If the problem persists, consider searching the community forums for known issues or troubleshooting guides specific to your model.` 

Even with higher parameter models the issue isn't known

### LM's Answer with Rag
`According to the documentation, a flashing red light on the router indicates that the system is starting up or the firmware is being upgraded. It's recommended not to disconnect or power off the router during this process. Please wait for a few moments and check if the router continues to flash red. If it stops flashing and shows a different LED pattern, you can proceed with resetting the router or seeking further assistance.`

This answer is far more helpful than the previous too as it is what is stated in the documentation.


## Finetuning
Finetuning is used to take the small (1B) i kinda useless model that was awful at following instruction to convert user questions into good vector database prompts
E.g

### Prompt
`Rewrite the text below into a concise search query (under 12 words). \n- Remove greetings, filler words, and irrelevant phrases. \n- Focus on the core question or concept.\n- In your output provide the rewritten query in <Answer></Answer> Tags\n<Question>Help my router isn't working its showing a flashing red light?</Question> <Answer>router not turning on, displaying flashing red light.`

### Before Finetuning
`Answer]<router not working> flash red light</Answer>`

Response doesn't follow requested format and is just key words extracted not ideal for a querying a vector db
### After Finetuning 
`<Answer>router not turning on, displaying flashing red light.</Answer>`

Now follows the quested format and is cohesive