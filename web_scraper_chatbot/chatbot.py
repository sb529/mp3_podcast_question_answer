import openai

# Set up your OpenAI API key
openai.api_key = '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'


def ask_question(prompt, context):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Specify the model you're using (gpt-4, gpt-3.5-turbo, etc.)
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"}
        ],
        max_tokens=200,
        temperature=0.7
    )
    return response['choices'][0]['message']['content'].strip()
