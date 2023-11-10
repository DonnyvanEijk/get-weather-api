# get-weather-api

## What does it do

This weather api is useful for fetching data from your current location and gathering weather data from that.
this can be used for as an example all kinds of weather applications.
Also, it is important to know when you are using the actually API_URL  of accuweather u will only have 50 requests daily.



## How it works

We are using 2 API's on webserver to gather weather data from your location this API keys 
will be needed to be placed by you bt yourself


## Why a weather api?

This is useful in all kinds of ways. From going to weather apps to websites with build in weather displayu
There are enough things possible with this API


## API routes used

The api routes we have used are from the accuweather service. and the ipinfo service route to your host on port 5000 where you will be able to see this data
also in the dotenv you may find 2 API_URL's u can comment the on out which you don't want to use. Also its important to know that the api url that is connected to accuweather actually grabs it from the API
but the other url takes it  from a https server which doesnt take api requests.


## Installation Guide

To install you need docker on your pc

Docker download :https://www.docker.com/products/docker-desktop/

Python 3.12 is needed
if you meet all the requirements the procedure is the following

1. Download the code
2. open the code in your code editor (Visual studio code, Pycharm ect.)
3. use requirements.txt to install all packages using: pip install -r requirements. txt in the terminal
4. do the following command in your code editor terminal: docker compose up -d
5. copy the .env.example contents and put it a new file .env insert the api keys or swap the api_url out for the fake mocking data (do this by adding a # in front of one of the url thats active and erase the other so the other api_url gets used )
6. go to this site and log in to https://developer.accuweather.com/ make a new application after logging in and use that as the weather_api_key, after that go to https://ipinfo.io/account/token and login to ipinfo then go to the token section and insert the ip_info_token value with the gathered token
7. and run the python script.
8. Open the server up on web http://127.0.0.1:5001

Now you have the script running the rest of the script explains itself

