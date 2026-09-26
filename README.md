# PocketSmart AI

PocketSmart AI is a GenAI-powered Smart Budget & Recommendation Assistant built using FastAPI, Jinja2, HTML, CSS, JavaScript, and Google Gemini.

The system provides budget-based recommendations for Home Interior Planning, Party Planning, and Jewelry Selection.

## Features

* Home Interior Budget Planner
* Party Budget Planner
* Jewelry Budget Planner
* Jewelry outfit image analysis
* AI-generated budget recommendations
* Budget breakdown and estimated costs
* User Registration and Login
* Dashboard
* Recommendation History
* Mock platform source suggestions
* Responsive web interface

## Technologies Used

* Python
* FastAPI
* Uvicorn
* Jinja2
* HTML
* CSS
* JavaScript
* Google Gemini API
* python-dotenv

## Main Modules

### Home Interior Planner

Users enter:

* Budget
* Room type
* Quantity

The AI generates a budget-friendly interior recommendation with estimated costs for:

* Furniture
* Lighting
* Decoration

The recommendation can mention suitable shopping sources such as Amazon and IKEA.

### Party Planner

Users enter:

* Budget
* Number of guests
* Event type
* Venue

The AI creates a party budget plan covering:

* Catering
* Decoration
* Entertainment

The recommendation can mention suitable platforms such as Swiggy, Zomato, and OYO.

### Jewelry Planner

Users enter:

* Budget
* Occasion
* Style

Users can also upload an outfit image.

The AI analyzes the outfit image and provides jewelry recommendations for:

* Earrings
* Necklace
* Bangles/Bracelet
* Ring

The recommendation can mention shopping sources such as Amazon and Flipkart.

## Authentication

PocketSmart AI includes basic authentication routes:

* `/register`
* `/login`
* `/logout`
* `/token`
* `/session-info`
* `/session-data`

The current project uses an in-memory user list for demonstration purposes.

## Recommendation History

The application stores generated recommendations during the current application session and provides them through the History page.

## Platform Data

The project uses mock/static platform data to demonstrate platform-based recommendations.

The current implementation does not use live Amazon, Flipkart, IKEA, Swiggy, Zomato, or OYO APIs.

## Project Structure

```text
PocketSmart_AI/
│
├── main.py
├── gemini_utils.py
├── mock_data.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env
│
├── templates/
│   ├── home.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── party.html
│   ├── jewelry.html
│   ├── result.html
│   ├── party_result.html
│   ├── jewelry_result.html
│   └── history.html
│
└── venv/
```

> The `venv/` and `.env` files should not be uploaded to GitHub.

## How to Run

### 1. Open the project

Open the `PocketSmart_AI` folder in VS Code.

### 2. Create a virtual environment

```powershell
python -m venv venv
```

### 3. Activate the virtual environment

On Windows PowerShell:

```powershell
venv\Scripts\activate
```

After activation, the terminal should show:

```text
(venv)
```

### 4. Install the required packages

```powershell
pip install -r requirements.txt
```

### 5. Configure the Gemini API key

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

Do not upload the `.env` file or your actual API key to GitHub.

### 6. Start the FastAPI server

```powershell
python -m uvicorn main:app --reload
```

### 7. Open the application

Open the following address in your browser:

```text
http://127.0.0.1:8000
```

## Useful Routes

| Route               | Purpose                   |
| ------------------- | ------------------------- |
| `/`                 | Home page                 |
| `/register`         | User registration         |
| `/login`            | User login                |
| `/dashboard`        | User dashboard            |
| `/party`            | Party planner             |
| `/jewelry`          | Jewelry planner           |
| `/history`          | Recommendation history    |
| `/generate-home`    | Home recommendations      |
| `/generate-party`   | Party recommendations     |
| `/generate-jewelry` | Jewelry recommendations   |
| `/test-ai`          | Test Gemini AI            |
| `/docs`             | FastAPI API documentation |
| `/startup`          | Application status        |

## Gemini AI Integration

Google Gemini is used to generate budget-aware recommendations based on the user's inputs.

The Jewelry Planner also supports an optional outfit image. The image is passed to Gemini together with the user's budget, occasion, and style so that the system can generate matching jewelry recommendations.

## Testing

The application was tested using:

* Home Interior budget recommendations
* Party budget recommendations
* Jewelry recommendations
* Jewelry outfit image analysis
* User registration
* Valid login
* Invalid login
* Dashboard
* Recommendation History
* FastAPI API documentation
* Gemini AI connectivity

## Current Limitations

* Platform recommendations currently use mock/static platform data rather than live third-party APIs.
* User accounts are stored in memory for demonstration.
* Passwords are not persisted in a production database.
* Session routes are basic demonstration implementations.

## Future Enhancements

* Integrate live product and service APIs.
* Add a database for persistent user accounts.
* Implement secure password hashing.
* Implement proper session/JWT authentication.
* Store recommendation history permanently.
* Add real-time product prices and availability.
* Improve recommendation personalization.

## Project Goal

PocketSmart AI aims to simplify budget planning by combining generative AI with user preferences and budget constraints to provide practical recommendations for home interiors, parties, and jewelry.

## Project Status

The main planner modules, Gemini AI integration, authentication flow, dashboard, recommendation history, and frontend pages have been implemented and tested.
