# South African Port Tariff Calculator

A FastAPI microservice that calculates port tariffs for South African ports based on vessel specifications. This calculator computes the following tariffs:

- Light Dues
- Port Dues
- Towage Dues
- Vehicle Traffic Services (VTS) Dues
- Pilotage Dues
- Running of Vessel Lines Dues

The application integrates with Google's Gemini Pro LLM to parse natural language queries and generate explanations for the calculated tariffs.

## Architecture

This project some best practices:

- **Clean Architecture**: Separation of concerns with modular components
- **API-First Design**: Well-documented FastAPI endpoints
- **Configuration Management**: Environment variables for sensitive data
- **Containerization**: Docker support for consistent deployment

## Project Structure

```
.
├── app/
│   ├── calculator.py      # Core tariff calculation logic
│   ├── config.py         # Configuration management
│   ├── llm_client.py     # Google Gemini LLM integration
│   ├── main.py          # FastAPI application entry point
│   ├── models.py        # Pydantic data models
│   ├── rules.json       # Tariff rules and rates
│   └── utils.py         # Utility functions
├── data/                # Data files
├── payload-example.txt  # Example payloads for testing
├── Dockerfile          # Container configuration
└── requirements.txt    # Python dependencies
```

## Setup

### Prerequisites

- Python 3.11+
- Google Gemini API key (for natural language processing)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd marcura-rag-tariffs
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_gemini_api_key" > .env
```

## Running the Application

### Local Development

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### Docker Deployment

```bash
# Build the Docker image
docker build -t sa-port-tariff-calculator .

# Run the container
docker run -p 8000:8000 -e GOOGLE_API_KEY=your_gemini_api_key sa-port-tariff-calculator
```

## API Usage

### Swagger Documentation

Access the interactive API documentation at http://localhost:8000/docs

### Natural Language Endpoint

**POST** `/nl_calculate` with JSON payload:

```json
{
  "query": "Calculate the different tariffs payable by the following vessel berthing at the port of Durban:\n\nVessel Name: XYZ\nBuilt: 2010\nType: Bulk Carrier\nDWT: 93,274\nGT / NT: 51,300 / 31,192\nLOA (m): 229.2\nBeam (m): 38\nMoulded Depth (m): 20.7\nLBP: 222\nDrafts SW S / W / T (m): 14.9 / 0 / 0\nSuez GT / NT: - / 49,069\nNumber of Holds: 7\nCargo Quantity: 40,000 MT\nDays Alongside: 3.39 days\nArrival Time: 15 Nov 2024 10:12\nDeparture Time: 22 Nov 2024 13:00\nActivity: Exporting Iron Ore\nNumber of Operations: 2"
}
```

## Testing the API

The repository includes a `payload-example.txt` file with example payloads for testing different scenarios. Here are the example queries you can use to test the API:

### 1. Durban Port Example
```json
{
    "query": "Calculate the different tariffs payable by the following vessel berthing at the port of Durban:\n\nGeneral\nVessel Name: Atlantic Breeze\nBuilt: 2016\n\nMain Details\nType: Container Ship\nDWT: 65,500\nGT / NT: 42,300 / 23,100\nLOA (m): 294.5\nBeam (m): 32.3\nMoulded Depth (m): 18.7\nLBP: 285\nDrafts SW S / W / T (m): 13.4 / 0 / 0\nSuez GT / NT: 41,900 / 22,800\n\nDRY\nNumber of Holds: 6\n\nCargo Details\nCargo Quantity: 2,800 TEU\nDays Alongside: 2.8 days\nArrival Time: 12 Dec 2024 07:00\nDeparture Time: 14 Dec 2024 15:00\n\nActivity/Operations\nActivity: Importing Containers\nNumber of Operations: 2"
}
```

### 2. Saldanha Port Example
```json
{
    "query": "Calculate the different tariffs payable by the following vessel berthing at the port of Saldanha:\n\nGeneral\nVessel Name: Iron Majesty\nBuilt: 2012\n\nMain Details\nType: Bulk Carrier\nDWT: 175,000\nGT / NT: 90,200 / 55,800\nLOA (m): 299.8\nBeam (m): 49.5\nMoulded Depth (m): 23.8\nLBP: 289\nDrafts SW S / W / T (m): 17.9 / 0 / 0\nSuez GT / NT: 89,000 / 54,900\n\nDRY\nNumber of Holds: 9\n\nCargo Details\nCargo Quantity: 165,000 MT\nDays Alongside: 4.2 days\nArrival Time: 8 Jan 2025 05:30\nDeparture Time: 12 Jan 2025 13:45\n\nActivity/Operations\nActivity: Exporting Iron Ore\nNumber of Operations: 2"
}
```

### 3. Richards Bay Port Example
```json
{
    "query": "Calculate the different tariffs payable by the following vessel berthing at the port of Richards_Bay:\n\nGeneral\nVessel Name: Coal Runner\nBuilt: 2009\n\nMain Details\nType: Bulk Carrier\nDWT: 78,000\nGT / NT: 43,500 / 25,200\nLOA (m): 226.0\nBeam (m): 36.2\nMoulded Depth (m): 19.2\nLBP: 219\nDrafts SW S / W / T (m): 13.9 / 0 / 0\nSuez GT / NT: 42,800 / 24,900\n\nDRY\nNumber of Holds: 7\n\nCargo Details\nCargo Quantity: 62,000 MT\nDays Alongside: 5.5 days\nArrival Time: 20 Feb 2025 10:00\nDeparture Time: 25 Feb 2025 12:30\n\nActivity/Operations\nActivity: Exporting Coal\nNumber of Operations: 2"
}
```

To test using curl:

```bash
# Test the natural language endpoint with any of the above examples
curl -X POST http://localhost:8000/nl_calculate \
  -H "Content-Type: application/json" \
  -d @payload-example.txt
```

## Implementation Details

1. The tariff rules are stored in `app/rules.json` and loaded at startup
2. The calculator (`app/calculator.py`) handles complex calculations like towage dues which vary by port and vessel size
3. Natural language processing uses Google's Gemini LLM (`app/llm_client.py`) to extract vessel specifications
4. The implementation strictly follows the official South African port tariff rules
5. Data models (`app/models.py`) ensure type safety and validation
6. Configuration management (`app/config.py`) handles environment variables and settings

## Dependencies

- FastAPI 0.110.0 - Web framework
- Uvicorn 0.25.0 - ASGI server
- Pydantic 2.6.0 - Data validation
- Python-dateutil 2.8.2 - Date handling
- Google-generativeai 0.3.1 - LLM integration

## Extension Points

For future enhancements:
- Implement a vector database for more complex tariff rule retrieval
- Add a caching layer for improved performance
- Create a React/Vue frontend for easier user interaction
- Add support for additional tariff types and special conditions
