 #!/usr/bin/python3

from typing import Any, Text, Dict, List

#import the rasa dependencies
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

#import the fetchable dependencies
from fetchable import FetchableClient
from fetchable import configuration



"""
Initialise a FetchableClient object to talk to the fetchable API.

Configure it to use the latest version of the Fetchable API.a

Surround it with try/except to catch the exception raised if
the API keys can't be read from the authentication file.
"""

try:
    client = FetchableClient(api_version=configuration.api_version.latest)
except:
    print("something went wrong initialising the Fetchable client")




"""
Class to handle the joke action
"""
class ActionFetchJoke(Action):

    # return the name of the action
    def name(self) -> Text:
        return "action_fetch_joke"


    # code to be executed when the action is called by rasa core
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # use the client object to fetch a random joke from Fetchable
        response = client.fetch_joke()

        # check for a successful response
        if response['status_code']==200:

            # concatenate the setup and the punchline of the joke and return
            # it to the user
            # e.g. "What's blue and not very heavy? Light blue"
            dispatcher.utter_message(response['setup']+" "+response['punchline'])

        # we'd like to check if the API can't be reached because of a connection error
        # so the user can reconnect the chatbot
        elif response['status_code']==1001:
            dispatcher.utter_message("Unfortunately, I cant connect to the internet right now")

        # catch all other errors and give a generic message back
        else:
            dispatcher.utter_message("Unfortunately, something went wrong")

        return []


"""
Class to handle the quote action
"""
class ActionFetchQuote(Action):

    # return the name of the action
    def name(self) -> Text:
        return "action_fetch_quote"


    # code to be executed when the action is called by rasa core
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # use the client object to fetch an inspirational quote from Fetchable
        quote_response = client.fetch_quote()

        # check for a successful response
        if quote_response['status_code']==200:

            # return a message in the form of <quote> by <author>
            # e.g. "Do, or do not. There is no try." by Yoda
            dispatcher.utter_message("{} by {}".format(quote_response['quote'], quote_response['author']))

        # we'd like to check if the API can't be reached because of a connection error
        # so the user can reconnect the chatbot
        elif quote_response['status_code']==1001:
            dispatcher.utter_message("Can't connect to the internet right now...")

        # catch all other errors and give a generic message back
        else:
            dispatcher.utter_message("Unfortunately, something went wrong")

        return []



"""
Class to handle the fun fact action
"""
class ActionFetchFunFact(Action):

    # return the name of the action
    def name(self) -> Text:
        return "action_fetch_fun_fact"


    # code to be executed when the action is called by rasa core
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # use the client object to fetch a random fun fact from Fetchable
        fun_fact_response = client.fetch_fun_fact()

        # check for a successful response
        if fun_fact_response['status_code']==200:
            # just return the text of the fun fact
            # e.g. "It is physically impossible for you to lick your elbow."
            dispatcher.utter_message(fun_fact_response['fun_fact'])

        # we'd like to check if the API can't be reached because of a connection error
        # so the user can reconnect the chatbot
        elif fun_fact_response['status_code']==1001:
            dispatcher.utter_message("Can't connect to the internet right now...")

        # catch all other errors and give a generic message back
        else:
            dispatcher.utter_message("Unfortunately, something went wrong")

        return []



"""
Class to handle the dictionary / word definition action
"""
class ActionFetchWordDefinition(Action):

    # return the name of the action
    def name(self) -> Text:
        return "action_fetch_word_definition"


    # code to be executed when the action is called by rasa core
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # get all the entities extracted by rasa
        entities = tracker.latest_message['entities']

        # cycle through them and extract the relavant one for us
        word = None
        for e in entities:
            if e['entity'] == "word":
                word = e['value']


        # sanity check to ensure it was filled by rasa
        if word:

            # use the client object to fetch the definition from Fetchable
            response = client.fetch_word_definition(word)

            # check for a successful response
            if response['status_code']==200:

                # words can have multiple meanings so check the length here

                # if there is only one meaning for the word
                if(len(response['meanings'])==1):
                    # even if there is only one meaning for the word, it still arrives in an array
                    # so extract the first element and give it back
                    dispatcher.utter_message("The definition of {} is {}.".format(word, response['meanings'][0]))


                # if there are multiple meanings
                else:
                    # say how many meanings the word has
                    user_response = "{} has {} meanings. ".format(word, len(response['meanings']))

                    # cycle through every meaning and append the meanings onto the
                    # text that will be given back to the user
                    for i, meaning in enumerate(response['meanings']):

                        # this is in the form "1. <meaning>"
                        user_response += str(i+1)+", "+meaning+" "


                    #strip the trailing space and return to the user
                    # e.g. "ameliorate has 2 meanings. 1, To make better; to improve; to meliorate.
                    # 2, To grow better; to meliorate; as, wine ameliorates by age."
                    dispatcher.utter_message(user_response.strip())

            # handle the case that Fetchable doesn't know that word,
            # hopefully won't happen that often (;
            elif response['status_code']==404:
                dispatcher.utter_message("I'm afraid I don't know that")

            # we'd like to check if the API can't be reached because of a connection error
            # so the user can reconnect the chatbot
            elif response['status_code']==1001:
                dispatcher.utter_message("Unfortunately, I cant connect to the internet right now")

            # catch all other errors and give a generic message back
            else:
                dispatcher.utter_message("Unfortunately, something went wrong")

        # if the word entity was not filled properly by rasa, then give a generic message back
        else:
            dispatcher.utter_message("I'm afraid I don't know what you mean")

        return []



"""
Class to handle the entity-attribute action
"""
class ActionFetchTrivia(Action):

    # return the name of the action
    def name(self) -> Text:
        return "action_fetch_trivia"


    # code to be executed when the action is called by rasa core
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        # get all the entities extracted by rasa
        entities = tracker.latest_message['entities']

        # cycle through them and extract the relavant one for us
        entity = None
        attribute = None
        for e in entities:
            if e['entity'] == "entity":
                entity = e['value']
            elif e['entity'] == "attribute":
                attribute = e['value']


        # sanity check to ensure they were filled by rasa
        if entity and attribute:

            # use the client object to fetch the data from Fetchable
            response = client.fetch_entity_attribute(entity, attribute)


            # check for a successful response
            if response['status_code']==200:

                # some attributes have units, e.g. 'length' has the unit of 'miles' or 'kilometers'
                # and some attributes do not have units, e.g. a countries government cannot be a unit.
                # check if this attribute has units or not

                if response['unit'] == "N/A":

                    # this attribute does not have units so return the text in the form:
                    # the <attribute> of <entity> is <value>
                    # e.g the goverment of Ireland is a democracy.
                    dispatcher.utter_message("The {} of {} is {}.".format(attribute, entity, response['value']))

                else:
                    # this attribute has units so return the text in the form:
                    # the <attribute> of <entity> is <value> <units>
                    # e.g the length of the amazon is 6400 kms
                    dispatcher.utter_message("The {} of {} is {} {}.".format(attribute, entity, response['value'], response['unit']))

            # handle the case that Fetchable doesn't know that piece of trivia,
            # hopefully won't happen that often (;
            elif response['status_code']==404:
                dispatcher.utter_message("I'm afraid I don't know that")

            # we'd like to check if the API can't be reached because of a connection error
            # so the user can reconnect the chatbot
            elif response['status_code']==1001:
                dispatcher.utter_message("Unfortunately, I cant connect to the internet right now")

            # catch all other errors and give a generic message back
            else:
                dispatcher.utter_message("Unfortunately, something went wrong")


        # if the entity and attributes entities were not filled properly by rasa,
        # then give a generic message back
        else:
            dispatcher.utter_message("I'm afraid I don't know what you mean")


        return []
