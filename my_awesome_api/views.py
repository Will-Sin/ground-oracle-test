from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import BookSerializer
from .models import Book
from .test_apps import chat_response, scenario_script


# ModelViewSet will handle GET and POST for Heroes without us having to do any more work.
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer()


# accepts PUT request and returns a custom response
class BookPostView(APIView):
    def put(self, request, book_number, scenario,):
        # Inputted text from user
        current_inquiry = request.data.get('book').get('current_inquiry')

        # SQL Object associated with Book Number inputed by user
        entry_object = Book.objects.get(book_number=book_number)
        chat_history = entry_object.chat_history

        # Searlizer for returning full SQL Object
        # serializer_class = BookSerializer(entry_object)
        # return Response(serializer_class.data)

        # Calling GPT and returning response
        gpt_response, new_chat_history = chat_response(current_inquiry, chat_history, scenario)

        # Edits chat_history on SQL Object, and then saves to database
        entry_object.chat_history = new_chat_history
        entry_object.save()

        return Response({"gpt response": f"{gpt_response}", "chat history": f"{chat_history}"})

        # return Response({"chat history": f"{chat_history}"})


class ScenarioScriptView(APIView):
    def put(self, request, book_number, scenario,):
        entry_object = Book.objects.get(book_number=book_number)
        next_scenario = entry_object.next_scenario

        if next_scenario == scenario:
            script = scenario_script(next_scenario)

            # Updates next_scenario entry for next response
            entry_object.next_scenario = next_scenario + 1
            entry_object.save()

            return Response({"scenario_script": f"{script}"})
        else:
            return Response({"scenario_script": "400"})