from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from pinecone import Pinecone
from groq import Groq
import os

# Initialize Flask with explicit template folder path
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)

# Load environment variables
load_dotenv()

# Initialize clients
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
groq_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_key)
dense_index = pc.Index("researcher")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query')
    
    results = dense_index.search(
        namespace="Research",
        query={
            "top_k": 4,
            "inputs": {
                'text': query
            }
        }
    )

    prompt = f"You are to assume you are an individual who connects passionate high school students to world class researchers. Assume after this prompt you are talking to a student, just state your answer no filler and pretend your talking to the student which the query for this student is {query} and your options are {results}. Pick the best researcher, not research paper, but best researcher to match a students interest, and give reasoning why this researcher is a great fit"
    
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.3-70b-versatile",
        stream=False,
    )

    return jsonify({'result': chat_completion.choices[0].message.content})

if __name__ == '__main__':
    app.run(debug=True)





