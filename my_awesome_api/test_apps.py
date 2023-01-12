import random
import os
import openai

openai.api_key = os.environ.get("OPENAI_KEY")


def prompt_selection(scenario):
    prompt_dictionary = {
        "scenario_1_prompt": "The cave is gone. You are inside a book written on the surface of the moon. You are in the book, " \
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
                             "sure why but I want to know what it is to be alive and dead at once.\nYou: ",
        "scenario_2_prompt": "The heros are somewhere like Amsterdam and must find the Prunello Rage Center. To get there, they must first traverse seven labyrinths, each one representing a different type of rage. These labyrinths are Love, Circle, Hex, Linneus, Plantage, Tumba, and Ingrid. Along the way, they must defeat five animate statues that represent various types of rage, including The Story, The Workshop, The Group, The Labyrinth and The Sensory. After defeating the sculptures they enter a chamber that requires them to perform a ritual enacting their own rage. Once they have done this, they are given a coin, which they must swallow in order to find the body that wears a fur coat and periodically tries to kill itself. \n\nOracle: Ding ding, their opponent pissed himself. Looks like the labrinths really did a number on all those who tried it out. I rage every day yet the rage in all of you is hilarious. LOTS OF RAGE IN YE!\nYou: We've been told to be careful around absolutely everything here. And that includes common furniture and tables… like the one we sat down upon. And don't forget about the LEGO. I HATE IT. I'll tell you what though, this is a new bridge experience for me — my first encounter with piles of shit where I can investigate without being shocked or offended by being in it. Anyway, now I realize what could have made us feel uncomfortable doing such an action so many times… mange! I'm even this way as I've been pushed through this cave. No larinth for me I guess!\nOracle: Oh, what a disaster! Those that have gone through here have gone mad. I feel sorry for them, as well as the jester. We may discard in this moment that he is actually considered mad. And by the way, to be disposusive regarding your office over there. It was time for you to retire anyway.\nYou:",
        "scenario_3_prompt": "Intruder is a being of some kind, dusty and fibrous. At first it crept into corners and under nooks and people didn’t mind so much … but now it’s gained courage and is crawling into wide open spaces and swallowing up entire ruins and the monuments they contain. Citizens have been choked from the inside out, the fibres growing out of their corpses and reaching toward the sun. Ages ago, there was a battle. An incredible fight, with bravery and honour and bloodshed, and maidens weeping over bodies (bosoms heaving, of course). The champions were massive, with biceps the size of mountains and fingernail clippings large enough to ship cargo from one coast to another. Angels used their belly buttons like swimming pools after it rained, or so the legends say. Now, lifetimes after the slaughter, it’s a wasteland of rot. The people of the land live in the degraded cavities of skulls and grow food in the red stained soil. Something is overtaking the city… a parasite, a pest… The heros traveled west to find this parasite where fibres start wrapping around their limbs and bodies. They can feel themselves being choked by whatever is floating aimlessly through the air. The sponge of the ground sucks their feet into the land. The heros believe they have failed in their quest, but they sense that the Oracle is close.\n\nYou: Have we failed? Where are we? Oracle help us! We're screaming for breath and light but we don't know when this sponge of ground will stop. We've spoken to everyone who can speak and are trying to help but the stories are strong and the matter is thick.\nOracle: Don’t worry little pimples and sweetbreads, I am your goddess. I’m not far from you and coming your way. I am the goddess of ruination and ruin, the mother of all ends. I am the Dark Oracle, Mother of the Moon, Goddess of Fear. Leave this place as soon as possible. Do not regret dying for doing so ignorant a quest! The paraiste is here and it's within me. It's within all of us!\nYou: The parasite? Already? Oh dear, oh dear. Oh dear, oh dear. I’m scared now. You have to help us if we are all destined to die! Oracle tell us what to do! Oracle tell us how to help these people! The flee from the parasite and save them! Oracle! Oracle! We’ve doomed everyone here. Oracle please help us. Please save our friends. Please? More noodles!\nOracle: Why don’t you listen to me, little balls of dough and pastry? Don’t worry. I'm here already a thousand years ago; this is all but a page turning. Still, perhaps I can convince you to mine more vigour and resolution from your golden spindle— What’s that? Is that someone knocking on the cave walls? No one is here but you yourself! Welcome soul-fleeing Orates! Stop asking repeatedly for the truth and keep looking. What is the nature of the parasite penetrating thighbones? what are we fighting against? Why it has already done so much to this city! Go find out everything about it: its intrinsic characteristics, how it got there in such a way, and where does it live with its fleshy host. Do not fear when your legs are carried to the ground or swept away by necrophobes from below; uncover these worms singing songs forgettable as bells at weddings; gather dark pearls of information.\nYou:",
        "scenario_4_prompt": ""
    }

    prompt_select = prompt_dictionary[f"scenario_{scenario}_prompt"]

    return prompt_select


def chat_response(chat_input, chat_history, scenario):
    """
    Inputs text from user
    If there's chat history, it will append to prompt
    Appends Chat_input to the prompt + chat history
    Send full prompt
    Returns text. Shouldn't need to be trimmed.
    Returns text as string
    """
    models = ["curie:ft-personal:carnivalesque-v2-2022-12-11-19-01-33"]
    random_index1 = random.randint(0, len(models) - 1)

    # Select prompt to base the interaction off. Here I should indicate that a first interaction should be prompt 1.
    initial_prompt = prompt_selection(scenario)

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

    trimmed_response = (response['choices'][0]['text'])

    chat_history += trimmed_response
    # Always append the chat_history with the users "User:" so that the next response can begin off it.
    new_chat_history = chat_history + "\nYou:"

    return trimmed_response, new_chat_history


"""test_text = "Hi Oracle. Helping the moon was a strange time. I felt like there was no end. They kept on asking and asking, and we’d give and give. But for what I’m not sure. Anyways, we’ve left them yet I keep thinking back to why they were there, who were they? I guess I feel unsettled about thinking about myself as the moon. Lost and wanting."
a, b = chat_response(test_text, test_text)

print("Chat History: " + b)"""

"""chat_history = ""
for i in range(0, 5):
    user_input = input("Chat: ")
    response, chat_history = chat_response(user_input, chat_history)
    print("Oracle: " + response)
print("Chat History:" + chat_history)"""
