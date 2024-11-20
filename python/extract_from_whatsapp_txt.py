import re
import pandas as pd
import datetime
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Load the chat data
file_path = 'WhatsApp Chat with Madalina.txt'  # Adjust path if needed

# Create the output directory
output_dir = 'analysis_results'
os.makedirs(output_dir, exist_ok=True)

# Function to extract phrases
def extract_phrase_counts(file_path, phrases):
    phrase_counts = {phrase: {'Ahmed': 0, 'Madalina': 0} for phrase in phrases}
    total_messages = {'Ahmed': 0, 'Madalina': 0}

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if re.match(r'.* - Ahmed Badr:', line):
                total_messages['Ahmed'] += 1
                for phrase in phrases:
                    if phrase.lower() in line.lower():
                        phrase_counts[phrase]['Ahmed'] += 1
            elif re.match(r'.* - Madalina:', line):
                total_messages['Madalina'] += 1
                for phrase in phrases:
                    if phrase.lower() in line.lower():
                        phrase_counts[phrase]['Madalina'] += 1

    return phrase_counts, total_messages

# Function to extract who starts the conversation
# Function to extract who starts the conversation after a long delay and sender change
def extract_conversation_initiation_with_delay(file_path, time_threshold_minutes=60):
    initiations = {'Ahmed': 0, 'Madalina': 0}
    previous_sender = None
    previous_message_time = None
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(r'(\d+/\d+/\d+, \d+:\d+\s?[AP]M) - (Ahmed Badr|Madalina):', line)
            if match:
                timestamp = match.group(1)
                sender = match.group(2)
                # Normalize the sender (convert 'Ahmed Badr' to 'Ahmed')
                sender = 'Ahmed' if sender == 'Ahmed Badr' else 'Madalina'
                current_message_time = datetime.strptime(timestamp, "%m/%d/%y, %I:%M %p")
                
                if previous_message_time is not None:
                    # Calculate time difference in minutes
                    time_difference = (current_message_time - previous_message_time).total_seconds() / 60
                    
                    # Check if the sender has changed AND time difference exceeds the threshold
                    if sender != previous_sender and time_difference >= time_threshold_minutes:
                        initiations[sender] += 1
                
                # Update the previous message details
                previous_message_time = current_message_time
                previous_sender = sender

    return initiations


# Function to calculate response times
def extract_response_time(file_path):
    response_times = {'Ahmed': [], 'Madalina': []}
    previous_message_time = None
    previous_sender = None

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(r'(\d+/\d+/\d+, \d+:\d+\s?[AP]M) - (Ahmed Badr|Madalina):', line)
            if match:
                timestamp = match.group(1)
                sender = match.group(2)
                sender = 'Ahmed' if sender == 'Ahmed Badr' else 'Madalina'
                
                # Parse the timestamp correctly
                current_message_time = datetime.strptime(timestamp, "%m/%d/%y, %I:%M %p")
                
                if previous_message_time and previous_sender != sender:
                    # Calculate the time difference in minutes
                    time_difference = (current_message_time - previous_message_time).total_seconds() / 60
                    
                    # Ensure that the time difference is positive before appending
                    if time_difference > 0:
                        response_times[previous_sender].append(time_difference)
                
                previous_message_time = current_message_time
                previous_sender = sender

    # Calculate the average response time for each person
    avg_response_time_ahmed = sum(response_times['Ahmed']) / len(response_times['Ahmed']) if response_times['Ahmed'] else 0
    avg_response_time_madalina = sum(response_times['Madalina']) / len(response_times['Madalina']) if response_times['Madalina'] else 0
    
    return avg_response_time_ahmed, avg_response_time_madalina



# Function to extract emoji counts
def extract_emoji_usage(file_path):
    emoji_pattern = re.compile('[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F700-\U0001F77F]')
    emoji_counter = {'Ahmed': Counter(), 'Madalina': Counter()}

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if re.match(r'.* - Ahmed Badr:', line):
                emojis = emoji_pattern.findall(line)
                emoji_counter['Ahmed'].update(emojis)
            elif re.match(r'.* - Madalina:', line):
                emojis = emoji_pattern.findall(line)
                emoji_counter['Madalina'].update(emojis)

    return emoji_counter

# Function to extract morning and night greetings
def extract_morning_night_greetings(file_path):
    greetings = {
        'good morning': {'Ahmed': 0, 'Madalina': 0},
        'good night': {'Ahmed': 0, 'Madalina': 0}
    }

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if re.match(r'.* - Ahmed Badr:', line):
                if 'good morning' in line.lower():
                    greetings['good morning']['Ahmed'] += 1
                if 'good night' in line.lower():
                    greetings['good night']['Ahmed'] += 1
            elif re.match(r'.* - Madalina:', line):
                if 'good morning' in line.lower():
                    greetings['good morning']['Madalina'] += 1
                if 'good night' in line.lower():
                    greetings['good night']['Madalina'] += 1

    return greetings

# Function to extract compliment counts
def extract_compliment_counts(file_path):
    compliments = {
        'pretty': {'Ahmed': 0, 'Madalina': 0},
        'beautiful': {'Ahmed': 0, 'Madalina': 0},
        'sweet': {'Ahmed': 0, 'Madalina': 0},
        'cute': {'Ahmed': 0, 'Madalina': 0}
    }

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if re.match(r'.* - Ahmed Badr:', line):
                for word in compliments:
                    if word in line.lower():
                        compliments[word]['Ahmed'] += 1
            elif re.match(r'.* - Madalina:', line):
                for word in compliments:
                    if word in line.lower():
                        compliments[word]['Madalina'] += 1

    return compliments

# Function to save metrics as CSV
def save_csv(data, filename):
    df = pd.DataFrame(data)
    csv_file = os.path.join(output_dir, filename)
    df.to_csv(csv_file, index=False)
    print(f"Saved CSV: {csv_file}")

# Main function to execute all analysis
def main():
    # Conversation initiations with time delay logic
    initiations = extract_conversation_initiation_with_delay(file_path, time_threshold_minutes=60)
    save_csv([{'Person': 'Ahmed', 'Initiations': initiations['Ahmed']},
              {'Person': 'Madalina', 'Initiations': initiations['Madalina']}],
             'conversation_initiations_with_delay.csv')

    # Response times
    avg_response_time_ahmed, avg_response_time_madalina = extract_response_time(file_path)
    save_csv([{'Person': 'Ahmed', 'Avg Response Time (min)': avg_response_time_ahmed},
              {'Person': 'Madalina', 'Avg Response Time (min)': avg_response_time_madalina}],
             'response_times.csv')

    # Emoji usage
    emoji_counts = extract_emoji_usage(file_path)
    save_csv([{'Person': 'Ahmed', 'Total Emojis': sum(emoji_counts['Ahmed'].values())},
              {'Person': 'Madalina', 'Total Emojis': sum(emoji_counts['Madalina'].values())}],
             'emoji_usage.csv')

    # Morning and night greetings
    greetings = extract_morning_night_greetings(file_path)
    save_csv([{'Person': 'Ahmed', 'Good Morning': greetings['good morning']['Ahmed'], 'Good Night': greetings['good night']['Ahmed']},
              {'Person': 'Madalina', 'Good Morning': greetings['good morning']['Madalina'], 'Good Night': greetings['good night']['Madalina']}],
             'morning_night_greetings.csv')

    # Compliments
    compliments = extract_compliment_counts(file_path)
    save_csv([{'Person': 'Ahmed', 'Pretty': compliments['pretty']['Ahmed'], 'Beautiful': compliments['beautiful']['Ahmed'],
               'Sweet': compliments['sweet']['Ahmed'], 'Cute': compliments['cute']['Ahmed']},
              {'Person': 'Madalina', 'Pretty': compliments['pretty']['Madalina'], 'Beautiful': compliments['beautiful']['Madalina'],
               'Sweet': compliments['sweet']['Madalina'], 'Cute': compliments['cute']['Madalina']}],
             'compliments.csv')

# Run the main function
if __name__ == "__main__":
    main()

