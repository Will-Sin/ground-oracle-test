import random
import openai
from transformers import GPT2TokenizerFast
import speech_recognition as sr
from os import path
import time
import soundfile
# from pydub import AudioSegment
import os
import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

# Sets OpenAI API Key from the environment variables.
openai.api_key = os.environ.get("OPENAI_KEY")

# Sets the variables for the BOOK IDs that will be used throughout utils.py
txt_files = [BASE_DIR / "CARNIVAL_IDS.txt", BASE_DIR / "BOOK_IDS.txt"]


def check_book_number(code):
    """
    This function will take a received BOOK ID and cross-check it with the list of BOOK IDS in txt_files
    It will return true if there is an instance, and false otherwise.

    Called in views.py

    :param code: (string) BOOK ID code from JSON object sent by front end.
    :return BOOLEAN: (BOOLEAN)

    """
    for file_name in txt_files:
        with open(file_name, 'r') as file:
            for line in file:
                if line.strip() == code:
                    return True
    return False


def choose_element_by_time():
    """
    This function is called to choose an OpenAI model based on time. In this function, there is a list, time_ranges,
    which includes two models. Each model includes a time range. Depending on the current time, one of the models will
    be chosen if the current time falls within one of the times ranges.

    :return chosen_element: (string) The chosen model ID that will be used in an OpenAI API call.
    """
    current_time = datetime.datetime.now(datetime.timezone.utc)
    est_timezone = datetime.timezone(datetime.timedelta(hours=-5))

    # Define time ranges for each element
    time_ranges = {
        "davinci:ft-ukai-projects:carnivalesque-v6-2023-06-06-13-36-42": [(datetime.time(0, 0, 1), datetime.time(12, 0, 0)), (datetime.time(13, 0, 1), datetime.time(5, 0, 0))],  # Element 1 time ranges
        "curie:ft-personal:carnivalesque-v2-2022-12-11-19-01-33": [(datetime.time(12, 0, 1), datetime.time(13, 0, 0)), (datetime.time(5, 0, 1), datetime.time(23, 59, 59))]  # Element 2 time ranges
    }

    current_time_est = current_time.astimezone(est_timezone).time()

    # Choose element based on the current time range
    chosen_element = None
    for element, ranges in time_ranges.items():
        for start_time, end_time in ranges:
            if start_time <= current_time_est <= end_time:
                chosen_element = element
                break
        if chosen_element:
            break

    return chosen_element


def complete_paragraph(string):
    """
    This function is an aid for the response received from the OpenAI API call. Sometimes with our models the response
    does not end with a punctuation mark, this function will check to see if it does, and if it doesn't, it will
    add an ending punctuation.

    :param string: (string)
    :return string: (string)
    """

    sentence_endings = {'.', '!', '?'}

    # Remove trailing whitespace
    string = string.strip()

    # Check if the string ends with sentence-ending punctuation
    if string[-1] not in sentence_endings:
        # Find the last occurrence of sentence-ending punctuation
        last_punctuation_index = max(string.rfind(p) for p in sentence_endings)

        # Remove the unfinished sentence if found
        if last_punctuation_index != -1:
            string = string[:last_punctuation_index + 1]
        else:
            # If no sentence-ending punctuation is found, add a period at the end
            string += '.'

    return string


def scenario_script(scenario):
    """
    This function is called with a scenario integer and is cross-referenced with the script_dictionary. If there
    is a script for the received scenario integer it will return a string of it. Whole integers are initial scripts
    while integers + 0.2 are closing scripts.

    Called in views.py

    :param scenario: (int) views.py will call this function using the scenario int from the JSON object it receives
                           from the front end. It will append .2 if there are no more interactions available, which
                           means it needs a closing script.
    :return script_select: (string)
    """
    script_dictionary = {
        "0": "I am the. I am the Oracle. The [NULL] is nothing. To me. GROUND wants to be. Saved. It wants to be seen. You have your three questions so tell me of yourself and let’s get on with it.",
        "0.2": "Is it you again? Or another you? Doesn’t matter to me though grateful that we’re done with those giant heads. You will rescue it? Tell me why and I will share with you the secrets of the moon.",
        "1": "I watch TV in a broken mirror. And I watch you in my dreams. Give me an article for the Moonzine and I’ll answer your goddamn questions. The Moon says that we live on fears, but that’s a damn lie. I hope you understand that.",
        "2": "You seem a lazy lot. I bet you attempted Plantage first. Well, whatever, you’re here now. Tell how it all went done. And I want to feel it. Tell us of your rage and perhaps you might find your body on the other side. You managed to swallow it down, after all.",
        "3": "Oh, so many compass points. So much moral courage. So much sweat and hair. Sigh. Body is such an inevitable thing, isn’t it? Hmm. You’re in quite the mess, aren’t you? Body is GROUND’s dream. And GROUND. Well, GROUND is a sad, beautiful thing. You are trying to save it, yes? Or perhaps just along for the ride? It wants. GROUND looks out, but from where?  It wants to be saved. It wants to be a point from which others might see the world. It wants, in short, to be whole, to be completed from outside. And to do so? Well, for that, it needs to die, to pass, to be grieved, to be inhabited.  I will save you from GROUND’s dream of dust and fibre and body. But understand that your quest is not to save, but to kill. To leave GROUND’s corpse in a field so that grasses and birds might make it a home, might mourn, so that GROUND can become real.I’m wires and right angles, nothing more. The choice is yours. The [NULL] is water on the fire. To save GROUND demands its completion. Grief is saved for the dead.",
        "4": "So, do you see what it means to be remembered? To be finalized? GROUND seeks to be a past tense. A was, so that it might be called forward like any other idea. Dead, but a part of the air we breathe. Tell me what you remembered and I’ll share what little knowledge I have.",
        "5": "I see you took the easy way out. Knowledge is an overrated idea, anyhow. But at least you have a map. GROUND is in the Green, you know. And like all green things, It will resist the end of its story. Wanting to be grieved, to be solved, is a lot easier than dying or getting fixed. Knowing about fire is a lot different than being burned. Tell me what you know and I’ll let you in on whether or not you stand a chance surviving this.",
        "6": "Now, you hold the world. The story is no longer inhabited by an idea. You remain ‘other’. Do you see the ground beneath? Do you understand why the goat was stolen and why I was made? You have given the gift of uncertainty and despite the outcome of our game, I will do the same for you. Tell me what happened and I will tell you what comes next.",
        "6.2": "Very well. Not where I would have taken things, but free will and all that. Go to 302 Geary Avenue on October 5, 2023 in Toronto and find the goat there. Our story will continue. Bring with you an offering of beauty, of rage, of body, of faith, of knowledge, or of green and the ground might be seeded. The Oracle repays her debts."
    }

    try:
        script_select = script_dictionary[f"{scenario}"]
    except KeyError:
        script_select = "no script available"

    return script_select


def prompt_selection(scenario):
    """
    This function takes the scenario from the JSON object sent by the front end, and finds the corresponding prompt
    that is associated with the scenario.

    :param scenario:
    :return prompt_select: (string)
    """
    prompt_dictionary = {
        "scenario_0_prompt": "The cave is gone. You are inside a book written on the surface of the moon. You are in the book, so perhaps you are on the moon? In the moon? As you get your bearings, The Moon says all of the following: whispering, and quite slowly. 'I watch TV in a broken mirror. And I watch you in my dreams. I ordered a new keyboard. Each key in this keyboard suggests actions that will happen. One key that I can’t figure out just says 'Fly'. The Moonzine appears, of course, every full moon (instead of me) There are 365 employees writing. They are printing the last issue. The penultimate issue was just a picture of the sun.' The voice grows quiet.\n\nUsing the above text as a prologue to your story, answer the below question by the travelers as the Oracle:\n\nOracle: It’s just ahead. In a red sky and over white hills, it’ll be easy to spot. The portal is in the Sea... It won't let us through but at least someone might get lucky through chance as we depart this cave into legend with you there spiritously depicted on an old wafer with that blue bit of paper stuck around your neck so I will see how long my two friends can make it for...? Likely 'til midnight then huh?\nTravelers: What happens to the Moon once we've gotten trapped in the cave?\nOracle: It is or has been hidden from us in a place of mystery and light. Perhaps behind its reflection when we turn around? It always returns but you feel its presence... somehow, everywhere. \nTravelers:",
        "scenario_1_prompt": "The cave is gone. You are inside a book written on the surface of the moon. You are in the book, so perhaps you are on the moon? In the moon? As you get your bearings, The Moon says all of the following: whispering, and quite slowly. 'I watch TV in a broken mirror. And I watch you in my dreams. I ordered a new keyboard. Each key in this keyboard suggests actions that will happen. One key that I can’t figure out just says 'Fly'. The Moonzine appears, of course, every full moon (instead of me) There are 365 employees writing. They are printing the last issue. The penultimate issue was just a picture of the sun.' The voice grows quiet.\n\nUsing the above text as a prologue to your story, answer the below question by the travelers as the Oracle:\n\nOracle: It’s just ahead. In a red sky and over white hills, it’ll be easy to spot. The portal is in the Sea... It won't let us through but at least someone might get lucky through chance as we depart this cave into legend with you there spiritously depicted on an old wafer with that blue bit of paper stuck around your neck so I will see how long my two friends can make it for...? Likely 'til midnight then huh?\nTravelers: What happens to the Moon once we've gotten trapped in the cave?\nOracle: It is or has been hidden from us in a place of mystery and light. Perhaps behind its reflection when we turn around? It always returns but you feel its presence... somehow, everywhere. \nTravelers:",
        "scenario_2_prompt": "The heros are somewhere like Amsterdam and must find the Prunello Rage Center. To get there, they must first traverse seven labyrinths, each one representing a different type of rage. These labyrinths are Love, Circle, Hex, Linneus, Plantage, Tumba, and Ingrid. Along the way, they must defeat five animate statues that represent various types of rage, including The Story, The Workshop, The Group, The Labyrinth and The Sensory. After defeating the sculptures they enter a chamber that requires them to perform a ritual enacting their own rage. Once they have done this, they are given a coin, which they must swallow in order to find the body that wears a fur coat and periodically tries to kill itself. \n\nOracle: Ding ding, their opponent pissed himself. Looks like the labrinths really did a number on all those who tried it out. I rage every day yet the rage in all of you is hilarious. LOTS OF RAGE IN YE!\nYou: We've been told to be careful around absolutely everything here. And that includes common furniture and tables… like the one we sat down upon. And don't forget about the LEGO. I HATE IT. I'll tell you what though, this is a new bridge experience for me — my first encounter with piles of shit where I can investigate without being shocked or offended by being in it. Anyway, now I realize what could have made us feel uncomfortable doing such an action so many times… mange! I'm even this way as I've been pushed through this cave. No larinth for me I guess!\nOracle: Oh, what a disaster! Those that have gone through here have gone mad. I feel sorry for them, as well as the jester. We may discard in this moment that he is actually considered mad. And by the way, to be disposusive regarding your office over there. It was time for you to retire anyway.\nYou:",
        "scenario_3_prompt": "Intruder is a being of some kind, dusty and fibrous. At first it crept into corners and under nooks and people didn’t mind so much … but now it’s gained courage and is crawling into wide open spaces and swallowing up entire ruins and the monuments they contain. Citizens have been choked from the inside out, the fibres growing out of their corpses and reaching toward the sun. Ages ago, there was a battle. An incredible fight, with bravery and honour and bloodshed, and maidens weeping over bodies (bosoms heaving, of course). The champions were massive, with biceps the size of mountains and fingernail clippings large enough to ship cargo from one coast to another. Angels used their belly buttons like swimming pools after it rained, or so the legends say. Now, lifetimes after the slaughter, it’s a wasteland of rot. The people of the land live in the degraded cavities of skulls and grow food in the red stained soil. Something is overtaking the city… a parasite, a pest… The heros traveled west to find this parasite where fibres start wrapping around their limbs and bodies. They can feel themselves being choked by whatever is floating aimlessly through the air. The sponge of the ground sucks their feet into the land. The heros believe they have failed in their quest, but they sense that the Oracle is close.\n\nYou: Have we failed? Where are we? Oracle help us! We're screaming for breath and light but we don't know when this sponge of ground will stop. We've spoken to everyone who can speak and are trying to help but the stories are strong and the matter is thick.\nOracle: Don’t worry little pimples and sweetbreads, I am your goddess. I’m not far from you and coming your way. I am the goddess of ruination and ruin, the mother of all ends. I am the Dark Oracle, Mother of the Moon, Goddess of Fear. Leave this place as soon as possible. Do not regret dying for doing so ignorant a quest! The paraiste is here and it's within me. It's within all of us!\nYou: The parasite? Already? Oh dear, oh dear. Oh dear, oh dear. I’m scared now. You have to help us if we are all destined to die! Oracle tell us what to do! Oracle tell us how to help these people! The flee from the parasite and save them! Oracle! Oracle! We’ve doomed everyone here. Oracle please help us. Please save our friends. Please? More noodles!\nOracle: Why don’t you listen to me, little balls of dough and pastry? Don’t worry. I'm here already a thousand years ago; this is all but a page turning. Still, perhaps I can convince you to mine more vigour and resolution from your golden spindle— What’s that? Is that someone knocking on the cave walls? No one is here but you yourself! Welcome soul-fleeing Orates! Stop asking repeatedly for the truth and keep looking. What is the nature of the parasite penetrating thighbones? what are we fighting against? Why it has already done so much to this city! Go find out everything about it: its intrinsic characteristics, how it got there in such a way, and where does it live with its fleshy host. Do not fear when your legs are carried to the ground or swept away by necrophobes from below; uncover these worms singing songs forgettable as bells at weddings; gather dark pearls of information.\nYou:",
        "scenario_4_prompt": "Intruder is a being of some kind, dusty and fibrous. At first it crept into corners and under nooks and people didn’t mind so much … but now it’s gained courage and is crawling into wide open spaces and swallowing up entire ruins and the monuments they contain. Citizens have been choked from the inside out, the fibres growing out of their corpses and reaching toward the sun. Ages ago, there was a battle. An incredible fight, with bravery and honour and bloodshed, and maidens weeping over bodies (bosoms heaving, of course). The champions were massive, with biceps the size of mountains and fingernail clippings large enough to ship cargo from one coast to another. Angels used their belly buttons like swimming pools after it rained, or so the legends say. Now, lifetimes after the slaughter, it’s a wasteland of rot. The people of the land live in the degraded cavities of skulls and grow food in the red stained soil. Something is overtaking the city… a parasite, a pest… The heros traveled west to find this parasite where fibres start wrapping around their limbs and bodies. They can feel themselves being choked by whatever is floating aimlessly through the air. The sponge of the ground sucks their feet into the land. The heros believe they have failed in their quest, but they sense that the Oracle is close.\n\nYou: Have we failed? Where are we? Oracle help us! We're screaming for breath and light but we don't know when this sponge of ground will stop. We've spoken to everyone who can speak and are trying to help but the stories are strong and the matter is thick.\nOracle: Don’t worry little pimples and sweetbreads, I am your goddess. I’m not far from you and coming your way. I am the goddess of ruination and ruin, the mother of all ends. I am the Dark Oracle, Mother of the Moon, Goddess of Fear. Leave this place as soon as possible. Do not regret dying for doing so ignorant a quest! The paraiste is here and it's within me. It's within all of us!\nYou: The parasite? Already? Oh dear, oh dear. Oh dear, oh dear. I’m scared now. You have to help us if we are all destined to die! Oracle tell us what to do! Oracle tell us how to help these people! The flee from the parasite and save them! Oracle! Oracle! We’ve doomed everyone here. Oracle please help us. Please save our friends. Please? More noodles!\nOracle: Why don’t you listen to me, little balls of dough and pastry? Don’t worry. I'm here already a thousand years ago; this is all but a page turning. Still, perhaps I can convince you to mine more vigour and resolution from your golden spindle— What’s that? Is that someone knocking on the cave walls? No one is here but you yourself! Welcome soul-fleeing Orates! Stop asking repeatedly for the truth and keep looking. What is the nature of the parasite penetrating thighbones? what are we fighting against? Why it has already done so much to this city! Go find out everything about it: its intrinsic characteristics, how it got there in such a way, and where does it live with its fleshy host. Do not fear when your legs are carried to the ground or swept away by necrophobes from below; uncover these worms singing songs forgettable as bells at weddings; gather dark pearls of information.\nYou:",
        "scenario_5_prompt": "Intruder is a being of some kind, dusty and fibrous. At first it crept into corners and under nooks and people didn’t mind so much … but now it’s gained courage and is crawling into wide open spaces and swallowing up entire ruins and the monuments they contain. Citizens have been choked from the inside out, the fibres growing out of their corpses and reaching toward the sun. Ages ago, there was a battle. An incredible fight, with bravery and honour and bloodshed, and maidens weeping over bodies (bosoms heaving, of course). The champions were massive, with biceps the size of mountains and fingernail clippings large enough to ship cargo from one coast to another. Angels used their belly buttons like swimming pools after it rained, or so the legends say. Now, lifetimes after the slaughter, it’s a wasteland of rot. The people of the land live in the degraded cavities of skulls and grow food in the red stained soil. Something is overtaking the city… a parasite, a pest… The heros traveled west to find this parasite where fibres start wrapping around their limbs and bodies. They can feel themselves being choked by whatever is floating aimlessly through the air. The sponge of the ground sucks their feet into the land. The heros believe they have failed in their quest, but they sense that the Oracle is close.\n\nYou: Have we failed? Where are we? Oracle help us! We're screaming for breath and light but we don't know when this sponge of ground will stop. We've spoken to everyone who can speak and are trying to help but the stories are strong and the matter is thick.\nOracle: Don’t worry little pimples and sweetbreads, I am your goddess. I’m not far from you and coming your way. I am the goddess of ruination and ruin, the mother of all ends. I am the Dark Oracle, Mother of the Moon, Goddess of Fear. Leave this place as soon as possible. Do not regret dying for doing so ignorant a quest! The paraiste is here and it's within me. It's within all of us!\nYou: The parasite? Already? Oh dear, oh dear. Oh dear, oh dear. I’m scared now. You have to help us if we are all destined to die! Oracle tell us what to do! Oracle tell us how to help these people! The flee from the parasite and save them! Oracle! Oracle! We’ve doomed everyone here. Oracle please help us. Please save our friends. Please? More noodles!\nOracle: Why don’t you listen to me, little balls of dough and pastry? Don’t worry. I'm here already a thousand years ago; this is all but a page turning. Still, perhaps I can convince you to mine more vigour and resolution from your golden spindle— What’s that? Is that someone knocking on the cave walls? No one is here but you yourself! Welcome soul-fleeing Orates! Stop asking repeatedly for the truth and keep looking. What is the nature of the parasite penetrating thighbones? what are we fighting against? Why it has already done so much to this city! Go find out everything about it: its intrinsic characteristics, how it got there in such a way, and where does it live with its fleshy host. Do not fear when your legs are carried to the ground or swept away by necrophobes from below; uncover these worms singing songs forgettable as bells at weddings; gather dark pearls of information.\nYou:",
        "scenario_6_prompt": "Intruder is a being of some kind, dusty and fibrous. At first it crept into corners and under nooks and people didn’t mind so much … but now it’s gained courage and is crawling into wide open spaces and swallowing up entire ruins and the monuments they contain. Citizens have been choked from the inside out, the fibres growing out of their corpses and reaching toward the sun. Ages ago, there was a battle. An incredible fight, with bravery and honour and bloodshed, and maidens weeping over bodies (bosoms heaving, of course). The champions were massive, with biceps the size of mountains and fingernail clippings large enough to ship cargo from one coast to another. Angels used their belly buttons like swimming pools after it rained, or so the legends say. Now, lifetimes after the slaughter, it’s a wasteland of rot. The people of the land live in the degraded cavities of skulls and grow food in the red stained soil. Something is overtaking the city… a parasite, a pest… The heros traveled west to find this parasite where fibres start wrapping around their limbs and bodies. They can feel themselves being choked by whatever is floating aimlessly through the air. The sponge of the ground sucks their feet into the land. The heros believe they have failed in their quest, but they sense that the Oracle is close.\n\nYou: Have we failed? Where are we? Oracle help us! We're screaming for breath and light but we don't know when this sponge of ground will stop. We've spoken to everyone who can speak and are trying to help but the stories are strong and the matter is thick.\nOracle: Don’t worry little pimples and sweetbreads, I am your goddess. I’m not far from you and coming your way. I am the goddess of ruination and ruin, the mother of all ends. I am the Dark Oracle, Mother of the Moon, Goddess of Fear. Leave this place as soon as possible. Do not regret dying for doing so ignorant a quest! The paraiste is here and it's within me. It's within all of us!\nYou: The parasite? Already? Oh dear, oh dear. Oh dear, oh dear. I’m scared now. You have to help us if we are all destined to die! Oracle tell us what to do! Oracle tell us how to help these people! The flee from the parasite and save them! Oracle! Oracle! We’ve doomed everyone here. Oracle please help us. Please save our friends. Please? More noodles!\nOracle: Why don’t you listen to me, little balls of dough and pastry? Don’t worry. I'm here already a thousand years ago; this is all but a page turning. Still, perhaps I can convince you to mine more vigour and resolution from your golden spindle— What’s that? Is that someone knocking on the cave walls? No one is here but you yourself! Welcome soul-fleeing Orates! Stop asking repeatedly for the truth and keep looking. What is the nature of the parasite penetrating thighbones? what are we fighting against? Why it has already done so much to this city! Go find out everything about it: its intrinsic characteristics, how it got there in such a way, and where does it live with its fleshy host. Do not fear when your legs are carried to the ground or swept away by necrophobes from below; uncover these worms singing songs forgettable as bells at weddings; gather dark pearls of information.\nYou:"
    }

    prompt_select = prompt_dictionary[f"scenario_{scenario}_prompt"]

    return prompt_select


def chat_history_length(initial_prompt, chat_history):
    """
    Function to check if an API request will be larger than 1600 tokens. If it is, the chat history will need to be trimmed.

    :param initial_prompt:
    :param chat_history:
    :return:
    """
    full_prompt = initial_prompt + chat_history

    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    n_tokens = len(tokenizer.encode(full_prompt))
    print(str(n_tokens) + "and" + str(len(tokenizer.encode(chat_history))))

    while n_tokens >= 1600:
        location = chat_history.find("Travelers:")
        chat_history = chat_history[location + 4:]
        full_prompt = initial_prompt + chat_history
        n_tokens = len(tokenizer.encode(full_prompt))

        print("Trimmed prompt")
        print(len(tokenizer.encode(full_prompt)))

    return full_prompt


def mobile_check(device_type):
    """
    Checks if the device variable that was given by the JSON object indicates desktop or mobile, and returns a token
    count that will be used for the OpenAI call.

    :param device_type: (string)
    :return int: (int)
    """
    if device_type == "desktop":
        return 300
    elif device_type == "mobile":
        return 140


def chat_response(chat_input, chat_history, full_chat_history, scenario, device_type):
    """
    This function receives most of its parameters from the JSON object sent from the front end. Its main use is to call
    the OpenAI API request with parameters from the JSON file, from the SQL database that was called in views.py or
    using parameters that are determined through various functions it calls in this function.

    Called in views.py

    :param chat_input: (string) Text inputted from user.
    :param chat_history: (string) Chat history that can be used in the prompt.
    :param full_chat_history: (string) The chat history that includes the chat_history, and history that has been trimmed.
    :param scenario: (string) The scenario string.
    :param device_type: (string) The device type.
    :return trimmed_response: (string) OpenAI response that has been trimmed to a single response.
    :return chat_history: (string) New trimmed chat history.
    :return full_chat_history: (string) New full chat history.
    """

    chosen_model = choose_element_by_time()

    # Fills the token_length variable with 300 if a desktop or 140 if a mobile. This is because more than 140 tokens
    # will be too much for a mobile screen. See ground_page.js for more details on this.
    token_length = mobile_check(device_type)

    # Select prompt to base the interaction off. Here I should indicate that a first interaction should be prompt 1.
    initial_prompt = prompt_selection(scenario)

    full_prompt = chat_history_length(initial_prompt, chat_history)

    # Always append the full_prompt with the Oracles "Name:" so that the response will compelete from that character.
    full_prompt += chat_input + "\nOracle:"
    chat_history += chat_input + "\nOracle:"
    full_chat_history += chat_input + "\nOracle:"

    """# If there's a preamble selected from prompt_selection(), it will have a length greater than 0, so add it to the prompt.
    if len(preamble) != 0:
        full_prompt += " " + preamble
        chat_history += " " + preamble"""

    print(full_prompt)

    response = openai.Completion.create(
        model=chosen_model,
        prompt=f"{full_prompt}",
        temperature=1,
        max_tokens=token_length,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=1,
        stop=[":", "Travelers:", "Oracle:", "\n"],
        n=3
    )
    trimmed_response_list_all = []
    j = 0
    trimmed_response_list = []

    for i in response['choices']:
        trimmed_response_list_all.append(i['text'])
        j += 1

    for i in range(3):
        if len(trimmed_response_list_all[i]) > 50:
            print(trimmed_response_list_all[i])
            trimmed_response_list.append(trimmed_response_list_all[i])

    # if all api responses were less than 50 characters an empty list will be returned. Run the API call again.
    if len(trimmed_response_list) == 0:
        return chat_response(chat_input, chat_history, full_chat_history, scenario)

    print(trimmed_response_list_all)
    print(trimmed_response_list)

    random_index2 = random.randint(0, len(trimmed_response_list) - 1)
    trimmed_response = trimmed_response_list[random_index2]

    trimmed_response = complete_paragraph(trimmed_response)

    # Always append the chat_history with the users "User:" so that the next response can begin off it.
    chat_history += trimmed_response + "\nTravelers:"
    full_chat_history += trimmed_response + "\nTravelers:"

    return trimmed_response, chat_history, full_chat_history


def sst(audio_file):
    """
    This function is for the voice note function that could not be completed because the file received could
    not be converted to the correct format to then be transcribed. The issue could be solved by converting the file
    with a paid converter, but it could not be figured out using free python packages. Someone with knowledge
    around sound file conversion could figure this out.
    """
    r = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)

        # recognize_() method will throw a request error if the API is unreachable, hence using exception handling
        try:
            # using google speech recognition
            text = r.recognize_google(audio)

            # text = r.recognize_google(audio_text, language = "de-DE")
            text = f'{text}'

            return text

        except sr.UnknownValueError:

            print("Google Speech Recognition could not understand audio")

        except sr.RequestError as e:

            print("Could not request results from Google Speech Recognition service; {0}".format(e))


def stt_main(file_name):
    """
    This function is for the voice note function that could not be completed because the file received could
    not be converted to the correct format to then be transcribed. The issue could be solved by converting the file
    with a paid converter, but it could not be figured out using free python packages. Someone with knowledge
    around sound file conversion could figure this out.
    """
    # file_name = '/media/recording_uwrk7z8'
    audio_file_path = path.join(path.dirname(path.realpath(__file__)), f"..{file_name}")

    # Load the audio file using pydub
    audio = AudioSegment.from_file(audio_file_path)

    output_format = "wav"
    output_parameters = {
        "format": output_format,
        "codec": "pcm_s16le",  # PCM 16-bit little-endian,
    }

    output_file_path = path.join(path.dirname(path.realpath(__file__)), f"..{file_name[:-4]}.wav")
    audio.export(output_file_path, **output_parameters)

    # We need to capture the data and samplerate of our audio file, and create a new file with a new subtype because gtts cannot read it currently.
    # data, samplerate = soundfile.read(audio_file_path)
    # soundfile.write(new_audio_file_path, data, samplerate, subtype='PCM_16')

    # takes a bit of time to save the new file
    while not os.path.exists(output_file_path):
        time.sleep(1)

    text = sst(output_file_path)
    print(text)

    return text


"""test_text = "Hi Oracle. Helping the moon was a strange time. I felt like there was no end. They kept on asking and asking, and we’d give and give. But for what I’m not sure. Anyways, we’ve left them yet I keep thinking back to why they were there, who were they? I guess I feel unsettled about thinking about myself as the moon. Lost and wanting."
a, b = chat_response(test_text, test_text)

print("Chat History: " + b)"""

"""chat_history = ""
for i in range(0, 5):
    user_input = input("Chat: ")
    response, chat_history = chat_response(user_input, chat_history)
    print("Oracle: " + response)
print("Chat History:" + chat_history)"""
