from flask import Flask, render_template, request, jsonify
from joblib import load
import requests


app = Flask(__name__)

# Load the movie data and similarity matrix
movies = load('./movies.joblib')
similarity = load('./recommended.joblib')

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else None

def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(enumerate(similarity[index]), reverse=True, key=lambda x: x[1])
        recommended_movie_names = [movies.iloc[i[0]].title for i in distances[1:6]]
        recommended_movie_posters = [fetch_poster(movies.iloc[i[0]].movie_id) for i in distances[1:6]]
        return recommended_movie_names, recommended_movie_posters
    except IndexError:
        return [], []

@app.route('/', methods=['GET', 'POST'])
def home():
    recommended_movie_names, recommended_movie_posters = [], []
    if request.method == 'POST':
        selected_movie = request.form.get('movie')
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    movie_list = movies['title'].tolist()
    return render_template('index.html', movie_list=movie_list, recommendations=zip(recommended_movie_names, recommended_movie_posters))

if __name__ == '__main__':
    app.run(debug=True)
