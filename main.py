from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from gemini_utils import ask_gemini

app = FastAPI(title="PocketSmart AI")

templates = Jinja2Templates(directory="templates")
history = []

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html"
    )


@app.get("/test-ai")
def test_ai():
    answer = ask_gemini(
        "Give me 3 simple budget tips for a college student."
    )

    return {"recommendation": answer}


@app.get("/generate-home")
def generate_home(
    request: Request,
    budget: int,
    room: str,
    quantity: int
):
    prompt = f"""
You are PocketSmart AI, a smart home interior budget assistant.

User details:
Budget: ₹{budget}
Room type: {room}
Quantity: {quantity}

Create a practical home interior recommendation within the user's budget.

Divide the budget into:
1. Furniture
2. Lighting
3. Decoration

Mention suitable items and approximate prices.

IMPORTANT:
- Keep the total within ₹{budget}.
- Use simple plain text.
- Do not use markdown symbols such as ** or ###.
- End with the Grand Total.

Example format:

Budget Breakdown
Furniture: ₹...
Lighting: ₹...
Decoration: ₹...

Furniture
- Item: ₹...
- Item: ₹...

Lighting
- Item: ₹...

Decoration
- Item: ₹...

Grand Total: ₹...
"""

    answer = ask_gemini(prompt)


    history.append({
        "type": "Home Interior",
        "details": f"Budget: ₹{budget} | Room: {room} | Quantity: {quantity}",
        "recommendation": answer
})

    
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "recommendation": answer,
            "budget": budget,
            "room": room,
            "quantity": quantity
        }
    )
@app.get("/generate-party")
def generate_party(
    request: Request,
    budget: int,
    guests: int,
    event_type: str,
    venue: str
):
    prompt = f"""
You are PocketSmart AI, a smart party budget assistant.

User details:
Total Budget: ₹{budget}
Number of Guests: {guests}
Event Type: {event_type}
Venue: {venue}

Create a practical party plan within the user's budget.

Divide the budget into:
1. Catering
2. Decoration
3. Entertainment

Mention suitable options and approximate prices.

IMPORTANT:
- Keep the total within ₹{budget}.
- Consider the number of guests.
- Use simple plain text.
- End with the Grand Total.

Format:

Budget Breakdown
Catering: ₹...
Decoration: ₹...
Entertainment: ₹...

Catering
- Item: ₹...
- Item: ₹...

Decoration
- Item: ₹...
- Item: ₹...

Entertainment
- Item: ₹...

Grand Total: ₹...
"""

    answer = ask_gemini(prompt)

    history.append({
        "type": "Party Planning",
        "details": f"Budget: ₹{budget} | Guests: {guests} | Event: {event_type} | Venue: {venue}",
        "recommendation": answer
    })

    return templates.TemplateResponse(
        request=request,
        name="party_result.html",
        context={
            "recommendation": answer,
            "budget": budget,
            "guests": guests,
            "event_type": event_type,
            "venue": venue
        }
    )
@app.get("/party")
def party(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="party.html"
    )
@app.get("/jewelry")
def jewelry(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="jewelry.html"
    )
@app.post("/generate-jewelry")
async def generate_jewelry(request: Request):
    form = await request.form()

    budget = int(form["budget"])
    occasion = form["occasion"]
    style = form["style"]

    outfit_image = form.get("outfit_image")

    image_bytes = None
    mime_type = None

    if outfit_image and hasattr(outfit_image, "read"):
        image_bytes = await outfit_image.read()
        mime_type = getattr(outfit_image, "content_type", "image/jpeg")

    prompt = f"""
You are PocketSmart AI, a smart jewelry budget assistant.

User details:
Budget: ₹{budget}
Occasion: {occasion}
Style preference: {style}

Create practical jewelry recommendations within the user's budget.

If an outfit image is provided, analyze its colors and overall aesthetic
and suggest jewelry that matches the outfit.

Recommend:
1. Earrings
2. Necklace
3. Bangles or Bracelet
4. Ring

IMPORTANT:
- Keep the total within ₹{budget}.
- Match the recommendations to the occasion and style.
- If an outfit image is provided, use its colors and aesthetic.
- Mention approximate prices.
- Use simple plain text.
- End with the Grand Total.

Format:

Budget Breakdown
Earrings: ₹...
Necklace: ₹...
Bangles/Bracelet: ₹...
Ring: ₹...

Earrings
- Item: ₹...

Necklace
- Item: ₹...

Bangles/Bracelet
- Item: ₹...

Ring
- Item: ₹...

Grand Total: ₹...
"""
    answer = ask_gemini(
        prompt,
        image_bytes=image_bytes,
        mime_type=mime_type
    )

    history.append({
        "type": "Jewelry Recommendation",
        "details": f"Budget: ₹{budget} | Occasion: {occasion} | Style: {style}",
        "recommendation": answer
    })

    return templates.TemplateResponse(
        request=request,
        name="jewelry_result.html",
        context={
            "recommendation": answer,
            "budget": budget,
            "occasion": occasion,
            "style": style
        }
    )
@app.get("/history")
def show_history(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "history": history
        }
    )