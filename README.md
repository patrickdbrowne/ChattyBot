# ChattyBot

## What is ChattyBot
I have a project on an Artificially Intelligent Chatbot based on a package called Rasa. This program uses Natural Language Understanding to interpret the user’s message and APIs to retrieve live data for responses. The user can type phrases into the GUI interface to get:

- the time in most cities;<br>
- the weather in most cities;<br>
- general information on any country;<br>
- a definition and example for most words;<br>
- the latest COVID data in most countries;<br>
- a joke;<br>
- a trivia question;<br>
- music metadata when the link to an artist is pasted; and<br>
- a song played on Spotify in the browser.<br></br>

The conversation displayed can be exported, or cleared, and the program can read out its responses to the user. There are 6 categories and 6 blacklist options the user can choose to be included in the Chatbot’s jokes in the “Settings” tab. The program may speak its responses to the user when the “voice” button is toggled on. Voice settings can also be altered in settings, including the rate, volume and gender of the text-to-speech module.

## How to use ChattyBot
1. Install the necessary requirements in a virtual environment - must be run in Python Version 3.8.
2. If you are running the program for the first time, type "rasa train" into the terminal and wait until the Rasa model is saved to another file.
3. Run main.py in the terminal.
4. Interact with the GUI once the terminal outputs: "Rasa server is up and running."
5. Follow https://stackoverflow.com/questions/39632667/how-do-i-kill-the-process-currently-using-a-port-on-localhost-in-windows to kill port 5055 if there is an issue with re-running the programming.

## Future improvements
The program is complete but I'd still like to add some new features, including:
1. Animating the bot's response onto the terminal one letter at a time using Canvas in Tkinter
2. Adding sound each time a button is clicked
3. Adding multiple bot responses per intent, so it can be slightly more dynamic
4. Indicate that the bot is thinking before responding with an animation, by using threading so the window doesn't completely freeze for a few seconds.
5. Export the RASA bot onto social media sites like Discord and websites.
