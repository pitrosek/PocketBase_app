from flask import Flask, jsonify, request, render_template_string
import requests

app = Flask(__name__)

POCKETBASE_API = 'http://127.0.0.1:8090/api/collections'

@app.route('/')
def index():
    # Získání kolekcí z PocketBase
    try:
        r = requests.get(POCKETBASE_API)
        r.raise_for_status()
        collections = r.json().get('items', [])
    except Exception as e:
        collections = []
    
    # Jednoduchý HTML dashboard
    html = '''
    <html>
    <head>
    <title>PocketBase Manager</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6fa; margin: 0; padding: 0; }
        .container { max-width: 700px; margin: 40px auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 12px #0001; padding: 32px; }
        h1 { color: #2d3a4a; margin-bottom: 8px; }
        h2 { color: #4a5a6a; margin-top: 32px; }
        ul { list-style: none; padding: 0; }
        li { background: #f0f3f7; margin: 8px 0; padding: 12px 16px; border-radius: 8px; display: flex; align-items: center; justify-content: space-between; }
        .col-name { font-weight: bold; color: #2d3a4a; }
        .col-id { color: #888; font-size: 0.95em; margin-left: 8px; }
        a { color: #1976d2; text-decoration: none; margin-left: 12px; }
        a:hover { text-decoration: underline; }
        form { margin-top: 24px; display: flex; gap: 12px; }
        input[type="text"], input[name="name"] { padding: 8px; border: 1px solid #cfd8dc; border-radius: 6px; font-size: 1em; }
        button { background: #1976d2; color: #fff; border: none; border-radius: 6px; padding: 8px 18px; font-size: 1em; cursor: pointer; transition: background 0.2s; }
        button:hover { background: #125ea7; }
        .empty { color: #aaa; font-style: italic; }
    </style>
    </head>
    <body>
    <div class="container">
        <h1>PocketBase Manager</h1>
        <h2>Kolekce</h2>
        <ul>
        {% if collections %}
            {% for col in collections %}
                <li>
                    <span class="col-name">{{ col['name'] }}</span>
                    <span class="col-id">(id: {{ col['id'] }})</span>
                    <span>
                        <a href="/collections/{{ col['id'] }}/records?html=1">Zobrazit záznamy</a>
                    </span>
                </li>
            {% endfor %}
        {% else %}
            <li class="empty">Žádné kolekce</li>
        {% endif %}
        </ul>
        <h3>Vytvořit novou kolekci</h3>
        <form method="post" action="/collections">
            <input type="text" name="name" placeholder="Název kolekce" required>
            <button type="submit">Vytvořit</button>
        </form>
    </div>
    </body>
    </html>
    '''
    return render_template_string(html, collections=collections)

# Výpis všech kolekcí
@app.route('/collections', methods=['GET'])
def list_collections():
    try:
        r = requests.get(POCKETBASE_API)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vytvoření nové kolekce (API i z formuláře)
@app.route('/collections', methods=['POST'])
def create_collection():
    if request.is_json:
        data = request.json
    else:
        # Z HTML formuláře
        data = {"name": request.form.get("name", "")}
    try:
        r = requests.post(POCKETBASE_API, json=data)
        r.raise_for_status()
        if request.is_json:
            return jsonify(r.json())
        else:
            return '<p>Kolekce vytvořena. <a href="/">Zpět</a></p>'
    except Exception as e:
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        else:
            return f'<p>Chyba: {str(e)} <a href="/">Zpět</a></p>'

# Výpis všech záznamů v kolekci (HTML i JSON)
@app.route('/collections/<collection_id>/records', methods=['GET'])
def list_records(collection_id):
    url = f"http://127.0.0.1:8090/api/collections/{collection_id}/records"
    try:
        r = requests.get(url)
        r.raise_for_status()
        records = r.json().get('items', [])
    except Exception as e:
        records = []
        if request.args.get('html') == '1':
            return render_template_string('<p>Chyba: {{ error }} <a href="/">Zpět</a></p>', error=str(e))
        else:
            return jsonify({'error': str(e)}), 500

    if request.args.get('html') == '1':
        html = '''
        <html>
        <head>
        <title>Záznamy kolekce</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6fa; margin: 0; padding: 0; }
            .container { max-width: 700px; margin: 40px auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 12px #0001; padding: 32px; }
            h2 { color: #2d3a4a; }
            ul { list-style: none; padding: 0; }
            li { background: #f0f3f7; margin: 8px 0; padding: 12px 16px; border-radius: 8px; }
            .empty { color: #aaa; font-style: italic; }
            a { color: #1976d2; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
        </head>
        <body>
        <div class="container">
            <h2>Záznamy kolekce {{ collection_id }}</h2>
            <ul>
            {% if records %}
                {% for rec in records %}
                    <li>{{ rec }}</li>
                {% endfor %}
            {% else %}
                <li class="empty">Žádné záznamy</li>
            {% endif %}
            </ul>
            <a href="/">Zpět na kolekce</a>
        </div>
        </body>
        </html>
        '''
        return render_template_string(html, records=records, collection_id=collection_id)
    else:
        return jsonify({'items': records})

# Smazání kolekce podle id
@app.route('/collections/<collection_id>', methods=['DELETE'])
def delete_collection(collection_id):
    try:
        url = f"{POCKETBASE_API}/{collection_id}"
        r = requests.delete(url)
        r.raise_for_status()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Přidání záznamu do kolekce
