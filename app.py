from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import httpx

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Mount a static directory in case you add CSS/JS later
app.mount("/static", StaticFiles(directory="static"), name="static")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = os.getenv(
    "OPENAI_API_URL",
    "https://api.openai.com/v1/chat/completions",
)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )


async def call_openai_chat(dish_name: str) -> dict:
    """
    Call an OpenAI-compatible Chat Completion endpoint.
    Default uses OpenAI's API shape.
    Returns a dict with {"ingredients": str, "recipe": str}.
    """
    if not OPENAI_API_KEY:
        # No key available — fall back to a local generator
        return generate_recipe_mock(dish_name)

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    prompt = (
        "You are a helpful chef assistant. Given the name of a dish, "
        "output two clearly labeled sections:\n"
        "Ingredients:\n- a newline separated list of ingredients\n\n"
        "Recipe:\n- a step-by-step recipe for how to prepare the dish.\n"
        f"Dish: {dish_name}\n\n"
        "Respond in JSON only with keys 'ingredients' and 'recipe'."
    )

    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 600,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(OPENAI_API_URL, json=data, headers=headers)
        resp.raise_for_status()
        body = resp.json()

    # Extract assistant text
    # This code expects the response to follow the chat completions shape
    assistant_text = ""
    if "choices" in body and len(body["choices"]) > 0:
        assistant_text = (
            body["choices"][0]
            .get("message", {})
            .get("content", "")
        )
    else:
        assistant_text = body.get("text", "")

    # Try to parse JSON from assistant_text
    try:
        import json

        parsed = json.loads(assistant_text)
        ingredients = parsed.get("ingredients", "")
        recipe = parsed.get("recipe", "")
        return {"ingredients": ingredients, "recipe": recipe}
    except Exception:
        # Fallback: place the raw assistant text into 'recipe'
        return {"ingredients": "", "recipe": assistant_text}


def generate_recipe_mock(dish_name: str) -> dict:
    """
    Simple heuristic fallback generator that produces ingredients and a recipe.
    Use this if you don't have an API key or prefer offline behavior.
    """
    name = dish_name.strip().title()
    ingredients = [
        "2 cups of main ingredient",
        "1 tbsp oil",
        "1 tsp salt",
        "1/2 cup water",
        "spices to taste",
    ]

    recipe_steps = [
        f"Prepare the ingredients for {name}.",
        "Heat the oil in a pan over medium heat.",
        "Add the main ingredient and cook for 5-7 minutes.",
        "Add water and simmer until cooked through.",
        "Adjust seasoning and serve hot.",
    ]

    return {
        "ingredients": "\n".join(ingredients),
        "recipe": "\n".join(recipe_steps),
    }


@app.post("/generate", response_class=HTMLResponse)
async def generate(request: Request, dish: str = Form(...)):
    # Call the AI (or fallback)
    try:
        result = await call_openai_chat(dish)
    except httpx.HTTPStatusError as e:
        # If API call fails, return an error page
        return templates.TemplateResponse(
            "result.html",
            {"request": request, "error": str(e), "dish": dish},
        )

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "dish": dish,
            "ingredients": result.get("ingredients"),
            "recipe": result.get("recipe"),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
