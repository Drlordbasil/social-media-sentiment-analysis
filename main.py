import requests
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import json
import re
import os

nltk.download('vader_lexicon')


class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze_sentiment(self, text):
        sentiment = self.analyzer.polarity_scores(text)

        if sentiment['compound'] >= 0.05:
            return 'Positive'
        elif sentiment['compound'] <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'


class SocialMediaScraper:
    def __init__(self, analyzer):
        self.analyzer = analyzer

    def scrape_social_media(self, platform, keyword, num_posts):
        url = self.get_social_media_url(platform, keyword)
        response = requests.get(url)

        if response.status_code == 200:
            content = response.content
            soup = BeautifulSoup(content, 'html.parser')

            posts = soup.find_all('div', class_='post')
            scraped_posts = []

            for post in posts[:num_posts]:
                text = post.find('div', class_='post-text').text.strip()
                sentiment = self.analyzer.analyze_sentiment(text)
                scraped_posts.append({'text': text, 'sentiment': sentiment})

            return scraped_posts
        else:
            raise Exception('Failed to retrieve social media content')

    def get_social_media_url(self, platform, keyword):
        platform = platform.lower()

        if platform == 'twitter':
            return f'https://twitter.com/search?q={keyword}&src=typed_query'
        elif platform == 'facebook':
            return f'https://www.facebook.com/search/posts/?q={keyword}'
        elif platform == 'instagram':
            return f'https://www.instagram.com/explore/tags/{keyword}/'
        elif platform == 'linkedin':
            return f'https://www.linkedin.com/search/results/content/?keywords={keyword}&origin=GLOBAL_SEARCH_HEADER'
        else:
            raise Exception('Invalid social media platform')


class SentimentVisualizer:
    def visualize_sentiment_summary(self, sentiment_data):
        df = pd.DataFrame(sentiment_data)
        plt.figure(figsize=(10, 6))
        sns.countplot(x='sentiment', data=df, order=[
                      'Positive', 'Neutral', 'Negative'])
        plt.title('Sentiment Analysis Summary')
        plt.xlabel('Sentiment')
        plt.ylabel('Count')
        plt.show()


class EmailNotifier:
    def send_email_notification(self, email, subject, body):
        msg = MIMEMultipart()
        msg['From'] = 'your_email@example.com'
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('your_email@example.com', 'your_password')
        server.send_message(msg)
        server.quit()


class SentimentAnalysisResultsSaver:
    def save_sentiment_analysis_results(self, results, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_path = os.path.join(
            output_dir, f'sentiment_analysis_{current_datetime}.json')

        with open(file_path, 'w') as file:
            json.dump(results, file)


class SentimentAnalysisTool:
    def __init__(self):
        self.analyzer = SentimentAnalyzer()
        self.scraper = SocialMediaScraper(self.analyzer)
        self.visualizer = SentimentVisualizer()
        self.results_saver = SentimentAnalysisResultsSaver()
        self.email_notifier = EmailNotifier()

    def run(self):
        platform = input(
            'Enter the social media platform (Twitter, Facebook, Instagram, LinkedIn): ')
        keyword = input('Enter the keyword to search: ')
        num_posts = int(input('Enter the number of posts to analyze: '))
        output_dir = input('Enter the output directory to save the results: ')
        email_notification = input(
            'Enable email notification? (yes/no): ').lower()

        try:
            scraped_posts = self.scraper.scrape_social_media(
                platform, keyword, num_posts)

            sentiment_data = []
            for post in scraped_posts:
                sentiment_score = self.analyzer.analyze_sentiment(post['text'])
                sentiment_data.append(
                    {'text': post['text'], 'sentiment': sentiment_score})

            self.visualizer.visualize_sentiment_summary(sentiment_data)

            self.results_saver.save_sentiment_analysis_results(
                sentiment_data, output_dir)

            if email_notification == 'yes':
                email = input('Enter your email address: ')
                subject = 'Sentiment Analysis Results'
                body = f'The sentiment analysis for keyword "{keyword}" on {platform} has been completed.'
                self.email_notifier.send_email_notification(
                    email, subject, body)

            print('Sentiment analysis completed successfully.')

        except Exception as e:
            print(f'Error: {str(e)}')


if __name__ == '__main__':
    tool = SentimentAnalysisTool()
    tool.run()
