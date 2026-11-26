#!/usr/bin/env python3
"""Record MYMS status to computer CSV using only the Python standard library."""
import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

FIELDS = ["schema", "computer_utc", "device_id", "device_utc_s", "uptime_s",
          "air_c", "wall_c", "sensors_fresh", "state", "target_c", "remaining_s",
          "heater_command", "fan_command", "fault", "simulation", "connection_error"]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    # Keep recording tied to the configured device instead of following redirects.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_status(url, timeout=5):
    request = urllib.request.Request(url.rstrip("/") + "/api/status")
    with urllib.request.build_opener(NoRedirect).open(request, timeout=timeout) as response:
        status = json.load(response)
    if not isinstance(status, dict) or "device_id" not in status or "recording" not in status:
        raise ValueError("Response is not MYMS status JSON")
    return status


def row_for(status=None, error=""):
    row = dict.fromkeys(FIELDS, "")
    row.update(schema=1, computer_utc=datetime.now(timezone.utc).isoformat(), connection_error=error)
    if status is not None:
        for key in ("device_id", "uptime_s", "air_c", "wall_c", "sensors_fresh", "state",
                    "target_c", "remaining_s", "fault", "simulation"):
            row[key] = status.get(key)
        row["device_utc_s"] = status.get("utc_s")
        row["heater_command"] = status.get("heater")
        row["fan_command"] = status.get("fan")
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Device base URL, e.g. http://192.168.4.1")
    parser.add_argument("--interval", type=float, default=5, help="Sampling interval in seconds (default 5)")
    parser.add_argument("--duration", type=float, default=3600, help="Recording duration in seconds (default 3600)")
    parser.add_argument("--output", type=Path, help="New CSV path; existing files are never overwritten")
    args = parser.parse_args()
    parsed = urllib.parse.urlsplit(args.url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ("", "/"):
        parser.error("Use a base HTTP(S) URL without embedded credentials, path, query or fragment")
    if not math.isfinite(args.interval) or args.interval < 1 or not math.isfinite(args.duration) or args.duration < args.interval:
        parser.error("Interval must be >=1 second and duration >= interval, with finite values")
    # Check the endpoint before creating a file. A later disconnect writes a gap row.
    try:
        first = fetch_status(args.url)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Cannot connect: {exc}\n")
    root = Path(__file__).resolve().parents[1]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    output = args.output or root / "measurements" / f"myms-{stamp}.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    deadline = started + args.duration
    next_sample = started
    rows = 0
    with output.open("x", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        print(f"Recording to {output}; Ctrl+C stops cleanly. Keep this computer awake and connected.")
        try:
            while time.monotonic() < deadline:
                time.sleep(max(0, next_sample - time.monotonic()))
                if time.monotonic() >= deadline:
                    break
                try:
                    status = first if rows == 0 else fetch_status(args.url, timeout=min(5, args.interval))
                    row = row_for(status)
                except urllib.error.HTTPError as exc:
                    row = row_for(error=f"HTTP {exc.code}")
                    if exc.code in (401, 403):
                        writer.writerow(row)
                        print("Device rejected the request; stopping.")
                        break
                except (OSError, ValueError) as exc:
                    row = row_for(error=str(exc))
                writer.writerow(row)
                file.flush()
                rows += 1
                next_sample += args.interval
                # Missed intervals stay as gaps; never burst requests to catch up.
                if next_sample < time.monotonic():
                    next_sample = time.monotonic() + args.interval
        except KeyboardInterrupt:
            print("\nStopped.")
    print(f"Saved {rows} samples to {output}")


if __name__ == "__main__":
    main()
