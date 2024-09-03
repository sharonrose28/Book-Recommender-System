import streamlit as st
import random

def set_current_book(isbn):
    st.session_state['current_book_isbn'] = isbn

def set_current_user(user_id):
    st.session_state['current_user_id'] = user_id

def update_friend_list(friends_list):
    st.session_state['friend_list'] = friends_list

def display_book(column, book_info):
    with column:
        st.button('📚', key=random.random(), on_click=set_current_book, args=(book_info['ISBN'],))
        st.image(book_info['Image-URL-M'], use_column_width=True)
        st.caption(book_info['Book-Title'])

def show_recommendations(book_df):
    num_items = book_df.shape[0]
    if num_items > 0:
        columns = st.columns(num_items)
        book_items = book_df.to_dict(orient='records')
        list(map(display_book, columns, book_items))

def handle_invalid_credentials():
    st.sidebar.error('Invalid User ID! Please try again.')

def greet_new_user():
    st.sidebar.success('Welcome to BookCrossing! Start reading to get personalized recommendations..')

def friend_already_added():
    st.sidebar.info('This user is already in your friend list.')

def friend_not_found_message():
    st.sidebar.error('User not found. Please enter a valid User ID.')

