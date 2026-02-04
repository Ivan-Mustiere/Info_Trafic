import os
from datetime import datetime, time as dt_time

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://api:8000/api/predict")


def build_payload(
	numero_route: int,
	selected_date,
	selected_time: dt_time,
	debit_horaire: float,
	taux_occupation: float,
):
	hour_value = selected_time.hour + selected_time.minute / 60.0
	jour_semaine = selected_date.weekday()  # Monday=0
	is_weekend = jour_semaine >= 5

	return {
		"numero_route": int(numero_route),
		"debit_horaire": float(debit_horaire),
		"taux_occupation": float(taux_occupation),
		"jour_semaine": int(jour_semaine),
		"is_weekend": bool(is_weekend),
		"heure": float(hour_value),
	}


st.set_page_config(page_title="Info Trafic – Prédiction", layout="centered")

st.markdown(
	"""
	<style>
	.badge { display: inline-block; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 700; font-size: 1.1rem; }
	.badge-ok { background: #d4edda; color: #155724; }
	.badge-warning { background: #fff3cd; color: #856404; }
	.badge-danger { background: #f8d7da; color: #721c24; }
	</style>
	""",
	unsafe_allow_html=True,
)

st.markdown('<div class="app-title">Prédiction d\'état du trafic</div>', unsafe_allow_html=True)
st.markdown(
	'<div class="app-subtitle">Renseignez une date et une heure pour obtenir une prédiction de l\'état du trafic.</div>',
	unsafe_allow_html=True,
)

with st.sidebar:
	st.header("Paramètres API")
	api_url = st.text_input("URL API", value=API_URL)

st.subheader("Entrées du modèle")

col1, col2 = st.columns(2)

with col1:
	numero_route = st.number_input(
		"Numéro de route", min_value=0, value=1, step=1
	)
	selected_date = st.date_input("Date")
	selected_time = st.time_input("Heure")

with col2:
	debit_horaire = st.number_input(
		"Débit horaire", min_value=0.0, max_value=10000.0, value=1000.0, step=10.0
	)
	taux_occupation = st.number_input(
		"Taux d'occupation", min_value=0.0, max_value=100.0, value=5.0, step=0.1
	)

payload = build_payload(
	numero_route=numero_route,
	selected_date=selected_date,
	selected_time=selected_time,
	debit_horaire=debit_horaire,
	taux_occupation=taux_occupation,
)

st.caption(
	f"Jour de semaine: {payload['jour_semaine']} | Week-end: {payload['is_weekend']} | Heure: {payload['heure']:.2f}"
)

if st.button("Prédire"):
	try:
		response = requests.post(api_url, json=payload, timeout=10)
		response.raise_for_status()
		data = response.json()
		prediction = str(data.get("prediction", "N/A"))
		label = prediction.lower()
		if "bloqu" in label:
			badge_class = "badge-danger"
		elif "satur" in label:
			badge_class = "badge-warning"
		else:
			badge_class = "badge-ok"
		st.markdown(
			f"<div class='card'><div class='badge {badge_class}'>Prédiction : {prediction}</div></div>",
			unsafe_allow_html=True,
		)
		with st.expander("Payload envoyé"):
			st.json(payload)
	except requests.exceptions.RequestException as exc:
		st.error(f"Erreur API: {exc}")
