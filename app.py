from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

DATASET_PATH = r"D:\RECIPE_RECOMMENDER\AITRAINX_DATASET.csv"

try:
    df = pd.read_csv(DATASET_PATH)
    print(f"Dataset loaded successfully. Rows: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Sample ingredients_name: {df['ingredients_name'].head().tolist()}")
except Exception as e:
    print(f"Error loading dataset: {e}")
    df = pd.DataFrame()

df['ingredients_name'] = df['ingredients_name'].fillna('')
df['ingredients_processed'] = df['ingredients_name'].apply(lambda x: ' '.join(x.lower().split(',')))
df['ingredients_list'] = df['ingredients_name'].apply(lambda x: [i.strip().lower() for i in str(x).split(',')] if pd.notna(x) and x else [])

tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(df['ingredients_processed']).toarray()
print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")

def calculate_ingredient_overlap(user_ingredients, recipe_ingredients):
    user_set = set(ing.lower().strip() for ing in user_ingredients)
    recipe_set = set(ing.lower().strip() for ing in recipe_ingredients)
    return len(user_set.intersection(recipe_set))

def recommend_recipes(available_ingredients, constraints):
    user_ingredients = [ing.lower().strip() for ing in available_ingredients if ing.strip()]
    if not user_ingredients:
        return []

    user_input = ' '.join(user_ingredients)
    user_vector = tfidf.transform([user_input]).toarray()

    similarity_scores = cosine_similarity(user_vector, tfidf_matrix)[0]
    df['similarity'] = similarity_scores
    df['overlap'] = df['ingredients_list'].apply(lambda x: calculate_ingredient_overlap(user_ingredients, x))
    
    df['matched_ingredients'] = df['ingredients_list'].apply(
        lambda x: ', '.join(sorted(set(user_ingredients).intersection(set(x))))
    )
    
    candidate_df = df[df['overlap'] > 0]

    taste = constraints.get('taste', '').lower()
    if taste:
        taste_keywords = {
            'sweet': ['sugar', 'honey', 'chocolate'],
            'sour': ['lemon', 'vinegar', 'lime'],
            'spicy': ['chili', 'pepper', 'paprika']
        }
        keywords = taste_keywords.get(taste, [])
        taste_filtered = candidate_df[candidate_df['ingredients_name'].str.contains('|'.join(keywords), case=False, na=False)]
        if len(taste_filtered) >= 3:
            candidate_df = taste_filtered
        print(f"After taste filter ({taste}): {len(candidate_df)} recipes")

    if 'course' in constraints and constraints['course']:
        candidate_df = candidate_df[candidate_df['course'].str.lower() == constraints['course'].lower()]
    
    if 'dietary' in constraints and constraints['dietary']:
        if constraints['dietary'] == 'vegetarian':
            candidate_df = candidate_df[~candidate_df['ingredients_name'].str.contains('fish|chicken|prawns', case=False, na=False)]
        elif constraints['dietary'] == 'non-vegetarian':
            candidate_df = candidate_df[candidate_df['ingredients_name'].str.contains('fish|chicken|prawns', case=False, na=False)]

    if len(candidate_df) < 3:
        candidate_df = df[df['overlap'] > 0]
    
    top_recipes = candidate_df.sort_values(['overlap', 'similarity'], ascending=[False, False]).head(3)
    return top_recipes[['name', 'description', 'ingredients_name', 'overlap', 'image_url', 'prep_time (in mins)', 'cook_time (in mins)', 'matched_ingredients']].to_dict('records')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    data = request.json
    available_ingredients = data.get('ingredients', '').split(',')
    constraints = {
        'max_time': data.get('max_time', ''),
        'course': data.get('course', ''),
        'dietary': data.get('dietary', ''),
        'taste': data.get('taste', '')
    }
    recommendations = recommend_recipes(available_ingredients, constraints)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True, port=5000)