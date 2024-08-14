from textblob import TextBlob
from googleapiclient.discovery import build
import random
import json
import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QDateTimeEdit
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

# Set up YouTube API client
YOUTUBE_API_KEY = 'AIzaSyBqaqlwc7dUvPwTKM8jqdGAgbfCk_mIxsI'  # Replace with your API key
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# List of good wishes to be used after gratitude input
good_wishes = [
    "That`s great! May your day be filled with positivity and joy!",
    "Good for you! Wishing you a day full of success and happiness!",
    "Awesome! May your hard work bring fruitful results today!",
    "Great! Hope you find peace and fulfillment in everything you do today!",
    "Love it! Sending you good vibes for a fantastic day ahead!"
]

# Directory to store user profiles
USER_PROFILE_DIR = "user_profiles"

# Ensure the directory exists
os.makedirs(USER_PROFILE_DIR, exist_ok=True)

# Function to load user profile
def load_user_profile(user_name):
    profile_path = os.path.join(USER_PROFILE_DIR, f"{user_name}.json")
    if os.path.exists(profile_path):
        with open(profile_path, "r") as file:
            return json.load(file)
    else:
        # Create a new profile if one doesn't exist
        return {
            "name": user_name,
            "emotional_states": [],
            "preferred_videos": [],
            "gratitude_entries": []
        }

# Function to save user profile
def save_user_profile(user_profile):
    profile_path = os.path.join(USER_PROFILE_DIR, f"{user_profile['name']}.json")
    with open(profile_path, "w") as file:
        json.dump(user_profile, file, indent=4)

# Function to perform sentiment analysis on user input
def analyze_sentiment(user_input):
    blob = TextBlob(user_input)
    sentiment = blob.sentiment.polarity
    if sentiment > 0.1:
        return "happy"
    elif sentiment < -0.1:
        return "sad"
    else:
        return "neutral"

# Function to search for YouTube videos based on emotion
def get_youtube_video(emotion, user_profile):
    search_terms = {
        "happy": "motivational success stories",
        "sad": "uplifting and comforting videos",
        "neutral": "general motivational videos",
        "stressed": "stress relief and relaxation videos",
        "unmotivated": "high energy motivational speeches",
        "anxious": "calm and soothing videos"
    }

    existing_video_urls = [video['video_url'] for video in user_profile['preferred_videos']]

    request = youtube.search().list(
        part="snippet",
        maxResults=10,  # Retrieve more videos to increase options
        q=search_terms.get(emotion, "motivational videos"),
        type="video"
    )
    response = request.execute()

    # Filter out videos that have already been recommended to the user
    new_videos = [
        video for video in response['items']
        if f"https://www.youtube.com/watch?v={video['id']['videoId']}" not in existing_video_urls
    ]

    if new_videos:
        # Choose a random new video from the results
        video = random.choice(new_videos)
        video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
        return video['snippet']['title'], video_url
    else:
        # If all videos have been shown before, return a message
        return None, None

class ChatbotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set window properties
        self.setWindowTitle("Motivational Chatbot")
        self.setGeometry(100, 100, 500, 400)

        # Create layout
        layout = QVBoxLayout()

        # User Name Entry
        self.name_label = QLabel("Enter your name:")
        layout.addWidget(self.name_label)
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # Gratitude Entry
        self.gratitude_label = QLabel("What are you grateful for today?")
        layout.addWidget(self.gratitude_label)
        self.gratitude_input = QLineEdit()
        layout.addWidget(self.gratitude_input)

        # Emotion Entry
        self.emotion_label = QLabel("How are you feeling today?")
        layout.addWidget(self.emotion_label)
        self.emotion_input = QLineEdit()
        layout.addWidget(self.emotion_input)

        # Good Wish Label
        self.wish_label = QLabel("")
        layout.addWidget(self.wish_label)

        # Video Recommendation Label
        self.video_label = QLabel("")
        self.video_label.setWordWrap(True)
        layout.addWidget(self.video_label)

        # Watch Video Button
        self.watch_video_button = QPushButton("Watch Video")
        self.watch_video_button.setDisabled(True)
        self.watch_video_button.clicked.connect(self.watch_video)
        layout.addWidget(self.watch_video_button)

        # Submit Button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.motivational_chatbot)
        layout.addWidget(self.submit_button)

        # Reminder Setup
        self.reminder_label = QLabel("Set a daily reminder for check-ins:")
        layout.addWidget(self.reminder_label)

        self.reminder_time = QDateTimeEdit(QDateTime.currentDateTime())
        self.reminder_time.setDisplayFormat("HH:mm")
        layout.addWidget(self.reminder_time)

        self.reminder_button = QPushButton("Set Reminder")
        self.reminder_button.clicked.connect(self.set_reminder)
        layout.addWidget(self.reminder_button)

        # Set the layout
        self.setLayout(layout)

        # Daily check-in timer
        self.daily_timer = QTimer(self)
        self.daily_timer.timeout.connect(self.daily_check_in)
        self.daily_timer.start(24 * 60 * 60 * 1000)  # Check every 24 hours

    def motivational_chatbot(self):
        user_name = self.name_input.text().strip()

        if not user_name:
            QMessageBox.warning(self, "Input Error", "Please enter your name.")
            return

        # Load or create user profile
        user_profile = load_user_profile(user_name)

        gratitude_input = self.gratitude_input.text().strip()

        if not gratitude_input:
            QMessageBox.warning(self, "Input Error", "Please enter what you are grateful for today.")
            return

        # Store the gratitude entry
        user_profile["gratitude_entries"].append(gratitude_input)

        # Random good wish
        wish = random.choice(good_wishes)
        self.wish_label.setText(wish)

        user_input = self.emotion_input.text().strip()

        if not user_input:
            QMessageBox.warning(self, "Input Error", "Please enter how you are feeling today.")
            return

        # Analyze sentiment
        emotion = analyze_sentiment(user_input)

        # Store the emotional state
        user_profile["emotional_states"].append(emotion)

        # Get a relevant YouTube video based on the emotion, ensuring no duplicates
        video_title, video_url = get_youtube_video(emotion, user_profile)

        if video_title and video_url:
            # Store the preferred video if a new one was found
            user_profile["preferred_videos"].append({
                "emotion": emotion,
                "video_title": video_title,
                "video_url": video_url
            })

            self.video_label.setText(f"Based on how you're feeling, I think you might like this video: {video_title}")
            self.watch_video_button.setDisabled(False)
            self.watch_video_button.video_url = video_url
        else:
            self.video_label.setText("I've shown you all the videos I could find for your current emotion. Maybe try a different feeling?")
            self.watch_video_button.setDisabled(True)

        # Save user profile
        save_user_profile(user_profile)

    def watch_video(self):
        QDesktopServices.openUrl(QUrl(self.watch_video_button.video_url))

    def set_reminder(self):
        reminder_time = self.reminder_time.time().toString("HH:mm")
        QMessageBox.information(self, "Reminder Set", f"Reminder set for {reminder_time} every day.")
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.send_reminder)
        reminder_datetime = QDateTime.currentDateTime()
        reminder_datetime.setTime(self.reminder_time.time())
        time_to_reminder = max(0, reminder_datetime.toMSecsSinceEpoch() - QDateTime.currentDateTime().toMSecsSinceEpoch())
        self.reminder_timer.start(time_to_reminder)

    def send_reminder(self):
        QMessageBox.information(self, "Daily Reminder", "It's time for your daily check-in!")
        self.reminder_timer.start(24 * 60 * 60 * 1000)  # Reset for the next day

    def daily_check_in(self):
        QMessageBox.information(self, "Daily Check-In", "How are you feeling today? Don't forget to update your status!")
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChatbotGUI()
    ex.show()
    sys.exit(app.exec_())
