# LucidWebSearch
A web search extension for Oobabooga's text-generation-webui


https://github.com/RandomInternetPreson/LucidWebSearch/assets/6488699/a136bac1-0e16-47cb-a005-80a8d06a11b4



https://github.com/RandomInternetPreson/LucidWebSearch/assets/6488699/907e0cd9-8535-4700-9984-773e6b8b3a0d




## Instructions for Use
**This only works with Google Chrome working in debugging mode**  
          &nbsp;&nbsp;&nbsp;&nbsp;Step 1: Close all instances of Chrome  
          &nbsp;&nbsp;&nbsp;&nbsp;Step 2: enter this into a seperate Windows command prompt (change the chrome.exe location if it is installed somewhere different than the example) --incognito can be             added at the end to open in that mode:
          
          "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 
          
**Enable Google Search**: Toggle this to activate or deactivate the web search feature.

**Web Search Fetch Length (characters)**: Specify the maximum length of content to fetch (in characters). This helps in limiting the response for large web pages.

**The workflow follows this sequence of trigger statments that must start the user input**  
          &nbsp;&nbsp;&nbsp;&nbsp;`search`  
          &nbsp;&nbsp;&nbsp;&nbsp;`additional links`  
          &nbsp;&nbsp;&nbsp;&nbsp;`please expand`  
          &nbsp;&nbsp;&nbsp;&nbsp;`go to`  
          
**Search**: Type 'search' followed by your query to search the web.  
          &nbsp;&nbsp;&nbsp;&nbsp;Example: `search recent submarine implosion`  
          &nbsp;&nbsp;&nbsp;&nbsp;Example: `search current time in Austin Texas ** do not reply with anything extra, simply the date and time please`  
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Everything after `**` will not be entered into the search but will be contextualized when the AI analyzes the web page.
          
**Additional Links**: Type 'additional links' to get more related links.  
          &nbsp;&nbsp;&nbsp;&nbsp;Example: `additional links provide me with one wikipedia link that has more information` links the AI collects can be seen in the website_links.txt file in the web_search extension folder.  
          &nbsp;&nbsp;&nbsp;&nbsp;Example: `additional links provide me with one link that has more information`          
          &nbsp;&nbsp;&nbsp;&nbsp;Be careful, the AI will visit each link it lists and gather data from each when you invoke the **please expand** input.  
          
**Please Expand**: Use this command to expand on the fetched content.  
          &nbsp;&nbsp;&nbsp;&nbsp;Example: `please expand search the page for more information and then generate a 5 paragraph report for me`

**Go To**: Use this command to go to a specific website.  
          &nbsp;&nbsp;&nbsp;&nbsp;Example: `go to https://forecast.weather.gov/MapClick.php?lat=38.579440000000034&lon=-121.49084999999997 and give me a 5 day forcast using only cute emojis in a table format` If doing multiple urls put spaces (not commas) between each url.  
          
## Recommendations
It is recommended that you run your textgen-webui interface in a browser other than Chrome.  In addition have both browsers open and in view so you can monitor the sites the AI is visiting.  
Use with Superbooga(v1 or v2) to help retain multiple search sessions if doing a lot of researching.
        
## Safety and Privacy
Please avoid searching for sensitive or personal information.  
Your Google Chrome browser will be used to executes searches, be mindful of the sites you give the AI access to under your various logged in websites.  Monitor the websites your AI is visiting through the chat and the open instance of Google Chrome.  

## Limitations
Some websites may not be accessible or properly formatted for data extraction.
The maximum character limit for website digestion is set by the user, if information you need is at the very end of a long web page try different sites or changing your search criteria.

## Troubleshooting
If you encounter issues, ensure you closed all previous Chrome instances before loading it in debugging mode.

## Feedback and Support
For feedback or support, please raise an issue on [[GitHub Repository](https://github.com/RandomInternetPreson/LucidWebSearch)https://github.com/RandomInternetPreson/LucidWebSearch].

## How it works
When you enter a phrase beginning with `search` the text after the word search will be entered into the Google Chrome browser as a google search.

The resulting web page is printed as temp_webpage.pdf

This printed web page is scanned and the text and links are separated out into website_links.txt and website_text.txt files

The website_text.txt is sent to the AI with your request and incorporated into its response

If the user is satisfied with the response no additional input is needed, however if the user wants to dive deeper into a subject they can ask the AI to retrieve a number of urls from the initial Google search.

When you enter a phrase beginning with `additional links` along with some context like the number of links, the AI is fed the website_links.txt file and then chooses which link to reply back with based off the user criteria.

The link(s) are parsed out of the AI's response and each link in the response is visited and digested when you enter a phrase beginning with `please expand` The AI will go to each site and contextualized the users requests when providing an output.

At any point the user can invoke the `go to` request, the user follows the request with a url and some context, then the LLM goes to the site(s) to review the contents and responds while trying to accomidate the user's request.

## Extras
I don't know much python and I started my project by editing code here: https://github.com/simbake/web_search specifically code for the input_modifier and ui checkbox.
