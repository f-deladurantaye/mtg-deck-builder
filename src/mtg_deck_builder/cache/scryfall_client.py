"""Scryfall API client with caching."""

import requests
from typing import Any

from .scryfall_cache import ScryfallCache


class ScryfallClient:
    """Client for Scryfall API with read-through caching."""

    BASE_URL = "https://api.scryfall.com"

    def __init__(self, cache: ScryfallCache | None = None):
        """Initialize the client.

        Args:
            cache: Optional ScryfallCache instance. If None, creates default cache.
        """
        self.cache = cache or ScryfallCache()

    def search_cards(
        self, query: str, page: int = 1, use_cache: bool = True
    ) -> dict[str, Any]:
        """Search for cards using Scryfall API.

        Args:
            query: Scryfall search query
            page: Page number (default 1)
            use_cache: Whether to use cache (default True)

        Returns:
            Scryfall API response JSON
        """
        cache_key = f"search:{query}"

        # Try cache first
        if use_cache:
            cached = self.cache.get(cache_key, page)
            if cached:
                return cached

        # Fetch from API
        url = f"{self.BASE_URL}/cards/search"
        params = {"q": query, "page": page}
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Cache the response
        if use_cache:
            self.cache.set(cache_key, data, page)

        return data

    def get_all_cards(
        self, query: str = "is:commander", use_cache: bool = True
    ) -> list[dict[str, Any]]:
        """Get all cards matching a query (handles pagination).

        Args:
            query: Scryfall search query
            use_cache: Whether to use cache

        Returns:
            List of all card objects
        """
        all_cards = []
        page = 1
        has_more = True

        while has_more:
            response = self.search_cards(query, page=page, use_cache=use_cache)
            cards = response.get("data", [])
            all_cards.extend(cards)

            has_more = response.get("has_more", False)
            page += 1

        return all_cards
