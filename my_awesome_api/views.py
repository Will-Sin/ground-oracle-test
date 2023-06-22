from rest_framework import viewsets
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .serializers import BookSerializer, UserSerializer
from .models import Book, User, PackageForm
from .utils import chat_response, scenario_script, stt_main, check_book_number
from django.core.exceptions import ObjectDoesNotExist

# ModelViewSet will handle GET and POST without us having to do any more work.
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer()


class BookPostView(APIView):
    """
    Accepts a request from text response from the front end and will return the chat_history, Oracle response and number of interactions available.
    """
    def put(self, request, book_number, user_cave, scenario, ):
        # if / else statement to check if the combined CAVE and Book Number exists (i.e. if a user has created a profile
        # yet.) It will either get the SQL object, or create one.

        if not check_book_number(book_number):
            response_object = {
                "Book ID": "Invalid"
            }

            return Response(response_object)
        else:
            if Book.objects.get(book_number=book_number).exists():
                if User.objects.filter(book_number=book_number, cave=user_cave).exists():
                    entry_user_object = User.objects.get(book_number=book_number, cave=user_cave)
                else:
                    entry_user_object = User.objects.create(book_number=book_number, cave=user_cave)
            else:
                entry_book_object = Book.objects.create(book_number=book_number)
                entry_user_object = User.objects.create(book_number=book_number, cave=user_cave)

        # Retrieves the inputted text from the user.
        inputed_text = request.data.get('book').get('current_inquiry')

        # Gathers the variables from the SQL object. Chat_history being the trimmed chat history that is in proper
        # length in accordance to the max length of the OpenAI API call. Full_chat_history is the full chat history for
        # archival reasons.
        chat_history = entry_book_object.chat_history
        full_chat_history = entry_book_object.full_chat_history
        previous_interactions = entry_user_object.interactions_available

        # If the Book ID is 4 characters, its for Carnival so give them 4 interactions with the Oracle
        # This should either be turned into its own view (A carnival view?) or put somewhere else.
        if len(book_number) == 4:
            # Add 3 entries for speaking to the Oracle
            entry_user_object.interactions_available = 3

        # Searlizer for returning full SQL Object
        # serializer_class = BookSerializer(entry_object)
        # return Response(serializer_class.data)

        # This calls the OpenAI function using the users text, the trimmed chat history, full chat history and the
        # corresponding scenario that was given in the request. It returns the GPT response, and the new chat histories.
        gpt_response, new_chat_history, new_full_chat_history = chat_response(inputed_text, chat_history,
                                                                              full_chat_history, scenario)

        # Removes an interaction available after interacting with the Oracle
        new_iteractions = previous_interactions - 1
        entry_user_object.interactions_available = new_iteractions
        entry_user_object.save()

        # Edits chat_history on SQL Object, and then saves to database
        entry_book_object.chat_history = new_chat_history
        entry_book_object.full_chat_history = new_full_chat_history
        entry_book_object.save()

        # Define the standard response object for this call that will be returned to the front end.
        response_object = {
            "gpt response": f"{gpt_response}",
            "chat history": f"{chat_history}",
            "interactions_available": f"{new_iteractions}"
        }

        return Response(response_object)


class ScenarioScriptView(APIView):
    """
    Accepts a request from the first page of the Oracle where the user enters in the Book ID, their CAVE, and their
    scenario numbers.

    The below retrieves the SQL entry associated with the users CAVE and Book ID, and then returns a response
    with a script from the Oracle if it's their first time interacting with the Oracle for that scenario, and a
    number of interactions available.

    The response will then be received by the front end which will determine if the user needs to produce a voice note
    or not based on how many interactions are available for the user.

    """

    def put(self, request, book_number, user_cave, scenario):

        # if / else statement to check if the combined CAVE and Book Number exists (i.e. if a user has created a profile
        # yet.) It will either get the SQL object, or create one.
        if not check_book_number(book_number):
            response_object = {
                "Book ID": "Invalid"
            }

            return Response(response_object)
        else:
            if User.objects.filter(book_number=book_number, cave=user_cave).exists():
                entry_object = User.objects.get(book_number=book_number, cave=user_cave)
            else:
                entry_object = User.objects.create(book_number=book_number, cave=user_cave)

        # Gathers the variables from the SQL object. Next scenario indicates what scenario is up next for the user.
        # Example: if the user enters Scenario 2 on the front end, and the variable next_scenario from the SQL object is
        # 1, that means the user is now playing on a new scenario, and will be prompted with Oracle script if needed.
        next_scenario = entry_object.next_scenario
        interactions_available = entry_object.interactions_available

        # Define the standard response object for this call that will be returned to the front end.
        response_object = {
            "scenario_script": "",
            "interactions_available": f"{interactions_available}"
        }

        # Updates the next_scenario variable in the SQL object to show that the user has played this scenario at least
        # once, so next time they come back to the Oracle on this current scenario they won't be given the initial
        # script.
        #
        # If the scenario selected by the user is equal to the next_scenario variable form the SQL object then a script
        # will be added to the response object if there is a script available, this is called through the
        # scenario_scription() function. Otherwise, the text "no script needed" will be returned in the response object.
        if next_scenario == scenario:
            entry_object.next_scenario = next_scenario + 1
            entry_object.save()

            response_object['scenario_script'] = f"{scenario_script(next_scenario)}"
        else:
            response_object['scenario_script'] = "no script needed"

        return Response(response_object)


class PresenterPackageFormView(APIView):
    def post(self, request):
        hope_response = request.data.get('hope')
        fear_response = request.data.get('fear')

        entry_object = PackageForm.objects.order_by('hope').first()

        previous_hope = entry_object.hope
        entry_object.hope = previous_hope + f"\n{hope_response}"

        previous_fear = entry_object.fear
        entry_object.fear = previous_fear + f"\n{fear_response}"

        entry_object.save()

        response_object = {
            "Response": "201"
        }

        return Response(response_object)


class FileView(APIView):
    """
    This function accepts a .wav voice file, saves it, transcribes it, and returns a response from the Oracle. It will
    also add 3 interactions to the users SQL object and returns the amount of interactions available (should always
    be 3.)
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, book_number, user_cave, scenario, *args, **kwargs):

        # if / else statement to check if the combined CAVE and Book Number exists (i.e. if a user has created a profile
        # yet.) It will either get the SQL object, or create one.
        if User.objects.filter(book_number=book_number, cave=user_cave).exists():
            entry_user_object = User.objects.get(book_number=book_number, cave=user_cave)
        else:
            entry_user_object = User.objects.create(book_number=book_number, cave=user_cave)

        # Gathers the variables from the SQL object.
        entry_book_object = Book.objects.get(book_number=book_number)
        chat_history = entry_book_object.chat_history
        full_chat_history = entry_book_object.full_chat_history
        previous_interactions = entry_user_object.interactions_available

        # Saves the voice file to the users SQL object and returns an error response if error.
        user_serializer = UserSerializer(entry_user_object, data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Add 3 entries for speaking to the Oracle
        new_iteractions = previous_interactions + 3
        entry_user_object.interactions_available = new_iteractions

        # Make the call to translate the voice to text
        text = stt_main(user_serializer.data['file'])

        # Make the call to the Oracle Model
        gpt_response, new_chat_history, new_full_chat_history = chat_response(text, chat_history,
                                                                              full_chat_history, scenario)

        response_object = {
            "interactions_available": f"{new_iteractions}",
            "gpt response": f"{gpt_response}",
            "chat history": f"{chat_history}"
        }

        entry_book_object.chat_history = new_chat_history
        entry_book_object.full_chat_history = new_full_chat_history
        entry_book_object.save()

        entry_user_object.file.delete()

        entry_user_object.save()

        return Response(response_object, status=status.HTTP_201_CREATED)



