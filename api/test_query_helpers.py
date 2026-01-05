"""
Script de test pour toutes les opérations CRUD
"""
from database import SessionLocal
import query_helpers as qh

def print_section(title):
    """Affiche un titre de section."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_artist_crud():
    """Test CRUD pour les artistes."""
    print_section("TEST CRUD - ARTISTES")
    db = SessionLocal()
    
    # CREATE
    print("\n1. CREATE - Création d'un artiste")
    artist = qh.create_artist(
        db, 
        name="Daft Punk Test",
        url="http://last.fm/music/daft-punk-test",
        pictureURL="http://example.com/image.jpg"
    )
    print(f"     Artiste créé: ID={artist.id}, Name={artist.name}")
    
    # READ
    print("\n2. READ - Lecture de l'artiste")
    retrieved = qh.get_artist(db, artist.id)
    print(f"     Artiste récupéré: {retrieved}")
    
    # READ by name
    print("\n3. READ by name - Recherche par nom")
    found = qh.get_artist_by_name(db, "Daft Punk Test")
    print(f"     Trouvé par nom: {found.name}")
    
    # UPDATE
    print("\n4. UPDATE - Mise à jour de l'artiste")
    updated = qh.update_artist(
        db, 
        artist.id, 
        url="http://last.fm/music/updated-url"
    )
    print(f"     URL mise à jour: {updated.url}")
    
    # DELETE
    print("\n5. DELETE - Suppression de l'artiste")
    success = qh.delete_artist(db, artist.id)
    print(f"     Artiste supprimé: {success}")
    
    # Vérifier la suppression
    deleted = qh.get_artist(db, artist.id)
    print(f"     Vérification: artiste existe = {deleted is not None}")
    
    db.close()


def test_user_crud():
    """Test CRUD pour les utilisateurs."""
    print_section("TEST CRUD - UTILISATEURS")
    db = SessionLocal()
    
    # CREATE
    print("\n1. CREATE - Création d'un utilisateur")
    user = qh.create_user(db, user_id=99999)
    print(f"     Utilisateur créé: ID={user.userID}")
    
    # READ
    print("\n2. READ - Lecture de l'utilisateur")
    retrieved = qh.get_user(db, 99999)
    print(f"     Utilisateur récupéré: {retrieved}")
    
    # DELETE
    print("\n3. DELETE - Suppression de l'utilisateur")
    success = qh.delete_user(db, 99999)
    print(f"     Utilisateur supprimé: {success}")
    
    db.close()


def test_tag_crud():
    """Test CRUD pour les tags."""
    print_section("TEST CRUD - TAGS")
    db = SessionLocal()
    
    # CREATE
    print("\n1. CREATE - Création d'un tag")
    tag = qh.create_tag(db, "test-tag")
    print(f"     Tag créé: ID={tag.tagID}, Value={tag.tagValue}")
    
    # READ
    print("\n2. READ - Lecture du tag")
    retrieved = qh.get_tag_by_id(db, tag.tagID)
    print(f"     Tag récupéré: {retrieved}")
    
    # READ by value
    print("\n3. READ by value - Recherche par valeur")
    found = qh.get_tag_by_value(db, "test-tag")
    print(f"     Trouvé par valeur: {found.tagValue}")
    
    # UPDATE
    print("\n4. UPDATE - Mise à jour du tag")
    updated = qh.update_tag(db, tag.tagID, "updated-test-tag")
    print(f"     Tag mis à jour: {updated.tagValue}")
    
    # DELETE
    print("\n5. DELETE - Suppression du tag")
    success = qh.delete_tag(db, tag.tagID)
    print(f"     Tag supprimé: {success}")
    
    db.close()


def test_user_artist_crud():
    """Test CRUD pour les écoutes (user-artist)."""
    print_section("TEST CRUD - ÉCOUTES (USER-ARTIST)")
    db = SessionLocal()
    
    # Créer un utilisateur et un artiste pour les tests
    user = qh.create_user(db, 88888)
    artist = qh.create_artist(db, "Test Artist for Listening")
    
    # CREATE
    print("\n1. CREATE - Enregistrement d'une écoute")
    listen = qh.create_user_artist(db, user.userID, artist.id, weight=100)
    print(f"     Écoute créée: User={listen.userID}, Artist={listen.artistID}, Weight={listen.weight}")
    
    # READ
    print("\n2. READ - Lecture de l'écoute")
    retrieved = qh.get_user_listening_count(db, user.userID, artist.id)
    print(f"     Écoute récupérée: Weight={retrieved.weight}")
    
    # UPDATE
    print("\n3. UPDATE - Mise à jour du poids d'écoute")
    updated = qh.update_user_artist(db, user.userID, artist.id, 250)
    print(f"     Poids mis à jour: {updated.weight}")
    
    # INCREMENT
    print("\n4. INCREMENT - Incrémentation du poids")
    incremented = qh.increment_listening_weight(db, user.userID, artist.id, 50)
    print(f"     Poids après incrémentation: {incremented.weight}")
    
    # DELETE
    print("\n5. DELETE - Suppression de l'écoute")
    success = qh.delete_user_artist(db, user.userID, artist.id)
    print(f"     Écoute supprimée: {success}")
    
    # Nettoyage
    qh.delete_user(db, user.userID)
    qh.delete_artist(db, artist.id)
    
    db.close()


def test_friendship_crud():
    """Test CRUD pour les amitiés."""
    print_section("TEST CRUD - AMITIÉS")
    db = SessionLocal()
    
    # Créer deux utilisateurs
    user1 = qh.create_user(db, 77777)
    user2 = qh.create_user(db, 77778)
    
    # CREATE
    print("\n1. CREATE - Création d'une amitié bidirectionnelle")
    friendship = qh.create_friendship(db, user1.userID, user2.userID, bidirectional=True)
    print(f"     Amitié créée: {friendship}")
    
    # READ
    print("\n2. READ - Vérification de l'amitié")
    are_friends = qh.are_friends(db, user1.userID, user2.userID)
    print(f"     Sont amis: {are_friends}")
    
    friends_ids = qh.get_user_friends_ids(db, user1.userID)
    print(f"     Amis de user1: {friends_ids}")
    
    # DELETE
    print("\n3. DELETE - Suppression de l'amitié")
    success = qh.delete_friendship(db, user1.userID, user2.userID, bidirectional=True)
    print(f"     Amitié supprimée: {success}")
    
    # Vérification
    still_friends = qh.are_friends(db, user1.userID, user2.userID)
    print(f"     Encore amis après suppression: {still_friends}")
    
    # Nettoyage
    qh.delete_user(db, user1.userID)
    qh.delete_user(db, user2.userID)
    
    db.close()


def test_user_tagged_artist_crud():
    """Test CRUD pour les tags appliqués."""
    print_section("TEST CRUD - TAGS APPLIQUÉS (USER-TAGGED-ARTIST)")
    db = SessionLocal()
    
    # Créer les entités nécessaires
    user = qh.create_user(db, 66666)
    artist = qh.create_artist(db, "Test Artist for Tagging")
    tag = qh.create_tag(db, "experimental")
    
    # CREATE
    print("\n1. CREATE - Application d'un tag à un artiste")
    tagged = qh.create_user_tagged_artist(
        db, 
        user.userID, 
        artist.id, 
        tag.tagID,
        day=5,
        month=1,
        year=2026
    )
    print(f"     Tag appliqué: User={tagged.userID}, Artist={tagged.artistID}, Tag={tagged.tagID}")
    
    # READ
    print("\n2. READ - Récupération des tags pour un artiste")
    artist_tags = qh.get_artist_tags(db, artist.id)
    print(f"     Tags de l'artiste: {[(tag_val, count) for tag_val, count in artist_tags]}")
    
    # READ - Artistes par tag
    print("\n3. READ - Artistes avec le tag 'experimental'")
    artists_with_tag = qh.get_artists_by_tag(db, "experimental")
    print(f"     Artistes trouvés: {[a.name for a in artists_with_tag]}")
    
    # DELETE
    print("\n4. DELETE - Suppression du tag appliqué")
    success = qh.delete_user_tagged_artist(
        db, 
        user.userID, 
        artist.id, 
        tag.tagID, 
        tagged.timestamp
    )
    print(f"     Tag supprimé: {success}")
    
    # Nettoyage
    qh.delete_user(db, user.userID)
    qh.delete_artist(db, artist.id)
    qh.delete_tag(db, tag.tagID)
    
    db.close()


def test_analytics():
    """Test des fonctions analytiques."""
    print_section("TEST - FONCTIONS ANALYTIQUES")
    db = SessionLocal()
    
    # Statistiques globales
    print("\n1. Statistiques globales")
    stats = qh.get_global_statistics(db)
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Artistes populaires
    print("\n2. Top 5 artistes les plus populaires")
    popular = qh.get_most_popular_artists(db, limit=5)
    for i, (artist_id, name, weight) in enumerate(popular, 1):
        print(f"   {i}. {name} (ID: {artist_id}): {weight} écoutes")
    
    # Tags populaires
    print("\n3. Top 5 tags les plus utilisés")
    popular_tags = qh.get_most_popular_tags(db, limit=5)
    if popular_tags:
        for i, (tag_id, tag_value, count) in enumerate(popular_tags, 1):
            print(f"   {i}. {tag_value} (ID: {tag_id}): {count} utilisations")
    else:
        print("      Aucun tag appliqué trouvé dans la base de données")
        print("   Note: La table 'user_taggedartists' semble vide")
    
    # Utilisateurs actifs
    print("\n4. Top 5 utilisateurs les plus actifs")
    active_users = qh.get_most_active_users(db, limit=5)
    for i, (user_id, count) in enumerate(active_users, 1):
        print(f"   {i}. User {user_id}: {count} artistes écoutés")
    
    db.close()


def run_all_crud_tests():
    """Exécute tous les tests CRUD."""
    print("\n" + " " * 35)
    print("TESTS CRUD COMPLETS - LAST.FM")
    print(" " * 35)
    
    try:
        test_artist_crud()
        test_user_crud()
        test_tag_crud()
        test_user_artist_crud()
        test_friendship_crud()
        test_user_tagged_artist_crud()
        test_analytics()
        
        print("\n" + " " * 35)
        print("TOUS LES TESTS CRUD SONT RÉUSSIS")
        print(" " * 35 + "\n")
        
    except Exception as e:
        print(f"\n ERREUR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_crud_tests()