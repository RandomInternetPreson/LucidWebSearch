import gradio as gr
import modules.shared as shared
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
import base64
import fitz  # PyMuPDF
import os
import textwrap

search_access = False

#"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct file paths using os.path.join
pdf_path = os.path.join(base_dir, "temp_webpage.pdf")
output_txt_path = os.path.join(base_dir, "website_text.txt")
output_txt_path_links = os.path.join(base_dir, "website_links.txt")
additional_links_output_path = os.path.join(base_dir, "additional_links_output.txt")


# Function to print page as PDF with specified margins
def print_to_pdf(driver, file, margin_top=0, margin_bottom=0, margin_left=0, margin_right=0):
    print_options = {
        'landscape': False,
        'displayHeaderFooter': False,
        'printBackground': True,
        'preferCSSPageSize': True,
        'marginTop': margin_top,
        'marginBottom': margin_bottom,
        'marginLeft': margin_left,
        'marginRight': margin_right
    }
    result = driver.execute_cdp_cmd("Page.printToPDF", print_options)
    with open(file, 'wb') as f:
        f.write(base64.b64decode(result['data']))

# Function to extract text and links from a PDF and write to a file
# def extract_text_and_links_from_pdf(pdf_path, output_txt_path, append=False):
    # mode = 'a' if append else 'w'
    # with open(output_txt_path, mode, encoding='utf-8') as file:
        # doc = fitz.open(pdf_path)
        # for page_num, page in enumerate(doc):
            # file.write(f"Page {page_num + 1}\n\n")
            # file.write(page.get_text() + '\n')
            # links = page.get_links()
            # for link in links:
                # if 'uri' in link:
                    # file.write("Link: " + link['uri'] + '\n')
            # file.write("\n")

def extract_text_and_links_from_pdf(pdf_path, output_txt_path, append=False):
    mode = 'a' if append else 'w'
    with open(output_txt_path, mode, encoding='utf-8') as file:
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc):
            file.write(f"Page {page_num + 1}\n\n")  # Page number
            file.write(page.get_text() + '\n')  # Text of the page
            file.write("\n")  # Add space between pages
            
# # Function to extract clickable links from a PDF
# def extract_clickable_links_from_pdf(pdf_path, output_txt_path, append=False):
    # mode = 'a' if append else 'w'
    # with open(output_txt_path, mode, encoding='utf-8') as file, fitz.open(pdf_path) as doc:
        # for page_num, page in enumerate(doc):
            # file.write(f"Page {page_num + 1}\n\n")
            
            # # Iterate through all links on the page
            # links = page.get_links()
            # for link in links:
                # if 'uri' in link:
                    # file.write(f"Link: {link['uri']}\n")
            # file.write("\n")
            
# Function to extract clickable links from a PDF, excluding links containing 'google'
def extract_clickable_links_from_pdf(pdf_path, output_txt_path, append=False):
    mode = 'a' if append else 'w'
    with open(output_txt_path, mode, encoding='utf-8') as file, fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc):
            file.write(f"Page {page_num + 1}\n\n")
            
            # Iterate through all links on the page
            links = page.get_links()
            for link in links:
                if 'uri' in link and 'google' not in link['uri']:
                    file.write(f"Link: {link['uri']}\n")
            file.write("\n")

# def construct_url(query):
    # query = urllib.parse.quote_plus(query)
    # return f"https://en.wikipedia.org/wiki/{query}"
    
def construct_url(query):
    query = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?hl=en&q={query}"

def extract_content_from_url(query):
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    url = construct_url(query)
    driver.get(url)

    #pdf_path = r"L:\OobTesting\text-generation-webui-main\extensions\web_search\temp_webpage.pdf"
    print_to_pdf(driver, pdf_path, margin_top=0.4, margin_bottom=0.4, margin_left=0.4, margin_right=0.4)

    driver.quit()

    #output_txt_path = r"L:\OobTesting\text-generation-webui-main\extensions\web_search\website_text.txt"
    extract_text_and_links_from_pdf(pdf_path, output_txt_path, append=False)
    
    #pdf_path = r"L:\OobTesting\text-generation-webui-main\extensions\web_search\temp_webpage.pdf"  # Update with your actual PDF file path
    #output_txt_pathLinks = r"L:\OobTesting\text-generation-webui-main\extensions\web_search\website_links.txt"  # Update with your desired output file path
    output_txt_pathLinks = output_txt_path_links

    # Extract clickable links from the PDF and write them to a text file
    extract_clickable_links_from_pdf(pdf_path, output_txt_pathLinks, append=False)

    with open(output_txt_path, 'r', encoding='utf-8') as file:
        content = file.read()

    return content


def extract_content_from_url_links(query):

    
    #pdf_path = r"L:\OobTesting\text-generation-webui-main\extensions\web_search\temp_webpage.pdf"  # Update with your actual PDF file path
    #output_txt_pathLinks = r"L:\OobTesting\text-generation-webui-main\extensions\web_search\website_links.txt"  # Update with your desired output file path
    output_txt_pathLinks = output_txt_path_links
    # Extract clickable links from the PDF and write them to a text file
    #extract_clickable_links_from_pdf(pdf_path, output_txt_pathLinks, append=False)

    with open(output_txt_pathLinks, 'r', encoding='utf-8') as file:
        content = file.read()

    return content

# New function for expanded search
def extract_content_from_url_ExpandedSearch(url, should_append):
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get(url)

    #pdf_path = r"L:\OobTesting\text-generation-webui-main\extensions\web_search\temp_webpage.pdf"
    print_to_pdf(driver, pdf_path, margin_top=1.25, margin_bottom=1.25, margin_left=1.25, margin_right=1.25)

    driver.quit()

    extract_text_and_links_from_pdf(pdf_path, output_txt_path, append=should_append)
    extract_clickable_links_from_pdf(pdf_path, output_txt_path_links, append=should_append)


    return "Content extracted from URL: " + url


# def extract_urls_from_text(text):
    # urls = []
    # for line in text.split('\n'):
        # if line.startswith('http') or 'http' in line:
            # # Extract the URL from markdown link format [Link Text](URL)
            # start = line.find('(')
            # end = line.find(')', start + 1)
            # if start != -1 and end != -1:
                # url = line[start+1:end]
                # urls.append(url)
    # return urls
    
def extract_urls_from_text(text):
    # Define pairs of start and end indicators
    indicator_pairs = [
        ('https://', '&gt;'),
        ('http://', '&gt;'),
        ('http://', ')'),
        ('https://', ')'),
        # Add more pairs as needed
    ]

    urls = []
    for line in text.split('\n'):
        for start_indicator, end_indicator in indicator_pairs:
            start = line.find(start_indicator)
            while start != -1:
                end = line.find(end_indicator, start)
                if end != -1:
                    url = line[start:end]  # Extract URL without the end_indicator
                    urls.append(url)
                    start = line.find(start_indicator, end)  # Look for next URL
                else:
                    break
    print(urls)  # For debugging
    return urls


additional_links_flag = False  # Global variable to track the "additional links" condition
def input_modifier(user_input, state):
    global additional_links_flag, fetch_length  # Use the global variable
    if search_access:
        # if user_input.lower().startswith("search"):
            # shared.processing_message = "*Searching online...*"
            # query = user_input.replace("search", "").strip()
            # state["context"] = "The answer to User question is provided to you in a generated content. Give a truthful and correct answer. Answer the question"
            # search_data = extract_content_from_url(query)
            # user_prompt = f"User question: {user_input}\n Extracted content: {search_data}"
            # print (user_prompt)
            # return str(user_prompt)
        # shared.processing_message = "*Typing...*"
        
        if user_input.lower().startswith("search"):
            shared.processing_message = "*Searching online...*"
            # Split the input at the colon and use the part before the colon
            query = user_input.split("**")[0].replace("search", "").strip()
            state["context"] = "The answer to User question is provided to you in a generated content. Give a truthful and correct answer. Answer the question"
            search_data = extract_content_from_url(query)
            user_prompt = f"User question: {user_input}\n Extracted content: {search_data}"
            user_prompt = user_prompt[:fetch_length]
            print(user_prompt)
            return str(user_prompt)
        shared.processing_message = "*Typing...*"
        
        if user_input.lower().startswith("additional links"):
            additional_links_flag = True
            shared.processing_message = "*Searching online...*"
            query = user_input.replace("additional links", "").strip()
            state["context"] = "You are given a list of hyperlinks, choose up to 5 that you think will best answer the Users' question"
            search_data = extract_content_from_url_links(query)
            user_prompt = f"User request: {user_input}\n Extracted content: {search_data}"
            user_prompt = user_prompt[:fetch_length]
            print (user_prompt)
            return str(user_prompt)
        shared.processing_message = "*Typing...*"
        
        if user_input.lower().startswith("please expand"):
            shared.processing_message = "*Searching online...*"
            #additional_links_output_path = r"L:\OobTesting\text-generation-webui-main\extensions\web_search\additional_links_output.txt"
            
            with open(additional_links_output_path, 'r', encoding='utf-8') as file:
                content = file.read()
                urls = extract_urls_from_text(content)

            should_append = len(urls) > 1
            
            # Process each URL and append the content
            for url in urls:
                extract_content_from_url_ExpandedSearch(url, should_append)

            # After processing all URLs, read the content from website_text.txt
            #temp_links_path = r"L:\OobTesting\text-generation-webui-main\extensions\web_search\website_text.txt"
            #temp_links_path = output_txt_path
            with open(output_txt_path, 'r', encoding='utf-8') as file:
                search_data = file.read()

            user_prompt = f"User request: {user_input}\n Extracted content: {search_data}"
            user_prompt = user_prompt[:fetch_length]
            return str(user_prompt)

        shared.processing_message = "*Typing...*"
    return user_input
    
# Gradio UI code...
# You can include your Gradio interface setup here

# Global variable to store the fetch length
fetch_length = 6000  # Default value, you can adjust this

def update_fetch_length(new_length):
    global fetch_length
    try:
        fetch_length = int(new_length)  # Convert the input to an integer
    except ValueError:
        pass  # In case of invalid input, keep the old value
    return fetch_length


# def ui():
    # global search_access
    # checkbox = gr.Checkbox(value=search_access, label="Enable Google Search")
    # checkbox.change(fn=update_search_access, inputs=checkbox)
    # return checkbox, search_access
    
def ui():
    global search_access, fetch_length
    with gr.Accordion("Please Read To use LucidWebSearch Properly", open=False):
        gr.Markdown(textwrap.dedent("""
        ### Instructions for Use
        - **This only works with Google Chrome working in debugging mode**  
          &nbsp;&nbsp;&nbsp;&nbsp;Step 1: Close all instances of Chrome  
          &nbsp;&nbsp;&nbsp;&nbsp;Step 2: enter this into a seperate Windows command prompt (change the chrome.exe location if it is installed somewhere different than the example) --incognito can be added at the end to open in that mode: `"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222`   
        - **Enable Google Search**: Toggle this to activate or deactivate the web search feature.
        - **Web Search Fetch Length (characters)**: Specify the maximum length of content to fetch (in characters). This helps in limiting the response for large web pages.  
        - **The workflow follows this sequence of trigger statments that must start the user input**  
          &nbsp;&nbsp;&nbsp;&nbsp;`search`  
          &nbsp;&nbsp;&nbsp;&nbsp;`additional links`  
          &nbsp;&nbsp;&nbsp;&nbsp;`please expand`  
        - **Search**: Type 'search' followed by your query to search the web.  
          &nbsp;&nbsp;&nbsp;&nbsp;Example: `search recent submarine implosion`  
          &nbsp;&nbsp;&nbsp;&nbsp;Example: `search current time in Austin Texas ** do not reply with anything extra, simply the date and time please`  
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Everything after `**` will not be entered into the search but will be contextualized when the AI analyzes the web page.
        - **Additional Links**: Type 'additional links' to get more related links.  
          &nbsp;&nbsp;&nbsp;&nbsp;Example: `additional links provide me with one wikipedia link that has more information` links the AI collects can be seen in the website_links.txt file in the web_search extension folder.  
          &nbsp;&nbsp;&nbsp;&nbsp;Example: `additional links provide me with one link that has more information`          
          &nbsp;&nbsp;&nbsp;&nbsp;Be careful, the AI will visit each link it lists and gather data from each when you invoke the **please expand** input.  
        - **Please Expand**: Use this command to expand on the fetched content.  
          &nbsp;&nbsp;&nbsp;&nbsp;Example: `please expand search the page for more information and then generate a 5 paragraph report for me`  
          
        ### Recommendations
        - It is recommended that you run your textgen-webui interface in a browser other than Chrome.  In addition have both browsers open and in view so you can monitor the sites the AI is visiting.  
        - Use with Superbooga(v1 or v2) to help retain multiple search sessions if doing a lot of researching.
        ### Safety and Privacy
        - Please avoid searching for sensitive or personal information.  
        - Your Google Chrome browser will be used to executes searches, be mindful of the sites you give the AI access to under your various logged in websites.  Monitor the websites your AI is visiting through the chat and the open instance of Google Chrome.  

        ### Limitations
        - Some websites may not be accessible or properly formatted for data extraction.
        - The maximum character limit for website digestion is set by the user, if information you need is at the very end of a long web page try different sites or changing your search criteria.

        ### Troubleshooting
        - If you encounter issues, ensure you closed all previous Chrome instances before loading it in debugging mode.

        ### Feedback and Support
        - For feedback or support, please raise an issue on https://github.com/RandomInternetPreson/LucidWebSearch

        ### How it works
        - For feedback or support, please raise an issue on https://github.com/RandomInternetPreson/LucidWebSearch/tree/main#how-it-works
        """))
    checkbox = gr.Checkbox(value=search_access, label="Enable Google Search")
    textbox = gr.Textbox(value=str(fetch_length), label="Web Search Fetch Length (characters)")
    checkbox.change(fn=update_search_access, inputs=checkbox)
    textbox.change(fn=update_fetch_length, inputs=textbox)
    return gr.Column([checkbox, textbox]), search_access
    
    
def update_search_access(checkbox_value):
    global search_access
    search_access = checkbox_value  # assign the value of the checkbox to the variable
    return search_access, checkbox_value
    
def output_modifier(output):
    global additional_links_flag

    if additional_links_flag:
        # Write output to a text file when the flag is True
        #with open(r"L:\OobTesting\text-generation-webui-main\extensions\web_search\additional_links_output.txt", 'w') as file:
        with open(additional_links_output_path, 'w') as file:
            file.write(output)
        additional_links_flag = False  # Reset the flag after writing

    print(output)
    return output


def bot_prefix_modifier(prefix):
    return prefix
