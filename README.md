# PocketSmart AI

PocketSmart AI is a GenAI-powered budget recommendation assistant built using FastAPI, Jinja2, and Google Gemini.

## Features

- Home Interior Budget Planner
- Party Budget Planner
- Jewelry Budget Planner
- Jewelry outfit image analysis
- AI-generated budget recommendations
- Budget breakdown and estimated costs
- Recommendation History

## Technologies Used

- Python
- FastAPI
- Jinja2
- HTML
- CSS
- Google Gemini API

## Main Modules

### Home Interior Planner

Users enter:
- Budget
- Room type
- Quantity

The AI generates a budget-friendly interior recommendation with estimated costs for furniture, lighting, and decoration.

### Party Planner

Users enter:
- Budget
- Number of guests
- Event type
- Venue

The AI creates a party budget plan covering catering, decoration, and entertainment.

### Jewelry Planner

Users enter:
- Budget
- Occasion
- Style

Users can also upload an outfit image. The AI analyzes the outfit and suggests suitable jewelry within the given budget.

## How to Run

1. Create and activate the virtual environment.

2. Install the required packages:

```bash
pip install -r requirements.txt