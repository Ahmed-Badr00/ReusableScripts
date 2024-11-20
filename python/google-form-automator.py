import random
import time
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Define probability distributions
probabilities = {
    "age_group": {
        "options": ["Under 18", "18–24", "25–34", "35–44", "45–54", "55 and above"],
        "weights": [0.00, 1.00, 0.00, 0.00, 0.00, 0.00]
    },
    "gender": {
        "options": ["Male", "Female"],
        "weights": [0.55, 0.45]
    },
    "occupation": {
        "options": ["Student", "Employed", "Self-employed", "Retired"],
        "weights": [0.70, 0.25, 0.04, 0.01]
    },
    "annual_income": {
        "options": ["Less than $10,000", "$10,000–$25,000", "$25,000–$50,000", "More than $50,000"],
        "weights": [0.70, 0.20, 0.08, 0.02]
    },
    # Add other distributions as needed
}

def create_driver():
    """Create and configure Chrome WebDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service('/usr/bin/chromedriver')  # Update with the correct path for your ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def choose_option(question_key):
    """Choose an option based on the probabilities for the given question."""
    if question_key not in probabilities:
        return None
    options = probabilities[question_key]["options"]
    weights = probabilities[question_key]["weights"]
    return np.random.choice(options, p=weights)

def fill_form(form_url, num_submissions=1, delay=2):
    """Fill the Google Form with random responses"""
    driver = create_driver()
    successful_submissions = 0
    
    try:
        print("\nInitializing browser...")
        driver.get(form_url)
        time.sleep(5)  # Increased initial wait time
        
        print(f"Current URL: {driver.current_url}")
        print("Page title:", driver.title)
        
        for i in range(num_submissions):
            try:
                print(f"\nAttempting submission {i + 1}/{num_submissions}")
                
                if i > 0:
                    driver.get(form_url)
                    time.sleep(3)
                
                selectors = [
                    ".freebirdFormviewerComponentsQuestionBaseRoot",
                    ".freebirdFormviewerViewNumberedItemContainer",
                    ".freebirdFormviewerViewItemsItemItem",
                    "div[role='listitem']",
                    ".freebirdFormviewerComponentsQuestionRadioRoot",
                    ".freebirdFormviewerComponentsQuestionCheckboxRoot"
                ]
                
                questions = []
                for selector in selectors:
                    questions = driver.find_elements(By.CSS_SELECTOR, selector)
                    if questions:
                        print(f"Found {len(questions)} questions using selector: {selector}")
                        break
                
                if not questions:
                    print("No questions found with any selector")
                    continue
                
                for q_idx, question in enumerate(questions, 1):
                    try:
                        print(f"\nProcessing question {q_idx}")
                        
                        question_key = None
                        if q_idx == 1:  # Map first question to age group
                            question_key = "age_group"
                        elif q_idx == 2:  # Map second question to gender
                            question_key = "gender"
                        elif q_idx == 3:  # Map third question to occupation
                            question_key = "occupation"
                        elif q_idx == 4:  # Map fourth question to annual income
                            question_key = "annual_income"
                        # Add mappings for other questions as needed
                        
                        selected_option = None
                        if question_key:
                            selected_option = choose_option(question_key)
                            print(f"Question {q_idx}: Selected '{selected_option}' based on probabilities.")
                        
                        # Try different selectors for radio buttons
                        radio_selectors = [
                            'div[role="radio"]',
                            'label.docssharedWizToggleLabeledContainer',
                            '.freebirdFormviewerComponentsQuestionRadioChoice'
                        ]
                        
                        options = []
                        for selector in radio_selectors:
                            options = question.find_elements(By.CSS_SELECTOR, selector)
                            if options:
                                print(f"Found {len(options)} radio options using selector: {selector}")
                                break
                        
                        if options and selected_option:
                            for option in options:
                                if selected_option in option.text:
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
                                    time.sleep(0.5)
                                    driver.execute_script("arguments[0].click();", option)
                                    print(f"Clicked option '{selected_option}'")
                                    break
                        
                        # Try different selectors for checkboxes (if applicable)
                        checkbox_selectors = [
                            'div[role="checkbox"]',
                            '.freebirdFormviewerComponentsQuestionCheckboxChoice',
                            'label.docssharedWizToggleLabeledContainer'
                        ]
                        
                        options = []
                        for selector in checkbox_selectors:
                            options = question.find_elements(By.CSS_SELECTOR, selector)
                            if options:
                                print(f"Found {len(options)} checkbox options using selector: {selector}")
                                break
                        
                        if options:
                            num_select = random.randint(1, min(3, len(options)))
                            for option in random.sample(options, num_select):
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
                                time.sleep(0.5)
                                driver.execute_script("arguments[0].click();", option)
                            print(f"Selected {num_select} checkbox options")
                            continue
                            
                        print("No options found for this question")
                            
                    except Exception as e:
                        print(f"Error processing question {q_idx}: {str(e)}")
                        continue
                
                # Submit the form
                print("\nLooking for submit button...")
                submit_selectors = [
                    "div[role='button']",
                    ".freebirdFormviewerViewNavigationSubmitButton",
                    "div.freebirdFormviewerViewNavigationButtons div[role='button']",
                    "div.freebirdFormviewerViewNavigationLeftButtons div[role='button']",
                    "button[type='submit']"
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.text.lower() in ['submit', 'send', 'next', 'إرسال', '']:
                            submit_button = button
                            print(f"Found submit button using selector: {selector}")
                            break
                    if submit_button:
                        break
                
                if submit_button:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", submit_button)
                    print("Clicked submit button")
                    
                    time.sleep(2)
                    if "formResponse" in driver.current_url or "viewform" not in driver.current_url:
                        print(f"✓ Response {i + 1} submitted successfully")
                        successful_submissions += 1
                    else:
                        print("× Form might not have been submitted successfully")
                else:
                    print("Could not find submit button")
                    # Debug information about visible buttons
                    all_buttons = driver.find_elements(By.CSS_SELECTOR, "div[role='button']")
                    print(f"Found {len(all_buttons)} total buttons on page")
                    for idx, btn in enumerate(all_buttons):
                        print(f"Button {idx + 1} text: '{btn.text}'")
                
                time.sleep(delay)
                
            except Exception as e:
                print(f"Error during submission {i + 1}: {str(e)}")
                continue
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        driver.quit()
        print(f"\nCompleted {successful_submissions} successful submissions out of {num_submissions} attempts")

def main():
    form_url = input("Enter your Google Form URL: ")
    if "forms.gle" in form_url:
        print("Converting short URL to full URL...")
        driver = create_driver()
        try:
            driver.get(form_url)
            time.sleep(2)
            form_url = driver.current_url
            print(f"Full URL: {form_url}")
        finally:
            driver.quit()
    
    try:
        num_submissions = int(input("Enter number of responses to generate (default: 5): ") or 5)
        delay = float(input("Enter delay between submissions in seconds (default: 2): ") or 2)
    except ValueError:
        print("Invalid input. Using default values.")
        num_submissions = 5
        delay = 2
    
    print("\nStarting form automation...")
    print(f"URL: {form_url}")
    print(f"Number of submissions: {num_submissions}")
    print(f"Delay between submissions: {delay} seconds")
    
    fill_form(form_url, num_submissions, delay)

if __name__ == "__main__":
    main()
