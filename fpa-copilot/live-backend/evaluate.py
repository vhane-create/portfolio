"""Opt-in real OpenAI evaluation: billable API calls, no fake results."""
import asyncio,os,json
from openai import AsyncOpenAI
from app import facts
CASES=["Calculate the total expense variance and label favorable or unfavorable.","What is the Technology department variance?","What caused the expense overspend?"]
async def main():
    if not os.getenv("OPENAI_API_KEY"):raise SystemExit("Set OPENAI_API_KEY privately")
    client=AsyncOpenAI()
    for prompt in CASES:
        r=await client.responses.create(model=os.getenv("OPENAI_MODEL","gpt-6-luna"),instructions="Use only this synthetic dataset: "+json.dumps(facts())+". Do not invent causes. Expense actual above budget is unfavorable.",input=prompt,max_output_tokens=300,store=False)
        print(json.dumps({"prompt":prompt,"answer":r.output_text,"review_required":True}))
if __name__=="__main__":asyncio.run(main())

