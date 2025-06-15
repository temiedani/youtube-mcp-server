from typing import Any

from mcp.server.fastmcp import FastMCP
from yt_helper import construct_video_url, search_youtube
from youtube_api import (
    get_video_details,
    get_channel_info,
    get_video_comments,
    get_trending_videos,
    get_related_videos,
    get_video_transcript,
)

# Initialize FastMCP server
mcp = FastMCP("videos")


def format_video(video: dict[str, Any]) -> str:
    """Format a video feature into a readable string."""
    return f"""
        Title: {video.get("title", "Unknown")}
        Channel: {video.get("channel_title", video.get("channel", "Unknown"))}
        Duration: {video.get("duration", "Unknown")}
        Description: {video.get("description", "No description available")}
        Views: {video.get("view_count", video.get("views", "Unknown"))}
        Likes: {video.get("like_count", "Unknown")}
        Comments: {video.get("comment_count", "Unknown")}
        URL: {construct_video_url(video.get("id", "dQw4w9WgXcQ"))}
        Published: {video.get("published_at", video.get("publish_time", "Unknown"))}
       """


def format_channel(channel: dict[str, Any]) -> str:
    """Format a channel feature into a readable string."""
    return f"""
        Channel Name: {channel.get("title", "Unknown")}
        Subscribers: {channel.get("subscriber_count", "Unknown")}
        Total Videos: {channel.get("video_count", "Unknown")}
        Total Views: {channel.get("view_count", "Unknown")}
        Description: {channel.get("description", "No description available")}
        Created: {channel.get("published_at", "Unknown")}
       """


def format_comment(comment: dict[str, Any]) -> str:
    """Format a comment into a readable string."""
    return f"""
        Author: {comment.get("author", "Unknown")}
        Text: {comment.get("text", "No text available")}
        Likes: {comment.get("like_count", "0")}
        Posted: {comment.get("published_at", "Unknown")}
       """


@mcp.tool()
async def get_videos(search: str, max_results: int) -> str:
    """Get videos for a search query.

    Args:
        search: Search query string
        max_results: Maximum number of results to return
    """
    results = search_youtube(search, max_results=max_results)
    if not results:
        return "No videos found."

    videos = [format_video(video) for video in results]
    return "\n---\n".join(videos)


@mcp.tool()
async def get_video_info(video_id: str) -> str:
    """Get detailed information about a video.

    Args:
        video_id: YouTube video ID
    """
    video = get_video_details(video_id)
    if not video:
        return "No video found."
    return format_video(video)


@mcp.tool()
async def get_channel_details(channel_id: str) -> str:
    """Get detailed information about a YouTube channel.

    Args:
        channel_id: YouTube channel ID
    """
    channel = get_channel_info(channel_id)
    if not channel:
        return "No channel found."
    return format_channel(channel)


@mcp.tool()
async def get_video_comments_tool(video_id: str, max_results: int = 100) -> str:
    """Get comments for a video.

    Args:
        video_id: YouTube video ID
        max_results: Maximum number of comments to return (default: 100)
    """
    comments = get_video_comments(video_id, max_results=max_results)
    if not comments:
        return "No comments found or comments are disabled."
    
    formatted_comments = [format_comment(comment) for comment in comments]
    return "\n---\n".join(formatted_comments)


@mcp.tool()
async def get_trending_videos_tool(region_code: str = "US", max_results: int = 50) -> str:
    """Get trending videos for a region.

    Args:
        region_code: Two-letter ISO country code (default: "US")
        max_results: Maximum number of videos to return (default: 50)
    """
    videos = get_trending_videos(region_code, max_results=max_results)
    if not videos:
        return "No trending videos found."
    
    formatted_videos = [format_video(video) for video in videos]
    return "\n---\n".join(formatted_videos)


@mcp.tool()
async def get_related_videos_tool(video_id: str, max_results: int = 25) -> str:
    """Get videos related to a specific video.

    Args:
        video_id: YouTube video ID
        max_results: Maximum number of videos to return (default: 25)
    """
    videos = get_related_videos(video_id, max_results=max_results)
    if not videos:
        return "No related videos found."
    
    formatted_videos = [format_video(video) for video in videos]
    return "\n---\n".join(formatted_videos)


@mcp.tool()
async def summarize_video(video_id: str, include_comments: bool = True) -> str:
    """Get a comprehensive summary of a YouTube video.
    
    Args:
        video_id: YouTube video ID
        include_comments: Whether to include top comments in the summary (default: True)
    """
    # Get video details
    video = get_video_details(video_id)
    if not video:
        return "No video found."
    
    # Get transcript
    transcript = get_video_transcript(video_id)
    
    # Get comments if requested
    comments = []
    if include_comments:
        comments = get_video_comments(video_id, max_results=5)
    
    # Build the summary
    summary = []
    
    # Add video metadata
    summary.append("=== Video Summary ===")
    summary.append(f"Title: {video['title']}")
    summary.append(f"Channel: {video['channel_title']}")
    summary.append(f"Duration: {video['duration']}")
    summary.append(f"Views: {video['view_count']}")
    summary.append(f"Likes: {video['like_count']}")
    summary.append(f"Published: {video['published_at']}")
    summary.append(f"URL: {construct_video_url(video_id)}")
    
    # Add description
    if video.get('description'):
        summary.append("\n=== Description ===")
        summary.append(video['description'])
    
    # Add transcript summary if available
    if transcript:
        summary.append("\n=== Transcript Summary ===")
        # Combine transcript segments into a single text
        full_transcript = " ".join(segment['text'] for segment in transcript)
        # Take first 500 characters as a preview
        transcript_preview = full_transcript[:500] + "..." if len(full_transcript) > 500 else full_transcript
        summary.append(transcript_preview)
    else:
        summary.append("\n=== Transcript ===")
        summary.append("No transcript available for this video.")
    
    # Add top comments if requested
    if include_comments and comments:
        summary.append("\n=== Top Comments ===")
        for comment in comments:
            summary.append(f"\n{comment['author']}:")
            summary.append(comment['text'])
            summary.append(f"Likes: {comment['like_count']}")
    
    return "\n".join(summary)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
