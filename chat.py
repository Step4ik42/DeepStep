from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
import sys
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

# Создать pipeline
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
)

# Прочитать токен telegramm
print ('BOT_TOKEN', sys.argv[1])

# Инмциализировать переменную - словарь users
users = {}

# Назначить переменную BOT_TOKEN
BOT_TOKEN = sys.argv[1]

# Функция обработчика при выборе /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global users

    user= update.message.from_user

    # получить userid и username
    id= user['id']
    name= user['username']
    print(id,name)
    await update.message.reply_text(
        "Привет! Жду ваших указаний! Пишите по английски"
    )

# Функция обработчика при выборе /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Доступные команды: /start, /help"
    )

# Функция обработчика /echo
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global users
    user_message = update.message.text
    user= update.message.from_user

    # получить userid и username
    id= user['id']
    name= user['username']
    print(id,name, user_message)
    if len(user_message.split()) >= 256:
        bot_answer = "Too Long question. Keep it short!"
    else:
        bot_messages = [
            {"role": "user", "content": user_message},
        ]

        prompt = tokenizer.apply_chat_template(
            bot_messages,
            tokenize=False,
            add_generation_prompt=True
        )

        outputs = pipe(
            prompt,
            max_new_tokens=512,
            temperature=1,  # Меньшее значение
            do_sample=True,
            return_full_text=False,  # Исключает ввод запроса в ответ
            eos_token_id=tokenizer.eos_token_id
        )

        bot_answer = outputs[0]["generated_text"]
        print(bot_answer)
    await update.message.reply_text(bot_answer)



# Основная функция бота
def main() -> None:
    # Создать объект бота
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавить обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запустить бота
    application.run_polling()

if __name__ == "__main__":
    main()
