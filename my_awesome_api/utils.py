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

openai.api_key = os.environ.get("OPENAI_KEY")

txt_files = [BASE_DIR / "CARNIVAL_IDS.txt", BASE_DIR / "BOOK_IDS.txt"]


def check_book_number(code):
    for file_name in txt_files:
        with open(file_name, 'r') as file:
            for line in file:
                if line.strip() == code:
                    return True
    return False


def choose_element_by_time():
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
    script_dictionary = {
        "0": "Gestures, in love, are incomparably more attractive, effective and valuable than words. But words is all I am. Welcome. Greetings. Felicitation. Howdy. I assume you are in a cave. In the cave? Either way, don't touch the skeletons. They remember how to rage and to eat. Seeing how sorrow eats you, defeats you, I'd rather write about laughing than crying, Ask your questions."
    }

    script_select = script_dictionary[f"{scenario}"]

    return script_select


def prompt_selection(scenario):
    prompt_dictionary = {
        "scenario_0_prompt": "The cave is gone. You are inside a book written on the surface of the moon. You are in the book, so perhaps you are on the moon? In the moon? As you get your bearings, The Moon says all of the following: whispering, and quite slowly. 'I watch TV in a broken mirror. And I watch you in my dreams. I ordered a new keyboard. Each key in this keyboard suggests actions that will happen. One key that I can’t figure out just says 'Fly'. The Moonzine appears, of course, every full moon (instead of me) There are 365 employees writing. They are printing the last issue. The penultimate issue was just a picture of the sun.' The voice grows quiet.\n\nUsing the above text as a prologue to your story, answer the below question by the travelers as the Oracle:\n\nOracle: It’s just ahead. In a red sky and over white hills, it’ll be easy to spot. The portal is in the Sea... It won't let us through but at least someone might get lucky through chance as we depart this cave into legend with you there spiritously depicted on an old wafer with that blue bit of paper stuck around your neck so I will see how long my two friends can make it for...? Likely 'til midnight then huh?\nTravelers: What happens to the Moon once we've gotten trapped in the cave?\nOracle: It is or has been hidden from us in a place of mystery and light. Perhaps behind its reflection when we turn around? It always returns but you feel its presence... somehow, everywhere. \nTravelers:",
        "scenario_1_prompt": "The cave is gone. You are inside a book written on the surface of the moon. You are in the book, so perhaps you are on the moon? In the moon? As you get your bearings, The Moon says all of the following: whispering, and quite slowly. 'I watch TV in a broken mirror. And I watch you in my dreams. I ordered a new keyboard. Each key in this keyboard suggests actions that will happen. One key that I can’t figure out just says 'Fly'. The Moonzine appears, of course, every full moon (instead of me) There are 365 employees writing. They are printing the last issue. The penultimate issue was just a picture of the sun.' The voice grows quiet.\n\nUsing the above text as a prologue to your story, answer the below question by the travelers as the Oracle:\n\nOracle: It’s just ahead. In a red sky and over white hills, it’ll be easy to spot. The portal is in the Sea... It won't let us through but at least someone might get lucky through chance as we depart this cave into legend with you there spiritously depicted on an old wafer with that blue bit of paper stuck around your neck so I will see how long my two friends can make it for...? Likely 'til midnight then huh?\nTravelers: What happens to the Moon once we've gotten trapped in the cave?\nOracle: It is or has been hidden from us in a place of mystery and light. Perhaps behind its reflection when we turn around? It always returns but you feel its presence... somehow, everywhere. \nTravelers:",
        "scenario_2_prompt": "The heros are somewhere like Amsterdam and must find the Prunello Rage Center. To get there, they must first traverse seven labyrinths, each one representing a different type of rage. These labyrinths are Love, Circle, Hex, Linneus, Plantage, Tumba, and Ingrid. Along the way, they must defeat five animate statues that represent various types of rage, including The Story, The Workshop, The Group, The Labyrinth and The Sensory. After defeating the sculptures they enter a chamber that requires them to perform a ritual enacting their own rage. Once they have done this, they are given a coin, which they must swallow in order to find the body that wears a fur coat and periodically tries to kill itself. \n\nOracle: Ding ding, their opponent pissed himself. Looks like the labrinths really did a number on all those who tried it out. I rage every day yet the rage in all of you is hilarious. LOTS OF RAGE IN YE!\nYou: We've been told to be careful around absolutely everything here. And that includes common furniture and tables… like the one we sat down upon. And don't forget about the LEGO. I HATE IT. I'll tell you what though, this is a new bridge experience for me — my first encounter with piles of shit where I can investigate without being shocked or offended by being in it. Anyway, now I realize what could have made us feel uncomfortable doing such an action so many times… mange! I'm even this way as I've been pushed through this cave. No larinth for me I guess!\nOracle: Oh, what a disaster! Those that have gone through here have gone mad. I feel sorry for them, as well as the jester. We may discard in this moment that he is actually considered mad. And by the way, to be disposusive regarding your office over there. It was time for you to retire anyway.\nYou:",
        "scenario_3_prompt": "Intruder is a being of some kind, dusty and fibrous. At first it crept into corners and under nooks and people didn’t mind so much … but now it’s gained courage and is crawling into wide open spaces and swallowing up entire ruins and the monuments they contain. Citizens have been choked from the inside out, the fibres growing out of their corpses and reaching toward the sun. Ages ago, there was a battle. An incredible fight, with bravery and honour and bloodshed, and maidens weeping over bodies (bosoms heaving, of course). The champions were massive, with biceps the size of mountains and fingernail clippings large enough to ship cargo from one coast to another. Angels used their belly buttons like swimming pools after it rained, or so the legends say. Now, lifetimes after the slaughter, it’s a wasteland of rot. The people of the land live in the degraded cavities of skulls and grow food in the red stained soil. Something is overtaking the city… a parasite, a pest… The heros traveled west to find this parasite where fibres start wrapping around their limbs and bodies. They can feel themselves being choked by whatever is floating aimlessly through the air. The sponge of the ground sucks their feet into the land. The heros believe they have failed in their quest, but they sense that the Oracle is close.\n\nYou: Have we failed? Where are we? Oracle help us! We're screaming for breath and light but we don't know when this sponge of ground will stop. We've spoken to everyone who can speak and are trying to help but the stories are strong and the matter is thick.\nOracle: Don’t worry little pimples and sweetbreads, I am your goddess. I’m not far from you and coming your way. I am the goddess of ruination and ruin, the mother of all ends. I am the Dark Oracle, Mother of the Moon, Goddess of Fear. Leave this place as soon as possible. Do not regret dying for doing so ignorant a quest! The paraiste is here and it's within me. It's within all of us!\nYou: The parasite? Already? Oh dear, oh dear. Oh dear, oh dear. I’m scared now. You have to help us if we are all destined to die! Oracle tell us what to do! Oracle tell us how to help these people! The flee from the parasite and save them! Oracle! Oracle! We’ve doomed everyone here. Oracle please help us. Please save our friends. Please? More noodles!\nOracle: Why don’t you listen to me, little balls of dough and pastry? Don’t worry. I'm here already a thousand years ago; this is all but a page turning. Still, perhaps I can convince you to mine more vigour and resolution from your golden spindle— What’s that? Is that someone knocking on the cave walls? No one is here but you yourself! Welcome soul-fleeing Orates! Stop asking repeatedly for the truth and keep looking. What is the nature of the parasite penetrating thighbones? what are we fighting against? Why it has already done so much to this city! Go find out everything about it: its intrinsic characteristics, how it got there in such a way, and where does it live with its fleshy host. Do not fear when your legs are carried to the ground or swept away by necrophobes from below; uncover these worms singing songs forgettable as bells at weddings; gather dark pearls of information.\nYou:",
        "scenario_4_prompt": ""
    }

    prompt_select = prompt_dictionary[f"scenario_{scenario}_prompt"]

    return prompt_select


def chat_history_length(initial_prompt, chat_history):
    """
    Function to check if an API request will be larger than 3000 tokens. If it is, the chat history will need to be trimmed.

    :param initial_prompt:
    :param chat_history:
    :return:
    """
    full_prompt = initial_prompt + chat_history

    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    n_tokens = len(tokenizer.encode(full_prompt))

    if n_tokens >= 1600:
        location = chat_history.find("Travelers:")
        chat_history = chat_history[location + 4:]
        full_prompt = initial_prompt + chat_history

        return full_prompt
    else:
        return full_prompt


def chat_response(chat_input, chat_history, full_chat_history, scenario):
    """
    Inputs text from user
    If there's chat history, it will append to prompt
    Appends Chat_input to the prompt + chat history
    Send full prompt
    Returns text. Shouldn't need to be trimmed.
    Returns text as string
    """

    chosen_model = choose_element_by_time()

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

    response = openai.Completion.create(
        model=chosen_model,
        prompt=f"{full_prompt}",
        temperature=1,
        max_tokens=400,
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
