from flask import Flask, jsonify, request
from flask_cors import CORS
import pyodbc

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200", "methods": ["GET", "POST", "PUT", "DELETE"]}})

# Opret forbindelse til SQL Server
def get_db_connection():
    conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=JobReporting;Trusted_Connection=yes")
    return conn

# GET: Hent alle virksomheder
@app.route('/api/company', methods=['GET'])
def get_companies():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT Id, name, Location, CompanySize, Creating, Facts, Offering, CompanyOffer, Motivation, Notes FROM dbo.Company')
    companies = []
    for row in cursor.fetchall():
        companies.append({
            'Id': row[0],
            'name': row[1],
            'location': row[2],
            'companySize': row[3],
            'creating': row[4],
            'facts': row[5],
            'offering': row[6],
            'companyOffer': row[7],
            'motivation': row[8],
            'notes': row[9]
        })
    cursor.close()
    conn.close()
    return jsonify(companies)

# POST: Opret en ny virksomhed
@app.route('/api/company', methods=['POST'])
def create_company():
    new_company = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO dbo.Company (name, location, companySize, creating, facts, offering, companyoffer, motivation, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (new_company['name'], new_company['location'], new_company['companySize'], new_company['creating'],
          new_company['facts'], new_company['offering'], new_company['companyoffer'], new_company['motivation'],
          new_company['notes']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(new_company), 201  # Returner den nyoprettede virksomhed med statuskode 201

@app.route('/api/company/<int:id>', methods=['PUT'])
def update_company(id):
    updated_company = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Opdater forespørgslen
    cursor.execute("""
        UPDATE dbo.Company
        SET name = ?, location = ?, companySize = ?, creating = ?, facts = ?, offering = ?, companyoffer = ?, motivation = ?, notes = ?
        WHERE Id = ?
    """, (updated_company['name'], updated_company['location'], updated_company['companySize'], updated_company['creating'],
          updated_company['facts'], updated_company['offering'], updated_company['companyoffer'], updated_company['motivation'],
          updated_company['notes'], id))
    
    # Kontrollér om nogen rækker blev opdateret
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Company not found"}), 404

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify(updated_company), 200


# DELETE: Slet en virksomhed
@app.route('/api/company/<int:id>', methods=['DELETE'])
def delete_company(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM dbo.Company WHERE Id = ?', id)
    conn.commit()
    cursor.close()
    conn.close()
    return '', 204  # Returner statuskode 204, som indikerer, at ressourcen er blevet slettet

if __name__ == '__main__':
    app.run(debug=True)
