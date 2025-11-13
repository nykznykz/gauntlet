"""Adaptive downsampling utilities for portfolio history"""
from typing import List, Tuple
from app.models.portfolio_history import PortfolioHistory


def calculate_optimal_interval(record_count: int, target_points: int = 800) -> int:
    """
    Calculate the optimal time interval (in minutes) for downsampling.

    Args:
        record_count: Total number of history records
        target_points: Target number of data points after downsampling

    Returns:
        Interval in minutes (0=no downsampling, 5, 15, 30, 60, 120, 240, 1440)
    """
    if record_count <= 1000:
        return 0  # No downsampling needed

    # Calculate how much we need to reduce
    downsample_ratio = record_count / target_points

    # Map to standard intervals based on ratio
    if downsample_ratio <= 2:
        return 5      # 5-minute buckets
    elif downsample_ratio <= 4:
        return 15     # 15-minute buckets
    elif downsample_ratio <= 8:
        return 30     # 30-minute buckets
    elif downsample_ratio <= 16:
        return 60     # 1-hour buckets
    elif downsample_ratio <= 32:
        return 120    # 2-hour buckets
    elif downsample_ratio <= 64:
        return 240    # 4-hour buckets
    else:
        return 1440   # Daily buckets


def downsample_history(
    records: List[PortfolioHistory],
    interval_minutes: int
) -> List[PortfolioHistory]:
    """
    Downsample portfolio history to specified interval.
    Takes the last record in each time bucket (most recent state in that period).

    Args:
        records: List of portfolio history records (should be sorted by time)
        interval_minutes: Time bucket size in minutes (e.g., 60 for hourly)

    Returns:
        Downsampled list of records
    """
    if not records or interval_minutes == 0:
        return records

    # Group records by time buckets
    buckets = {}

    for record in records:
        # Get the timestamp
        recorded_time = record.recorded_at

        # Calculate minutes since Unix epoch, then round down to interval
        total_minutes = int(recorded_time.timestamp() / 60)
        bucket_minutes = (total_minutes // interval_minutes) * interval_minutes

        # Convert back to timestamp for bucket key
        bucket_timestamp = bucket_minutes * 60

        # Keep the latest record in each bucket
        if bucket_timestamp not in buckets:
            buckets[bucket_timestamp] = record
        else:
            if record.recorded_at > buckets[bucket_timestamp].recorded_at:
                buckets[bucket_timestamp] = record

    # Return sorted by time
    result = list(buckets.values())
    result.sort(key=lambda r: r.recorded_at)
    return result


def adaptive_downsample(
    records: List[PortfolioHistory],
    target_points: int = 800
) -> Tuple[List[PortfolioHistory], int]:
    """
    Adaptively downsample records based on volume.

    Returns raw data if record count is small (<= 1000 records).
    Otherwise, downsamples to approximately target_points using an optimal interval.

    Args:
        records: List of portfolio history records
        target_points: Target number of points after downsampling (default 800)

    Returns:
        Tuple of (downsampled_records, interval_used_in_minutes)
        interval_used_in_minutes will be 0 if no downsampling was applied
    """
    record_count = len(records)

    # Calculate optimal interval based on record count
    optimal_interval = calculate_optimal_interval(record_count, target_points)

    if optimal_interval == 0:
        # No downsampling needed - return all raw data
        return records, 0

    # Apply downsampling
    downsampled = downsample_history(records, optimal_interval)
    return downsampled, optimal_interval
