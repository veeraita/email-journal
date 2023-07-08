import random


def select_random_prompts(prompt_file, k=3):
    with open(prompt_file, 'r') as file:
        prompts = file.readlines()
        random_prompts = random.choices(prompts, k=k)
        return [rp.strip() for rp in random_prompts]


def create_message_text(prompt_file):
    msg = "It's time for today's journal entry!\n\nHere are some ideas to get your thoughts flowing:\n\n"
    # Select a few random prompts
    random_prompts = select_random_prompts(prompt_file, k=3)
    msg += '\n'.join(random_prompts)
    return msg
