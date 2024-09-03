import streamlit as st
import pandas as pd
import template as t
import random

# Set page configuration
st.set_page_config(layout="wide")

# Load datasets
books_df = pd.read_csv('data/BX-Books.csv', sep=';', encoding='latin-1')
ratings_df = pd.read_csv('data/BX-Book-Ratings-Subset.csv', sep=';', encoding='latin-1')
users_df = pd.read_csv('data/BX-Users.csv', sep=';', encoding='latin-1')

# Initialize session state
if 'current_book_isbn' not in st.session_state:
    st.session_state['current_book_isbn'] = '0385486804'

if 'current_user_id' not in st.session_state:
    st.session_state['current_user_id'] = 98783

if 'friend_list' not in st.session_state:
    st.session_state['friend_list'] = [277427, 278026, 277523, 276680]


# Main content
st.title("Welcome to Book Recommender")

st.markdown("Explore book recommendations based on your reading history, friends' choices, and similar interests.")


# Display consent message
if 'consent_given' not in st.session_state:
    st.info('By using this app, you consent to our data handling practices. We comply with GDPR regulations.')
    if st.button("I Agree"):
        st.session_state['consent_given'] = True

# Book recommendation section
selected_book_df = books_df[books_df['ISBN'] == st.session_state['current_book_isbn']]
col1, col2 = st.columns([3, 5])

with col1:
    st.image(selected_book_df['Image-URL-L'].values[0], use_column_width=True)

with col2:
    st.header(selected_book_df['Book-Title'].values[0])
    st.subheader(f"Author: {selected_book_df['Book-Author'].values[0]}")
    st.caption(f"Published: {selected_book_df['Year-Of-Publication'].values[0]} | Publisher: {selected_book_df['Publisher'].values[0]}")

# Display recommendations based on user’s reading history
st.subheader('Explore More Books by Your Favorite Authors')
user_books = ratings_df[ratings_df['User-ID'] == st.session_state['current_user_id']].merge(books_df, on='ISBN')
favorite_authors = user_books['Book-Author'].unique()
recommended_books = books_df[books_df['Book-Author'].isin(favorite_authors) & ~books_df['Book-Title'].isin(user_books['Book-Title'])].sample(10)
t.show_recommendations(recommended_books)

# Display recommendations based on friends’ reading
st.subheader('Books Trending Among Your Friends')
friends_books = ratings_df[ratings_df['User-ID'].isin(st.session_state['friend_list'])].merge(books_df, on='ISBN')
trending_books = friends_books.drop_duplicates(subset=['Book-Title']).sample(10)
t.show_recommendations(trending_books)

# Display recommendations based on similar book ratings
st.subheader('Books Loved by Similar Readers')
book_ratings_group = ratings_df.groupby('ISBN')['User-ID'].apply(list).to_dict()
selected_book_users = book_ratings_group.get(st.session_state['current_book_isbn'], [])
similar_books = []

for isbn, users in book_ratings_group.items():
    if isbn != st.session_state['current_book_isbn']:
        intersection = set(selected_book_users) & set(users)
        union = set(selected_book_users) | set(users)
        jaccard_similarity = len(intersection) / len(union)
        if 0 < jaccard_similarity < 0.5:
            similar_books.append((isbn, jaccard_similarity))

similar_books_df = pd.DataFrame(similar_books, columns=['ISBN', 'Jaccard Similarity']).sort_values(by='Jaccard Similarity', ascending=False).head(10)
similar_books_df = books_df[books_df['ISBN'].isin(similar_books_df['ISBN'])]
t.show_recommendations(similar_books_df)

# About us section
st.subheader('About Book Recommender')
st.write("Book Recommender connects readers worldwide, offering personalized book recommendations based on your reading history, friends' activities, and shared interests. If no friends are added, the system initializes your list with four User-IDs: [277427, 278026, 277523, 276680]. Discover books loved by others with similar tastes.")
# Sidebar for user interactions
st.sidebar.header('User Interaction')
user_id_input = st.sidebar.text_input("Enter User-ID", placeholder="e.g., 98783")
if st.sidebar.button("Log In"):
    if user_id_input.isdigit() and int(user_id_input) in ratings_df['User-ID'].unique():
        t.set_current_user(int(user_id_input))
        st.sidebar.success('Successfully logged in!')
    else:
        t.handle_invalid_credentials()

friend_id_input = st.sidebar.text_input("Add a Friend", placeholder="e.g., 277427")
if st.sidebar.button("Add Friend"):
    if friend_id_input.isdigit():
        friend_id = int(friend_id_input)
        if friend_id not in st.session_state['friend_list']:
            if friend_id in ratings_df['User-ID'].unique():
                st.session_state['friend_list'].append(friend_id)
                t.update_friend_list(st.session_state['friend_list'])
                t.friend_already_added()
            else:
                t.friend_not_found_message()
        else:
            t.friend_already_added()
    else:
        t.friend_not_found_message()
