# Reddit Image Grabber
Download images from a subreddit. You can choose how many posts to scan, filter according to time and how to sort the subreddit.
##
## Important: 

**In order to use the script, you need to use your own credentials.**  
See this page for simple, quick instructions:

https://www.reddit.com/prefs/apps

When you have your information, edit the credentials.json file and put in your information.

Example:

    {"client_id": "YOUR_CLIENT_ID", "client_secret": "YOUR_CLIENT_SECRET", "password": "YOUR_ACCOUNT_PASSWORD", "username": "YOUR_ACCOUNT_USERNAME", "user_agent": "YOUR_USER_AGENT"}
    
## 
Images will be downloaded into folders with the subreddit's name, inside the folder where the script is running.
##

#### Dependencies:
1. praw `pip install praw`
2. requests `pip install requests`

##
The original code (found on Reddit) is included, it is a terminal version. I wrapped it in a GUI and added a few things. Thanks to the original author(s).