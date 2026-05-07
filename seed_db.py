# SPDX-License-Identifier: GPL-2.0-only
from app import create_app, db
from app.models import User, Location
from sqlalchemy.exc import IntegrityError

def seed():
    app = create_app()
    with app.app_context():
        # 1. Criar utilizador xx2
        username = "xx2"
        password = "xx2"
        email = "xx2@example.com"
        
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"Utilizador {username} criado.")
        else:
            print(f"Utilizador {username} já existe.")

        # 2. Adicionar localizações (Dados precisos via pesquisa web)
        locations_data = [
            {"name": "Lisboa", "lat": 38.7223, "lon": -9.1393, "elev": 45, "is_default": True},
            {"name": "Glasgow", "lat": 55.8642, "lon": -4.2518, "elev": 40},
            {"name": "Ilha do Corvo", "lat": 39.6728, "lon": -31.1144, "elev": 36},
            {"name": "Sydney", "lat": -33.8678, "lon": 151.2073, "elev": 37},
            {"name": "Buenos Aires", "lat": -34.6037, "lon": -58.3816, "elev": 25},
            {"name": "Luanda", "lat": -8.8368, "lon": 13.2343, "elev": 73},
            {"name": "Póvoa de Santa Iria", "lat": 38.8610, "lon": -9.0645, "elev": 20},
            {"name": "Moimenta da Beira", "lat": 40.9851, "lon": -7.6177, "elev": 697}
        ]

        default_loc = None
        for loc_info in locations_data:
            loc = Location.query.filter_by(name=loc_info["name"], user_id=user.id).first()
            if not loc:
                loc = Location(
                    name=loc_info["name"],
                    latitude=loc_info["lat"],
                    longitude=loc_info["lon"],
                    elevation=loc_info["elev"],
                    user_id=user.id
                )
                db.session.add(loc)
                db.session.commit()
                print(f"Localização {loc.name} adicionada.")
            else:
                # Atualizar campos se já existir
                loc.latitude = loc_info["lat"]
                loc.longitude = loc_info["lon"]
                loc.elevation = loc_info["elev"]
                db.session.commit()
                print(f"Localização {loc.name} atualizada com dados precisos.")
            
            if loc_info.get("is_default"):
                default_loc = loc

        if default_loc and user.default_location_id != default_loc.id:
            user.default_location_id = default_loc.id
            db.session.commit()
            print(f"Localização default definida para {default_loc.name}.")

if __name__ == "__main__":
    seed()
