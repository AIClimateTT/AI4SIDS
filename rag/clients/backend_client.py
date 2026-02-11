"""
Backend API Client
==================
Thin HTTP client for the AI4SIDS Data Backend API.
Each specialist agent uses this to fetch only the data it needs.
"""
import time
import httpx
from typing import Optional, Dict, Any, List
from urllib.parse import quote


class BackendClient:
    """HTTP client wrapper for the AI4SIDS data backend API."""

    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._locations_cache: Optional[Dict[str, Any]] = None
        self._cache_ts: float = 0
        self._cache_ttl: float = 300  # 5 minutes

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Make a GET request and return the JSON response, or None on failure."""
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            print(f"[BackendClient] Error fetching {url}: {e}")
            return None

    # ------------------------------------------------------------------
    # Location endpoints
    # ------------------------------------------------------------------

    def get_locations(self) -> Optional[Dict[str, Any]]:
        """GET /api/locations — cached for 5 minutes."""
        now = time.time()
        if self._locations_cache and (now - self._cache_ts) < self._cache_ttl:
            return self._locations_cache
        data = self._get("/api/locations")
        if data:
            self._locations_cache = data
            self._cache_ts = now
        return data

    def get_location_names(self) -> List[str]:
        """Return a list of location name strings from the cached locations."""
        data = self.get_locations()
        if not data:
            return []
        locations = data.get("locations", [])
        return [loc["name"] for loc in locations if "name" in loc]

    # ------------------------------------------------------------------
    # Real-time / per-location endpoints
    # ------------------------------------------------------------------

    def get_real_time(self, location: str) -> Optional[Dict[str, Any]]:
        """GET /api/real-time/{location}"""
        return self._get(f"/api/real-time/{quote(location)}")

    # ------------------------------------------------------------------
    # System-wide endpoints
    # ------------------------------------------------------------------

    def get_system_update(self) -> Optional[Dict[str, Any]]:
        """GET /api/system-update — all locations overview + alerts."""
        return self._get("/api/system-update")

    # ------------------------------------------------------------------
    # River gauge endpoints
    # ------------------------------------------------------------------

    def get_river_timeline(self, location: str, minutes: int = 5) -> Optional[Dict[str, Any]]:
        """GET /api/timeline/{location}"""
        return self._get(f"/api/timeline/{quote(location)}", params={"minutes": minutes})

    def get_river_history(self, location: str, points: int = 20) -> Optional[Dict[str, Any]]:
        """GET /api/history/{location}"""
        return self._get(f"/api/history/{quote(location)}", params={"points": points})

    # ------------------------------------------------------------------
    # Analytics endpoints
    # ------------------------------------------------------------------

    def get_analytics(self, location: str, hours_back: int = 24) -> Optional[Dict[str, Any]]:
        """GET /api/analytics/by-name/{location}"""
        return self._get(f"/api/analytics/by-name/{quote(location)}", params={"hours_back": hours_back})

    # ------------------------------------------------------------------
    # Social media endpoints
    # ------------------------------------------------------------------

    def get_social_summary(self) -> Optional[Dict[str, Any]]:
        """GET /api/social/summary — aggregate sentiment across all locations."""
        return self._get("/api/social/summary")

    # ------------------------------------------------------------------
    # Risk endpoints
    # ------------------------------------------------------------------

    def get_risk_summary(self) -> Optional[Dict[str, Any]]:
        """GET /api/risk/summary — locations grouped by risk level."""
        return self._get("/api/risk/summary")

    # ------------------------------------------------------------------
    # Statistics / health
    # ------------------------------------------------------------------

    def get_data_stats(self) -> Optional[Dict[str, Any]]:
        """GET /api/data-statistics"""
        return self._get("/api/data-statistics")

    def is_healthy(self) -> bool:
        """Quick health check — can we reach the backend?"""
        try:
            data = self.get_locations()
            return data is not None
        except Exception:
            return False
