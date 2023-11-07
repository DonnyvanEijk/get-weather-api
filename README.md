# get-weather-api
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
6. and run the python script.
7. Open the server up on web http://127.0.0.1:5001


Now you have the script running the rest of the script explains itself