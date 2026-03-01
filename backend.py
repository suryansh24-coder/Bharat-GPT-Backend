import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
# Note: install required packages: pip install flask flask-cors requests openai
import openai

app = Flask(__name__)
CORS(app) # Enable CORS for frontend requests

# ==========================================
# CONFIGURATION
# Insert your actual API keys here
# ==========================================
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "YOUR_SERPAPI_KEY_HERE")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")

openai.api_key = OPENAI_API_KEY

# Cache setup (Dict based for simple 10-minute cache)
CACHE = {}
CACHE_EXPIRY_SECONDS = 600  # 10 minutes

@app.route('/api/search', methods=['POST'])
def proxy_search():
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"error": "Missing query parameter"}), 400
        
        query = data.get('query').strip()
        
        # 1. Check Cache
        current_time = time.time()
        if query in CACHE:
            if current_time - CACHE[query]['timestamp'] < CACHE_EXPIRY_SECONDS:
                return jsonify(CACHE[query]['data'])
            else:
                del CACHE[query] # Expired

        # 2. Fetch from Search API (SerpAPI for Google Search)
        search_url = "https://serpapi.com/search.json"
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": 5
        }
        
        search_res = requests.get(search_url, params=params)
        
        if search_res.status_code != 200:
            return jsonify({
                "error": "Failed to fetch from Search API", 
                "details": "Ensure your SERPAPI_KEY is correct."
            }), 500
            
        search_data = search_res.json()
        organic_results = search_data.get('organic_results', [])
        
        if not organic_results:
            return jsonify({
                "status": "no_results",
                "message": "No verified results found for this query."
            })

        # 3. Extract logic
        top_results = []
        snippets_for_llm = []
        
        official_link = None
        wikipedia_link = None
        
        for idx, res in enumerate(organic_results[:5]):
            title = res.get('title', '')
            snippet = res.get('snippet', '')
            link = res.get('link', '')
            thumbnail = res.get('thumbnail', None)
            
            # Prioritize first non-wikipedia link as 'Official' if available initially
            if 'wikipedia.org' in link and not wikipedia_link:
                wikipedia_link = link
            elif not official_link and 'wikipedia.org' not in link:
                official_link = link

            top_results.append({
                "title": title,
                "snippet": snippet,
                "link": link,
                "thumbnail": thumbnail
            })
            snippets_for_llm.append(f"Source {idx+1}: {title}\nSnippet: {snippet}")

        # 4. Generate Summarized Answer ONLY from fetched snippets (No Hallucination)
        llm_prompt = (
            f"You are a strict and accurate search summarizer. Given the following search snippets fetched in real-time online, "
            f"write a brief, informative summary to answer the user's query.\n"
            f"STRICT RULE: Do NOT use ANY outside knowledge. Use ONLY the provided snippets. "
            f"If the snippets do not contain enough information to answer, state that you cannot verify the answer based on the search results.\n\n"
            f"User Query: {query}\n\n"
            f"Fetched Snippets:\n" + "\n\n".join(snippets_for_llm)
        )

        try:
            # We attempt chat completion if key exists
            if OPENAI_API_KEY and OPENAI_API_KEY != "YOUR_OPENAI_API_KEY_HERE":
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a precise search assistant. You only output truth from the provided snippets."},
                        {"role": "user", "content": llm_prompt}
                    ],
                    max_tokens=250,
                    temperature=0.1
                )
                llm_summary = response.choices[0].message.content.strip()
            else:
                # Fallback if OPENAI key is not configured, we manually just combine top snippets
                llm_summary = "API Key not configured. Using raw snippet: " + snippets_for_llm[0]
                
        except Exception as e:
             llm_summary = "An error occurred while building the summary using the LLM."

        # 5. Build final structured response
        final_result = {
            "status": "success",
            "query": query,
            "summary": llm_summary,
            "results": top_results,
            "official_link": official_link,
            "wikipedia_link": wikipedia_link
        }

        # Save to cache
        CACHE[query] = {
            'timestamp': current_time,
            'data': final_result
        }

        return jsonify(final_result)
        
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

if __name__ == '__main__':
    print("Starting Search Proxy Backend on port 5000...")
    app.run(port=5000, debug=True)
