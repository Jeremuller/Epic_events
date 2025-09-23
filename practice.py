from database import SessionLocal, Base, engine
from models import User, Client, Contract, Event
from datetime import datetime, timedelta

# Initialisation
session = SessionLocal()
print("Session sqlalchemy démarrée")

# Supprime toutes les tables existantes
Base.metadata.drop_all(engine)
print("🧹 Toutes les tables ont été supprimées.")

# Recrée les tables
Base.metadata.create_all(engine)
print("✅ Tables recréées.")

# === ÉTAPE 1 : CRUD pour User ===
print("\n--- Test CRUD pour User ---")

# CREATE : Créer un utilisateur
user1 = User(
    first_name="Pierre",
    last_name="Dupont",
    username="pdupont",
    password="secure123",
    email="pierre@example.com",
    role="commercial"
)
session.add(user1)
session.commit()
print(f"✅ Utilisateur créé : {user1.first_name} (ID: {user1.user_id})")

# UPDATE : Mettre à jour le rôle de l'utilisateur
user1.role = "management"  # Changement de rôle
session.commit()
print(f"🔄 Rôle mis à jour : {user1.role}")

# READ : Lister tous les utilisateurs
all_users = session.query(User).all()
print("📖 Liste de tous les utilisateurs :")
for user in all_users:
    print(f"- {user.first_name} {user.last_name} (Rôle: {user.role})")

# === ÉTAPE 2 : CRUD pour Client ===
print("\n--- Test CRUD pour Client ---")

# CREATE : Créer un client lié à user1 (Pierre Dupont)
client1 = Client(
    first_name="Alice",
    last_name="Martin",
    business_name="Martin & Cie",
    telephone="0123456789",
    email="alice@example.com",
    first_contact=datetime.now(),
    last_update=datetime.now(),
    commercial_contact_id=user1.user_id  # Lien à l'utilisateur commercial créé précédemment
)
session.add(client1)
session.commit()
print(f"✅ Client créé : {client1.first_name} {client1.last_name} (ID: {client1.client_id})")

# Vérifier la relation Client → User
print(f"📖 Commercial associé : {client1.commercial_contact.first_name} {client1.commercial_contact.last_name}")

# READ : Récupérer le client par ID
retrieved_client = session.query(Client).filter_by(client_id=client1.client_id).first()
print(f"📖 Client récupéré : {retrieved_client.first_name} {retrieved_client.last_name}")

# READ : Lister tous les clients
all_clients = session.query(Client).all()
print("📖 Liste de tous les clients :")
for client in all_clients:
    print(f"- {client.first_name} {client.last_name} (Email: {client.email})")

# UPDATE : Mettre à jour les informations du client
retrieved_client.last_name = "Durand"  # Changement de nom
retrieved_client.telephone = "0987654321"  # Nouveau téléphone
session.commit()
print(
    f"🔄 Client mis à jour : {retrieved_client.first_name} {retrieved_client.last_name} "
    f"(Tél: {retrieved_client.telephone})")


# DELETE : Supprimer le client (commenté pour l'instant)
# session.delete(retrieved_client)
# session.commit()
# print("🗑️ Client supprimé.")

# CREATE : Créer un deuxième client (lié au même utilisateur ou à un autre)
client2 = Client(
    first_name="Bob",
    last_name="Smith",
    business_name="Smith Corp",
    telephone="0112233445",
    email="bob@example.com",
    first_contact=datetime.now(),
    last_update=datetime.now(),
    commercial_contact_id=user1.user_id  # Même commercial (Pierre)
)
session.add(client2)
session.commit()
print(f"✅ Deuxième client créé : {client2.first_name} {client2.last_name} (ID: {client2.client_id})")

# Vérifier les clients gérés par user1 (Pierre)
print(f"\n📖 Clients gérés par {user1.first_name} :")
for client in user1.clients:
    print(f"- {client.first_name} {client.last_name} (ID: {client.client_id})")

# Tester la relation bidirectionnelle Client ↔ User
print(f"\n🔄 Relation Client → User :")
for client in [client1, client2]:
    print(f"Client {client.first_name} est géré par {client.commercial_contact.first_name}")

print(f"\n🔄 Relation User → Clients :")
print(f"L'utilisateur {user1.first_name} gère {len(user1.clients)} clients :")
for client in user1.clients:
    print(f"- {client.first_name} {client.last_name}")


# === ÉTAPE 3 : CRUD pour Contract ===
print("\n--- Test CRUD pour Contract ---")

# CREATE : Créer un contrat pour client1 (Alice) avec user1 (Pierre)
contract1 = Contract(
    total_price=1500.00,
    rest_to_pay=1500.00,
    creation=datetime.now(),
    signed=False,
    client_id=client1.client_id,  # Lien au client Alice
    commercial_contact_id=user1.user_id  # Lien à l'utilisateur Pierre
)
session.add(contract1)
session.commit()
print(f"✅ Contrat 1 créé : ID {contract1.contract_id}, Montant = {contract1.total_price}")

# CREATE : Créer un deuxième contrat pour client2 (Bob) avec user1 (Pierre)
contract2 = Contract(
    total_price=2000.00,
    rest_to_pay=2000.00,
    creation=datetime.now(),
    signed=False,
    client_id=client2.client_id,  # Lien au client Bob
    commercial_contact_id=user1.user_id
)
session.add(contract2)
session.commit()
print(f"✅ Contrat 2 créé : ID {contract2.contract_id}, Montant = {contract2.total_price}")

# READ : Récupérer un contrat par ID
retrieved_contract = session.query(Contract).filter_by(contract_id=contract1.contract_id).first()
print(
    f"📖 Contrat 1 récupéré : Client = {retrieved_contract.client.first_name}, "
    f"Montant = {retrieved_contract.total_price}")

# UPDATE : Mettre à jour le contrat 1 (le signer et régler)
retrieved_contract.signed = True
retrieved_contract.rest_to_pay = 0.00
session.commit()
print(f"🔄 Contrat 1 mis à jour : Signé = {retrieved_contract.signed}, Reste à payer = {retrieved_contract.rest_to_pay}")

# READ : Lister tous les contrats d'un client (ex: Alice)
print(f"\n📖 Contrats de {client1.first_name} :")
for contract in client1.contracts:
    print(f"- ID: {contract.contract_id}, Montant: {contract.total_price}, Signé: {contract.signed}")

# READ : Lister tous les contrats d'un utilisateur (ex: Pierre)
print(f"\n📖 Contrats gérés par {user1.first_name} :")
for contract in user1.contracts:
    print(f"- ID: {contract.contract_id}, Client: {contract.client.first_name}, Montant: {contract.total_price}")

# DELETE : Supprimer un contrat (optionnel, décommenter pour tester)
# session.delete(contract1)
# session.commit()
# print(f"🗑️ Contrat {contract1.contract_id} supprimé.")


# === ÉTAPE 4 : CRUD pour Event ===
print("\n--- Test CRUD pour Event ---")

# CREATE : Créer un utilisateur "support" pour les événements (si pas déjà fait)
user2 = User(
    first_name="Marie",
    last_name="Curie",
    username="mcurie",
    password="support123",
    email="marie@example.com",
    role="support"
)
session.add(user2)
session.commit()
print(f"✅ Utilisateur support créé : {user2.first_name} (ID: {user2.user_id})")

# CREATE : Créer un événement pour client1 (Alice) avec user2 (Marie)
event1 = Event(
    name="Réunion de suivi",
    notes="Discuter des prochaines étapes du projet...",
    start_datetime=datetime.now(),
    end_datetime=datetime.now() + timedelta(hours=1),
    location="Visio",
    attendees=3,
    client_id=client1.client_id,  # Lien au client Alice
    support_contact_id=user2.user_id  # Lien à l'utilisateur Marie (support)
)
session.add(event1)
session.commit()
print(f"✅ Événement 1 créé : {event1.name} (ID: {event1.event_id})")

# CREATE : Créer un deuxième événement pour client2 (Bob) avec user2 (Marie)
event2 = Event(
    name="Atelier technique",
    notes="Formation sur le nouveau produit...",
    start_datetime=datetime.now() + timedelta(days=1),
    end_datetime=datetime.now() + timedelta(days=1, hours=2),
    location="Bureau",
    attendees=5,
    client_id=client2.client_id,  # Lien au client Bob
    support_contact_id=user2.user_id
)
session.add(event2)
session.commit()
print(f"✅ Événement 2 créé : {event2.name} (ID: {event2.event_id})")

# READ : Récupérer un événement par ID
retrieved_event = session.query(Event).filter_by(event_id=event1.event_id).first()
print(
    f"📖 Événement 1 récupéré : {retrieved_event.name}, "
    f"Client = {retrieved_event.client.first_name}, "
    f"Support = {retrieved_event.support_contact.first_name}"
)

# UPDATE : Mettre à jour l'événement 1 (changer la localisation)
retrieved_event.location = "Salle de réunion A"
session.commit()
print(f"🔄 Événement 1 mis à jour : Lieu = {retrieved_event.location}")

# READ : Lister tous les événements d'un client (ex: Alice)
print(f"\n📖 Événements de {client1.first_name} :")
for event in client1.events:
    print(f"- {event.name} (ID: {event.event_id}, Lieu: {event.location})")

# READ : Lister tous les événements d'un utilisateur (ex: Marie)
print(f"\n📖 Événements gérés par {user2.first_name} :")
for event in user2.events:
    print(f"- {event.name} (Client: {event.client.first_name}, Lieu: {event.location})")

# DELETE : Supprimer un événement (optionnel)
# session.delete(event1)
# session.commit()
# print(f"🗑️ Événement {event1.event_id} supprimé.")


# Fermer la session
session.close()
print("\n🔌 Session fermée.")
