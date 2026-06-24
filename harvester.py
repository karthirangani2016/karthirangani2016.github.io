import requests
import os
import sys

KNOWLEDGE_FILE = "knowledge/general.txt"

def harvest(topic):
    print(f"[*] SEA is researching: {topic}...")
    
    # Wikipedia requires a User-Agent header
    headers = {
        'User-Agent': 'SeaHarvester/1.0 (karthikeya@example.com)'
    }
    
    formatted_topic = topic.strip().title().replace(' ', '_')
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_topic}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            summary = data.get('extract', "I couldn't find a clear summary, Sir.")
            title = data.get('title', topic)
            
            # Clean up the summary (limit to first two sentences for speed)
            sentences = summary.split('. ')
            short_summary = ". ".join(sentences[:2])
            if not short_summary.endswith('.'): short_summary += '.'

            # Format for the Neural Brain (Question / Answer)
            question = f"What is {title}?"
            answer = short_summary.replace("\n", " ") 
            
            # Append to knowledge
            with open(KNOWLEDGE_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n{question}\n{answer}\n")
            
            print(f"[+] Knowledge acquired: {title}")
        else:
            print(f"[-] Research failed. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"[!] Error during research: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
        harvest(topic)
    else:
        print("Usage: python3 harvester.py [Topic Name]")
