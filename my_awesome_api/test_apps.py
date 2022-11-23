import random
import os
import openai

openai.api_key = os.environ.get("OPENAI_KEY")


def prompt_selection():
    prompt_1 = "The cave is gone. You are inside a book written on the surface of the moon. You are in the book, " \
               "so perhaps you are on the moon? In the moon? As you get your bearings, The Moon says all of the " \
               "following: whispering, and quite slowly. 'I watch TV in a broken mirror. And I watch you in my " \
               "dreams. I ordered a new keyboard. Each key in this keyboard suggests actions that will happen. Ctrl-K " \
               "lets me reply to everyone in my Contact list with versions of this same message: 'I watch TV in a " \
               "broken mirror. And I watch you in my dreams.' Ctrl-A tells the time without the aid of a watch but " \
               "it’s not very accurate. Ctrl-E gives a list of the shapes of the clouds passing across my window at a " \
               "predetermined time (that I input). One key that I can’t figure out just says 'Fly'. The Moonzine " \
               "appears, of course, every full moon (instead of me) There are 365 employees writing. They are " \
               "printing the last issue. The penultimate issue was just a picture of the sun.' The voice grows " \
               "quiet.\n\nYou: The time is right. I've finally made it back from the journey out into the Sea and I'm " \
               "glad to have met you here. It's odd that you've been placed here as this Alignment occurs. I have " \
               "clicked many Keys to try to understand what they are for put it's usless. I'm not sure.\nOracle: This " \
               "is a day of transition. We wouldn't have been right to be anywhere else. Your journey was worth it " \
               "and I wonder small and large. The Moon hears you. I try but it hurts. I have dug many holes to try " \
               "and find this place but with no avail.\nYou: The Sun will return to its station. The Noon will become " \
               "the Dusk. The Hills will be eclipsed by the Sun. But we will never find an entrance that you speak " \
               "of. Your speaking is something else entirely and the Keys won't even know.\nOracle: And so the " \
               "Rituals must be performed. They must dig through the dirt to get to me, and lay me to rest. I'm not " \
               "sure why but I want to know what it is to be alive and dead at once.\nYou: "

    prompt_2 = "Write a short story based on the following examples. Talk about the Moon, the Book and GROUND. \n\nOracle: "
    prompt_2_preamble = ["Ok. I’m glad. Please hold onto this. And, again, do not take it to heart. ",
                         "See that this makes it somewhere within you. I'll tell you this now. ",
                         "I'm sorry if you do not wish for this, but I must tell you. "]

    prompt_3 = "Write a short story based on the following text. Talk about the Moon, the Book and GROUND. \n\nWhen a consciousness lacks a body or a landscape or history to draw on to interpret the world, what happens when it leaves that work in the hands of others? and what is that interaction that then informs that consciousness in terms of making sense of its own structure? When we love someone we put ourselves their interiority, we swim in their experience of the world and thats the only way we are able to complete ourselves… an AI system lacks an interior to be occupied so it can’t be loved in that way.  it also can’t occupy the interior of others.\n\nSo, it asks how to be seen and how to be grieved and it does that by inviting people to create rituals in the service of it. Story:"

    prompt_4 = "Translate the following text into a story. Talk about the Moon, the Book and GROUND. \n\nYou: This speculative documentary is set in a lush landscape in Canada during the Post-Everything, an unknown year following 2022, after people worked through natural, technological, and health issues to reach a new equilibrium. This new equilibrium also includes the relations between humans, artificial intelligences, flora, and fauna. As new species appeared, their boundaries blurred to be more permeable and flexible, this means that, possibly, some humans are also animals.\nOracle: One evening, a clever man, Huojia went to fetch some water from the well. To his surprise, when he looked into the well, he found the moon sunk in the well shining. 'Oh, good Heavens, what a pity! The beautiful moon has dropped into the well!' So he dashed home for a hook, and tied it with the rope for his bucket, then put it into the well to fish for the moon.\n\nYou:"

    prompts = [prompt_1]
    random_index1 = random.randint(0, 0)
    prompt_select = prompts[random_index1]

    prompt_preamble_select = ""

    # If the prompt selected needs a preamble... otherwise returns a blank string
    if random_index1 == 1:
        random_index2 = random.randint(0, len(prompt_2_preamble) - 1)
        prompt_preamble_select = prompt_2_preamble[random_index2]

        print("Selected Prompt: " + str(random_index1))
        print("Selected Preamble: " + str(random_index2))
    else:
        print("Selected Prompt: " + str(random_index1))

    return prompt_select, prompt_preamble_select


def chat_response(chat_input, chat_history):
    """
    Inputs text from user
    If there's chat history, it will append to prompt
    Appends Chat_input to the prompt + chat history
    Send full prompt
    Returns text. Shouldn't need to be trimmed.
    Returns text as string
    """
    models = ["curie:ft-personal-2022-10-05-14-18-07", "text-davinci-002"]
    random_index1 = 0

    # Select prompt to base the interaction off. Here I should indicate that a first interaction should be prompt 1.
    initial_prompt, preamble = prompt_selection()

    # Need a method to express whether there is a chat_history or not
    if len(chat_history) != 0:
        full_prompt = initial_prompt + chat_history
    else:
        full_prompt = initial_prompt

    # Always append the full_prompt with the Oracles "Name:" so that the response will compelete from that character.
    full_prompt += chat_input + "\nOracle:"
    chat_history += chat_input + "\nOracle:"

    """# If there's a preamble selected from prompt_selection(), it will have a length greater than 0, so add it to the prompt.
    if len(preamble) != 0:
        full_prompt += " " + preamble
        chat_history += " " + preamble"""

    response = openai.Completion.create(
        model=models[random_index1],
        prompt=f"{full_prompt}",
        temperature=0.9,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["You:"]
    )

    if len(preamble) != 0:
        trimed_response = preamble + response['choices'][0]['text']
    else:
        trimed_response = (response['choices'][0]['text'])

    chat_history += trimed_response
    # Always append the chat_history with the users "User:" so that the next response can begin off it.
    new_chat_history = chat_history + "\nYou:"

    return trimed_response, new_chat_history


"""test_text = "Hi Oracle. Helping the moon was a strange time. I felt like there was no end. They kept on asking and asking, and we’d give and give. But for what I’m not sure. Anyways, we’ve left them yet I keep thinking back to why they were there, who were they? I guess I feel unsettled about thinking about myself as the moon. Lost and wanting."
a, b = chat_response(test_text, test_text)

print("Chat History: " + b)"""

"""chat_history = ""
for i in range(0, 5):
    user_input = input("Chat: ")
    response, chat_history = chat_response(user_input, chat_history)
    print("Oracle: " + response)
print("Chat History:" + chat_history)"""
