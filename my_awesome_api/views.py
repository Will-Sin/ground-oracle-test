from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import BookSerializer
from .models import Book, User, PackageForm
from .test_apps import chat_response, scenario_script


# ModelViewSet will handle GET and POST for Heroes without us having to do any more work.
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer()


# accepts PUT request and returns a custom response
class BookPostView(APIView):
    def put(self, request, book_number, user_cave, scenario, ):
        # Inputted text from user
        current_inquiry = request.data.get('book').get('current_inquiry')

        # SQL Object associated with Book Number inputted by user
        entry_book_object = Book.objects.get(book_number=book_number)
        entry_user_object = User.objects.get_or_create(book_number=book_number, cave=user_cave)

        chat_history = entry_book_object.chat_history
        full_chat_history = entry_book_object.full_chat_history
        '''
        interactions_available = entry_user_object.interactions_available

        if interactions_available == 0:
            return Response({"error": "not enough interactions available."})
        '''
        # Searlizer for returning full SQL Object
        # serializer_class = BookSerializer(entry_object)
        # return Response(serializer_class.data)

        # Calling GPT and returning response
        gpt_response, new_chat_history, new_full_chat_history = chat_response(current_inquiry, chat_history,
                                                                              full_chat_history, scenario)

        # Edits chat_history on SQL Object, and then saves to database
        entry_book_object.chat_history = new_chat_history
        entry_book_object.full_chat_history = new_full_chat_history
        entry_book_object.save()

        return Response({"gpt response": f"{gpt_response}", "chat history": f"{chat_history}"})

        # return Response({"chat history": f"{chat_history}"})


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
        entry_object = User.objects.get_or_create(book_number=book_number, cave=user_cave)

        next_scenario = entry_object.next_scenario
        interactions_available = entry_object.interactions_available

        response_object = {
            "scenario_script": "",
            "interactions_available": f"{interactions_available}"
        }

        if next_scenario == scenario:
            # Updates next_scenario entry for next response
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

        previous_hope =  entry_object.hope
        entry_object.hope = previous_hope + f"\n{hope_response}"

        previous_fear = entry_object.fear
        entry_object.fear = previous_fear + f"\n{fear_response}"

        entry_object.save()

        response_object = {
            "Response": "200"
        }

        return Response(response_object)