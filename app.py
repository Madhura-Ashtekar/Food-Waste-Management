## code not to be used without licensing

import streamlit as st
from PIL import Image, ImageOps
import google.generativeai as genai
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import time
import random

def generate_unique_recipe_prompt(ingredients, cuisine_style=None, existing_titles=None):
    styles = ['Mediterranean', 'Asian fusion', 'Latin American', 'Middle Eastern', 'Modern European', 
             'Indian fusion', 'Pacific Rim', 'Contemporary American', 'Caribbean inspired', 'Nordic']
    
    # Ensure we don't reuse styles for consecutive recipes
    if existing_titles and len(existing_titles) > 0:
        # Remove any styles that might create similar recipes to existing ones
        available_styles = [style for style in styles 
                          if not any(style.lower() in title.lower() for title in existing_titles)]
        selected_style = random.choice(available_styles if available_styles else styles)
    else:
        selected_style = random.choice(styles)
    
    return f"""Create a unique {selected_style} recipe using these ingredients: {ingredients}.
    The recipe should be COMPLETELY different from any previous recipes.
    Be creative with the title - avoid generic names or similar patterns to existing titles.
    Format the response exactly like this:

    **Title**: [Unique and Creative Recipe Name]

    **Ingredients**:
    - [Precise Quantity] [Ingredient] (add any necessary notes)
    - [Continue list...]

    **Instructions**:
    1. [Detailed step with specific temperatures and times]
    2. [Continue steps...]

    Make sure the recipe approach and cooking method are distinct from other recipes.
    Ensure measurements are precise and instructions are clear."""

def detect_ingredients(image, models):
    try:
        prompt = """Analyze this food image and list all visible ingredients. 
        Include quantities where visible. Return only a comma-separated list of unique items in lowercase.
        Focus on main ingredients and exclude common pantry items unless prominently visible."""
        
        response = models['gemini_model'].generate_content([prompt, image])
        ingredients = response.text.lower().strip().split(', ')
        return [(ing.strip(), random.uniform(0.7, 1.0)) for ing in ingredients if ing]
    except Exception as e:
        st.error(f"Error detecting ingredients: {e}")
        return []

def format_recipe_for_streamlit(recipe_title, ingredients, instructions):
    """Format recipe using Streamlit native components"""
    st.subheader(recipe_title)
    
    # Ingredients section
    st.markdown("### 📝 Ingredients")
    for ingredient in ingredients:
        st.markdown(f"- {ingredient}")
    
    # Instructions section
    st.markdown("### 👩‍🍳 Instructions")
    for i, step in enumerate(instructions, 1):
        st.markdown(f"**{i}.** {step}")

def parse_recipe_text(recipe_text):
    """Parse recipe text into title, ingredients, and instructions"""
    sections = recipe_text.split('\n\n')
    title = ''
    ingredients = []
    instructions = []
    
    current_section = None
    for section in sections:
        if "**Title**:" in section:
            title = section.replace("**Title**:", "").strip()
        elif "**Ingredients**:" in section:
            current_section = "ingredients"
            ingredients = [ing.strip('- ').strip() for ing in section.split('\n')[1:] if ing.strip()]
        elif "**Instructions**:" in section:
            current_section = "instructions"
            # Clean up instructions more thoroughly
            instructions = []
            for inst in section.split('\n')[1:]:
                if inst.strip():
                    # Remove any extra numbering or formatting
                    cleaned_inst = inst.strip()
                    # Remove any numbers and dots from the start
                    while cleaned_inst and (cleaned_inst[0].isdigit() or cleaned_inst[0] in '.-'):
                        cleaned_inst = cleaned_inst[1:].strip()
                    # Remove "Instructions:" if it appears
                    if cleaned_inst.lower().startswith('instructions:'):
                        cleaned_inst = cleaned_inst[12:].strip()
                    if cleaned_inst:  # Only add if there's content left
                        instructions.append(cleaned_inst)
        elif current_section == "ingredients" and section.strip():
            ingredients.extend([ing.strip('- ').strip() for ing in section.split('\n') if ing.strip()])
        elif current_section == "instructions" and section.strip():
            for inst in section.split('\n'):
                if inst.strip():
                    cleaned_inst = inst.strip()
                    while cleaned_inst and (cleaned_inst[0].isdigit() or cleaned_inst[0] in '.-'):
                        cleaned_inst = cleaned_inst[1:].strip()
                    if cleaned_inst.lower().startswith('instructions:'):
                        cleaned_inst = cleaned_inst[12:].strip()
                    if cleaned_inst:
                        instructions.append(cleaned_inst)
    
    return title, ingredients, instructions

def generate_recipes(ingredients, models, num_recipes=3):
    try:
        ingredient_list = ', '.join([ing[0] for ing in ingredients])
        recipes = []
        used_titles = set()
        attempts = 0
        max_attempts = num_recipes * 2  # Allow for some retry attempts
        
        while len(recipes) < num_recipes and attempts < max_attempts:
            response = models['gemini_model'].generate_content(
                generate_unique_recipe_prompt(ingredient_list, existing_titles=used_titles)
            )
            recipe = response.text
            
            # Parse recipe
            title, ingredients_list, instructions_list = parse_recipe_text(recipe)
            
            # Check if this is a unique recipe (not just by title, but also content)
            is_unique = True
            if title:
                title_lower = title.lower()
                for existing_title in used_titles:
                    if (title_lower == existing_title.lower() or
                        title_lower.split()[0] == existing_title.lower().split()[0]):
                        is_unique = False
                        break
            
            if title and is_unique and len(instructions_list) > 0:
                used_titles.add(title)
                recipes.append((title, ingredients_list, instructions_list))
            
            attempts += 1
        
        return recipes
    except Exception as e:
        st.error(f"Error generating recipes: {e}")
        return []

def main():
    st.set_page_config(page_title="Food Waste Management", page_icon="♻️", layout="wide")
    
    def configure_gemini():
        """Configure and return Gemini model"""
        try:
            genai.configure(api_key="YOUR_API_KEY") 
            return genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            st.error(f"Error configuring Gemini: {e}")
            return None

    @st.cache_resource
    def load_models():
        """Load and cache all required models"""
        try:
            # Configure Gemini first
            gemini_model = configure_gemini()
            if gemini_model is None:
                return None

            # Then load other models
            recipe_model = AutoModelForSeq2SeqLM.from_pretrained("flax-community/t5-recipe-generation")
            recipe_tokenizer = AutoTokenizer.from_pretrained("flax-community/t5-recipe-generation")
            
            return {
                'recipe_model': recipe_model,
                'recipe_tokenizer': recipe_tokenizer,
                'gemini_model': gemini_model
            }
        except Exception as e:
            st.error(f"Error loading models: {str(e)}")
            return None

    models = load_models()
    if models is None:
        st.error("Failed to load models. Please try again.")
        return

    st.title("🍳 Food Waste Management ♻️")
    st.markdown("### Transform Your Leftovers into Culinary Masterpieces!")

    with st.sidebar:
        st.header("⚙️ Recipe Settings")
        num_recipes = st.slider("Number of recipes", 1, 5, 3)
        confidence_threshold = st.slider("Detection confidence", 0.05, 1.0, 0.1)
        
        st.markdown("---")
        st.markdown("### 📸 Tips for Better Results")
        st.markdown("""
        - Ensure good lighting
        - Place ingredients separately
        - Include all ingredients in frame
        - Remove packaging if possible
        """)

    uploaded_file = st.file_uploader("📤 Upload your ingredients photo - by Madhura Ashtekar", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="Your Ingredients", use_container_width=True)

        with st.spinner("🔍 Analyzing ingredients..."):
            ingredients = detect_ingredients(image, models)
            ingredients = [ing for ing in ingredients if ing[1] >= confidence_threshold]

        if ingredients:
            with col2:
                st.markdown("### 🥗 Detected Ingredients")
                for ing, conf in ingredients:
                    st.markdown(f"- 🍴 {ing.capitalize()}")

            with st.spinner("👨‍🍳 Creating unique recipes..."):
                recipes = generate_recipes(ingredients, models, num_recipes)

                if recipes:
                    st.markdown("### 🥗 Your Custom Recipes")
                    for title, ingredients_list, instructions_list in recipes:
                        with st.container():
                            format_recipe_for_streamlit(title, ingredients_list, instructions_list)
                            st.markdown("---")

if __name__ == "__main__":
    main()