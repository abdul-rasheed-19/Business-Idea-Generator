import os
import re
import pandas as pd

from google import genai
from dotenv import load_dotenv


# ==========================================
# 1. LOAD DATASET
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

csv_path = os.path.join(
    BASE_DIR,
    "dataset",
    "business_ideas.csv"
)

df = pd.read_csv(csv_path)


# ==========================================
# 2. EXTRACT BUDGET
# ==========================================

def extract_budget(user_input):

    text = user_input.lower()
    text = text.replace(",", "")
    text = text.replace("₹", "")

    numbers = re.findall(r"\d+", text)

    if not numbers:
        return None

    budget = int(numbers[0])

    if "lakh" in text:
        budget = budget * 100000

    return budget


# ==========================================
# 3. SEARCH AND RANK BUSINESS IDEAS
# ==========================================

def search_business_ideas(user_input):

    if user_input is None:
        return df.iloc[0:0].copy()

    user_input = user_input.lower().strip()
    results = df.copy()

    results["Score"] = 0

    # Category matching
    categories = [
        "technology",
        "fitness",
        "food",
        "marketing",
        "education",
        "travel",
        "photography",
        "design",
        "e-commerce",
        "agriculture",
        "real estate"
    ]

    for category in categories:

        if category in user_input:

            mask = (
                results["Category"]
                .astype(str)
                .str.lower()
                .str.contains(category, na=False)
            )

            results.loc[mask, "Score"] += 25
            break

    # Online / Offline matching
    if "online" in user_input:

        mask = (
            results["Mode"]
            .astype(str)
            .str.lower()
            .str.contains("online", na=False)
        )

        results.loc[mask, "Score"] += 20

    elif "offline" in user_input:

        mask = (
            results["Mode"]
            .astype(str)
            .str.lower()
            .str.contains("offline", na=False)
        )

        results.loc[mask, "Score"] += 20

    # Budget matching
    budget = extract_budget(user_input)

    if budget is not None:

        budget_mask = (
            (results["Budget_Min_INR"] <= budget)
            &
            (results["Budget_Max_INR"] >= budget)
        )

        results.loc[budget_mask, "Score"] += 30

    # Skill matching
    skills = [
        "python",
        "marketing",
        "sales",
        "design",
        "photography",
        "cooking",
        "teaching",
        "seo",
        "ai",
        "fitness"
    ]

    for skill in skills:

        if skill in user_input:

            skill_mask = (
                results["Skills_Required"]
                .astype(str)
                .str.lower()
                .str.contains(skill, na=False)
            )

            results.loc[skill_mask, "Score"] += 25

    # Sort by score
    results = results.sort_values(
        by="Score",
        ascending=False
    )

    return results.head(5)

# ==========================================
# 4. GEMINI SETUP
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found. "
        "Please check your .env file."
    )

client = genai.Client(api_key=api_key)


# ==========================================
# 5. GENERATE AI RESPONSE
# ==========================================

def generate_ai_response(
    user_message,
    recommendations,
    conversation_history
):

    # --------------------------------------
    # Prepare business information
    # --------------------------------------

    if recommendations.empty:

        business_context = (
            "No suitable business ideas were "
            "found in the dataset."
        )

    else:

        business_context = recommendations[
            [
                "Business_Name",
                "Category",
                "Budget_Min_INR",
                "Budget_Max_INR",
                "Skills_Required",
                "Mode",
                "Target_Audience",
                "Revenue_Model",
                "Difficulty",
                "Description",
                "Score"
            ]
        ].to_string(index=False)


    # --------------------------------------
    # Prepare conversation history
    # --------------------------------------

    history_text = ""

    for message in conversation_history:

        history_text += (
            f"{message['role']}: "
            f"{message['content']}\n"
        )


    # --------------------------------------
    # Gemini prompt
    # --------------------------------------

    prompt = f"""
You are an AI Business Mentor.

You are helping a user find and develop
business ideas.

Previous conversation:

{history_text}

Latest user message:

{user_message}

Business ideas found in the dataset:

{business_context}

Your job is to respond naturally and helpfully.

Rules:

1. Remember the previous conversation.
2. Understand follow-up questions.
3. Recommend suitable business ideas.
4. Explain why an idea matches the user.
5. Mention investment when relevant.
6. Mention required skills when relevant.
7. Mention the revenue model when relevant.
8. Do not invent dataset information.
9. Answer general business questions as a business mentor.
10. Keep the response clear and practical.
11. Do not repeat the entire previous response unnecessarily.

Speak like a friendly and practical business mentor.
"""


    # --------------------------------------
    # Send request to Gemini
    # --------------------------------------

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


# ==========================================
# 6. BUSINESS PLAN GENERATOR
# ==========================================

def generate_business_plan(
    user_message,
    recommendations,
    conversation_history
):

    # --------------------------------------
    # Prepare conversation history
    # --------------------------------------

    history_text = ""

    for message in conversation_history:

        history_text += (
            f"{message['role']}: "
            f"{message['content']}\n"
        )


    # --------------------------------------
    # Prepare dataset information
    # --------------------------------------

    if recommendations.empty:

        business_context = (
            "No new matching business idea "
            "was found."
        )

    else:

        business_context = recommendations[
            [
                "Business_Name",
                "Category",
                "Budget_Min_INR",
                "Budget_Max_INR",
                "Skills_Required",
                "Mode",
                "Target_Audience",
                "Revenue_Model",
                "Difficulty",
                "Description"
            ]
        ].to_string(index=False)


    # --------------------------------------
    # Business plan prompt
    # --------------------------------------

    prompt = f"""
You are an AI Business Mentor.

The user wants a practical business plan
for the business idea discussed in the conversation.

Previous conversation:

{history_text}

Latest user request:

{user_message}

Business information from the dataset:

{business_context}

Create a clear and practical business plan.

Use this structure:

# 📋 Business Plan

## 💡 1. Business Idea

## 🎯 2. Target Customers

## ❗ 3. Problem

## ✅ 4. Solution

## 💰 5. Investment

## 💵 6. Revenue Model

## 🛠️ 7. Required Skills

## 📢 8. Marketing Strategy

## ⚠️ 9. Challenges

## 📅 10. First 30 Days Action Plan

Rules:

1. Remember the previous conversation.
2. Understand which business idea the user means.
3. Use dataset information when available.
4. Do not invent dataset values.
5. Clearly identify general suggestions.
6. Keep the plan realistic.
7. Keep the explanation easy to understand.
8. Act like a friendly and practical business mentor.
"""


    # --------------------------------------
    # Send request to Gemini
    # --------------------------------------

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


# ==========================================
# 7. BUSINESS IDEA COMPARISON
# ==========================================

def generate_business_comparison(
    user_message,
    conversation_history
):

    # Prepare previous conversation
    history_text = ""

    for message in conversation_history:
        history_text += (
            f"{message['role']}: "
            f"{message['content']}\n"
        )

    prompt = f"""
You are an AI Business Mentor.

The user wants to compare business ideas that
were previously discussed in the conversation.

Previous conversation:
--------------------------------------
{history_text}
--------------------------------------

Current user request:
{user_message}

Compare the relevant business ideas from the
previous conversation.

Use this structure:

# 📊 Business Idea Comparison

| Factor | Idea 1 | Idea 2 |
|---|---|---|
| Business Name | | |
| Investment | | |
| Skills Required | | |
| Target Audience | | |
| Revenue Model | | |
| Difficulty | | |
| Mode | | |

## ⭐ Which One Is Better?

Explain which idea is more suitable and why.

## 🎯 Recommendation

Give a practical recommendation based on the
user's budget, skills and goals.

Rules:

1. Only compare ideas that were actually discussed.
2. Do not invent dataset values.
3. If a value is unavailable, say "Not specified".
4. Clearly identify estimates or general advice.
5. Keep the comparison practical and easy to understand.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text