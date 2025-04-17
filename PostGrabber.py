import praw
from ContentFilter import ContentFilter

class PostGrabber:
    def __init__(self):
        # PRAW Setup
        self.reddit = praw.Reddit(
            client_id="uoLVZTiIA8t1q1iHRLDeYg",
            client_secret="Zg5uoJA5llNeoLaE-esNiE3QpObdMQ",
            password="Dandschen!?529",
            user_agent="PostExtractor by /u/Distinct-Respect-274",
            username="Distinct-Respect-274",
        )

        # Instanziiere den ContentFilter
        self.filter = ContentFilter("badwords.json", min_severity=2)

        # Wunschsubreddits und weitere Parameter
        self.subreddits = [
            "AmItheAsshole", "TwoHotTakes", "TrueOffMyChest", "entitledparents",
            "tifu", "EntitledPeople", "Confession", "ProRevenge"
        ]
        self.min_upvotes = 500
        self.posts_per_subreddit = 3
        self.min_length = 600
        self.max_length = 1000
        self.thread_limit = 100
        self.time_window = "week"
        self.top_posts = []

    # Funktion zur Berechnung der Engagement-Rate
    def calculate_engagement_rate(self, post):
        try:
            return post.score / (post.num_comments + 1)  # Verhindert Division durch 0
        except ZeroDivisionError:
            return 0

    # Hauptfunktion zum Abrufen der besten Posts
    def grab_posts(self):
        for subreddit_name in self.subreddits:
            subreddit = self.reddit.subreddit(subreddit_name)
            count = 0

            for submission in subreddit.top(time_filter=self.time_window, limit=self.thread_limit):
                text = submission.selftext.strip()
                engagement_rate = self.calculate_engagement_rate(submission)

                # Bedingung für Post-Auswahl: Upvotes, Kommentare und Engagement-Rate
                if (
                        submission.score >= self.min_upvotes
                        and not submission.stickied
                        and text
                        and self.min_length <= len(text) <= self.max_length
                        and engagement_rate > 0.5  # Beispiel-Schwelle für Engagement-Rate
                ):
                    self.top_posts.append({
                        "subreddit": subreddit_name,
                        "title": self.filter.censor(submission.title.strip()),
                        "text": self.filter.censor(text),
                        "engagement_rate": engagement_rate,
                        "score": submission.score,
                        "num_comments": submission.num_comments
                    })
                    count += 1

                if count >= self.posts_per_subreddit:
                    break

        return self.top_posts
