# Food-Waste-Management 🍳♻️
A web application that helps reduce food waste by generating creative recipes from ingredients you already have using gemini vision (flash 1.5) and streamlit

![shutterstock_611209640-scaled-e1663877375117](https://github.com/user-attachments/assets/3c8614d3-c0ec-4436-907c-c4c67593f916)


**Features**

- Ingredient detection from images using Google's Gemini Vision model
- Multiple unique recipe generation with diverse cuisine styles
- Simple and intuitive user interface
- Real-time recipe creation with step-by-step instructions

**Dependencies**

streamlit
google-generativeai
transformers
Pillow
torch

**Usage**

- Upload a photo of your ingredients
- The app detects ingredients automatically
- Select number of recipes (1-5)
- Get unique recipes with ingredients and instructions


<img width="1384" alt="Screenshot 2025-01-28 at 4 59 13 PM" src="https://github.com/user-attachments/assets/ce63f50f-bc44-4f30-8612-8402c0a73577" />


<img width="1359" alt="Screenshot 2025-01-28 at 4 12 32 PM" src="https://github.com/user-attachments/assets/ed006265-d865-4613-a434-a11d3291eabb" />


<img width="1012" alt="Screenshot 2025-01-28 at 4 12 44 PM" src="https://github.com/user-attachments/assets/5c3d20dd-ce19-4a62-ba55-820e555a9274" />


**Technical Details**

Uses Gemini Vision API for ingredient detection
Implements recipe diversity algorithm to ensure unique recipes
Caches models for improved performance
Handles various image formats (JPG, JPEG, PNG)

**Contributing**

Feel free to open issues and submit pull requests.

**License**

MIT License
