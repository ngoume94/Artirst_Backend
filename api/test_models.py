"""
Tests pour valider les modèles Last.fm
Version avec requêtes simples pour exploration des données
"""
from database import SessionLocal
from models import User, Artist, Tag, UserArtist, UserTaggedArtist, UserFriend

def test_artists():
    """Tester la récupération de quelques artistes"""
    print("\n" + "="*60)
    print("TEST 1: Récupération des artistes")
    print("="*60)
    
    db = SessionLocal()
    
    artists = db.query(Artist).limit(10).all()
    
    if artists:
        for artist in artists:
            print(f"ID: {artist.id} | Nom: {artist.name}")
            print(f"  URL: {artist.url}")
            print(f"  Nombre d'écoutes: {len(artist.listeners)}")
            print(f"  Nombre de tags: {len(artist.tags_received)}")
            print("-" * 50)
    else:
        print(" Aucun artiste trouvé dans la base de données.")
    
    db.close()


def test_users():
    """Tester la récupération de quelques utilisateurs"""
    print("\n" + "="*60)
    print("TEST 2: Récupération des utilisateurs")
    print("="*60)
    
    db = SessionLocal()
    
    users = db.query(User).limit(5).all()
    
    if users:
        for user in users:
            print(f"UserID: {user.userID}")
            print(f"  Artistes écoutés: {len(user.listened_artists)}")
            print(f"  Tags créés: {len(user.tagged_artists)}")
            print(f"  Amis: {len(user.get_all_friends_ids())}")
            print("-" * 50)
    else:
        print(" Aucun utilisateur trouvé.")
    
    db.close()


def test_user_artists():
    """Tester les relations utilisateur-artiste (écoutes)"""
    print("\n" + "="*60)
    print("TEST 3: Relations Utilisateur-Artiste")
    print("="*60)
    
    db = SessionLocal()
    
    # Récupérer les 10 écoutes les plus importantes
    top_listens = (
        db.query(UserArtist)
        .order_by(UserArtist.weight.desc())
        .limit(10)
        .all()
    )
    
    if top_listens:
        print("Top 10 des écoutes:")
        for listen in top_listens:
            print(f"UserID: {listen.userID} | "
                  f"Artiste: {listen.artist.name} | "
                  f"Écoutes: {listen.weight}")
    else:
        print(" Aucune relation utilisateur-artiste trouvée.")
    
    db.close()


def test_tags():
    """Tester les tags"""
    print("\n" + "="*60)
    print("TEST 4: Tags populaires")
    print("="*60)
    
    db = SessionLocal()
    
    # Récupérer les tags les plus utilisés
    from sqlalchemy import func
    
    popular_tags = (
        db.query(Tag, func.count(UserTaggedArtist.tagID).label('usage_count'))
        .join(UserTaggedArtist)
        .group_by(Tag.tagID)
        .order_by(func.count(UserTaggedArtist.tagID).desc())
        .limit(10)
        .all()
    )
    
    if popular_tags:
        print("Top 10 des tags les plus utilisés:")
        for tag, count in popular_tags:
            print(f"Tag: '{tag.tagValue}' | Utilisations: {count}")
    else:
        print(" Aucun tag trouvé.")
    
    db.close()


def test_user_tagged_artists():
    """Tester les tags appliqués par les utilisateurs aux artistes"""
    print("\n" + "="*60)
    print("TEST 5: Tags appliqués aux artistes")
    print("="*60)
    
    db = SessionLocal()
    
    tagged_entries = db.query(UserTaggedArtist).limit(10).all()
    
    if tagged_entries:
        for entry in tagged_entries:
            print(f"UserID: {entry.userID} a tagué "
                  f"'{entry.artist.name}' avec '{entry.tag.tagValue}'")
            print(f"  Date: {entry.day}/{entry.month}/{entry.year}")
            print("-" * 50)
    else:
        print(" Aucun tag d'artiste trouvé.")
    
    db.close()


def test_friendships():
    """Tester les relations d'amitié"""
    print("\n" + "="*60)
    print("TEST 6: Relations d'amitié")
    print("="*60)
    
    db = SessionLocal()
    
    # Trouver un utilisateur avec des amis
    user_with_friends = (
        db.query(User)
        .join(UserFriend, User.userID == UserFriend.userID)
        .first()
    )
    
    if user_with_friends:
        print(f"UserID: {user_with_friends.userID}")
        friends_ids = user_with_friends.get_all_friends_ids()
        print(f"  Nombre total d'amis: {len(friends_ids)}")
        print(f"  IDs des amis: {sorted(list(friends_ids))[:10]}...")
    else:
        print(" Aucune relation d'amitié trouvée.")
    
    db.close()


def test_artist_by_genre():
    """Rechercher des artistes par tag (équivalent de genre)"""
    print("\n" + "="*60)
    print("TEST 7: Artistes par tag 'rock'")
    print("="*60)
    
    db = SessionLocal()
    
    # Trouver les artistes taggés "rock"
    rock_artists = (
        db.query(Artist)
        .join(UserTaggedArtist)
        .join(Tag)
        .filter(Tag.tagValue.like('%rock%'))
        .distinct()
        .limit(10)
        .all()
    )
    
    if rock_artists:
        print(f"Trouvé {len(rock_artists)} artistes avec le tag 'rock':")
        for artist in rock_artists:
            print(f"  - {artist.name}")
    else:
        print(" Aucun artiste rock trouvé.")
    
    db.close()


def test_user_statistics():
    """Statistiques détaillées d'un utilisateur"""
    print("\n" + "="*60)
    print("TEST 8: Statistiques détaillées d'un utilisateur")
    print("="*60)
    
    db = SessionLocal()
    
    # Prendre le premier utilisateur avec des données
    user = (
        db.query(User)
        .join(UserArtist)
        .first()
    )
    
    if user:
        print(f"Statistiques pour UserID: {user.userID}")
        print(f"  Nombre d'artistes écoutés: {len(user.listened_artists)}")
        
        # Top 5 artistes les plus écoutés par cet utilisateur
        top_artists = sorted(
            user.listened_artists, 
            key=lambda x: x.weight, 
            reverse=True
        )[:5]
        
        print(f"  Top 5 artistes:")
        for i, listen in enumerate(top_artists, 1):
            print(f"    {i}. {listen.artist.name} ({listen.weight} écoutes)")
        
        print(f"  Nombre de tags créés: {len(user.tagged_artists)}")
        print(f"  Nombre d'amis: {len(user.get_all_friends_ids())}")
    else:
        print(" Aucun utilisateur avec données trouvé.")
    
    db.close()


def test_database_statistics():
    """Statistiques globales de la base de données"""
    print("\n" + "="*60)
    print("TEST 9: Statistiques globales")
    print("="*60)
    
    db = SessionLocal()
    
    total_users = db.query(User).count()
    total_artists = db.query(Artist).count()
    total_tags = db.query(Tag).count()
    total_listens = db.query(UserArtist).count()
    total_tagged = db.query(UserTaggedArtist).count()
    total_friendships = db.query(UserFriend).count()
    
    print(f"Total utilisateurs: {total_users}")
    print(f"Total artistes: {total_artists}")
    print(f"Total tags: {total_tags}")
    print(f"Total écoutes (user-artist): {total_listens}")
    print(f"Total tags appliqués: {total_tagged}")
    print(f"Total relations d'amitié: {total_friendships}")
    
    db.close()


def run_all_tests():
    """Exécuter tous les tests"""
    print("\n" + " " * 30)
    print("TESTS DES MODÈLES LAST.FM")
    print(" " * 30)
    
    try:
        test_database_statistics()
        test_artists()
        test_users()
        test_user_artists()
        test_tags()
        test_user_tagged_artists()
        test_friendships()
        test_artist_by_genre()
        test_user_statistics()
        
        print("\n" + " " * 30)
        print("TOUS LES TESTS SONT TERMINÉS")
        print(" " * 30 + "\n")
        
    except Exception as e:
        print(f"\n ERREUR: {e}")
        print("Vérifiez que la base de données contient des données.\n")


if __name__ == "__main__":
    run_all_tests()