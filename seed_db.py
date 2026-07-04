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
            {"name": "Moimenta da Beira", "lat": 40.9851, "lon": -7.6177, "elev": 697},
            {"name": "Porto", "lat": 41.1579, "lon": -8.6291, "elev": 83},
            {"name": "Coimbra", "lat": 40.2033, "lon": -8.4103, "elev": 100},
            {"name": "Faro", "lat": 37.0179, "lon": -7.9308, "elev": 8},
            {"name": "Évora", "lat": 38.5714, "lon": -7.9096, "elev": 279},
            {"name": "Funchal (Madeira)", "lat": 32.6500, "lon": -16.9080, "elev": 98},
            {"name": "Ponta Delgada (Açores)", "lat": 37.7412, "lon": -25.6756, "elev": 45},
            {"name": "Observatório Alqueva", "lat": 38.2667, "lon": -7.5333, "elev": 200},
            {"name": "Serra da Estrela (Torre)", "lat": 40.3218, "lon": -7.6129, "elev": 1993}
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

        # 3. Adicionar objetos celestes do catálogo (DSOs e Estrelas)
        from app.models import CelestialObject
        
        objects_data = [
            {"name": "M31", "ra": 0.712, "dec": 41.269, "category": "DSO", "description": "Galáxia de Andromeda"},
            {"name": "M42", "ra": 5.588, "dec": -5.391, "category": "DSO", "description": "Nebulosa de Orion"},
            {"name": "M45", "ra": 3.790, "dec": 24.117, "category": "DSO", "description": "Pleiades"},
            {"name": "M13", "ra": 16.695, "dec": 36.460, "category": "DSO", "description": "Enxame de Hércules"},
            {"name": "M51", "ra": 13.498, "dec": 47.195, "category": "DSO", "description": "Galáxia do Remoinho"},
            {"name": "M81", "ra": 9.926, "dec": 69.065, "category": "DSO", "description": "Galáxia de Bode"},
            {"name": "M27", "ra": 19.993, "dec": 22.721, "category": "DSO", "description": "Nebulosa do Haltere"},
            {"name": "M57", "ra": 18.885, "dec": 33.029, "category": "DSO", "description": "Nebulosa do Anel"},
            {"name": "M44", "ra": 8.667, "dec": 19.667, "category": "DSO", "description": "Enxame da Colmeia"},
            {"name": "Polaris", "ra": 2.530, "dec": 89.264, "category": "Star", "description": "Estrela Polar"}
        ]

        for obj_info in objects_data:
            obj = CelestialObject.query.filter_by(name=obj_info["name"]).first()
            if not obj:
                obj = CelestialObject(
                    name=obj_info["name"],
                    ra=obj_info["ra"],
                    dec=obj_info["dec"],
                    category=obj_info["category"],
                    description=obj_info["description"]
                )
                db.session.add(obj)
                db.session.commit()
                print(f"Objeto {obj.name} adicionado ao catálogo.")
            else:
                obj.ra = obj_info["ra"]
                obj.dec = obj_info["dec"]
                obj.category = obj_info["category"]
                obj.description = obj_info["description"]
                db.session.commit()
                print(f"Objeto {obj.name} atualizado.")

if __name__ == "__main__":
    seed()

