import os
import whisper
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
from nltk.corpus import stopwords
from pytubefix import YouTube
from pytubefix.cli import on_progress
import ffmpeg


# Ensure that the necessary NLTK data is downloaded
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')

# Function to download YouTube video
def download_video(url):
    yt = YouTube(url, use_oauth=True, allow_oauth_cache=True, on_progress_callback=on_progress)
    ys = yt.streams.get_highest_resolution()
    video_file_path = ys.download()  # Downloads and returns the path of the video file
    return video_file_path

# Function to transcribe video using Whisper
def transcribe_video(file_path):
    model = whisper.load_model("base")  # Load Whisper model
    result = model.transcribe(file_path)  # Transcribe video
    return result["text"]

# Function to summarize transcription
def summarize_text(text):
    summarizer = pipeline("summarization")
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
    return summary

# Function to generate question and answers from summary
def generate_qa_pairs(text):
    sentences = sent_tokenize(text)
    qa_pairs = []

    for sentence in sentences:
        words = word_tokenize(sentence)
        tagged_words = pos_tag(words)

        # Find the main subject (noun) and verb in the sentence
        subject = None
        verb = None
        for word, pos in tagged_words:
            if pos in ['NN', 'NNS', 'NNP', 'NNPS'] and not subject:
                subject = word  # First noun as subject
            if pos.startswith('VB') and not verb:
                verb = word  # First verb as action

        # Formulate a more relevant question and answer
        if subject and verb:
            question = f"What does '{subject}' do in the context of the text?"
            answer = f"The text states that '{subject}' {verb}."
            qa_pairs.append({"question": question, "answer": answer})
        elif subject:
            question = f"What is '{subject}' in the context of the text?"
            answer = f"'{subject}' is described in the text."
            qa_pairs.append({"question": question, "answer": answer})

    return qa_pairs

# Function to recommend associative memory techniques
def recommend_associations(answer):
    # Simple associative recommendations based on common types of nouns
    associations = {
        "person": "Try associating this person with someone you know.",
        "place": "Think about a place you have visited that relates to this location.",
        "object": "Imagine using or interacting with this object in your daily life and associating it with a daily life object to remember it easy.",
        "concept": "Relate this concept to a similar idea or theory you already understand.",
        "event": "Connect this event with a personal experience or a historical event."
    }

    # Identify the type of the noun (simplified approach)
    word_tag = pos_tag([answer])[0][1]
    if word_tag.startswith('NNP'):
        recommendation = associations.get("person", "Associate this concept with something familiar in your life to remember it easier.")
    elif word_tag.startswith('NN'):
        recommendation = associations.get("object", "Associate this concept with something familiar in your life to remember it easier.")
    else:
        recommendation = associations.get("concept", "Associate this concept with something familiar in your life to remember it easier.")

    return recommendation

# Main function
def main():
    # Prompt user to enter the YouTube video URL
    url = input("Please enter the YouTube video URL: ")

    # Step 1: Download the video
    print("Downloading video...")
    video_path = download_video(url)

    # Step 2: Transcribe the video
    print("Transcribing video...")
    transcription = transcribe_video(video_path)

    # Step 3: Summarize the transcription
    print("Summarizing transcription...")
    summary = summarize_text(transcription)

    # Step 4: Generate question-answer pairs
    print("Generating questions and answers...")
    qa_pairs = generate_qa_pairs(summary)

    # Display the results
    print("\nSummary:")
    print(summary)

    print("\nQuestions and Answers with Recommendations:")
    for idx, qa in enumerate(qa_pairs):
        print(f"Q{idx+1}: {qa['question']}")
        print(f"A{idx+1}: {qa['answer']}")
        if idx == 0:
            print(f"Recommendation: {recommend_associations(qa['answer'])}")

    print("\nLearning Recommendation:")
    print("It's recommended to focus on 2-3 concepts per day, ensuring that you understand and retain each concept well.")
    print("Review these concepts regularly to reinforce the connections in your brain.")

# Example usage
if __name__ == "__main__":
    main()

