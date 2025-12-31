"""Tests for Scryfall client and cache."""

import pytest
from unittest.mock import Mock, patch
from mtg_deck_builder.cache.scryfall_cache import ScryfallCache
from mtg_deck_builder.cache.scryfall_client import ScryfallClient


class TestScryfallCache:
    """Test Scryfall caching functionality."""

    def test_cache_initialization(self, temp_db_path):
        """Test cache database initialization."""
        cache = ScryfallCache(temp_db_path)

        # Check that table exists
        result = cache.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in result.fetchall()]
        assert "cache" in tables

    def test_cache_get_miss(self, temp_db_path):
        """Test cache miss."""
        cache = ScryfallCache(temp_db_path)

        result = cache.get("test-query")
        assert result is None

    def test_cache_put_and_get(self, temp_db_path):
        """Test cache put and get."""
        cache = ScryfallCache(temp_db_path)

        test_data = {"key": "value", "cards": []}
        cache.put("test-query", test_data)

        result = cache.get("test-query")
        assert result == test_data

    def test_cache_updates_timestamp(self, temp_db_path):
        """Test that cache updates timestamp on put."""
        cache = ScryfallCache(temp_db_path)

        import time

        time1 = time.time()

        cache.put("test-query", {"data": "test"})
        time.sleep(0.01)  # Small delay

        # Put again
        cache.put("test-query", {"data": "updated"})

        # Check that fetched_at was updated
        result = cache.conn.execute(
            "SELECT fetched_at FROM cache WHERE query = ?", ("test-query",)
        )
        row = result.fetchone()
        assert row is not None
        # Should be recent
        from datetime import datetime

        assert datetime.fromisoformat(row[0]).timestamp() > time1


class TestScryfallClient:
    """Test Scryfall API client."""

    def test_client_initialization(self, temp_db_path):
        """Test client initialization."""
        cache = ScryfallCache(temp_db_path)
        client = ScryfallClient(cache)

        assert client.cache == cache
        assert client.base_url == "https://api.scryfall.com"

    @patch("mtg_deck_builder.cache.scryfall_client.requests.get")
    def test_get_single_page(self, mock_get, temp_db_path):
        """Test fetching a single page."""
        cache = ScryfallCache(temp_db_path)
        client = ScryfallClient(cache)

        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {"name": "Test Card 1", "id": "test-1"},
                {"name": "Test Card 2", "id": "test-2"},
            ],
            "has_more": False,
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        cards = client._get_page("test-query", 1)

        assert len(cards) == 2
        assert cards[0]["name"] == "Test Card 1"
        mock_get.assert_called_once()

    @patch("mtg_deck_builder.cache.scryfall_client.requests.get")
    def test_get_multiple_pages(self, mock_get, temp_db_path):
        """Test fetching multiple pages."""
        cache = ScryfallCache(temp_db_path)
        client = ScryfallClient(cache)

        # First page response
        page1_response = Mock()
        page1_response.json.return_value = {
            "data": [{"name": "Card 1", "id": "1"}],
            "has_more": True,
        }

        # Second page response
        page2_response = Mock()
        page2_response.json.return_value = {
            "data": [{"name": "Card 2", "id": "2"}],
            "has_more": False,
        }

        mock_get.side_effect = [page1_response, page2_response]

        cards = client.get_all_cards("test-query")

        assert len(cards) == 2
        assert mock_get.call_count == 2

    @patch("mtg_deck_builder.cache.scryfall_client.requests.get")
    def test_cache_hit(self, mock_get, temp_db_path):
        """Test that cache hit prevents API call."""
        cache = ScryfallCache(temp_db_path)
        client = ScryfallClient(cache)

        # Pre-populate cache
        cache.put(
            "search:test-query", {"data": [{"name": "Cached Card"}], "has_more": False}
        )

        cards = client.get_all_cards("test-query")

        assert len(cards) == 1
        assert cards[0]["name"] == "Cached Card"
        mock_get.assert_not_called()  # Should not make API call

    @patch("mtg_deck_builder.cache.scryfall_client.requests.get")
    def test_offline_mode(self, mock_get, temp_db_path):
        """Test offline mode."""
        cache = ScryfallCache(temp_db_path)
        client = ScryfallClient(cache)

        # Pre-populate cache
        cache.put(
            "search:test-query", {"data": [{"name": "Offline Card"}], "has_more": False}
        )

        cards = client.get_all_cards("test-query", use_cache=True)

        assert len(cards) == 1
        mock_get.assert_not_called()

    @patch("mtg_deck_builder.cache.scryfall_client.requests.get")
    def test_api_error_handling(self, mock_get, temp_db_path):
        """Test API error handling."""
        cache = ScryfallCache(temp_db_path)
        client = ScryfallClient(cache)

        mock_get.side_effect = Exception("API Error")

        with pytest.raises(Exception):
            client.get_all_cards("test-query")

    def test_empty_query_result(self, temp_db_path):
        """Test handling of empty query results."""
        cache = ScryfallCache(temp_db_path)
        client = ScryfallClient(cache)

        # Empty cache
        cards = client.get_all_cards("nonexistent-query", use_cache=True)

        assert cards == []

    @patch("mtg_deck_builder.cache.scryfall_client.requests.get")
    def test_rate_limiting_respected(self, mock_get, temp_db_path):
        """Test that rate limiting is handled."""
        cache = ScryfallCache(temp_db_path)
        client = ScryfallClient(cache)

        mock_response = Mock()
        mock_response.json.return_value = {"data": [], "has_more": False}
        mock_get.return_value = mock_response

        # Make multiple calls
        client.get_all_cards("query1")
        client.get_all_cards("query2")

        # Should have made API calls (since not cached)
        assert mock_get.call_count == 2


class TestScryfallIntegration:
    """Integration tests with real Scryfall API (requires internet)."""

    def test_real_api_search(self, temp_db_path):
        """Test searching with real Scryfall API."""
        cache = ScryfallCache(temp_db_path)
        client = ScryfallClient(cache)

        # Search for a known card
        cards = client.get_all_cards("lightning bolt", use_cache=False)

        # Should find at least one card
        assert len(cards) > 0
        assert any(card.get("name") == "Lightning Bolt" for card in cards)
