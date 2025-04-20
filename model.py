import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model = AutoModelForCausalLM.from_pretrained(
    "deepseek-ai/deepseek-coder-6.7b-instruct",
    trust_remote_code=True,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    device_map="mps"  # Automatically uses GPU if available
)
tokenizer = AutoTokenizer.from_pretrained(
    "deepseek-ai/deepseek-coder-6.7b-instruct",
    trust_remote_code=True
)

# Create pipeline
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    #  device="mps" # Use the same device as the model (GPU/CPU)
)



bot_messages = [
    {"role": "user", "content": "write python script to summarize array number"},
]

prompt = tokenizer.apply_chat_template(
    bot_messages,
    tokenize=False,
    add_generation_prompt=True  # Adds "<|begin_of_sentence|>Assistant:"
)

outputs = pipe(
    prompt,
    max_new_tokens=512,
    temperature=1,  # Lower = more deterministic, higher = creative
    do_sample=True,
    return_full_text=False,  # Exclude the input prompt in output
    eos_token_id=tokenizer.eos_token_id
)

bot_answer = outputs[0]["generated_text"]
print(bot_answer)

