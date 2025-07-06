import streamlit as st
import pickle
import pandas as pd
import numpy as np
import requests
import os

from dotenv import load_dotenv
load_dotenv()

# ------------------- Helper Function ------------------- #
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {TMDB_API_KEY}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/original{poster_path}"
    except:
        pass

    return "https://placehold.co/600x900?text=No+Image"

# ------------------- Recommendation Function ------------------- #
def recommend(movie):
    try:
        idx = movie_df[movie_df['title'].str.lower() == movie.lower()].index[0]
    except IndexError:
        return [], []

    simscore = similarities[idx]
    similar_indices = simscore.argsort()[::-1]
    top_movies_index = [i for i in similar_indices if i != idx][:5]

    recommended_movies = movie_df.iloc[top_movies_index]['title'].tolist()
    recommended_ids = movie_df.iloc[top_movies_index]['id'].tolist()
    recommended_posters = [fetch_poster(movie_id) for movie_id in recommended_ids]

    return recommended_movies, recommended_posters

# ------------------- Load Data ------------------- #
movies = pickle.load(open('movies_dict.pkl', 'rb'))
movie_df = pd.DataFrame.from_dict(movies)
vectors = np.load('vectors.npy')
similarities = pickle.load(open('similarity.pkl', 'rb'))

# ------------------- Streamlit App ------------------- #
st.set_page_config(page_title="Popcorn Time", layout="wide")
left, middle, right = st.columns([1,8,1], vertical_alignment="center")
with middle:
    st.columns(3)[1].title('Popcorn Time')

selected_movie = st.selectbox(
    "Choose a Movie", index = None,
    options = movie_df['title'].values,
     placeholder='choose a movie title',
)

# CSS Animation Block
st.markdown("""
    <style>
    .poster-container {
        animation: slide-in 0.8s ease forwards;
        transform: translateY(-50px);
        opacity: 0;
    }
    @keyframes slide-in {
        0% {
            transform: translateY(-50px);
            opacity: 0;
        }
        100% {
            transform: translateY(0);
            opacity: 1;
        }
    }
    </style>
""", unsafe_allow_html=True)
left, middle, right = st.columns([1,3,1], vertical_alignment="center")
if middle.button("Watch More",use_container_width=True):
    names, posters = recommend(selected_movie)

    if names and posters:
        cols = st.columns(len(names))
        for i in range(len(names)):
            with cols[i]:
                st.markdown(
                    f"""
                    <div class="poster-container">
                        <img src="{posters[i]}" style="width:100%; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);" />
                        <p style="text-align:center; font-weight:bold;">{names[i]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.warning("Could not fetch recommendations.")
