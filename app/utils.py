import math
from datetime import datetime
import re
import json
from typing import Optional, Dict


def ceil_units(value: float, unit: float) -> int:
    """
    Calculate ceiling of value/unit (e.g., ceiling of GT/100)
    
    Args:
        value: The value to divide
        unit: The unit to divide by
        
    Returns:
        The ceiling of value/unit
    """
    return math.ceil(value / unit)


def hours_between(start: datetime, end: datetime) -> float:
    """
    Calculate hours between two datetimes
    
    Args:
        start: Start datetime
        end: End datetime
        
    Returns:
        Hours between start and end as float
    """
    return (end - start).total_seconds() / 3600


def format_query_to_single_line(query: str) -> str:
    """
    Convert a free-form natural language query into a single-line string format.
    This is useful for API calls and testing.
    
    Args:
        query (str): The free-form query string with newlines and spaces
        
    Returns:
        str: A single-line formatted query string
    """
    # Remove extra whitespace and newlines
    query = re.sub(r'\s+', ' ', query.strip())
    
    # Replace multiple spaces with a single space
    query = re.sub(r' +', ' ', query)
    
    return query


def prepare_query_for_api(query: str) -> Dict[str, str]:
    """
    Prepare a query for API submission by properly formatting and escaping it.
    
    Args:
        query (str): The raw query string
        
    Returns:
        Dict[str, str]: A properly formatted JSON payload
    """
    # First format the query to a single line
    formatted_query = format_query_to_single_line(query)
    
    # Create the payload with proper JSON escaping
    payload = {
        "query": formatted_query
    }
    
    return payload


def format_query_from_file(file_path: str) -> Optional[Dict[str, str]]:
    """
    Read a query from a file and prepare it for API submission.
    
    Args:
        file_path (str): Path to the file containing the query
        
    Returns:
        Optional[Dict[str, str]]: Formatted query payload or None if file not found
    """
    try:
        with open(file_path, 'r') as f:
            query = f.read()
        return prepare_query_for_api(query)
    except FileNotFoundError:
        return None


# Example usage:
if __name__ == "__main__":
    # Example query
    example_query = """
    Calculate the different tariffs payable by the following vessel berthing at the port of Durban:

    General
    Vessel Name: Atlantic Breeze
    Built: 2016

    Main Details
    Type: Container Ship
    DWT: 65,500
    GT / NT: 42,300 / 23,100
    LOA (m): 294.5
    Beam (m): 32.3
    Moulded Depth (m): 18.7
    LBP: 285
    Drafts SW S / W / T (m): 13.4 / 0 / 0
    Suez GT / NT: 41,900 / 22,800

    DRY
    Number of Holds: 6

    Cargo Details
    Cargo Quantity: 2,800 TEU
    Days Alongside: 2.8 days
    Arrival Time: 12 Dec 2024 07:00
    Departure Time: 14 Dec 2024 15:00

    Activity/Operations
    Activity: Importing Containers
    Number of Operations: 2
    """
    
    # Convert to API-ready payload
    payload = prepare_query_for_api(example_query)
    print("API Payload:")
    print(json.dumps(payload, indent=2))
    
    # Example of reading from file
    file_payload = format_query_from_file("payload-example.txt")
    if file_payload:
        print("\nPayload from file:")
        print(json.dumps(file_payload, indent=2))