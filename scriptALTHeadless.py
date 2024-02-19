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
import requests
import subprocess

search_access = True
use_large_ocr_model = False
use_full_precision = False
use_low_vram = False
ocr_everything = False
auto_pdf_link_ocr = True


#"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct file paths using os.path.join
pdf_path = os.path.join(base_dir, "temp_webpage.pdf")
output_txt_path = os.path.join(base_dir, "website_text.txt")
output_txt_path_links = os.path.join(base_dir, "website_links.txt")
additional_links_output_path = os.path.join(base_dir, "additional_links_output.txt")


# Function to print page as PDF with specified margins
def print_to_pdf(driver, file, margin_top=1.25, margin_bottom=1.25, margin_left=1.25, margin_right=1.25):
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

def extract_text_and_links_from_pdf(pdf_path, output_txt_path, append=False):
    mode = 'a' if append else 'w'
    with open(output_txt_path, mode, encoding='utf-8') as file:
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc):
            file.write(f"Page {page_num + 1}\n\n")  # Page number
            file.write(page.get_text() + '\n')  # Text of the page
            file.write("\n")  # Add space between pages
            

            
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
    #chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    

    url = construct_url(query)
    driver.get(url)

    print_to_pdf(driver, pdf_path, margin_top=0.4, margin_bottom=0.4, margin_left=0.4, margin_right=0.4)

    driver.quit()

    extract_text_and_links_from_pdf(pdf_path, output_txt_path, append=False)
    

    # Extract clickable links from the PDF and write them to a text file
    extract_clickable_links_from_pdf(pdf_path, output_txt_path_links, append=False)

    with open(output_txt_path, 'r', encoding='utf-8') as file:
        content = file.read()

    return content


def extract_content_from_url_links(query):

    with open(output_txt_path_links, 'r', encoding='utf-8') as file:
        content = file.read()

    return content


# ...

def extract_content_from_url_ExpandedSearch(url, should_append):
    chrome_options = Options()
    #chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    driver.get(url)

    if url.endswith('.pdf'):
        # Download the PDF using requests
        response = requests.get(url)
        if response.status_code == 200:
            pdf_filename = os.path.join(base_dir, os.path.basename(url))
            with open(pdf_filename, 'wb') as file:
                file.write(response.content)

            if auto_pdf_link_ocr:
                # Perform OCR if auto_pdf_link_ocr is True
                nougat_cmd = ["nougat", pdf_filename, "-o", base_dir, "--no-markdown", "--recompute"]

                if use_large_ocr_model:
                    nougat_cmd.extend(["-m", "0.1.0-base"])

                if use_full_precision and use_low_vram:
                    nougat_cmd.extend(["--full-precision", "--batchsize", "1"])
                elif use_full_precision:
                    nougat_cmd.append("--full-precision")
                elif use_low_vram:
                    nougat_cmd.extend(["--batchsize", "1"])

                subprocess.run(nougat_cmd)

                # Construct the path to the .mmd file within the output directory
                mmd_filename = os.path.join(base_dir, os.path.basename(pdf_filename).replace('.pdf', '.mmd'))

                # Write the OCR output to website_text.txt
                try:
                    with open(mmd_filename, 'r') as mmd_file, open(output_txt_path, 'a' if should_append else 'w') as txt_file:
                        txt_file.write(mmd_file.read())
                except PermissionError as e:
                    print(f"PermissionError: {e}")
            else:
                # Just extract text and links if auto_pdf_link_ocr is False
                extract_text_and_links_from_pdf(pdf_filename, output_txt_path, append=should_append)
                extract_clickable_links_from_pdf(pdf_filename, output_txt_path_links, append=should_append)
        else:
            print(f"Failed to download PDF from {url}. Status code: {response.status_code}")
    else:
        # Process for non-PDF URLs
        print_to_pdf(driver, pdf_path, margin_top=1.25, margin_bottom=1.25, margin_left=1.25, margin_right=1.25)

        # Extract clickable links from the printed PDF
        extract_clickable_links_from_pdf(pdf_path, output_txt_path_links, append=should_append)

        if ocr_everything:
            # Perform OCR using nougat, specifying the output directory
            nougat_cmd = ["nougat", pdf_filename, "-o", base_dir, "--no-markdown", "--recompute"]

            if use_large_ocr_model:
                nougat_cmd.extend(["-m", "0.1.0-base"])

            if use_full_precision and use_low_vram:
                nougat_cmd.extend(["--full-precision", "--batchsize", "1"])
            elif use_full_precision:
                nougat_cmd.append("--full-precision")
            elif use_low_vram:
                nougat_cmd.extend(["--batchsize", "1"])

            subprocess.run(nougat_cmd)

            # Construct the path to the .mmd file within the output directory
            mmd_filename = os.path.join(base_dir, "temp_webpage.mmd")

            # Write the OCR output to website_text.txt
            try:
                with open(mmd_filename, 'r') as mmd_file, open(output_txt_path, 'a' if should_append else 'w') as txt_file:
                    txt_file.write(mmd_file.read())
            except PermissionError as e:
                print(f"PermissionError: {e}")
        else:
            # Original processing for non-OCR
            extract_text_and_links_from_pdf(pdf_path, output_txt_path, append=should_append)

    driver.quit()

    return "Content extracted from URL: " + url


    
def extract_urls_from_text(text):
    # Define pairs of start and end indicators
    indicator_pairs = [
        ('https://', '&gt;'),
        ('http://', '&gt;'),
        ('http://', ')'),
        ('https://', ')'),
        ('https://', ' '),
        ('https://', '>'),
        # Add more pairs as needed added yet another pair, the variosu AIs have a plethora of ways to terminate and html in text when responding :c
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

        
        if user_input.lower().startswith("search"):
            shared.processing_message = "*Searching online...*"
            # Split the input at the colon and use the part before the colon
            query = user_input.split("**")[0].replace("search", "").strip()
            state["context"] = "The answer to User question is provided to you in a generated content. Give a truthful and correct answer. Answer the question and do not apologize"
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
            state["context"] = "You are given a list of hyperlinks, choose up to 5 that you think will best answer the Users' question and do not apologize"
            search_data = extract_content_from_url_links(query)
            user_prompt = f"User request: {user_input}\n Extracted content: {search_data}"
            user_prompt = user_prompt[:fetch_length]
            print (user_prompt)
            return str(user_prompt)
        shared.processing_message = "*Typing...*"
        
        if user_input.lower().startswith("please expand"):
            shared.processing_message = "*Searching online...*"
            
            with open(additional_links_output_path, 'r', encoding='utf-8') as file:
                content = file.read()
                urls = extract_urls_from_text(content)

            should_append = len(urls) > 1
            
            # Process each URL and append the content
            for url in urls:
                extract_content_from_url_ExpandedSearch(url, should_append)

            # After processing all URLs, read the content from website_text.txt
            with open(output_txt_path, 'r', encoding='utf-8') as file:
                search_data = file.read()

            user_prompt = f"User request: {user_input}\n Extracted content, remove extra formatting when returning markdown text, return simple markdown when rendering text that is provided in markdown and do not apologize: {search_data}"
            user_prompt = user_prompt[:fetch_length]
            return str(user_prompt)

        shared.processing_message = "*Typing...*"
        
        
        if user_input.lower().startswith("go to "):
            shared.processing_message = "*Searching online...*"
            query = user_input.replace("go to ", "").strip() + " "  # Adding a space at the end
            urls = extract_urls_from_text(query)

            should_append = len(urls) > 1
            
            # Process each URL and append the content
            for url in urls:
                extract_content_from_url_ExpandedSearch(url, should_append)

            # After processing all URLs, read the content from website_text.txt
            with open(output_txt_path, 'r', encoding='utf-8') as file:
                search_data = file.read()

            user_prompt = f"User request: {user_input}\n Extracted content and do not apologize: {search_data}"
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

    
def ui():
    global search_access, fetch_length, use_large_ocr_model, use_full_precision, use_low_vram, ocr_everything, auto_pdf_link_ocr
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
          &nbsp;&nbsp;&nbsp;&nbsp;`go to`          
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
        - **Go To**: Use this command to go to a specific website(s).  
          &nbsp;&nbsp;&nbsp;&nbsp;Example: `go to https://forecast.weather.gov/MapClick.php?lat=38.579440000000034&lon=-121.49084999999997 and give me a 5 day forcast using only cute emojis in a table format` If doing multiple urls put spaces (not commas) between each url.         
        
        ### Enable Auto PDF
        - If you "go to" a web page the is a pdf or your AI picks a web page that is a pdf, this will automatically use OCR to scan the downloaded pdf.  
        Example `go to https://physics.uwo.ca/~mhoude2/courses/PDF%20files/physics1501/Ch5-Gravitation.pdf and pick out a cool equation to explain to me`

        ### OCR Model Selection
        - You can select between 2 OCR models, a small and large model.  The small model will use about ~13GB with the large model using about 2.5GB+ more.  You can run the OCR models in a CPU mode, but 5GB of vram will still be used.  The OCR model nouget does not have a means of forcing the model to use CPU mode, however if you replace the device.py file with the one from my repo you can make it happen https://github.com/RandomInternetPreson/LucidWebSearch/blob/main/README.md#insructions-for-getting-cpu-mode-low-vram-to-work   

        ### Full Precision Option
        - Only applicable if you are running in CPU mode, this can speed up inferencing, enable it if CPU mode is too slow for you.  

        ### OCR Everything
        - Enabling this will execute OCR on both web pages and .pdf web pages. Very useful if doing research where scientific and mathematical symbols are displayed on a web page.  
        Example `go to https://en.wikipedia.org/wiki/Quantum_mechanics and write out the equation for the time evolution of a quantum state described by the Schrödinger equation that you read in the page, and explain each variable. When you are writing out the equations, can you give me markdown outputs and make sure there is only a single dollar sign at the beginning and end of the equation so I can render it with markdown?`
        
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
    auto_pdf_link_ocr_radio = gr.Radio(choices=["Enable Auto PDF Link OCR", "Disable Auto PDF Link OCR"], value="Enable Auto PDF Link OCR", label="Auto PDF Link OCR Option, if disabled will not automatically use OCR to read urls that point to pdfs")
    ocr_model_radio = gr.Radio(choices=["Use Small OCR Model", "Use Large OCR Model"], value="Use Small OCR Model", label="OCR Model Selection, small is ~13GB with the large model using about 2.5GB+ more, CPU is ~5GB of VRAM (see device.py replacement in repo)")
    full_precision_radio = gr.Radio(choices=["Disable Full Precision", "Enable Full Precision"], value="Disable Full Precision", label="Full Precision Option (can speed up OCR if using CPU device.py file)")
    low_vram_radio = gr.Radio(choices=["Disable Low Vram", "Enable Low Vram"], value="Disable Low Vram", label="Low Vram is the best I can do right now in lieu of no direct CPU only support")
    ocr_everything_radio = gr.Radio(choices=["Disable OCR Everything", "Enable OCR Everything"], value="Disable OCR Everything", label="OCR Everything Option, will OCR web pages and pdfs, useful for web pages with lots of equations")
    checkbox = gr.Checkbox(value=search_access, label="Enable Google Search")
    textbox = gr.Textbox(value=str(fetch_length), label="Web Search Fetch Length (characters)")
    
    checkbox.change(fn=update_search_access, inputs=checkbox)
    textbox.change(fn=update_fetch_length, inputs=textbox)
    full_precision_radio.change(fn=update_full_precision, inputs=full_precision_radio)
    low_vram_radio.change(fn=update_low_vram, inputs=low_vram_radio)
    ocr_everything_radio.change(fn=update_ocr_everything, inputs=ocr_everything_radio)
    ocr_model_radio.change(fn=update_ocr_model, inputs=ocr_model_radio)
    auto_pdf_link_ocr_radio.change(fn=update_auto_pdf_link_ocr, inputs=auto_pdf_link_ocr_radio)
    return gr.Column([checkbox, textbox, ocr_model_radio, full_precision_radio, low_vram_radio, ocr_everything_radio, auto_pdf_link_ocr_radio]), search_access
    
def update_auto_pdf_link_ocr(radio_value):
    global auto_pdf_link_ocr
    auto_pdf_link_ocr = (radio_value == "Enable Auto PDF Link OCR")
    return auto_pdf_link_ocr

    
def update_ocr_everything(radio_value):
    global ocr_everything
    ocr_everything = (radio_value == "Enable OCR Everything")
    return ocr_everything
    
def update_full_precision(radio_value):
    global use_full_precision
    use_full_precision = (radio_value == "Enable Full Precision")
    return use_full_precision
    
def update_low_vram(radio_value):
    global use_low_vram
    use_low_vram = (radio_value == "Enable Low Vram")
    return use_low_vram
    
def update_ocr_model(radio_value):
    global use_large_ocr_model
    use_large_ocr_model = (radio_value == "Use Large OCR Model")
    return use_large_ocr_model 
    
def update_search_access(checkbox_value):
    global search_access
    search_access = checkbox_value  # assign the value of the checkbox to the variable
    return search_access, checkbox_value
    
def output_modifier(output):
    global additional_links_flag

    if additional_links_flag:
        # Write output to a text file when the flag is True
        with open(additional_links_output_path, 'w') as file:
            file.write(output)
        additional_links_flag = False  # Reset the flag after writing

    print(output)
    return output


def bot_prefix_modifier(prefix):
    return prefix
