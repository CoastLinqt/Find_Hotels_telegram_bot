#  Telegram bot Hotels.com Bot

For correct operation, it is necessary:

## Install dependencies using the command:

-pip install -r requirements.txt

-Create a .env file and add it there:BOT_TOKEN ,RAPID_API_KEY

### Launch the python bot main.py
Bot Features:

/start (Starting the bot)

/help (Output help for commands)

/lowprice (Output of the cheapest hotels in the city)

/custom (Output of the most expensive hotels in the city)

/history (Output of the hotel search history)


### The principle of operation:

When the bot starts, the city is requested. A request is made and, if successful, the user is offered a choice of possible cities, followed by a survey of details.

After asking the user about the details of his journey, the bot makes a request request to the API of the site Hotels.com Upon successful response, the program will process all your needs and display a list of possible hotel options.

The search history is maintained using the SQLite database.