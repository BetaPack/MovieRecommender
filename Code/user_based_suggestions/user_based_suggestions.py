import pandas as pd
import sys
import requests
import os

sys.path.append("../../")

OMDB_API_KEY = 'b726fa05'

def get_movie_info(title):
    index=len(title)-6
    url = f"http://www.omdbapi.com/?t={title[0:index]}&apikey={OMDB_API_KEY}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        res=response.json()
        if(res['Response'] == "True"):
            return res
        else:  
            return { 'Title': title, 'imdbRating':"N/A", 'Genre':'N/A',"Poster":"https://www.creativefabrica.com/wp-content/uploads/2020/12/29/Line-Corrupted-File-Icon-Office-Graphics-7428407-1.jpg"}
    else:
        return  { 'Title': title, 'imdbRating':"N/A",'Genre':'N/A', "Poster":"https://www.creativefabrica.com/wp-content/uploads/2020/12/29/Line-Corrupted-File-Icon-Office-Graphics-7428407-1.jpg"}


def suggest_movies(feedback_data, dataset):
    # Parse feedback data to categorize liked and disliked genres
    liked_genres = []
    disliked_genres = []

    for movie, feedback in feedback_data.items():
        genres = dataset.loc[dataset['title'] == movie, 'genres'].values[0].split('|')
        if feedback == 'Like':
            liked_genres.extend(genres)
        elif feedback == 'Dislike':
            disliked_genres.extend(genres)

    # Convert lists to sets for better performance in filtering
    liked_genres = set(liked_genres)
    disliked_genres = set(disliked_genres)

    # Filter the dataset: Recommend movies with liked genres but exclude disliked genres
    recommendations = dataset[dataset['genres'].apply(lambda g: bool(liked_genres & set(g.split('|'))) and not bool(disliked_genres & set(g.split('|'))))]
    recommended_list = recommendations.head(10).to_dict(orient='records')
    print("Recommended List Before Random Sampling: ", recommended_list)
    if not recommended_list:
        sampled_rows = dataset.sample(n=10)
        recommended_list = sampled_rows.to_dict(orient='records')
    print("Recommended List Post Random Sampling: ", recommended_list)    
    
    current_path = os.getcwd()
    data_path = os.path.abspath(os.path.join(current_path, "../.."))
    data_path = os.path.join(os.path.join(data_path, "data"), "enriched_movies.csv")
    enriched_dataset = pd.read_csv(data_path)
    enriched_dataset.fillna("NA", inplace=True)
    plot_dict = dict()
    cast_dict = dict()
    boxOffice_dict = dict()
    for movie_detail in recommended_list:
        movie_info = get_movie_info(movie_detail["title"])
        movie_detail["poster"] = movie_info["Poster"]
        movie_detail["genre"] = movie_info["Genre"]
        movie_detail["imdbRating"] = movie_info["imdbRating"]

        limit = len(movie_detail["title"])-7
        movie_name = movie_detail["title"][:limit]
        if movie_name in list(enriched_dataset["title"]):
            plot = str(enriched_dataset[enriched_dataset["title"]==movie_name]["plot"].values[0])
            cast = enriched_dataset[enriched_dataset["title"]==movie_name]["cast"].values[0]
            boxOffice = enriched_dataset[enriched_dataset["title"]==movie_name]["boxOffice"].values[0]

            plot = plot if isinstance(plot, str) else "NA"
            cast = cast if isinstance(cast, str) else "NA"
            boxOffice = boxOffice if isinstance(boxOffice, str) else "NA"

            movie_detail["plot"] = plot
            movie_detail["cast"] = cast
            movie_detail["boxOffice"] = boxOffice
    return recommended_list