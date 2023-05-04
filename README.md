# How to use ChattyBot *
1. Install the necessary requirements in a virtual environment - must be run in Python Version 3.8.
2. If you are running the program for the first time, type "rasa train" into the terminal and wait until the Rasa model is saved to another file.
3. Run main.py in the terminal.
4. Interact with the GUI once the terminal outputs: "Rasa server is up and running."
5. Follow https://stackoverflow.com/questions/39632667/how-do-i-kill-the-process-currently-using-a-port-on-localhost-in-windows to kill port 5055 if there is an issue with re-running the programming.


* The program is complete but I'd still like to add some new features, including:
1. Animating the bot's response onto the terminal one letter at a time using Canvas in Tkinter
2. Adding sound each time a button is clicked
3. Adding multiple bot responses per intent, so it can be slightly more dynamic
4. Indicate that the bot is thinking before responding with an animation, by using threading so the window doesn't completely freeze for a few second.
5. Export the RASA bot onto social media sites like Discord and websites.
