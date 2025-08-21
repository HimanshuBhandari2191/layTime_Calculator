from __future__ import annotations

import os
import re
from typing import Dict, Any, List, Optional

from app.utils.text_extract import bytes_to_text


def extract_events(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """Extract events from SoF documents using OCR + pattern matching."""
    # Extract text from document
    text = bytes_to_text(file_bytes, filename)
    
    if not text:
        return {"filename": filename, "events": _demo_events(), "extraction_method": "fallback"}
    
    # Use enhanced regex extraction for event detection
    events = _enhanced_regex_extract(text)
    
    # Fallback to simple regex if enhanced doesn't find events
    if not events:
        events = _regex_extract(text)
    
    return {
        "filename": filename, 
        "events": events,
        "extraction_method": "enhanced_regex" if events else "simple_regex",
        "text_preview": text[:500] + "..." if len(text) > 500 else text
    }


def _enhanced_regex_extract(text: str) -> List[Dict[str, str]]:
    """Enhanced regex extraction with better maritime event patterns."""
    events = []
    
    # Maritime event patterns with context
    event_patterns = [
        r'(cargo\s+loading|loading\s+cargo).*?(\d{1,2}:\d{2}).*?(\d{1,2}:\d{2})',
        r'(berthing|anchoring).*?(\d{1,2}:\d{2}).*?(\d{1,2}:\d{2})',
        r'(pilot\s+onboard|pilot\s+embarked).*?(\d{1,2}:\d{2}).*?(\d{1,2}:\d{2})',
        r'(shifting|mooring).*?(\d{1,2}:\d{2}).*?(\d{1,2}:\d{2})',
        r'(discharge|unloading).*?(\d{1,2}:\d{2}).*?(\d{1,2}:\d{2})',
        r'(arrival|departure).*?(\d{1,2}:\d{2}).*?(\d{1,2}:\d{2})',
        r'(bunkering|crew\s+change).*?(\d{1,2}:\d{2}).*?(\d{1,2}:\d{2})',
    ]
    
    # Date patterns
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{2,4}',  # DD/MM/YYYY
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{1,2}-\d{1,2}-\d{2,4}',  # DD-MM-YYYY
    ]
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for event patterns
        for pattern in event_patterns:
            matches = re.findall(pattern, line, re.IGNORECASE)
            if matches:
                for match in matches:
                    if len(match) >= 3:
                        event = {
                            "name": match[0].title(),
                            "start": match[1],
                            "end": match[2],
                            "confidence": "high"
                        }
                        events.append(event)
        
        # Check for date + time patterns
        dates = []
        for date_pattern in date_patterns:
            date_matches = re.findall(date_pattern, line)
            dates.extend(date_matches)
        
        # If we found dates, look for time patterns
        if dates:
            time_pattern = r'\d{1,2}:\d{2}'
            times = re.findall(time_pattern, line)
            
            if len(times) >= 2:
                # Look for maritime keywords in the line
                maritime_keywords = [
                    "loading", "unloading", "berthing", "anchorage", "shifting",
                    "cargo", "discharge", "arrival", "departure", "pilot", "tug",
                    "mooring", "unmooring", "bunkering", "crew"
                ]
                
                if any(keyword in line.lower() for keyword in maritime_keywords):
                    event = {
                        "name": line[:100],  # First 100 chars as event name
                        "start": times[0],
                        "end": times[1],
                        "confidence": "medium"
                    }
                    events.append(event)
    
    return events


def _demo_events() -> List[Dict[str, str]]:
    """Demo events for testing when extraction fails."""
    return [
        {"name": "Vessel Arrived", "start": "2025-07-01T08:00:00Z", "end": "2025-07-01T08:15:00Z"},
        {"name": "Pilot Onboard", "start": "2025-07-01T08:30:00Z", "end": "2025-07-01T08:45:00Z"},
        {"name": "Berthing", "start": "2025-07-01T09:00:00Z", "end": "2025-07-01T09:30:00Z"},
    ]


KEYWORDS = [
    "loading", "berthing", "anchorage", "shifting", "unloading",
    "cargo", "discharge", "arrival", "departure", "pilot", "tug",
    "mooring", "unmooring", "bunkering", "crew change"
]

TIME_PATTERN = re.compile(
    # Matches various forms like 08:30, 8:30, 01/07/2025 08:30, 2025-07-01 08:30, etc.
    r"((\d{1,2}:\d{2})|((\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+\d{1,2}:\d{2})|(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}))",
    re.IGNORECASE,
)


def _regex_extract(text: str) -> List[Dict[str, str]]:
    """Fallback regex extraction for events and times."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    results: List[Dict[str, str]] = []
    
    for ln in lines:
        low = ln.lower()
        if any(k in low for k in KEYWORDS):
            matches = TIME_PATTERN.findall(ln)
            # Flatten matches and pick up to two time-like tokens
            times: List[str] = []
            for m in matches:
                candidate = m[0] if isinstance(m, tuple) else m
                if candidate:
                    times.append(candidate)
                if len(times) >= 2:
                    break
            
            results.append({
                "name": ln,
                "start": times[0] if len(times) >= 1 else "",
                "end": times[1] if len(times) >= 2 else "",
            })
    
    return results


