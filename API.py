# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# import torch

# app = FastAPI()

# class SingleInput(BaseModel):
#     comment: str

# # Load the BERT tokenizer and model
# tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
# model = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")


# @app.post("/analyze_sentiment/")
# def analyze_sentiment_endpoint(data: SingleInput):
#     comment = data.comment

#     if not comment:
#         raise HTTPException(status_code=400, detail="No comment provided")

#     tokenized_comment = tokenizer(comment, padding=True, truncation=True, return_tensors="pt")

#     # Perform sentiment analysis
#     with torch.no_grad():
#         outputs = model(**tokenized_comment)
#         logits = outputs.logits

#     # Determine sentiment
#     sentiment_id = torch.argmax(logits, dim=1).item()
#     print(sentiment_id)
#     # Convert sentiment_id to label
#     if sentiment_id > 3:
#         sentiment_label = "Positive"
#     elif sentiment_id < 3:
#         sentiment_label = "Negative"
#     else:
#         sentiment_label = "Neutral"

#     return {"sentiment": sentiment_label, "comment": comment, "status": "success", "message": "Sentiment analysis completed.", "sentiment_id": sentiment_id, "sentiment_label": sentiment_label}



# Now, trying using the youtube video id
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd
import googleapiclient.discovery

app = FastAPI()

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "AIzaSyC4Vx8G6nm3Ow9xq7NluTuCCJ1d_5w4YPE"  # Replace with your actual YouTube API key

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

class SingleInput(BaseModel):
    video_id: str

# Load the BERT tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")

def scrape_comments(video_id):
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100  # You can adjust the maximum number of comments to fetch
    )
    response = request.execute()

    comments = []

    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        comments.append(comment['textDisplay'])

    comments_df = pd.DataFrame(comments, columns=['comment'])
    return comments_df

@app.post("/analyze_sentiment/")
def analyze_sentiment_endpoint(data: SingleInput):
    video_id = data.video_id

    comments_df = scrape_comments(video_id)

    if comments_df.empty:
        raise HTTPException(status_code=400, detail="No comments found for the provided video ID")

    tokenized_comments = tokenizer(list(comments_df['comment']), padding=True, truncation=True, return_tensors="pt")

    # Perform sentiment analysis
    with torch.no_grad():
        outputs = model(**tokenized_comments)
        logits = outputs.logits

    # Determine sentiment for each comment
    sentiment_ids = torch.argmax(logits, dim=1).tolist()
    sentiment_labels = []
    for sentiment_id in sentiment_ids:
        if sentiment_id == 2:
            sentiment_labels.append("Positive")
        elif sentiment_id == 0:
            sentiment_labels.append("Negative")
        else:
            sentiment_labels.append("Neutral")

    sentiment_counts = {
        "positive": sentiment_labels.count("Positive"),
        "negative": sentiment_labels.count("Negative"),
        "neutral": sentiment_labels.count("Neutral")
    }

    return {"sentiment_counts": sentiment_counts, "comments_count": len(comments_df)}

# Example usage:
# Send a POST request to http://localhost:8000/analyze_sentiment/ with JSON body {"video_id": "YOUR_YOUTUBE_VIDEO_ID"}
# Replace YOUR_YOUTUBE_VIDEO_ID with the actual YouTube video ID you want to analyze
