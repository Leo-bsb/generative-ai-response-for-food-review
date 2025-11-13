# 🍽️ Food Review Reply AI 🚀

[![GitHub stars](https://img.shields.io/github/stars/leo-bsb/food-review-reply-ai?style=social)](https://github.com/leo-bsb/food-review-reply-ai/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Hugging Face Spaces](https://img.shields.io/badge/Deploy-Hugging%20Face%20Spaces-brightgreen)](https://huggingface.co/spaces/leo-bsb/bot-for-restaurant-reviews)
[![Twitter Follow](https://img.shields.io/twitter/follow/leo_bsb?style=social)](https://twitter.com/leo_bsb)

---

## Overview

**Food Review Reply AI** is an intelligent, end-to-end AI system that automatically generates personalized, empathetic, and context-aware responses to restaurant customer reviews — all in Brazilian Portuguese. It leverages cutting-edge generative AI and sentiment analysis to streamline customer service for restaurants, helping businesses engage authentically with their audience at scale.

Try it live on [Hugging Face Spaces](https://huggingface.co/spaces/leo-bsb/bot-for-restaurant-reviews).

---

## 🌟 Why This Project Matters

- **Customer Experience at Scale:** Automates meaningful and professional replies, saving hours of manual work.
- **Contextual Understanding:** Uses sentiment-aware prompts to tailor tone and content dynamically.
- **Language-Specific Excellence:** Optimized for Brazilian Portuguese with natural, fluent responses.
- **Real-World Impact:** Tested on authentic restaurant reviews for practical relevance.

---

## 🚀 Features

- **Sentiment Analysis:** Uses a multilingual BERT model to score reviews from 1 to 5 stars.
- **AI-Powered Text Generation:** Mistral-based model crafts professional responses tailored to sentiment.
- **Smart Categorization:** Classifies reviews into Positive (4-5 stars), Neutral (3 stars), or Negative (1-2 stars).
- **User-Friendly Interface:** Clean Gradio UI with quick examples, sentiment buttons, and one-click copy.
- **Real Dataset:** Built on actual restaurant reviews to ensure authenticity.
- **Robust API Integration:** Powered by Google Gemini with fallback and retry logic for reliability.

---

## 🧠 How It Works

1. **Input:** User submits a customer review in Portuguese.
2. **Sentiment Detection:** BERT model analyzes the text to assign a sentiment rating.
3. **Prompt Engineering:** Creates a sentiment-specific prompt to guide AI response tone.
4. **Response Generation:** Gemini-powered model generates a concise, empathetic reply.
5. **Output:** Displays sentiment label and the crafted response ready to be used.

---

## 🎯 Use Cases

- Restaurant managers automating reply workflows  
- Customer service teams accelerating feedback response  
- Data analysts monitoring customer sentiment trends  
- AI learners exploring practical NLP applications  

---

## 💻 Getting Started

### Prerequisites

- Python 3.9+
- Google API key for Gemini model:  
  Get it here ➡️ [Google AI Studio](https://makersuite.google.com/app/apikey)

### Installation

```bash
git clone https://github.com/leo-bsb/food-review-reply-ai.git
cd food-review-reply-ai
pip install -r requirements.txt
export GOOGLE_API_KEY="your_google_api_key_here"
python app.py
