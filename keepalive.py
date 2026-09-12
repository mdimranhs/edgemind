#!/usr/bin/env python3
"""
Intelligent keepalive script for Render free tier cold start prevention.

Run this on your local machine, Raspberry Pi, or free cloud VM (Oracle Cloud free tier).

Features:
- Runs only during "active hours" (saves API calls)
- Exponential backoff on failures
- Timezone-aware scheduling
- Health monitoring
"""

import os
import time
from datetime import datetime, time as dt_time
import httpx
import asyncio
from typing import Optional
import pytz


class IntelligentKeepalive:
    def __init__(
        self,
        api_url: str,
        ping_interval: int = 840,  # 14 minutes in seconds
        active_hours: tuple = (8, 22),  # 8 AM to 10 PM
        timezone: str = "UTC",
    ):
        self.api_url = api_url.rstrip("/")
        self.ping_interval = ping_interval
        self.active_hours = active_hours
        self.timezone = pytz.timezone(timezone)
        self.consecutive_failures = 0
        self.total_pings = 0
        self.total_failures = 0

    def is_active_hours(self) -> bool:
        """Check if current time is within active hours."""
        now = datetime.now(self.timezone)
        current_time = now.time()
        start, end = self.active_hours

        start_time = dt_time(start, 0)
        end_time = dt_time(end, 0)

        return start_time <= current_time <= end_time

    async def ping(self) -> bool:
        """Send lightweight ping to keep API warm."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_url}/ping")
                return response.status_code == 200
        except Exception as e:
            print(f"❌ Ping failed: {e}")
            return False

    def calculate_backoff(self) -> int:
        """Calculate backoff time based on consecutive failures."""
        if self.consecutive_failures == 0:
            return self.ping_interval

        # Exponential backoff: 14min, 28min, 56min, max 2hr
        backoff = min(
            self.ping_interval * (2 ** self.consecutive_failures),
            7200  # Max 2 hours
        )
        return backoff

    async def run(self):
        """Main keepalive loop."""
        print(f"🚀 Keepalive started for {self.api_url}")
        print(f"⏰ Active hours: {self.active_hours[0]:02d}:00 - {self.active_hours[1]:02d}:00 {self.timezone}")
        print(f"🔄 Ping interval: {self.ping_interval}s ({self.ping_interval // 60}min)")
        print("-" * 60)

        while True:
            now = datetime.now(self.timezone)

            if self.is_active_hours():
                # Active hours - send keepalive
                success = await self.ping()
                self.total_pings += 1

                if success:
                    self.consecutive_failures = 0
                    print(f"✅ [{now.strftime('%H:%M:%S')}] Ping successful ({self.total_pings} total)")
                else:
                    self.consecutive_failures += 1
                    self.total_failures += 1
                    print(f"⚠️  [{now.strftime('%H:%M:%S')}] Ping failed ({self.consecutive_failures} consecutive)")

                # Calculate next ping time with backoff
                sleep_time = self.calculate_backoff()

            else:
                # Outside active hours - sleep until next active period
                sleep_time = self._time_until_active()
                print(f"😴 [{now.strftime('%H:%M:%S')}] Outside active hours, sleeping {sleep_time // 60}min")

            # Display stats every 10 pings
            if self.total_pings % 10 == 0 and self.total_pings > 0:
                uptime = (self.total_pings - self.total_failures) / self.total_pings * 100
                print(f"📊 Stats: {self.total_pings} pings, {self.total_failures} failures, {uptime:.1f}% uptime")

            await asyncio.sleep(sleep_time)

    def _time_until_active(self) -> int:
        """Calculate seconds until next active period."""
        now = datetime.now(self.timezone)
        current_time = now.time()
        start_hour = self.active_hours[0]

        # If before start time today
        if current_time < dt_time(start_hour, 0):
            next_active = now.replace(hour=start_hour, minute=0, second=0)
            return int((next_active - now).total_seconds())

        # Otherwise, sleep until start time tomorrow
        tomorrow = now.replace(hour=start_hour, minute=0, second=0) + \
                   timedelta(days=1)
        return int((tomorrow - now).total_seconds())


# ============================================
# Configuration
# ============================================

async def main():
    # Replace with your Render URL
    API_URL = os.getenv("API_URL", "https://edgemind-api.onrender.com")

    # Configuration
    keepalive = IntelligentKeepalive(
        api_url=API_URL,
        ping_interval=840,           # 14 minutes (< 15min Render sleep)
        active_hours=(8, 22),        # 8 AM - 10 PM (your timezone)
        timezone="America/New_York",  # Change to your timezone
    )

    try:
        await keepalive.run()
    except KeyboardInterrupt:
        print("\n👋 Keepalive stopped by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")


if __name__ == "__main__":
    # Check dependencies
    try:
        import httpx
        import pytz
    except ImportError:
        print("📦 Installing dependencies...")
        os.system("pip install httpx pytz")
        print("✅ Dependencies installed. Please run again.")
        exit(0)

    from datetime import timedelta
    asyncio.run(main())
