import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer  # More language options
from nltk.corpus import stopwords
import pandas as pd

# Ensure necessary NLTK resources are downloaded
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Load your Spotify dataset (adjust file path and column names as needed)
data = pd.read_csv('spotify_songs.csv')

# Filter only English, Spanish, and German songs
data = data[data["language"].isin(["en", "es", "de"])]


# Function to process lyrics based on language

def get_language_name(lan):
    match lan:
        case "en":
            return "english"
        case "de":
            return "german"
        case "es":
            return "spanish"
        case _:
            print("didnt match language: ", lan)
            return "english"


def process_text(text, language):
    # Tokenize
    language = get_language_name(language)
    tokenized_words = word_tokenize(text, language)

    # Normalize (if applicable to the language)
    normalized_words = [word.lower() for word in tokenized_words]

    # Stemming (using appropriate stemmer for detected language)
    stemmer = SnowballStemmer(language)
    stemmed_words = [stemmer.stem(word) for word in normalized_words]

    # Remove stop words (if available for the language)
    stop_words = set(stopwords.words(language))  # Search set -> O(1)
    filtered_words = [word for word in stemmed_words if word not in stop_words]

    # Delete punctuation
    filtered_words = [word for word in filtered_words if word.isalnum()]

    return filtered_words
