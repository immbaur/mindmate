import os, requests, datetime, json

NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # optional; otherwise use free endpoints

def get_latest_news(topic: str, max_items: int = 3) -> list[dict]:
    """
    Mocked news fetcher – returns static fake results for testing.
    """
    if not topic:
        raise ValueError("topic required")

    from datetime import datetime, timedelta

    now = datetime.utcnow()
    return [
        {
            "title": f"Breaking {topic} News #{i+1}",
            "url": f"https://example.com/{topic.lower()}/{i+1}",
            "published_at": (now - timedelta(hours=i)).isoformat() + "Z",
        }
        for i in range(max_items)
    ]