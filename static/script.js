async function getRecommendations() {
  const ingredients = document.getElementById('ingredients').value.trim();
  const taste = document.getElementById('taste').value;
  const course = document.getElementById('course').value;
  const dietary = document.getElementById('dietary').value;

  if (!ingredients) {
    alert('Please enter at least one ingredient.');
    return;
  }

  const data = { ingredients, taste, course, dietary };

  try {
    const response = await fetch('/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const recommendations = await response.json();
    displayResults(recommendations, ingredients.split(',').map(i => i.trim()));
  } catch (error) {
    console.error('Error:', error);
    document.getElementById('results').innerHTML = '<p class="text-red-400 text-center">Something went wrong.</p>';
  }
}

function displayResults(recommendations, userIngredients) {
  const resultsDiv = document.getElementById('results');
  resultsDiv.innerHTML = '';

  if (!recommendations.length) {
    resultsDiv.innerHTML = '<p class="text-white text-center">No matching recipes found.</p>';
    return;
  }

  recommendations.forEach(recipe => {
    const card = document.createElement('div');
    card.className = 'bg-[#2f1f1f] p-6 mb-6 rounded-lg shadow-lg';

    card.innerHTML = `
      <h3 class="text-xl font-semibold text-[#fcefe6] mb-2">${recipe.name}</h3>
      <img src="${recipe.image_url}" alt="${recipe.name}" class="w-full h-48 object-cover rounded-md mb-4">
      <p class="text-[#d8c9c0] mb-2"><strong>Description:</strong> ${recipe.description}</p>
      <p class="text-[#d8c9c0] mb-2"><strong>Ingredients:</strong> ${recipe.ingredients_name}</p>
      <p class="text-[#d8c9c0] mb-2"><strong>Matched:</strong> ${recipe.matched_ingredients || 'None'}</p>
      <p class="text-[#d8c9c0] mb-2"><strong>Prep Time:</strong> ${recipe['prep_time (in mins)']} mins</p>
      <p class="text-[#d8c9c0]"><strong>Cook Time:</strong> ${recipe['cook_time (in mins)']} mins</p>
    `;
    
    resultsDiv.appendChild(card);
  });
}