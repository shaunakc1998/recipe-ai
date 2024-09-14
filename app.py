import streamlit as st
import json
import re
from sentence_transformers import SentenceTransformer
import anthropic
from pinecone import Pinecone, ServerlessSpec

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-MPNet-base-v2')

# Set your API keys (replace with your actual keys)
claude_api_key = "your-anthropic-api-key"
pinecone_api_key = "your-pinecone-api-key"

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=claude_api_key)

# Initialize the Pinecone client
pc = Pinecone(api_key=pinecone_api_key)

# Connect to or create the Pinecone index
index_name = "your-index-name"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,  # Adjust based on your embedding dimension
        metric="cosine",  # You can use other metrics like euclidean
        spec=ServerlessSpec(cloud="gcp", region="us-west1")
    )

# Connect to the existing Pinecone index
index = pc.Index(index_name)

# Function to validate user input
def validate_input(user_input):
    required_fields = ["mood", "cuisine", "season"]
    for field in required_fields:
        if not user_input.get(field):
            st.error(f"Error: {field} is required")
            return False
    return True

# Function to query Pinecone for similar recipes
def query_pinecone(user_input):
    input_text = f"{user_input['mood']} {user_input['cuisine']} {user_input['season']}"
    input_embedding = model.encode(input_text).tolist()

    results = index.query(
        vector=input_embedding,
        top_k=10,
        include_metadata=True
    )

    return results['matches']

# Function to combine user input with Pinecone matches
def combine_input_with_matches(user_input, matches):
    combined_text = (
        f"Mood: {user_input['mood']}. "
        f"Cuisine: {user_input['cuisine']}. "
        f"Season: {user_input['season']}.\n\n"
        f"Similar Recipes: \n"
    )
    if not matches:
        combined_text += "No similar recipes found."
    else:
        for match in matches:
            metadata = match.get('metadata', {})
            combined_text += (
                f"- Recipe Name: {metadata.get('recipe_name', 'N/A')}, "
                f"Ingredients: {metadata.get('ingredients', 'N/A')}, "
                f"Preparation Time: {metadata.get('prep_time', 'N/A')}\n"
            )

    return combined_text

# Function to generate recipes using Claude
# Function to generate recipes using Claude
def generate_recipe_kit(combined_input):
    input_text = (
        f"The following is the user-provided information, including their mood, cuisine preference, season, and similar recipe matches from the database:\n\n"
        f"{combined_input}\n\n"
        "Based on this information, please provide a detailed and structured response with the following sections:\n\n"
        
        "- Recommend 3 distinct recipes that align well with the mood, cuisine preferences, and season provided by the user.\n"
        "- For each recipe, explain why it is a good fit for the specific mood, cuisine, and season. Focus on how the ingredients and preparation style relate to these factors.\n\n"
        
        "- For each suggested recipe, provide a list of essential ingredients. Include items that contribute to the mood (e.g., comforting, energizing, festive) and are seasonal (e.g., fresh, warming).\n"
        "- Format the ingredients in a clean, bullet-point list so they are easy to read and follow.\n\n"
        
        "- For each recipe, give a realistic estimate of how long it will take to prepare and cook.\n"
        "- Note any steps that may take extra time, and suggest quicker options for busy days or more elaborate meals for celebrations or leisurely cooking.\n\n"
        
        "- Provide a clear, step-by-step guide for preparing and cooking each recipe.\n"
        "- The instructions should be numbered and concise, but detailed enough to follow easily.\n"
        "- If possible, offer any additional tips or techniques (e.g., ways to enhance flavors, seasonal ingredient swaps, or ways to make the dish healthier or more indulgent based on the user’s mood).\n\n"
        
        "- Offer optional tips for each recipe, such as possible side dishes or serving suggestions.\n"
        "- Mention any seasonal or mood-based enhancements, such as adding comfort with a warm sauce or lightening a dish with fresh herbs or citrus.\n"
    )

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1500,
            temperature=0.7,
            messages=[{"role": "user", "content": input_text}]
        )

        # Return the response as-is, we'll format it before displaying
        return response.content[0].text.strip()

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None


# Function to format recipes output
def format_recipes_output(output_text):
    # Split the output text into sections based on your required structure
    sections = re.split(r'###', output_text)  # Split using '###' to find the headers
    
    formatted_recipes = ""
    
    for section in sections:
        section = section.strip()  # Remove any leading/trailing spaces
        
        if "" in section:
            # Handle the Recipe Suggestions
            formatted_recipes += f"### Recipe Name\n{section}\n\n"
        
        elif "" in section:
            # Handle the Ingredients section
            formatted_recipes += f"### Ingredients\n{section}\n\n"
        
        elif "" in section:
            # Handle the Preparation Time section
            formatted_recipes += f"### Preparation Time\n{section}\n\n"
        
        elif "" in section:
            # Handle the Cooking Method section
            formatted_recipes += f"### Cooking Method\n{section}\n\n"
    
    return formatted_recipes

# Streamlit app
def app():
    # App Title and Description
    st.markdown("<h1 style='text-align: center; color: #FFA500;'>AI-Driven Recipe Generator</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center;'>Input your mood, preferred cuisine, and season, and get personalized recipes generated just for you!</p>",
        unsafe_allow_html=True
    )

    # Section Divider
    st.markdown("<hr style='border: 1px solid #FFA500;'>", unsafe_allow_html=True)

    # Input Fields with Icon for Mood
    mood = st.text_input("Enter your mood (e.g., Happy, Comforting)", placeholder="E.g., Happy, Comforting", help="Tell us how you're feeling!")
    cuisine = st.text_input("Enter your preferred cuisine (e.g., Italian, Indian)", placeholder="E.g., Italian, Indian", help="Choose your favorite cuisine.")
    season = st.selectbox("Select the season:", ["Winter", "Spring", "Summer", "Fall"])

    # Aesthetic Generate Button
    if st.button("🍽 Generate Recipe Kit"):
        # Add a progress spinner while generating the kit
        with st.spinner("Generating your personalized recipe kit..."):
            # Prepare user input
            user_input = {
                "mood": mood,
                "cuisine": cuisine,
                "season": season
            }

            # Validate input
            if validate_input(user_input):
                # Query Pinecone for similar recipes
                matches = query_pinecone(user_input)

                # Combine user input with Pinecone matches
                combined_input = combine_input_with_matches(user_input, matches)

                # Generate the recipe kit using Claude
                generated_output = generate_recipe_kit(combined_input)

                if generated_output:
                    # Format the recipes by splitting them and ensuring proper markdown
                    formatted_output = format_recipes_output(generated_output)

                    # Display the generated recipe suggestions in a collapsible section
                    with st.expander("🍳 Your Personalized Recipe Kit", expanded=True):
                        # Use uniform font and formatting for all sections
                        st.markdown(formatted_output, unsafe_allow_html=True)

    # Footer and Credits
    st.markdown("<hr style='border: 1px solid #FFA500;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Powered by AI • Made with 💖 for food lovers</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    app()
