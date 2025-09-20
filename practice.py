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
print(f"🔄 Client mis à jour : {retrieved_client.first_name} {retrieved_client.last_name} (Tél: {retrieved_client.telephone})")

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

# Fermer la session
session.close()
print("\n🔌 Session fermée.")
