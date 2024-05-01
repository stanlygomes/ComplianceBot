from flask import Flask, render_template, jsonify
import random

app = Flask(__name__, static_folder='img')

# Sample data with corresponding widget types and image paths
# Sample data with corresponding widget types and image paths
sample_data = [
    {"title": "News Highlights", "content": "News Highlights", "widget": "image", "image_path": "/img/actual-news.png"},
    {"title": "News", "content": "Powell", "widget": "image", "image_path": "/img/sample-highlight-image.png"},
    {"title": "Wolfy Chatbot", "content": "new wolfy chatbot", "widget": "chatbot", "image_path": "/img/tools.jpg"},

    
    {"title": "Market", "content": "Market Watch", "widget": "image", "image_path": "/img/market.png"}
]


# Route to display the grid
@app.route('/')
def display_grid():
    
    # Reshape the data into a 3x3 grid
    grid_data = [sample_data[i:i+3] for i in range(0, len(sample_data), 3)]
    return render_template('grid.html', grid_data=grid_data)

# Route to serve the chatbot HTML file
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')


# Route to fetch initial chatbot content
@app.route('/initial_content')
def get_initial_content():
    # Sample initial content for the chatbot
    initial_content = [
        {"content": "Welcome to our chatbot!", "widget": "chatbot"},
        {"content": "It's tax season, do you know our policies for compliance?", "widget": "chatbot"}
    ]
    return jsonify(initial_content)


if __name__ == '__main__':
    app.run(debug=True)
