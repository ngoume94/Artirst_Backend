"""SQLAlchemy CRUD Functions for Last.fm Artist API"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import Optional, List, Dict
from datetime import datetime

import models

# =============================================================================
# ARTISTES - CRUD
# =============================================================================

# CREATE
def create_artist(db: Session, name: str, url: str = None, pictureURL: str = None):
    """Crée un nouvel artiste dans la base."""
    db_artist = models.Artist(name=name, url=url, pictureURL=pictureURL)
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist

# READ
def get_artist(db: Session, artist_id: int):
    """Récupère un artiste par son ID."""
    return db.query(models.Artist).filter(models.Artist.id == artist_id).first()

def get_artist_by_name(db: Session, name: str):
    """Récupère un artiste par son nom exact (insensible à la casse)."""
    return db.query(models.Artist).filter(
        func.lower(models.Artist.name) == func.lower(name)
    ).first()

def get_artists(db: Session, skip: int = 0, limit: int = 100, name: str = None):
    """Récupère une liste d'artistes avec filtre par nom optionnel."""
    query = db.query(models.Artist)
    
    if name:
        query = query.filter(models.Artist.name.ilike(f"%{name}%"))
    
    return query.offset(skip).limit(limit).all()

def get_artist_count(db: Session):
    """Retourne le nombre total d'artistes."""
    return db.query(models.Artist).count()

# UPDATE
def update_artist(db: Session, artist_id: int, name: str = None, url: str = None, pictureURL: str = None):
    """Met à jour les informations d'un artiste."""
    db_artist = get_artist(db, artist_id)
    if not db_artist:
        return None
    
    if name is not None:
        db_artist.name = name
    if url is not None:
        db_artist.url = url
    if pictureURL is not None:
        db_artist.pictureURL = pictureURL
    
    db.commit()
    db.refresh(db_artist)
    return db_artist

# DELETE
def delete_artist(db: Session, artist_id: int):
    """Supprime un artiste (supprime d'abord manuellement ses relations)."""
    db_artist = get_artist(db, artist_id)
    if not db_artist:
        return False
    
    # Supprimer manuellement les relations pour éviter les problèmes de CASCADE
    db.query(models.UserArtist).filter(
        models.UserArtist.artistID == artist_id
    ).delete()
    
    db.query(models.UserTaggedArtist).filter(
        models.UserTaggedArtist.artistID == artist_id
    ).delete()
    
    db.delete(db_artist)
    db.commit()
    return True


# =============================================================================
# UTILISATEURS - CRUD
# =============================================================================

# CREATE
def create_user(db: Session, user_id: int):
    """Crée un nouvel utilisateur avec un ID spécifique."""
    # Vérifier si l'utilisateur existe déjà
    existing_user = get_user(db, user_id)
    if existing_user:
        return existing_user
    
    db_user = models.User(userID=user_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# READ
def get_user(db: Session, user_id: int):
    """Récupère un utilisateur par son ID."""
    return db.query(models.User).filter(models.User.userID == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Récupère une liste d'utilisateurs paginée."""
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user_count(db: Session):
    """Retourne le nombre total d'utilisateurs."""
    return db.query(models.User).count()

# UPDATE
# Les utilisateurs n'ont que l'ID comme attribut, donc pas de fonction update nécessaire

# DELETE
def delete_user(db: Session, user_id: int):
    """Supprime un utilisateur (supprime d'abord manuellement ses relations)."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    # Supprimer manuellement toutes les relations
    db.query(models.UserArtist).filter(
        models.UserArtist.userID == user_id
    ).delete()
    
    db.query(models.UserTaggedArtist).filter(
        models.UserTaggedArtist.userID == user_id
    ).delete()
    
    db.query(models.UserFriend).filter(
        or_(
            models.UserFriend.userID == user_id,
            models.UserFriend.friendID == user_id
        )
    ).delete()
    
    db.delete(db_user)
    db.commit()
    return True


# =============================================================================
# TAGS - CRUD
# =============================================================================

# CREATE
def create_tag(db: Session, tag_value: str):
    """Crée un nouveau tag."""
    # Vérifier si le tag existe déjà
    existing_tag = get_tag_by_value(db, tag_value)
    if existing_tag:
        return existing_tag
    
    db_tag = models.Tag(tagValue=tag_value)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

# READ
def get_tag_by_id(db: Session, tag_id: int):
    """Récupère un tag par son ID."""
    return db.query(models.Tag).filter(models.Tag.tagID == tag_id).first()

def get_tag_by_value(db: Session, tag_value: str):
    """Récupère un tag par sa valeur (insensible à la casse)."""
    return db.query(models.Tag).filter(
        func.lower(models.Tag.tagValue) == func.lower(tag_value)
    ).first()

def get_all_tags(db: Session, skip: int = 0, limit: int = 100):
    """Récupère tous les tags disponibles."""
    return db.query(models.Tag).offset(skip).limit(limit).all()

def get_tag_count(db: Session):
    """Retourne le nombre total de tags."""
    return db.query(models.Tag).count()

# UPDATE
def update_tag(db: Session, tag_id: int, new_value: str):
    """Met à jour la valeur d'un tag."""
    db_tag = get_tag_by_id(db, tag_id)
    if not db_tag:
        return None
    
    db_tag.tagValue = new_value
    db.commit()
    db.refresh(db_tag)
    return db_tag

# DELETE
def delete_tag(db: Session, tag_id: int):
    """Supprime un tag (supprime d'abord manuellement ses utilisations)."""
    db_tag = get_tag_by_id(db, tag_id)
    if not db_tag:
        return False
    
    # Supprimer manuellement toutes les utilisations du tag
    # car CASCADE ne fonctionne pas bien avec les clés primaires composites contenant des NULL
    db.query(models.UserTaggedArtist).filter(
        models.UserTaggedArtist.tagID == tag_id
    ).delete()
    
    db.delete(db_tag)
    db.commit()
    return True


# =============================================================================
# USER_ARTISTS (ÉCOUTES) - CRUD
# =============================================================================

# CREATE
def create_user_artist(db: Session, user_id: int, artist_id: int, weight: int):
    """Enregistre une nouvelle relation d'écoute utilisateur-artiste."""
    # Vérifier que l'utilisateur et l'artiste existent
    user = get_user(db, user_id)
    artist = get_artist(db, artist_id)
    
    if not user:
        # Créer l'utilisateur s'il n'existe pas
        user = create_user(db, user_id)
    
    if not artist:
        return None
    
    # Vérifier si la relation existe déjà
    existing = get_user_listening_count(db, user_id, artist_id)
    if existing:
        # Mettre à jour le weight existant
        return update_user_artist(db, user_id, artist_id, weight)
    
    db_user_artist = models.UserArtist(userID=user_id, artistID=artist_id, weight=weight)
    db.add(db_user_artist)
    db.commit()
    db.refresh(db_user_artist)
    return db_user_artist

# READ
def get_user_listening_count(db: Session, user_id: int, artist_id: int):
    """Récupère la relation d'écoute pour un couple utilisateur/artiste."""
    return db.query(models.UserArtist).filter(
        models.UserArtist.userID == user_id,
        models.UserArtist.artistID == artist_id
    ).first()

def get_user_artists(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Récupère tous les artistes écoutés par un utilisateur."""
    return (
        db.query(models.UserArtist)
        .filter(models.UserArtist.userID == user_id)
        .order_by(models.UserArtist.weight.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_top_artists_for_user(db: Session, user_id: int, limit: int = 10):
    """Récupère les artistes les plus écoutés par un utilisateur."""
    return (
        db.query(models.UserArtist)
        .filter(models.UserArtist.userID == user_id)
        .order_by(models.UserArtist.weight.desc())
        .limit(limit)
        .all()
    )

def get_artist_listeners(db: Session, artist_id: int, skip: int = 0, limit: int = 100):
    """Récupère tous les utilisateurs qui ont écouté un artiste."""
    return (
        db.query(models.UserArtist)
        .filter(models.UserArtist.artistID == artist_id)
        .order_by(models.UserArtist.weight.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_listening_count(db: Session):
    """Retourne le nombre total de relations user-artist."""
    return db.query(models.UserArtist).count()

# UPDATE
def update_user_artist(db: Session, user_id: int, artist_id: int, new_weight: int):
    """Met à jour le nombre d'écoutes pour un utilisateur et un artiste."""
    db_user_artist = get_user_listening_count(db, user_id, artist_id)
    if not db_user_artist:
        return None
    
    db_user_artist.weight = new_weight
    db.commit()
    db.refresh(db_user_artist)
    return db_user_artist

def increment_listening_weight(db: Session, user_id: int, artist_id: int, increment: int = 1):
    """Incrémente le poids d'écoute d'un certain nombre."""
    db_user_artist = get_user_listening_count(db, user_id, artist_id)
    if not db_user_artist:
        # Créer la relation si elle n'existe pas
        return create_user_artist(db, user_id, artist_id, increment)
    
    db_user_artist.weight += increment
    db.commit()
    db.refresh(db_user_artist)
    return db_user_artist

# DELETE
def delete_user_artist(db: Session, user_id: int, artist_id: int):
    """Supprime une relation d'écoute utilisateur-artiste."""
    db_user_artist = get_user_listening_count(db, user_id, artist_id)
    if not db_user_artist:
        return False
    
    db.delete(db_user_artist)
    db.commit()
    return True


# =============================================================================
# USER_TAGGED_ARTISTS (TAGS APPLIQUÉS) - CRUD
# =============================================================================

# CREATE
def create_user_tagged_artist(
    db: Session, 
    user_id: int, 
    artist_id: int, 
    tag_id: int,
    day: int = None,
    month: int = None,
    year: int = None,
    timestamp: int = None
):
    """Crée une nouvelle assignation de tag."""
    # Générer un timestamp si non fourni
    if timestamp is None:
        timestamp = int(datetime.now().timestamp() * 1000)
    
    # Extraire date si non fournie
    if day is None or month is None or year is None:
        dt = datetime.fromtimestamp(timestamp / 1000)
        day = dt.day
        month = dt.month
        year = dt.year
    
    db_tagged = models.UserTaggedArtist(
        userID=user_id,
        artistID=artist_id,
        tagID=tag_id,
        timestamp=timestamp,
        day=day,
        month=month,
        year=year
    )
    db.add(db_tagged)
    db.commit()
    db.refresh(db_tagged)
    return db_tagged

# READ
def get_user_tagged_artists(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    artist_id: Optional[int] = None, 
    user_id: Optional[int] = None,
    tag_id: Optional[int] = None
):
    """Récupère les assignations de tags avec filtres optionnels."""
    query = db.query(models.UserTaggedArtist)

    if artist_id is not None:
        query = query.filter(models.UserTaggedArtist.artistID == artist_id)
    if user_id is not None:
        query = query.filter(models.UserTaggedArtist.userID == user_id)
    if tag_id is not None:
        query = query.filter(models.UserTaggedArtist.tagID == tag_id)

    return query.offset(skip).limit(limit).all()

def get_artist_tags(db: Session, artist_id: int, limit: int = 10):
    """Récupère les tags les plus utilisés pour un artiste."""
    return (
        db.query(
            models.Tag.tagValue,
            func.count(models.UserTaggedArtist.tagID).label('count')
        )
        .join(models.UserTaggedArtist)
        .filter(models.UserTaggedArtist.artistID == artist_id)
        .group_by(models.Tag.tagID)
        .order_by(func.count(models.UserTaggedArtist.tagID).desc())
        .limit(limit)
        .all()
    )

def get_artists_by_tag(db: Session, tag_value: str, skip: int = 0, limit: int = 100):
    """Récupère les artistes associés à un tag spécifique."""
    return (
        db.query(models.Artist)
        .join(models.UserTaggedArtist)
        .join(models.Tag)
        .filter(func.lower(models.Tag.tagValue) == func.lower(tag_value))
        .distinct()
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_tagged_count(db: Session):
    """Retourne le nombre total d'assignations de tags."""
    return db.query(models.UserTaggedArtist).count()

# UPDATE
# Pas vraiment de mise à jour pour les tags appliqués (on supprime et recrée)

# DELETE
def delete_user_tagged_artist(db: Session, user_id: int, artist_id: int, tag_id: int, timestamp: int):
    """Supprime une assignation de tag spécifique."""
    db_tagged = db.query(models.UserTaggedArtist).filter(
        models.UserTaggedArtist.userID == user_id,
        models.UserTaggedArtist.artistID == artist_id,
        models.UserTaggedArtist.tagID == tag_id,
        models.UserTaggedArtist.timestamp == timestamp
    ).first()
    
    if not db_tagged:
        return False
    
    db.delete(db_tagged)
    db.commit()
    return True

def delete_all_user_tags_for_artist(db: Session, user_id: int, artist_id: int):
    """Supprime tous les tags d'un utilisateur pour un artiste."""
    deleted_count = db.query(models.UserTaggedArtist).filter(
        models.UserTaggedArtist.userID == user_id,
        models.UserTaggedArtist.artistID == artist_id
    ).delete()
    
    db.commit()
    return deleted_count


# =============================================================================
# USER_FRIENDS (AMITIÉS) - CRUD
# =============================================================================

# CREATE
def create_friendship(db: Session, user_id: int, friend_id: int, bidirectional: bool = True):
    """
    Crée une relation d'amitié.
    Si bidirectional=True, crée les deux directions de l'amitié.
    """
    # Vérifier que les utilisateurs existent
    user = get_user(db, user_id)
    friend = get_user(db, friend_id)
    
    if not user:
        user = create_user(db, user_id)
    if not friend:
        friend = create_user(db, friend_id)
    
    # Vérifier si l'amitié existe déjà
    if are_friends(db, user_id, friend_id):
        return None
    
    # Créer la première direction
    friendship1 = models.UserFriend(userID=user_id, friendID=friend_id)
    db.add(friendship1)
    
    # Créer la direction inverse si demandé
    if bidirectional:
        friendship2 = models.UserFriend(userID=friend_id, friendID=user_id)
        db.add(friendship2)
    
    db.commit()
    db.refresh(friendship1)
    return friendship1

# READ
def get_user_friends(db: Session, user_id: int):
    """Récupère toutes les relations d'amitié d'un utilisateur (bidirectionnel)."""
    return db.query(models.UserFriend).filter(
        or_(
            models.UserFriend.userID == user_id,
            models.UserFriend.friendID == user_id
        )
    ).all()

def get_user_friends_ids(db: Session, user_id: int) -> List[int]:
    """Récupère uniquement les IDs des amis d'un utilisateur."""
    friendships = get_user_friends(db, user_id)
    friends_ids = set()
    
    for friendship in friendships:
        if friendship.userID == user_id:
            friends_ids.add(friendship.friendID)
        else:
            friends_ids.add(friendship.userID)
    
    return list(friends_ids)

def are_friends(db: Session, user_id1: int, user_id2: int) -> bool:
    """Vérifie si deux utilisateurs sont amis."""
    return db.query(models.UserFriend).filter(
        or_(
            and_(models.UserFriend.userID == user_id1, models.UserFriend.friendID == user_id2),
            and_(models.UserFriend.userID == user_id2, models.UserFriend.friendID == user_id1)
        )
    ).first() is not None

def get_friendship_count(db: Session):
    """Retourne le nombre total de relations d'amitié."""
    return db.query(models.UserFriend).count()

# UPDATE
# Pas de mise à jour pour les amitiés (on crée ou supprime)

# DELETE
def delete_friendship(db: Session, user_id: int, friend_id: int, bidirectional: bool = True):
    """
    Supprime une relation d'amitié.
    Si bidirectional=True, supprime les deux directions.
    """
    deleted = 0
    
    # Supprimer la première direction
    friendship1 = db.query(models.UserFriend).filter(
        models.UserFriend.userID == user_id,
        models.UserFriend.friendID == friend_id
    ).first()
    
    if friendship1:
        db.delete(friendship1)
        deleted += 1
    
    # Supprimer la direction inverse si demandé
    if bidirectional:
        friendship2 = db.query(models.UserFriend).filter(
            models.UserFriend.userID == friend_id,
            models.UserFriend.friendID == user_id
        ).first()
        
        if friendship2:
            db.delete(friendship2)
            deleted += 1
    
    if deleted > 0:
        db.commit()
        return True
    
    return False


# =============================================================================
# REQUÊTES ANALYTIQUES
# =============================================================================

def get_global_statistics(db: Session) -> Dict[str, int]:
    """Retourne un dictionnaire des statistiques globales de la base."""
    return {
        "total_artists": get_artist_count(db),
        "total_users": get_user_count(db),
        "total_tags": get_tag_count(db),
        "total_listens": get_listening_count(db),
        "total_tagged": get_tagged_count(db),
        "total_friendships": get_friendship_count(db)
    }

def get_most_popular_artists(db: Session, limit: int = 10):
    """Retourne les artistes ayant le plus gros cumul d'écoutes."""
    return (
        db.query(
            models.Artist.id,
            models.Artist.name, 
            func.sum(models.UserArtist.weight).label('total_weight')
        )
        .join(models.UserArtist)
        .group_by(models.Artist.id)
        .order_by(func.sum(models.UserArtist.weight).desc())
        .limit(limit)
        .all()
    )

def get_most_popular_tags(db: Session, limit: int = 10):
    """Retourne les tags les plus utilisés."""
    return (
        db.query(
            models.Tag.tagID,
            models.Tag.tagValue,
            func.count(models.UserTaggedArtist.tagID).label('usage_count')
        )
        .join(models.UserTaggedArtist)
        .group_by(models.Tag.tagID)
        .order_by(func.count(models.UserTaggedArtist.tagID).desc())
        .limit(limit)
        .all()
    )

def get_most_active_users(db: Session, limit: int = 10):
    """Retourne les utilisateurs les plus actifs."""
    return (
        db.query(
            models.User.userID,
            func.count(models.UserArtist.userID).label('listen_count')
        )
        .join(models.UserArtist)
        .group_by(models.User.userID)
        .order_by(func.count(models.UserArtist.userID).desc())
        .limit(limit)
        .all()
    )

def get_user_statistics(db: Session, user_id: int) -> Optional[Dict]:
    """Retourne des statistiques détaillées pour un utilisateur."""
    user = get_user(db, user_id)
    
    if not user:
        return None
    
    return {
        "userID": user_id,
        "artists_listened": db.query(models.UserArtist).filter(
            models.UserArtist.userID == user_id
        ).count(),
        "tags_created": db.query(models.UserTaggedArtist).filter(
            models.UserTaggedArtist.userID == user_id
        ).count(),
        "friends_count": len(get_user_friends_ids(db, user_id)),
        "top_artists": get_top_artists_for_user(db, user_id, limit=5)
    }

def get_artist_statistics(db: Session, artist_id: int) -> Optional[Dict]:
    """Retourne des statistiques détaillées pour un artiste."""
    artist = get_artist(db, artist_id)
    
    if not artist:
        return None
    
    total_weight = db.query(
        func.sum(models.UserArtist.weight)
    ).filter(
        models.UserArtist.artistID == artist_id
    ).scalar() or 0
    
    listener_count = db.query(models.UserArtist).filter(
        models.UserArtist.artistID == artist_id
    ).count()
    
    return {
        "artistID": artist_id,
        "name": artist.name,
        "total_listens": total_weight,
        "listener_count": listener_count,
        "tags_count": db.query(models.UserTaggedArtist).filter(
            models.UserTaggedArtist.artistID == artist_id
        ).count(),
        "top_tags": get_artist_tags(db, artist_id, limit=5)
    }

def search_artists_by_tag(db: Session, tags: List[str], skip: int = 0, limit: int = 100):
    """Recherche des artistes qui ont TOUS les tags spécifiés."""
    query = db.query(models.Artist)
    
    for tag_value in tags:
        query = query.filter(
            models.Artist.id.in_(
                db.query(models.UserTaggedArtist.artistID)
                .join(models.Tag)
                .filter(func.lower(models.Tag.tagValue) == func.lower(tag_value))
            )
        )
    
    return query.distinct().offset(skip).limit(limit).all()

def get_similar_users(db: Session, user_id: int, limit: int = 10):
    """Trouve des utilisateurs similaires basés sur les artistes écoutés en commun."""
    user_artists = db.query(models.UserArtist.artistID).filter(
        models.UserArtist.userID == user_id
    ).subquery()
    
    similar_users = (
        db.query(
            models.UserArtist.userID,
            func.count(models.UserArtist.artistID).label('common_artists')
        )
        .filter(
            models.UserArtist.artistID.in_(user_artists),
            models.UserArtist.userID != user_id
        )
        .group_by(models.UserArtist.userID)
        .order_by(func.count(models.UserArtist.artistID).desc())
        .limit(limit)
        .all()
    )
    
    return similar_users

def recommend_artists_for_user(db: Session, user_id: int, limit: int = 10):
    """Recommande des artistes basés sur les utilisateurs similaires."""
    similar_users = get_similar_users(db, user_id, limit=20)
    similar_user_ids = [u[0] for u in similar_users]
    
    listened_artists = db.query(models.UserArtist.artistID).filter(
        models.UserArtist.userID == user_id
    ).subquery()
    
    recommended = (
        db.query(
            models.Artist,
            func.sum(models.UserArtist.weight).label('total_weight')
        )
        .join(models.UserArtist)
        .filter(
            models.UserArtist.userID.in_(similar_user_ids),
            models.Artist.id.notin_(listened_artists)
        )
        .group_by(models.Artist.id)
        .order_by(func.sum(models.UserArtist.weight).desc())
        .limit(limit)
        .all()
    )
    
    return recommended