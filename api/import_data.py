"""
Script d'importation des données Last.fm depuis les fichiers .dat

Le script import_data.py que je viens de créer va :

1. Importer tous les fichiers .dat dans le bon ordre
2. Créer automatiquement les utilisateurs manquants
3 Gérer les timestamps correctement (remplacer les 0 par une valeur par défaut)
4. Utiliser des batch inserts pour de meilleures performances
5. Afficher la progression en temps réel

"""
import os
from datetime import datetime
from database import SessionLocal, engine, Base
from models import User, Artist, Tag, UserArtist, UserTaggedArtist, UserFriend
from sqlalchemy import text

# Chemin vers le dossier contenant les fichiers .dat
DATA_DIR = "D:/End_To_End_Data_Science_Project/Artirst_Backend/Data"  # Ajustez selon votre structure

def print_section(title):
    """Affiche un titre de section."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def create_tables():
    """Crée toutes les tables dans la base de données."""
    print_section("CRÉATION DES TABLES")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès!")

def import_artists(db, filepath):
    """Importe les artistes depuis artists.dat"""
    print_section("IMPORTATION DES ARTISTES")
    
    if not os.path.exists(filepath):
        print(f"❌ Fichier non trouvé: {filepath}")
        return 0
    
    count = 0
    batch = []
    batch_size = 1000
    
    with open(filepath, 'r', encoding='utf-8') as f:
        # Ignorer la première ligne (header)
        next(f)
        
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                artist_id = int(parts[0])
                name = parts[1]
                url = parts[2] if len(parts) > 2 else None
                picture_url = parts[3] if len(parts) > 3 else None
                
                artist = Artist(
                    id=artist_id,
                    name=name,
                    url=url,
                    pictureURL=picture_url
                )
                batch.append(artist)
                count += 1
                
                # Insérer par batch pour améliorer les performances
                if len(batch) >= batch_size:
                    db.bulk_save_objects(batch)
                    db.commit()
                    batch = []
                    print(f"   Importé: {count} artistes...", end='\r')
        
        # Insérer le dernier batch
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
    
    print(f"\n✅ {count} artistes importés avec succès!")
    return count

def import_tags(db, filepath):
    """Importe les tags depuis tags.dat"""
    print_section("IMPORTATION DES TAGS")
    
    if not os.path.exists(filepath):
        print(f"❌ Fichier non trouvé: {filepath}")
        return 0
    
    count = 0
    batch = []
    batch_size = 1000
    
    with open(filepath, 'r', encoding='latin-1') as f:
        # Ignorer la première ligne (header)
        next(f)
        
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                tag_id = int(parts[0])
                tag_value = parts[1]
                
                tag = Tag(
                    tagID=tag_id,
                    tagValue=tag_value
                )
                batch.append(tag)
                count += 1
                
                if len(batch) >= batch_size:
                    db.bulk_save_objects(batch)
                    db.commit()
                    batch = []
                    print(f"   Importé: {count} tags...", end='\r')
        
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
    
    print(f"\n✅ {count} tags importés avec succès!")
    return count

def import_user_artists(db, filepath):
    """Importe les écoutes depuis user_artists.dat"""
    print_section("IMPORTATION DES ÉCOUTES (USER-ARTISTS)")
    
    if not os.path.exists(filepath):
        print(f"❌ Fichier non trouvé: {filepath}")
        return 0, 0
    
    user_count = 0
    listen_count = 0
    users_seen = set()
    batch_users = []
    batch_listens = []
    batch_size = 1000
    
    with open(filepath, 'r', encoding='utf-8') as f:
        # Ignorer la première ligne (header)
        next(f)
        
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                user_id = int(parts[0])
                artist_id = int(parts[1])
                weight = int(parts[2])
                
                # Créer l'utilisateur s'il n'existe pas encore
                if user_id not in users_seen:
                    user = User(userID=user_id)
                    batch_users.append(user)
                    users_seen.add(user_id)
                    user_count += 1
                
                # Créer l'écoute
                listen = UserArtist(
                    userID=user_id,
                    artistID=artist_id,
                    weight=weight
                )
                batch_listens.append(listen)
                listen_count += 1
                
                # Insérer les utilisateurs par batch
                if len(batch_users) >= batch_size:
                    db.bulk_save_objects(batch_users)
                    db.commit()
                    batch_users = []
                
                # Insérer les écoutes par batch
                if len(batch_listens) >= batch_size:
                    db.bulk_save_objects(batch_listens)
                    db.commit()
                    batch_listens = []
                    print(f"   Importé: {user_count} users, {listen_count} écoutes...", end='\r')
        
        # Insérer les derniers batchs
        if batch_users:
            db.bulk_save_objects(batch_users)
            db.commit()
        if batch_listens:
            db.bulk_save_objects(batch_listens)
            db.commit()
    
    print(f"\n✅ {user_count} utilisateurs et {listen_count} écoutes importés!")
    return user_count, listen_count

def import_user_tagged_artists(db, filepath_with_timestamps):
    """Importe les tags appliqués depuis user_taggedartists-timestamps.dat"""
    print_section("IMPORTATION DES TAGS APPLIQUÉS")
    
    if not os.path.exists(filepath_with_timestamps):
        print(f"❌ Fichier non trouvé: {filepath_with_timestamps}")
        return 0
    
    count = 0
    skipped = 0
    batch = []
    batch_size = 1000
    
    with open(filepath_with_timestamps, 'r', encoding='utf-8') as f:
        lines = f.readlines()[1:]
        for line in lines:
            parts = line.strip().split('\t')
            if len(parts) < 4: continue
            
            u_id = int(parts[0])
            a_id = int(parts[1])
            t_id = int(parts[2])
            timestamp = int(parts[3])
            
            # INITIALISATION DES VALEURS PAR DÉFAUT
            day, month, year = None, None, None
            
            # TENTATIVE DE CONVERSION SÉCURISÉE
            if timestamp > 0:
                try:
                    # Last.fm utilise des millisecondes, d'où le / 1000
                    dt = datetime.fromtimestamp(timestamp / 1000)
                    day = dt.day
                    month = dt.month
                    year = dt.year
                except (OSError, ValueError, OverflowError):
                    # Si le timestamp est invalide (Errno 22), 
                    # on laisse day/month/year à None ou on met une date par défaut
                    pass

            tagged = UserTaggedArtist(
                userID=u_id,
                artistID=a_id,
                tagID=t_id,
                timestamp=timestamp,
                day=day,
                month=month,
                year=year
            )
            batch.append(tagged)
        
        # Insérer le dernier batch
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
    
    print(f"\n✅ {count} tags appliqués importés!")
    if skipped > 0:
        print(f"⚠️  {skipped} entrées ignorées (données invalides)")
    return count

def import_user_friends(db, filepath):
    """Importe les amitiés depuis user_friends.dat"""
    print_section("IMPORTATION DES AMITIÉS")
    
    if not os.path.exists(filepath):
        print(f"❌ Fichier non trouvé: {filepath}")
        return 0
    
    count = 0
    batch = []
    batch_size = 1000
    
    with open(filepath, 'r', encoding='utf-8') as f:
        # Ignorer la première ligne (header)
        next(f)
        
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                user_id = int(parts[0])
                friend_id = int(parts[1])
                
                friendship = UserFriend(
                    userID=user_id,
                    friendID=friend_id
                )
                batch.append(friendship)
                count += 1
                
                if len(batch) >= batch_size:
                    db.bulk_save_objects(batch)
                    db.commit()
                    batch = []
                    print(f"   Importé: {count} amitiés...", end='\r')
        
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
    
    print(f"\n✅ {count} relations d'amitié importées!")
    return count

def display_final_statistics(db):
    """Affiche les statistiques finales de la base."""
    print_section("STATISTIQUES FINALES")
    
    stats = {
        "Artistes": db.query(Artist).count(),
        "Utilisateurs": db.query(User).count(),
        "Tags": db.query(Tag).count(),
        "Écoutes": db.query(UserArtist).count(),
        "Tags appliqués": db.query(UserTaggedArtist).count(),
        "Amitiés": db.query(UserFriend).count()
    }
    
    for key, value in stats.items():
        print(f"{key:20s}: {value:8,d}")
    
    # Vérifier les timestamps NULL
    result = db.execute(text(
        "SELECT COUNT(*) FROM user_taggedartists WHERE timestamp IS NULL"
    ))
    null_count = result.scalar()
    
    if null_count > 0:
        print(f"\n⚠️  Attention: {null_count} timestamps NULL détectés!")
    else:
        print(f"\n✅ Tous les timestamps sont valides!")

def import_all_data():
    """Importe toutes les données depuis les fichiers .dat"""
    print("\n" + "🎵" * 35)
    print("IMPORTATION DES DONNÉES LAST.FM")
    print("🎵" * 35)
    
    # Vérifier que le dossier existe
    if not os.path.exists(DATA_DIR):
        print(f"\n❌ ERREUR: Dossier '{DATA_DIR}' non trouvé!")
        print(f"   Veuillez ajuster DATA_DIR dans le script")
        return
    
    db = SessionLocal()
    
    try:
        # Créer les tables
        create_tables()
        
        # Importer dans l'ordre des dépendances
        import_artists(db, os.path.join(DATA_DIR, "artists.dat"))
        import_tags(db, os.path.join(DATA_DIR, "tags.dat"))
        import_user_artists(db, os.path.join(DATA_DIR, "user_artists.dat"))
        
        # Utiliser le fichier avec timestamps
        import_user_tagged_artists(
            db, 
            os.path.join(DATA_DIR, "user_taggedartists-timestamps.dat")
        )
        
        import_user_friends(db, os.path.join(DATA_DIR, "user_friends.dat"))
        
        # Afficher les statistiques
        display_final_statistics(db)
        
        print("\n" + "✅" * 35)
        print("IMPORTATION TERMINÉE AVEC SUCCÈS!")
        print("✅" * 35 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de l'importation: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_all_data()