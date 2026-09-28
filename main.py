from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from gemini_utils import ask_gemini
from mock_data import HOME_SOURCES, PARTY_SOURCES, JEWELRY_SOURCES

import json
import re
import asyncio
import os

from database import (
    create_users_table,
    create_user,
    get_user,
    save_history,
    get_history
)


# =========================
# APP
# =========================

app = FastAPI(title="PocketSmart AI")

create_users_table()


# =========================
# SESSION
# =========================

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv(
        "SESSION_SECRET_KEY",
        "pocketsmart-demo-secret-key"
    )
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="templates")


# =========================
# HELPER - CLEAN GEMINI JSON
# =========================

def extract_json(text):

    if not text:
        raise ValueError("Empty Gemini response")

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        json_text = text[start:end + 1]

        try:
            return json.loads(json_text)

        except json.JSONDecodeError:

            last_brace = json_text.rfind("}")

            if last_brace != -1:

                json_text = json_text[:last_brace + 1]

                return json.loads(json_text)

    raise ValueError(
        "Could not extract valid JSON from Gemini response"
    )


# =========================
# REGISTER PAGE
# =========================

@app.get("/register")
def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )


# =========================
# REGISTER
# =========================

@app.post("/register")
async def register(request: Request):

    form = await request.form()

    name = str(form["name"]).strip()
    email = str(form["email"]).strip().lower()
    password = str(form["password"]).strip()

    try:

        create_user(
            name,
            email,
            password
        )

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    except Exception as e:

        print("REGISTER ERROR:", e)

        return {
            "message": "This email is already registered."
        }


# =========================
# LOGIN PAGE
# =========================

@app.get("/login")
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


# =========================
# LOGIN
# =========================

@app.post("/login")
async def login(request: Request):

    form = await request.form()

    email = str(form["email"]).strip().lower()
    password = str(form["password"]).strip()

    print("LOGIN EMAIL:", email)

    user = get_user(
        email,
        password
    )

    if user:

        request.session["email"] = user["email"]
        request.session["name"] = user["name"]

        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "name": user["name"]
            }
        )

    return {
        "message": "Invalid email or password"
    }


# =========================
# TOKEN
# =========================

@app.post("/token")
async def token(request: Request):

    form = await request.form()

    email = form["email"]
    password = form["password"]

    user = get_user(
        email,
        password
    )

    if user:

        return {
            "access_token": "demo-token",
            "token_type": "bearer"
        }

    return {
        "message": "Invalid email or password"
    }


# =========================
# LOGOUT
# =========================

@app.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303
    )


# =========================
# SESSION INFO
# =========================

@app.get("/session-info")
def session_info(request: Request):

    email = request.session.get("email")
    name = request.session.get("name")

    if email:

        return {
            "logged_in": True,
            "name": name,
            "email": email
        }

    return {
        "logged_in": False,
        "message": "No active session"
    }


# =========================
# SESSION DATA
# =========================

@app.get("/session-data")
def session_data(request: Request):

    email = request.session.get("email")
    name = request.session.get("name")

    if email:

        return {
            "name": name,
            "email": email
        }

    return {
        "message": "No session data available"
    }


# =========================
# RECOMMENDATIONS DETAILS
# =========================

@app.get("/recommendations-details")
async def recommendations_details(request: Request):

    email = request.session.get("email")

    if not email:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    recommendations = get_history(email)

    return templates.TemplateResponse(
        request=request,
        name="recommendations_details.html",
        context={
            "recommendations": recommendations
        }
    )


# =========================
# HISTORY
# =========================

@app.get("/history")
def show_history(request: Request):

    email = request.session.get("email")

    if not email:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "history": get_history(email)
        }
    )


# =========================
# STARTUP
# =========================

@app.get("/startup")
def startup():

    return {
        "message": "PocketSmart AI is running successfully!"
    }


# =========================
# DASHBOARD
# =========================

@app.get("/dashboard")
def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "name": request.session.get("name")
        }
    )


# =========================
# HOME PAGE
# =========================

@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="home.html"
    )


@app.get("/home")
def home_planner(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="home_planner.html"
    )


# =========================
# PARTY PLANNER PAGE
# =========================

@app.get("/party")
def party_planner(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="party.html"
    )


# =========================
# TEST GEMINI
# =========================

@app.get("/test-ai")
def test_ai():

    answer = ask_gemini(
        "Give me 3 simple budget tips for a college student."
    )

    return {
        "recommendation": answer
    }


# =========================
# HOME INTERIOR
# =========================

@app.get("/generate-home")
def generate_home(
    request: Request,
    budget: int,
    room: str,
    quantity: int,
    lights: int = 0,
    fans: int = 0,
    furniture: int = 0,
    dining_tables: int = 0,
    additional_info: str = ""
):

    prompt = f"""
You are PocketSmart AI, a smart home interior budget assistant.

Create a personalized home interior budget plan.

USER DETAILS:
Total Budget: ₹{budget}
Rooms: {room}
Lights/Fixtures: {lights}
Ceiling Fans: {fans}
Furniture Pieces: {furniture}
Dining Tables: {dining_tables}
Additional Information: {additional_info}

Create realistic recommendations within the total budget.

IMPORTANT:
- The total of all items must NOT exceed ₹{budget}.
- Use Amazon and IKEA as shopping sources where relevant.
- Give realistic Indian prices.
- Keep quantities according to the user's requirements.
- Return ONLY valid JSON.
- Do not use markdown.

Use EXACTLY this JSON structure:

{{
    "total_budget": {budget},
    "remaining_budget": 0,

    "lighting": {{
        "allocation": 0,
        "items": [
            {{
                "item": "Item name",
                "description": "Short description",
                "price": 0,
                "quantity": 1,
                "shopping_links": ["Amazon", "IKEA"]
            }}
        ]
    }},

    "ceiling_fans": {{
        "allocation": 0,
        "items": [
            {{
                "item": "Ceiling fan",
                "description": "Short description",
                "price": 0,
                "quantity": 1,
                "shopping_links": ["Amazon"]
            }}
        ]
    }},

    "furniture": {{
        "allocation": 0,
        "items": [
            {{
                "item": "Furniture item",
                "description": "Short description",
                "price": 0,
                "quantity": 1,
                "shopping_links": ["Amazon", "IKEA"]
            }}
        ]
    }},

    "additional_suggestions": [
        "Suggestion 1",
        "Suggestion 2",
        "Suggestion 3"
    ]
}}

Make sure allocation values and item prices are consistent with the total budget.
"""

    source_text = "\n".join(
        [
            f"{source['platform']}: {source['description']}"
            for source in HOME_SOURCES
        ]
    )

    prompt += f"""

Available shopping sources:
{source_text}

Use these sources in the shopping_links fields.
"""

    try:

        answer = ask_gemini(prompt)

        recommendation_data = extract_json(answer)

    except Exception as e:

        print("HOME AI ERROR:", e)

        lighting_amount = min(
            budget * 0.20,
            max(0, lights * 1500)
        )

        fan_amount = min(
            budget * 0.15,
            max(0, fans * 2500)
        )

        furniture_amount = min(
            budget * 0.45,
            max(0, furniture * 8000)
        )

        dining_amount = min(
            budget * 0.10,
            max(0, dining_tables * 5000)
        )

        total_used = (
            lighting_amount
            + fan_amount
            + furniture_amount
            + dining_amount
        )

        if total_used > budget:

            total_used = budget

        remaining = max(
            0,
            budget - total_used
        )

        recommendation_data = {

            "total_budget": budget,

            "remaining_budget": round(
                remaining,
                2
            ),

            "lighting": {

                "allocation": round(
                    lighting_amount,
                    2
                ),

                "items": [

                    {
                        "item": "LED Ceiling Light",
                        "description": (
                            "Energy-efficient lighting suitable "
                            "for the selected room."
                        ),
                        "price": 1500,
                        "quantity": lights,
                        "shopping_links": [
                            "Amazon",
                            "IKEA"
                        ]
                    }

                ] if lights > 0 else []
            },

            "ceiling_fans": {

                "allocation": round(
                    fan_amount,
                    2
                ),

                "items": [

                    {
                        "item": "Energy-Efficient Ceiling Fan",
                        "description": (
                            "Ceiling fan suitable for "
                            "everyday home use."
                        ),
                        "price": 2500,
                        "quantity": fans,
                        "shopping_links": [
                            "Amazon"
                        ]
                    }

                ] if fans > 0 else []
            },

            "furniture": {

                "allocation": round(
                    furniture_amount,
                    2
                ),

                "items": [

                    {
                        "item": "Modern Furniture Set",
                        "description": (
                            "Functional furniture option "
                            "suitable for the selected room."
                        ),
                        "price": 8000,
                        "quantity": furniture,
                        "shopping_links": [
                            "Amazon",
                            "IKEA"
                        ]
                    }

                ] if furniture > 0 else []
            },

            "additional_suggestions": [

                "Compare Amazon and IKEA prices before purchasing.",

                "Choose furniture based on available room space.",

                "Keep the remaining budget for additional home requirements."
            ]
        }

    # =========================
    # SAVE HOME HISTORY
    # =========================

    email = request.session.get("email")

    if email:

        save_history(
            email=email,
            history_type="Home Interior",
            details={
                "budget": budget,
                "room": room,
                "lights": lights,
                "fans": fans,
                "furniture": furniture,
                "dining_tables": dining_tables
            },
            recommendation=recommendation_data
        )

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "recommendation": recommendation_data,
            "room": room
        }
    )


# =========================
# PARTY PLANNER
# =========================

@app.get("/generate-party")
def generate_party(
    request: Request,
    budget: int,
    guests: int,
    event_type: str,
    venue: str = "",
    needs: list[str] = [],
    additional_info: str = ""
):

    prompt = f"""
You are PocketSmart AI, a smart party budget planning assistant.

Create a personalized party planning budget plan.

USER DETAILS:
Total Budget: ₹{budget}
Number of Guests: {guests}
Event Type: {event_type}
Venue: {venue}
Required Services: {", ".join(needs)}
Additional Information: {additional_info}

Create realistic recommendations within the total budget.

IMPORTANT:
- Total cost must not exceed the total budget.
- Consider the number of guests.
- Give realistic Indian prices.
- Use Swiggy, Zomato and OYO where relevant.
- Return ONLY valid JSON.
- Do not use markdown.

Use EXACTLY this structure:

{{
    "total_budget": {budget},
    "remaining_budget": 0,

    "catering": {{
        "allocation": 0,
        "items": []
    }},

    "decoration": {{
        "allocation": 0,
        "items": []
    }},

    "entertainment": {{
        "allocation": 0,
        "items": []
    }},

    "venue": {{
        "allocation": 0,
        "items": []
    }},

    "additional_suggestions": []
}}

Each item must contain:
item, description, price, quantity, shopping_links.
"""

    source_text = "\n".join(
        [
            f"{source['platform']}: {source['description']}"
            for source in PARTY_SOURCES
        ]
    )

    prompt += f"""

Available party planning sources:
{source_text}

Use these platforms in shopping_links where appropriate.
"""

    try:

        answer = ask_gemini(prompt)
        recommendation_data = extract_json(answer)

        # Make sure the template-required sections always exist.
        recommendation_data.setdefault(
            "total_budget",
            budget
        )

        recommendation_data.setdefault(
            "remaining_budget",
            0
        )

        recommendation_data.setdefault(
            "catering",
            {"allocation": 0, "items": []}
        )

        recommendation_data.setdefault(
            "decoration",
            {"allocation": 0, "items": []}
        )

        recommendation_data.setdefault(
            "entertainment",
            {"allocation": 0, "items": []}
        )

        recommendation_data.setdefault(
            "venue",
            {"allocation": 0, "items": []}
        )

        recommendation_data.setdefault(
            "additional_suggestions",
            []
        )

    except Exception as e:

        print("PARTY AI ERROR:", e)

        catering_amount = min(
            budget * 0.45,
            guests * 500
        )

        decoration_amount = min(
            budget * 0.20,
            budget
        )

        entertainment_amount = min(
            budget * 0.10,
            budget
        )

        venue_amount = min(
            budget * 0.20,
            budget
        )

        total_used = (
            catering_amount
            + decoration_amount
            + entertainment_amount
            + venue_amount
        )

        if total_used > budget:
            total_used = budget

        remaining = max(
            0,
            budget - total_used
        )

        recommendation_data = {

            "total_budget": budget,

            "remaining_budget": round(
                remaining,
                2
            ),

            "catering": {
                "allocation": round(
                    catering_amount,
                    2
                ),
                "items": [
                    {
                        "item": "Party Catering Package",
                        "description": (
                            "Food package suitable for "
                            "the selected number of guests."
                        ),
                        "price": 500,
                        "quantity": guests,
                        "shopping_links": [
                            "Swiggy",
                            "Zomato"
                        ]
                    }
                ] if guests > 0 else []
            },

            "decoration": {
                "allocation": round(
                    decoration_amount,
                    2
                ),
                "items": [
                    {
                        "item": "Party Decoration Set",
                        "description": (
                            "Decoration package suitable "
                            "for the selected event."
                        ),
                        "price": round(
                            decoration_amount,
                            2
                        ),
                        "quantity": 1,
                        "shopping_links": [
                            "Amazon"
                        ]
                    }
                ]
            },

            "entertainment": {
                "allocation": round(
                    entertainment_amount,
                    2
                ),
                "items": [
                    {
                        "item": "Party Entertainment",
                        "description": (
                            "Entertainment option suitable "
                            "for the selected event."
                        ),
                        "price": round(
                            entertainment_amount,
                            2
                        ),
                        "quantity": 1,
                        "shopping_links": [
                            "Amazon"
                        ]
                    }
                ]
            },

            "venue": {
                "allocation": round(
                    venue_amount,
                    2
                ),
                "items": [
                    {
                        "item": "Event Venue",
                        "description": (
                            "Venue suitable for the selected "
                            "event and number of guests."
                        ),
                        "price": round(
                            venue_amount,
                            2
                        ),
                        "quantity": 1,
                        "shopping_links": [
                            "OYO"
                        ]
                    }
                ]
            },

            "additional_suggestions": [
                "Compare Swiggy and Zomato catering options.",
                "Choose decorations according to the event type.",
                "Check venue capacity before booking.",
                "Plan entertainment according to the guest count."
            ]
        }

    email = request.session.get("email")

    if email:
        save_history(
            email=email,
            history_type="Party",
            details={
                "budget": budget,
                "guests": guests,
                "event_type": event_type,
                "venue": venue,
                "needs": needs,
                "additional_info": additional_info
            },
            recommendation=recommendation_data
        )

    return templates.TemplateResponse(
        request=request,
        name="party_result.html",
        context={
            "recommendation": recommendation_data,
            "budget": budget,
            "event_type": event_type,
            "guests": guests,
            "venue": venue,
            "additional_info": additional_info
        }
    )




    # =========================
    # SAVE PARTY HISTORY
    # =========================

    email = request.session.get("email")

    if email:

        save_history(
            email=email,
            history_type="Party",
            details={
                "budget": budget,
                "guests": guests,
                "event_type": event_type,
                "venue": venue,
                "additional_info": additional_info
            },
            recommendation=recommendation_data
        )

    return templates.TemplateResponse(
        request=request,
        name="party_result.html",
        context={
            "recommendation": recommendation_data,
            "event_type": event_type,
            "guests": guests
        }
    )


# =========================
# JEWELRY PAGE
# =========================

@app.get("/jewelry")
def jewelry_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="jewelry.html"
    )


# =========================
# JEWELRY RECOMMENDATIONS
# =========================

@app.post("/generate-jewelry")
async def generate_jewelry(request: Request):

    form = await request.form()

    budget = int(form["budget"])
    occasion = form["occasion"]
    style = form["style"]

    # Get uploaded outfit image

    outfit_image = form.get("outfit_image")

    image_bytes = None
    mime_type = None

    if outfit_image and hasattr(outfit_image, "read"):

        image_bytes = await outfit_image.read()
        mime_type = outfit_image.content_type

    # Default outfit analysis

    outfit_analysis = {
    "colors": "not available",
    "style": "not available",
    "formality": "not available"
}

    # =========================
    # GEMINI IMAGE ANALYSIS
    # =========================

    if image_bytes:

        analysis_prompt = f"""
Analyze the uploaded outfit image for a jewelry recommendation.

Return ONLY valid JSON in this exact structure:

{{
    "colors": "main outfit colors",
    "style": "casual/formal/traditional/etc.",
    "formality": "informal/semi-formal/formal"
}}

Do not include markdown or extra text.

The user's occasion is: {occasion}
The user's preferred jewelry style is: {style}
"""

        try:

            print(
                "GEMINI JEWELRY IMAGE ANALYSIS STARTED"
            )

            gemini_result = ask_gemini(
                analysis_prompt,
                image_bytes=image_bytes,
                mime_type=mime_type
            )

            if (
                "could not generate" in gemini_result.lower()
                or "quota" in gemini_result.lower()
                or "503" in gemini_result.lower()
            ):

                await asyncio.sleep(2)

                print(
                    "RETRYING GEMINI JEWELRY IMAGE ANALYSIS..."
                )

                gemini_result = ask_gemini(
                    analysis_prompt,
                    image_bytes=image_bytes,
                    mime_type=mime_type
                )

            parsed_result = extract_json(gemini_result)

            if isinstance(parsed_result, dict):

                outfit_analysis = {
                    "colors": parsed_result.get(
                        "colors",
                        outfit_analysis["colors"]
                    ),
                    "style": parsed_result.get(
                        "style",
                        outfit_analysis["style"]
                    ),
                    "formality": parsed_result.get(
                        "formality",
                        outfit_analysis["formality"]
                    )
                }

                print(
                    "GEMINI JEWELRY IMAGE ANALYSIS SUCCESS"
                )

        except Exception as e:

            print(
                "GEMINI JEWELRY IMAGE ANALYSIS ERROR:",
                e
            )

            print(
                "Using default outfit analysis."
            )

    # =========================
    # GEMINI JEWELRY GENERATION
    # =========================

    jewelry_prompt = f"""
Create personalized jewelry recommendations.

User information:

Budget: ₹{budget}
Occasion: {occasion}
Preferred jewelry style: {style}

Outfit analysis:
Colors: {outfit_analysis["colors"]}
Style: {outfit_analysis["style"]}
Formality: {outfit_analysis["formality"]}

Recommend exactly 3 jewelry items that match the outfit,
occasion, preferred style and budget.

The total price of all 3 items MUST be less than or equal
to the user's budget.

Return ONLY valid JSON in this exact structure:

{{
    "items": [
        {{
            "item": "jewelry item name",
            "description": "short explanation of why this item matches the outfit",
            "price": 0,
            "style": "jewelry style"
        }},
        {{
            "item": "jewelry item name",
            "description": "short explanation of why this item matches the outfit",
            "price": 0,
            "style": "jewelry style"
        }},
        {{
            "item": "jewelry item name",
            "description": "short explanation of why this item matches the outfit",
            "price": 0,
            "style": "jewelry style"
        }}
    ],
    "additional_suggestions": [
        "styling tip 1",
        "styling tip 2",
        "styling tip 3"
    ]
}}

Important:
- Prices must be realistic Indian rupee amounts.
- Keep the total within ₹{budget}.
- Match the jewelry colors/materials with the outfit.
- Consider the occasion.
- Consider the user's preferred style.
- Do not include shopping links.
- Do not include markdown.
"""

    generated_items = None
    additional_suggestions = []

    try:

        print(
            "GEMINI JEWELRY RECOMMENDATIONS STARTED"
        )

        jewelry_result = ask_gemini(jewelry_prompt)

        if (
            "could not generate" in jewelry_result.lower()
            or "quota" in jewelry_result.lower()
            or "503" in jewelry_result.lower()
        ):

            await asyncio.sleep(2)

            print(
                "RETRYING GEMINI JEWELRY RECOMMENDATIONS..."
            )

            jewelry_result = ask_gemini(jewelry_prompt)

        parsed_jewelry = extract_json(jewelry_result)

        if isinstance(parsed_jewelry, dict):

            if isinstance(
                parsed_jewelry.get("items"),
                list
            ):

                generated_items = parsed_jewelry["items"]

            if isinstance(
                parsed_jewelry.get("additional_suggestions"),
                list
            ):

                additional_suggestions = (
                    parsed_jewelry["additional_suggestions"]
                )

            print(
                "GEMINI JEWELRY RECOMMENDATIONS SUCCESS"
            )

    except Exception as e:

        print(
            "GEMINI JEWELRY RECOMMENDATIONS ERROR:",
            e
        )

    # =========================
    # FALLBACK RECOMMENDATIONS
    # =========================

    if not generated_items:

        generated_items = [

            {
                "item": "silver bracelet",
                "description": (
                    "A simple silver bracelet that "
                    "complements the outfit and keeps "
                    "the look elegant."
                ),
                "price": 500,
                "style": "elegant"
            },

            {
                "item": "minimalist silver ring",
                "description": (
                    "A clean silver ring that matches "
                    "the outfit without looking too heavy."
                ),
                "price": 700,
                "style": "minimalist"
            },

            {
                "item": "classic watch",
                "description": (
                    "A classic watch with a simple metal "
                    "finish that works well for formal outfits."
                ),
                "price": 3000,
                "style": "classic"
            }
        ]

        additional_suggestions = [

            "Keep the jewelry balanced with the outfit.",

            "Silver-toned accessories work well with cool colors.",

            "Avoid wearing too many statement pieces together."
        ]

    # =========================
    # ADD SHOPPING LINKS
    # =========================

    shopping_platforms = [
        "Amazon",
        "Flipkart",
        "Bluestone",
        "Tanishq",
        "CaratLane",
        "Melorra",
        "Mia"
    ]

    for item in generated_items:

        item["shopping_links"] = shopping_platforms

    # =========================
    # FINAL RECOMMENDATION DATA
    # =========================

    recommendation_data = {

        "total_budget": budget,

        "occasion": occasion,

        "style": style,

        "outfit_analysis": outfit_analysis,

        "items": generated_items,

        "additional_suggestions": additional_suggestions
    }

    # =========================
    # SAVE JEWELRY HISTORY
    # =========================

    email = request.session.get("email")

    if email:

        save_history(
            email=email,
            history_type="Jewelry",
            details={
                "budget": budget,
                "occasion": occasion,
                "style": style
            },
            recommendation=recommendation_data
        )

    # =========================
    # SHOW RESULT PAGE
    # =========================

    return templates.TemplateResponse(
        request=request,
        name="jewelry_result.html",
        context={
            "recommendation": recommendation_data
        }
    )