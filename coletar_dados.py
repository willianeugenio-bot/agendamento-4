import requests
import json
import os
from datetime import datetime, timedelta, timezone

# URIs dos novos assessores da equipe "Migração LP"
URIs = [
    "https://api.calendly.com/event_types/ea4bb07a-fb88-4049-9ee2-ab21d6cf660d", 
    "https://api.calendly.com/event_types/e65136bd-badd-424c-a63c-c6f46b428fb3"
]

# Mapeamento (As cores não aparecerão na tela final, mas mantemos por estrutura)
MAPA_NOMES = {
    "ea4bb07a-fb88-4049-9ee2-ab21d6cf660d": {"nome": "LP -", "cor": "#007bff"},
    "e65136bd-badd-424c-a63c-c6f46b428fb3": {"nome": "LP -", "cor": "#007bff"}
}

TOKEN = os.getenv("CALENDLY_TOKEN")
headers = {"Authorization": f"Bearer {TOKEN}"}

def obter_horarios():
    eventos_final = []
    agora_utc = datetime.now(timezone.utc)

    for uri in URIs:
        uuid = uri.split('/')[-1]
        info = MAPA_NOMES.get(uuid)
        
        if not info:
            continue # Pula se o UUID não estiver no mapa
            
        # Dividimos em duas buscas para respeitar o limite de 7 dias do Calendly
        # Fatias: [Hoje até dia 7] e [Dia 7 até dia 10]
        intervalos = [
            (agora_utc + timedelta(minutes=1), agora_utc + timedelta(days=7)),
            (agora_utc + timedelta(days=7, minutes=1), agora_utc + timedelta(days=14))
        ]
        
        for start_time, end_time in intervalos:
            params = {
                "event_type": uri,
                "start_time": start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "end_time": end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
            try:
                res = requests.get("https://api.calendly.com/event_type_available_times", headers=headers, params=params)
                if res.status_code == 200:
                    slots = res.json().get('collection', [])
                    for slot in slots:
                        eventos_final.append({
                            "title": f"Falar com {info['nome']}",
                            "start": slot['start_time'],
                            "url": slot['scheduling_url']
                        })
            except Exception as e:
                print(f"Erro ao processar {info['nome']}: {e}")

    with open("horarios.json", "w") as f:
        json.dump(eventos_final, f, indent=4)
    print("Arquivo horarios.json atualizado com sucesso (10 dias buscados).")

if __name__ == "__main__":
    obter_horarios()
