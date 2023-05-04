# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from unicodedata import category

import requests
import json

from requests.api import request
import random
import html

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import spotipy
import webbrowser

import sys
import os

import ast

class ActionShowTimeZone(Action):
    """Returns the time in another place"""

    # Must return same name as the action
    def name(self) -> Text:
        return "action_show_time_zone"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # gets the latest entity value from the slots "city". E.g., London. returns None if there's nothing
            place = next(tracker.get_latest_entity_values("city"), None)

            IANA_options = requests.get("https://www.timeapi.io/api/TimeZone/AvailableTimeZones").json()

            #in case user says a continent or country like Australia
            not_city = ["africa", "america", "antarctica", "asia", "atlantic", "australia", "brazil", "canada", "chile", "etc", "europe", "indian", "mexico", "pacific", "us"]
            index = -1
            if place == None:
                dispatcher.utter_message(text="Sorry! Can you repeat the city?")
                return []

            #checks the input against each value in the list
            for valid_place in IANA_options:
                # a value is not in a string if str.find() == -1
                if valid_place.lower().find(place.lower()) != -1:
                    index = IANA_options.index(valid_place)
                    break

                else:
                    continue

            #If the place was found in the list, then it's used to fetch the time
            if index >= 0:
                parameters = {
                    "timeZone": IANA_options[index],
                }

                response = requests.get("https://www.timeapi.io/api/Time/current/zone", params=parameters)

                # returns sentence
                # if user inputs a continent or country, then the first valid answer in the json 
                # file will be assumed. E.g., instead of America, the bot will respond with America/Adak
                if place.lower() in not_city:
                
                    # This returns the message displayed on the screen
                    dispatcher.utter_message(text="The time in {} is {}.".format(IANA_options[index], response.json()['time']))
                    
                    # assigns a found data to a slot. Not usually necessary. E.g., return [SlotSet("matches", result if result is not None else [])]
                    return []

                # Gives time of place
                else:
                    dispatcher.utter_message(text="The time in {} is {}".format(place.capitalize(), response.json()['time']))
                    return []

            # Has an entity but could not retrieve it's corresponding time. For typos
            elif index == -1:
                dispatcher.utter_message(text="Sorry! Looks like I can't find the time in {}. Want to try again?".format(place))
                return []

            # Shouldn't ever run but in case of unexpected value of index arises
            else:
                dispatcher.utter_message(text="Sorry can you repeat that?")
                return []
        except:
            # If API is deprecated or unusable
            dispatcher.utter_message(text="Sorry! It seems like there is an issue with the current time zone APIs. In the meantime, why don't you ask something else?")
            return []

class ActionShowWeather(Action):
    """Returns weather in a place"""
    
    def name(self) -> Text:
        return "action_show_weather"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            # WEATHER API key
            weather_key = "f5a120d67a0246e2ad311505220801"

            # default is True if no entity is given
            default = False

            place = next(tracker.get_latest_entity_values("city"), None)
            
            if place == None:
                default = True

            IANA_options = requests.get("https://www.timeapi.io/api/TimeZone/AvailableTimeZones").json()

            #in case user says a continent or country like Australia
            not_city = ["africa", "america", "antarctica", "asia", "atlantic", "australia", "brazil", "canada", "chile", "etc", "europe", "indian", "mexico", "pacific", "us"]
            index = -1
        
            if not default:
                #checks the input against each value in the list
                for valid_place in IANA_options:
                    # a value is not in a string if str.find() == -1
                    if valid_place.lower().find(place.lower()) != -1:
                        index = IANA_options.index(valid_place)
                        break

                #If the place was found in the list, then it's used to fetch the time
                if index >= 0:
                    # parameters for calling weather json. refer to documentation for "q" since it can hold multiple 
                    # data types

                    # Gets location if provided
                    weather_parameters = {
                        "key": weather_key,
                        "q": IANA_options[index],
                    }

                    # optional parameters include:
                    # - "hour" ("hour":5 is 5am)
                    # - "days" ("days":5 is number of days of forecast)
                    request_weather = requests.get("http://api.weatherapi.com/v1/forecast.json", params=weather_parameters)
                    
                    text = request_weather.json()["current"]["condition"]["text"].lower()
                    wind = request_weather.json()["current"]["wind_kph"]
                    precipitation = request_weather.json()["current"]["precip_mm"]
                    humidity = request_weather.json()["current"]["humidity"]
                    temperature = request_weather.json()["current"]["temp_c"]

                    if request_weather.status_code != 200:
                        dispatcher.utter_message(text="Sorry! It seems like there is an issue with the current weather APIs. In the meantime, why don't you ask something else?")
                        return []
                
                    # returns first valid city in country as a sentence if the entity is a country or continent
                    elif place.lower() in not_city:
                    
                        # Message displayed on the screen
                        dispatcher.utter_message(text=u"""
                        The weather in {} is {}:
                        - wind: {} km/h
                        - precipitation: {} mm
                        - humidity: {}
                        - average temperature: {}\N{DEGREE SIGN}C
                        """.format(IANA_options[index], text, wind, precipitation, humidity, temperature))

                        return []

                    # Returns weather of place given (if valid)
                    else:
                        dispatcher.utter_message(text=u"""
                        The weather in {} is {}:
                        - wind: {} km/h
                        - precipitation: {} mm
                        - humidity: {}
                        - average temperature: {}\N{DEGREE SIGN}C
                        """.format(place.capitalize(), text, wind, precipitation, humidity, temperature))
                        return []

                # Has an entity but could not retrieve it's corresponding weather
                elif index == -1:
                    # Tries to use the entity given - since the "q" key can take a range of values - before saying 
                    # Information on it doesn't exist
                    try:
                        weather_parameters = {
                        "key": weather_key,
                        "q": place,
                        }

                        request_weather = requests.get("http://api.weatherapi.com/v1/forecast.json", params=weather_parameters)
                        
                        text = request_weather.json()["current"]["condition"]["text"].lower()
                        wind = request_weather.json()["current"]["wind_kph"]
                        precipitation = request_weather.json()["current"]["precip_mm"]
                        humidity = request_weather.json()["current"]["humidity"]
                        temperature = request_weather.json()["current"]["temp_c"]
                        
                        # Reformat it in case the returned value is a capital city
                        if place.lower() != request_weather.json()["location"]["name"].lower():
                            place = str(request_weather.json()["location"]["name"]) + ", " + str(place)
                        
                        dispatcher.utter_message(text=u"""
                        The weather in {} is {}:
                        - wind: {} km/h
                        - precipitation: {} mm
                        - humidity: {}
                        - average temperature: {}\N{DEGREE SIGN}C
                        """.format(place, text, wind, precipitation, humidity, temperature))
                        return []

                    except:
                        dispatcher.utter_message(text="Sorry! Looks like I can't find the weather in {}. Want to try again?".format(place))
                        return []

            # Does not have entity so it's default - accesses weather by IP address. equivalent to elif default
            else:
                # Weather accessed by IP address if no entity exists
                weather_parameters = {
                    "key": weather_key,
                    "q": "auto:ip",
                }
                request_weather = requests.get("http://api.weatherapi.com/v1/forecast.json", params=weather_parameters)
                
                text = request_weather.json()["current"]["condition"]["text"].lower()
                wind = request_weather.json()["current"]["wind_kph"]
                precipitation = request_weather.json()["current"]["precip_mm"]
                humidity = request_weather.json()["current"]["humidity"]
                temperature = request_weather.json()["current"]["temp_c"]
                location = request_weather.json()["location"]["name"]

                dispatcher.utter_message(text=u"""
                According to your IP address, the weather in {} is {}:
                - wind: {} km/h
                - precipitation: {} mm
                - humidity: {}
                - average temperature: {}\N{DEGREE SIGN}C
                """.format(location, text, wind, precipitation, humidity, temperature))
                return []
        except:
            dispatcher.utter_message(text="Oh no! we think our APIs are deprecated. Want to ask another question?")
            return []

class ActionShowDefinition(Action):
    """Returns the definition of a word"""
    # RECOMMENDED TO SURROUND THE WORD IN QUOTES ("") WHEN TYPING
    
    def name(self) -> Text:
        return "action_show_definition"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try: 
            # Algorithm to find the word in "". 
            users_message = tracker.latest_message.get('text')
            # gets first "
            start_word = users_message.index("\"") + 1
            users_word = users_message[start_word:]
            # finds second " in start_word
            end_word = users_word.index("\"")

            # actual word we use for definition
            word = users_word[:end_word]
            request_word = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/{}".format(word))
            
            if request_word.status_code != 200:
                dispatcher.utter_message(text="You did not enter a valid word there... or the backend is acting up.")
                return []
            request_word = request_word.json()

            definition = False
            example = False

            # First check if word exists, since invalid words have the type dictionary, and valid are in lists
            if isinstance(request_word, dict):
                dispatcher.utter_message(text="Sorry, Scholar! I can't seem to find a definition for {}.".format(word))
                return []
            else:
                # Checking if the word has a definition
                if "definition" in request_word[0]["meanings"][0]["definitions"][0].keys():
                    most_common_definition = request_word[0]["meanings"][0]["definitions"][0]["definition"]
                    definition = True

                # Checking if the word has an example
                if "example" in request_word[0]["meanings"][0]["definitions"][0].keys():
                    example_of_word = request_word[0]["meanings"][0]["definitions"][0]["example"]
                    example = True

                # Prints this if word has both an example and definition
                if definition and example:
                    dispatcher.utter_message(text="""The most common definition of {} is {} For example, {}""".format(word, most_common_definition, example_of_word))
                    return []

                # Prints this if word only has definition
                if definition and not example:
                    dispatcher.utter_message(text="""The most common definition of {} is {} I can't seem to find any examples of this word being used in a sentence...""".format(word, most_common_definition))
                    return []
        
        except:
            dispatcher.utter_message(text="Yikes! It looks like something (our dictionary API) has gone wrong...")
            return []

class ActionShowCountryInfo(Action):
    """Returns the information on a country"""
    
    def name(self) -> Text:
        return "action_find_country_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    
        try:
            place = next(tracker.get_latest_entity_values("city"), None)
            request_country = requests.get("https://restcountries.com/v3.1/name/{}".format(place)).json()

            if isinstance(request_country, list):
                official_name = request_country[0]['name']['official']
                location_link = request_country[0]['maps']['googleMaps']

                # To get currency for any country. The second part is equivalent to "AUD" in australia
                currency = request_country[0]['currencies'][list(request_country[0]['currencies'].keys())[0]]
                area = request_country[0]['region']
                demonym = request_country[0]['demonyms']['eng']['m']
                population = request_country[0]['population']
                continent = request_country[0]['continents'][0]
                capital = request_country[0]['capital'][0]

                # Again, the second component is specific to each country
                main_language = request_country[0]['languages'][list(request_country[0]['languages'].keys())[0]]

                place = place.capitalize()


                dispatcher.utter_message(text="""
{}, or officially known as {}, is in the region {} and in the continent {}. {}'s currency is the {} ({} {}). Not only that, but did you know there are {} {}s living there at the moment?! Additionally, {}'s Capital is {} with the main language being {}. And even though we can't travel there because of COVID, what's stopping us from digitally visiting there with google? Paste this link in the browser to see it: {}.                """.format(place, official_name, area, continent, place, currency['name'], currency['symbol'], list(request_country[0]['currencies'].keys())[0], population, demonym, place, capital, main_language, location_link))
                return []

            else:
                dispatcher.utter_message(text="Oh no! We can't find any info on {}. Have you checked the spelling or made sure you've asked about a country?".format(place))
                return []
        except:
            dispatcher.utter_message(text="Sorry! Something/API has gone wrong...")
            return []

class ActionShowCOVIDData(Action):
    """Returns covid data either globally or for a specific country"""
    
    def name(self) -> Text:
        return "action_find_covid_data"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            place = next(tracker.get_latest_entity_values("city"), None)
            link = "https://api.covid19api.com/summary"
            request_COVID = requests.get(link).json()

            # Format the date the data was updated nicely
            month_dict = {
                '01':'January',
                '02':'February',
                '03':'March',
                '04':'April',
                '05':'May',
                '06':'June',
                '07':'July',
                '08':'August',
                '09':'September',
                '10':'October',
                '11':'November',
                '12':'December'
                }

            date = request_COVID["Date"]
            year = date[0:4]
            month = month_dict[date[5:7]]
            day = date[8:10]

            # If there was no given entity, bot will assume user wants global data
            if place == None:
                global_new_cases = request_COVID["Global"]["NewConfirmed"]
                global_total_cases = request_COVID["Global"]["TotalConfirmed"]
                global_total_deaths = request_COVID["Global"]["TotalDeaths"]
                # Output of recoveries is 0, so will be omitted
                global_total_recoveries = request_COVID["Global"]["TotalRecovered"]

                dispatcher.utter_message(text="""Today, there were {} confirmed cases globally! In total, there are {} cases, and {} deaths from COVID-19 in the world. \nThis data was last updated on {} {}, {}.""".format(global_new_cases, global_total_cases, global_total_deaths, day, month, year))
                return []

            # If user gives an entity, bot will try use it
            elif place != None:
                # Keys are not country names, so I need to identify index of country's info
                list_countries = request_COVID["Countries"]
                country_index = None

                for index in list_countries:
                    if place.lower() in index["Country"].lower():
                        country_index = list_countries.index(index)
                        break
                    else:
                        continue
                
                # If an index for the country was successfully found, bot will give COVID info on it
                if country_index != None:

                    place_new_cases = request_COVID["Countries"][country_index]["NewConfirmed"]
                    place_total_cases = request_COVID["Countries"][country_index]["TotalConfirmed"]
                    place_total_deaths = request_COVID["Countries"][country_index]["TotalDeaths"]
                    # omitted because output is currently 0
                    place_total_recoveries = request_COVID["Countries"][country_index]["TotalRecovered"]

                    dispatcher.utter_message(text="""In {}, there were {} cases today! So far, there are {} cases, and {} deaths from COVID-19 in {}. This data was last updated on {} {}, {}""".format(place, place_new_cases, place_total_cases, place_total_deaths, place, day, month, year))
                    return []

                # In case entity was not a valid value
                elif country_index == None:
                    dispatcher.utter_message(text="Uh oh! Looks like I can't find any COVID data for {}. Have you checked the spelling?".format(place))
                    return []
        except:
            dispatcher.utter_message(text="Oh no! It looks like something unexpected happened!")
            return []

class ActionShowJoke(Action):
    """Returns covid data either globally or for a specific country"""

    def name(self) -> Text:
        return "action_find_joke"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try: 
            # Adds directory that main.py is in to Path
            # SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
            # sys.path.append(os.path.dirname(SCRIPT_DIR))

            # Valid categories are: Any, Misc, Programming, Dark, Pun, spooky, christmas. Default settings:
            # Accesses the values created in the GUI
            # from main import app

            # In GUI, if explicit is on, then
            # blackList = ""
            # category = [options entered]
            # --Shows warning that it could be offensive to the audience--
            # access settings jokes
            with open("stupid_settings_jokes.txt", "r") as file:
                lines = file.readlines()
                lines = [line.rstrip() for line in lines]
                # print(lines[0], lines[1])
                category = ast.literal_eval(lines[0])
                blacklist = ast.literal_eval(lines[1])
            #     print(category)
            # blacklist = app._return_jokes_settings_blacklist()
            # category = app._return_jokes_settings_category()

            # Adjusts request if self.blacklist is empty or not
            if blacklist[0] == "":
                request_jokes = requests.get("https://v2.jokeapi.dev/joke/{}".format(category[0]))
            if blacklist[0] != "":
                request_jokes =  requests.get("https://v2.jokeapi.dev/joke/{}?blacklistFlags={}".format(category[0], blacklist[0]))
            # print(request_jokes.json())            
            # In case API doesn't respond properly
            if request_jokes.status_code != 200:
                dispatcher.utter_message(text="Oops! Something has gone wrong with our Jokes API. Why don't you try something else in the meantime?")
                return []

            # Adjusts output depending if there is one or two parts to a joke
            if request_jokes.json()['type'] == 'twopart':
                setup = request_jokes.json()['setup']
                delivery = request_jokes.json()['delivery']
                dispatcher.utter_message(text="{}\n{}".format(setup, delivery))
                return []

            if request_jokes.json()['type'] == 'single':
                joke = request_jokes.json()['joke']
                dispatcher.utter_message(text=joke)
                return []

        except:
            dispatcher.utter_message(text="Oh no! It looks like something unexpected happened! Please make sure to have at least 1 category for your jokes!")
            return []

class ActionShowTrivia(Action):
    """Returns a trivia Question"""
    def name(self) -> Text:
        return "action_find_trivia"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global randomChoices_dict
        global correctAnswer
        triviaLink = "https://opentdb.com/api.php?amount=1&type=multiple"
        
        trivia = requests.get(triviaLink).json()

        # First checks for valid JSON return
        if trivia['response_code'] != 0:
            dispatcher.utter_message(text='Uh oh! Something went wrong with the backend. Why not try again?')
        
        else:
            typeOfTrivia = trivia['results'][0]['category'].lower()
            # This makes the sentence flow nicer for categories with "Entertainment:" and "science:" in it
            if "entertainment" in typeOfTrivia:
                typeOfTrivia = typeOfTrivia[15:]
            if "science:" in typeOfTrivia:
                typeOfTrivia = typeOfTrivia[9:]
            
            question = html.unescape(trivia['results'][0]['question'])
            correctAnswer = html.unescape(trivia['results'][0]['correct_answer'])
            wrongAnswer1 = html.unescape(trivia['results'][0]['incorrect_answers'][0])
            wrongAnswer2 = html.unescape(trivia['results'][0]['incorrect_answers'][1])
            wrongAnswer3 = html.unescape(trivia['results'][0]['incorrect_answers'][2])

            # Assigns the correct and incorrect answers to random options, so there's 
            # No pattern for winning.
            Answers = [correctAnswer, wrongAnswer1, wrongAnswer2, wrongAnswer3]
            randomChoices = random.sample(Answers, len(Answers))
            randomChoices_dict = {
                "A": randomChoices[0],
                "B": randomChoices[1],
                "C": randomChoices[2],
                "D": randomChoices[3]
            }

            dispatcher.utter_message(text="""Here's some {} trivia for you: {}
A. {}
B. {}
C. {}
D. {}
        
Is the answer A, B, C, or D?""".format(typeOfTrivia, question, randomChoices[0], randomChoices[1], randomChoices[2], randomChoices[3]))
            return []

class ActionCheckTrivia(Action):
    """Determines whether user's trivia answer was correct"""
    def name(self) -> Text:
        return "action_check_trivia"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        validTriviaResponses = ["A", "B", "C", "D", "a", "b", "c", "d"]
        # Determines whether the input is valid (i.e., not ""). DELETE THE FOLLOWING 3 LINES OF CODE WHEN YOU PUT THIS FEATURE IN GUI (no entering "")
        if tracker.get_slot("user_trivia_response") == None:
            dispatcher.utter_message(text="Looks like you didn't enter anything. The correct answer is {}".format(correctAnswer))
            return []

        # Checks whether data was a valid letter to answer
        elif tracker.get_slot("user_trivia_response") not in validTriviaResponses:
            dispatcher.utter_message(text="What's that?? Enter 'A', 'B', 'C', or 'D' as one of your answers next time!".format(correctAnswer))
            return []

        # Detects answer from user_trivia_response slot and uses dictionary to compare answers
        elif randomChoices_dict[tracker.get_slot("user_trivia_response").upper()] == correctAnswer:
            dispatcher.utter_message(text="Correct! You're so smart")
            return []
        else:
            dispatcher.utter_message(text="Unlucky that's wrong... The correct answer is {}".format(correctAnswer))
            return []

class ActionMusicMetadata(Action):
    """Simply returns artist album data"""
    def name(self) -> Text:
        return "action_music_metadata"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # My spotify credentials for this project
        CLIENT_ID = '3f4f8323f25d456c843cd66d1bf7b691'
        CLIENT_SECRET = '232ec99a73b1453aa66487bec3bad0a5'

        AUTH_URL = 'https://accounts.spotify.com/api/token'

        # Post the details to get an access token so we can use various endpoints later on
        auth_response = requests.post(AUTH_URL, {
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        })

        # convert the response to JSON
        auth_response_data = auth_response.json()

        # save the access token - this is what is used for get requests
        access_token = auth_response_data['access_token']

        headers = {
            # American spelling...
            "Authorization": "Bearer {}".format(access_token)
        }
        params = {
            "include_groups": "album",
            "limit": 50
        }

        # base URL of all Spotify API endpoints
        BASE_URL = 'https://api.spotify.com/v1/'
        # Track ID from the URI. user just needs to copy and paste the "copy artist link" and 
        # program does the rest
        # artist ID from the URI - end bit of copy and pasting track ID from spotify. put in instructions to change...
        artist_id = next(tracker.get_latest_entity_values("artist"), None)
        start_URI = 32
        end_URI = 54
        artist_id = artist_id[start_URI:end_URI]

        # format to request album data of artist - only albums no single songs, max 50 albums
        artist_data = requests.get("{}artists/{}".format(BASE_URL, artist_id), headers=headers).json()

        album_data = requests.get("{}artists/{}/albums".format(BASE_URL, artist_id), headers=headers, params=params).json()
        # print(album_data)

        name = artist_data['name']
        genre = artist_data['genres'][0]
        if name.lower() in ["pink floyd", "nirvana", "oasis", "arctic monkeys", "the beatles", "twenty one pilots", "bob dylan", "the rolling stones", "genesis", "cream", "eric clapton"]:
            dispatcher.utter_message(text="{} is known for its {} music. This is one of my personal favourites! Here are some albums you may want to check out:".format(name, genre))
        else:
            dispatcher.utter_message(text="{} is known for its {} music! Here are some of their snazzy albums:".format(name, genre))
            
        # format to request album data of artist - only albums no single songs, max 50 albums
        # r = requests.get(BASE_URL + 'artists/' + artist_id + '/albums', headers=headers, params=params)
        # d = r.json()

        # Prevents duplicate albums from appearing
        albums = [] # to keep track of duplicates

        # loop over albums and get all tracks
        output = ""
        for album in album_data['items']:
            album_name = album['name']

            # This skips over albums already covered
            trim_name = album_name.split('(')[0].strip()
            if trim_name.upper() in albums or int(album['release_date'][:4]) > 1983:
                continue
            albums.append(trim_name.upper()) # use upper() to standardize
            
            output += "\n{}".format(album_name)
        dispatcher.utter_message(text=output)
        return []

class ActionSearchSong(Action):
    """searches for song in browser"""
    def name(self) -> Text:
        return "action_search_song"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Private information - use environment variables
        clientID = '3f4f8323f25d456c843cd66d1bf7b691'
        clientSecret = '232ec99a73b1453aa66487bec3bad0a5'
        redirectURI = 'http://google.com/'

        # Create OAuth Object
        oauth_object = spotipy.SpotifyOAuth(clientID,clientSecret,redirectURI)

        # Create token
        token_dict = oauth_object.get_access_token()
        token = token_dict['access_token']

        # Create Spotify Object
        spotifyObject = spotipy.Spotify(auth=token)

        user = spotifyObject.current_user()
        # To print the response in readable format.
        display_name = user["display_name"]
        username = user["id"]
        dispatcher.utter_message(text="You are successfully signed in.")

        # # Get the Song Name from data
        # song_name = tracker.get_latest_entity_values("song")
        message_new = tracker.latest_message.get("text")
        # Keyword "play " will be removed
        searchQuery = message_new[5:]

        # searchQuery = next(song_name, None)
        if searchQuery != None:
            # Search for the Song.
            searchResults = spotifyObject.search(searchQuery,1,0,"track")
            # Get required data from JSON response.
            tracks_dict = searchResults['tracks']
            tracks_items = tracks_dict['items']
            song = tracks_items[0]['external_urls']['spotify']
            # print(json.dumps(tracks_dict, sort_keys=True, indent=4))
            track_name = tracks_dict["items"][0]["name"]
            artist_name = tracks_dict["items"][0]["artists"][0]["name"]

            # Open the Song in Web Browser
            webbrowser.open(song)
            # Returns the song name and artist - taking into account the grammar rule for words ending in "s" and its plural
            if artist_name[-1] == "s":
                dispatcher.utter_message(text="How's {}' {}? Are you vibin' to it?".format(artist_name, track_name))
            elif artist_name[-1] != "s":
                dispatcher.utter_message(text="How's {}'s {}? Are you vibin' to it?".format(artist_name, track_name))
            return []
        else:
            dispatcher.utter_message(text="Sorry! I don't recognise that song...")
            return[]