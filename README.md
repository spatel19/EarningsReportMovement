# EarningsReportMovement
A small web-app that displays the recent stock price movement of the three largest companies reporting earnings today after close

To run the app clone it into your local machine and type "export FLASK_APP=flaskfin.py" and "export FLASK_ENV=development"

Create a cred.py file and generate an API key at https://www.alphavantage.co/support/#api-key and set API_KEY = the key you generate, then set mongoConnectionString = your connection string

Then enter "flask run" in terminal

The app should now run a local instance at localhost:5000
