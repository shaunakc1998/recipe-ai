# AI Driven Recipe Generator
An AI-driven recipe generator that recommends personalized recipes based on your mood, cuisine preference, and season, leveraging Pinecone and Claude AI.

## Project Overview
This project combines multiple AI services to create a seamless brand identity generation process:
- **Streamlit** is used to build an intuitive user interface that allows users to input their brand details.
- **Anthropic's Claude** generates personalized recipe kits, including mood-based recipe recommendations, ingredients, and preparation steps based on user input and seasonal preferences.
- **Pinecone**  is used to find similar recipes through vector similarity search, offering suggestions based on mood, cuisine, and season preferences.

The tool outputs:
- **Recipe suggestions** tailored to your mood, cuisine, and season.
- A list of **essential ingredients** with seasonal and mood-based explanations.
- Estimated **preparation time** for each recipe.
- A detailed, step-by-step **cooking method** with optional tips and serving suggestions.

## How It Works
1. **User Inputs**: The user provides details such as their mood, preferred cuisine, and season.
2. **AI-Powered Recipe Generation**: The system uses AI models (Claude by Anthropic) to generate personalized recipe suggestions, including ingredients, preparation steps, and cooking methods based on the user input.
3. **Recipe Similarity Search**: Pinecone is used to find and display similar recipes using vector similarity, helping the user explore options that fit their mood and preferences.
4. **Detailed Recipe Kit**: The tool outputs detailed recipes with ingredient lists, preparation time estimates, and mood-based explanations for each dish.

### Features
- **Custom Logo Generation**: Automatically generate logos based on your brand's identity and industry using OpenAI's DALL-E.
- **Brand Kit Creation**: Get recommendations on color schemes, fonts, and taglines based on the personality and industry of your brand.
- **Brand Similarity Search**: Compare your brand with similar ones in the market using Pinecone's vector search.
- **Intuitive UI**: A clean, user-friendly interface built with Streamlit makes the process easy and interactive.
