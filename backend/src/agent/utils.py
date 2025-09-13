from typing import Any, Dict, List
from langchain_core.messages import AnyMessage, AIMessage, HumanMessage


def get_research_topic(messages: List[AnyMessage]) -> str:
    """
    Get the research topic from the messages.
    """
    # check if request has a history and combine the messages into a single string
    if len(messages) == 1:
        research_topic = messages[-1].content
    else:
        research_topic = ""
        for message in messages:
            if isinstance(message, HumanMessage):
                research_topic += f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                research_topic += f"Assistant: {message.content}\n"
    return research_topic


def resolve_urls(urls_to_resolve: List[Any], id: int) -> Dict[str, str]:
    """
    Create a map of URLs to short URL identifiers.
    This is a simplified version for OpenAI compatible APIs.
    """
    # For OpenAI compatible APIs, we create a simple mapping
    # In a real implementation, you would process actual search results
    resolved_map = {}
    
    if isinstance(urls_to_resolve, list):
        for idx, url in enumerate(urls_to_resolve):
            # Handle different URL formats
            if isinstance(url, str):
                actual_url = url
            elif hasattr(url, 'web') and hasattr(url.web, 'uri'):
                actual_url = url.web.uri
            else:
                actual_url = f"https://example.com/source-{id}-{idx}"
            
            resolved_map[actual_url] = f"[{id}-{idx}]"
    
    return resolved_map


def insert_citation_markers(text, citations_list):
    """
    Inserts citation markers into a text string based on start and end indices.

    Args:
        text (str): The original text string.
        citations_list (list): A list of dictionaries, where each dictionary
                               contains 'start_index', 'end_index', and
                               'segment_string' (the marker to insert).
                               Indices are assumed to be for the original text.

    Returns:
        str: The text with citation markers inserted.
    """
    # Sort citations by end_index in descending order.
    # If end_index is the same, secondary sort by start_index descending.
    # This ensures that insertions at the end of the string don't affect
    # the indices of earlier parts of the string that still need to be processed.
    sorted_citations = sorted(
        citations_list, key=lambda c: (c["end_index"], c["start_index"]), reverse=True
    )

    modified_text = text
    for citation_info in sorted_citations:
        # These indices refer to positions in the *original* text,
        # but since we iterate from the end, they remain valid for insertion
        # relative to the parts of the string already processed.
        end_idx = citation_info["end_index"]
        marker_to_insert = ""
        for segment in citation_info["segments"]:
            marker_to_insert += f" [{segment['label']}]({segment['short_url']})"
        # Insert the citation marker at the original end_idx position
        modified_text = (
            modified_text[:end_idx] + marker_to_insert + modified_text[end_idx:]
        )

    return modified_text


def get_citations(response, resolved_urls_map):
    """
    Creates citation information for OpenAI compatible API responses.
    
    Since OpenAI API doesn't provide grounding metadata like Google Genai,
    this is a simplified version that creates basic citations.

    Args:
        response: The response object from the OpenAI compatible API
        resolved_urls_map: A dictionary mapping URLs to resolved short URLs

    Returns:
        list: A list of dictionaries representing citations with basic structure
    """
    citations = []
    
    # For OpenAI compatible APIs, we create simplified citations
    # In a real implementation, you would integrate with a search API
    # that provides proper source attribution
    
    if resolved_urls_map:
        for idx, (original_url, short_url) in enumerate(resolved_urls_map.items()):
            citation = {
                "start_index": 0,
                "end_index": len(response.content) if hasattr(response, 'content') else 0,
                "segments": [{
                    "label": f"Source {idx + 1}",
                    "short_url": short_url,
                    "value": original_url,
                }]
            }
            citations.append(citation)
    
    return citations
