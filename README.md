# ticket-bot
A discord ticket bot that also provides helpful assistance due to finetuning to be a support bot + rag/embeding to access specific support documents



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