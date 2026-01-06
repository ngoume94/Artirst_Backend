"""
API REST complète pour le dataset Last.fm
Artistes, Utilisateurs, Tags, Écoutes, Recommandations
"""
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

import models
import schemas
import query_helpers as qh
from database import SessionLocal, engine

# Création automatique des tables
models.Base.metadata.create_all(bind=engine)

api_description = """ 
Bienvenue dans l'API **Artirst_Backend** Cette API permet d'explorer et de gérer un jeu de données musical inspiré de la plateforme 
[Last.fm](https://www.last.fm/). Elle est conçue pour manipuler des données d'artistes, 
les comportements d'écoute des utilisateurs et l'organisation par tags.

###  Fonctionnalités disponibles :
* **Artistes** : Créer, modifier ou rechercher des artistes (nom, URL, photos).
* **Utilisateurs & Écoutes** : Gérer les profils et enregistrer le nombre d'écoutes (`weight`) pour chaque artiste.
* **Système de Tags** : Appliquer des étiquettes personnalisées aux artistes pour les classer par genre ou humeur.
* **Social & Analytics** : Gérer les listes d'amis et consulter des statistiques globales sur l'utilisation de la plateforme.
* **Recherche & Recommandations** : Trouver les artistes les plus populaires ou filtrer par tags spécifiques.

###  Navigation technique :
* **Pagination** : Tous les endpoints de liste supportent les paramètres `skip` et `limit`.
* **Tests en direct** : Utilisez l'interface **Swagger** ci-dessous pour tester vos requêtes avec des exemples pré-remplis.
* **Gestion d'erreurs** : L'API retourne des codes HTTP standardisés (404 pour un ID inconnu, 422 pour une erreur de validation).

"""

app = FastAPI(
    title="Last.fm Music API",
    description=api_description,
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dépendance DB
def get_db():
    """Crée une session de base de données pour chaque requête"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
# SECTION : ARTISTES (CRUD)
# =============================================================================

@app.post(
    "/artists/", 
    response_model=schemas.ArtistSimple, 
    tags=["Artists"],
    status_code=status.HTTP_201_CREATED,
    summary="Créer un artiste",
    response_description="L'artiste créé avec son ID"
)
def create_artist(artist: schemas.ArtistCreate, db: Session = Depends(get_db)):
    """
    Crée un nouvel artiste dans la base de données.
    
    - **name**: Nom de l'artiste (requis)
    - **url**: URL Last.fm de l'artiste (optionnel)
    - **pictureURL**: URL de l'image de l'artiste (optionnel)
    """
    return qh.create_artist(db, **artist.model_dump())


@app.get(
    "/artists/", 
    response_model=schemas.PaginatedArtists,
    tags=["Artists"],
    summary="Lister les artistes",
    response_description="Liste paginée d'artistes"
)
def list_artists(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(50, ge=1, le=500, description="Nombre max d'éléments à retourner"),
    name: Optional[str] = Query(None, description="Rechercher par nom (partiel)"),
    db: Session = Depends(get_db)
):
    """
    Récupère une liste paginée d'artistes avec recherche optionnelle.
    
    Limite maximale : 500 artistes par requête
    """
    artists = qh.get_artists(db, skip=skip, limit=limit, name=name)
    total = qh.get_artist_count(db)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": artists
    }


@app.get(
    "/artists/{artist_id}", 
    response_model=schemas.ArtistDetailed, 
    tags=["Artists"],
    summary="Détails d'un artiste",
    response_description="Artiste avec ses statistiques"
)
def get_artist(artist_id: int, db: Session = Depends(get_db)):
    """
    Récupère les informations complètes d'un artiste avec ses statistiques :
    - Total d'écoutes
    - Nombre d'auditeurs
    - Top 5 tags
    """
    stats = qh.get_artist_statistics(db, artist_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artiste {artist_id} introuvable"
        )
    
    # Convertir les top_tags en schéma approprié
    top_tags = [
        schemas.ArtistTagSummary(tagValue=tag_value, count=count)
        for tag_value, count in stats["top_tags"]
    ]
    
    return {
        "id": stats["artistID"],
        "name": stats["name"],
        "url": None,  # Non fourni par get_artist_statistics
        "pictureURL": None,
        "total_listens": stats["total_listens"],
        "listener_count": stats["listener_count"],
        "top_tags": top_tags
    }


@app.put(
    "/artists/{artist_id}", 
    response_model=schemas.ArtistSimple, 
    tags=["Artists"],
    summary="Mettre à jour un artiste"
)
def update_artist(
    artist_id: int, 
    artist_update: schemas.ArtistUpdate, 
    db: Session = Depends(get_db)
):
    """Met à jour les informations d'un artiste (tous les champs sont optionnels)"""
    updated = qh.update_artist(db, artist_id, **artist_update.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artiste {artist_id} introuvable"
        )
    return updated


@app.delete(
    "/artists/{artist_id}", 
    tags=["Artists"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un artiste"
)
def delete_artist(artist_id: int, db: Session = Depends(get_db)):
    """Supprime un artiste et toutes ses relations (écoutes, tags)"""
    success = qh.delete_artist(db, artist_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artiste {artist_id} introuvable"
        )
    return None


@app.get(
    "/artists/{artist_id}/listeners",
    response_model=List[schemas.ArtistListenerWithDetails],
    tags=["Artists"],
    summary="Auditeurs d'un artiste"
)
def get_artist_listeners(
    artist_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Récupère la liste des utilisateurs qui ont écouté cet artiste"""
    listeners = qh.get_artist_listeners(db, artist_id, skip=skip, limit=limit)
    return [
        {
            "weight": listener.weight,
            "user": {"userID": listener.userID}
        }
        for listener in listeners
    ]


@app.get(
    "/artists/{artist_id}/tags",
    response_model=List[schemas.ArtistTagSummary],
    tags=["Artists"],
    summary="Tags d'un artiste"
)
def get_artist_tags(
    artist_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Récupère les tags les plus utilisés pour cet artiste"""
    tags = qh.get_artist_tags(db, artist_id, limit=limit)
    return [
        schemas.ArtistTagSummary(tagValue=tag_value, count=count)
        for tag_value, count in tags
    ]


# =============================================================================
# SECTION : UTILISATEURS (CRUD)
# =============================================================================

@app.post(
    "/users/", 
    response_model=schemas.UserSimple, 
    tags=["Users"],
    status_code=status.HTTP_201_CREATED,
    summary="Créer un utilisateur"
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Crée un nouvel utilisateur avec un ID spécifique"""
    return qh.create_user(db, user.userID)


@app.get(
    "/users/",
    response_model=schemas.PaginatedUsers,
    tags=["Users"],
    summary="Lister les utilisateurs"
)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Récupère une liste paginée d'utilisateurs"""
    users = qh.get_users(db, skip=skip, limit=limit)
    total = qh.get_user_count(db)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": users
    }


@app.get(
    "/users/{user_id}", 
    response_model=schemas.UserStats, 
    tags=["Users"],
    summary="Profil utilisateur"
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Récupère le profil complet d'un utilisateur avec ses statistiques :
    - Nombre d'artistes écoutés
    - Nombre de tags créés
    - Nombre d'amis
    """
    stats = qh.get_user_statistics(db, user_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur {user_id} introuvable"
        )
    
    # Calculer le total d'écoutes
    total_listens = sum(artist.weight for artist in stats["top_artists"])
    
    return {
        "userID": stats["userID"],
        "artists_listened": stats["artists_listened"],
        "tags_created": stats["tags_created"],
        "friends_count": stats["friends_count"],
        "total_listens": total_listens
    }


@app.delete(
    "/users/{user_id}",
    tags=["Users"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un utilisateur"
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Supprime un utilisateur et toutes ses relations"""
    success = qh.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur {user_id} introuvable"
        )
    return None


@app.get(
    "/users/{user_id}/artists",
    response_model=List[schemas.UserArtistWithDetails],
    tags=["Users"],
    summary="Artistes écoutés par un utilisateur"
)
def get_user_artists(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Récupère la liste des artistes écoutés par un utilisateur, triés par nombre d'écoutes"""
    artists = qh.get_user_artists(db, user_id, skip=skip, limit=limit)
    return [
        {
            "weight": artist.weight,
            "artist": {
                "id": artist.artist.id,
                "name": artist.artist.name,
                "url": artist.artist.url,
                "pictureURL": artist.artist.pictureURL
            }
        }
        for artist in artists
    ]


@app.get(
    "/users/{user_id}/friends",
    response_model=List[int],
    tags=["Users"],
    summary="Amis d'un utilisateur"
)
def get_user_friends(user_id: int, db: Session = Depends(get_db)):
    """Récupère la liste des IDs des amis d'un utilisateur"""
    return qh.get_user_friends_ids(db, user_id)


@app.get(
    "/users/{user_id}/recommendations",
    response_model=List[schemas.RecommendedArtist],
    tags=["Users"],
    summary="Recommandations personnalisées"
)
def get_recommendations(
    user_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Recommande des artistes à un utilisateur basé sur :
    - Les utilisateurs avec des goûts similaires
    - Les artistes populaires qu'il n'a pas encore écoutés
    """
    recommendations = qh.recommend_artists_for_user(db, user_id, limit=limit)
    return [
        {
            "artist": {
                "id": artist.id,
                "name": artist.name,
                "url": artist.url,
                "pictureURL": artist.pictureURL
            },
            "score": int(score)
        }
        for artist, score in recommendations
    ]


# =============================================================================
# SECTION : TAGS (CRUD)
# =============================================================================

@app.post(
    "/tags/", 
    response_model=schemas.TagSimple, 
    tags=["Tags"],
    status_code=status.HTTP_201_CREATED,
    summary="Créer un tag"
)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    """Crée un nouveau tag (ou retourne celui existant)"""
    return qh.create_tag(db, tag.tagValue)


@app.get(
    "/tags/", 
    response_model=schemas.PaginatedTags,
    tags=["Tags"],
    summary="Lister les tags"
)
def list_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Récupère une liste paginée de tous les tags"""
    tags = qh.get_all_tags(db, skip=skip, limit=limit)
    total = qh.get_tag_count(db)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": tags
    }


@app.get(
    "/tags/{tag_id}",
    response_model=schemas.TagDetailed,
    tags=["Tags"],
    summary="Détails d'un tag"
)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """Récupère les informations d'un tag avec son nombre d'utilisations"""
    tag = qh.get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} introuvable"
        )
    
    # Compter les utilisations
    usage_count = db.query(models.UserTaggedArtist).filter(
        models.UserTaggedArtist.tagID == tag_id
    ).count()
    
    return {
        "tagID": tag.tagID,
        "tagValue": tag.tagValue,
        "usage_count": usage_count
    }


@app.put(
    "/tags/{tag_id}",
    response_model=schemas.TagSimple,
    tags=["Tags"],
    summary="Mettre à jour un tag"
)
def update_tag(
    tag_id: int,
    tag_update: schemas.TagUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour la valeur d'un tag"""
    updated = qh.update_tag(db, tag_id, tag_update.tagValue)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} introuvable"
        )
    return updated


@app.delete(
    "/tags/{tag_id}",
    tags=["Tags"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un tag"
)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """Supprime un tag et toutes ses utilisations"""
    success = qh.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} introuvable"
        )
    return None


@app.get(
    "/tags/{tag_id}/artists",
    response_model=List[schemas.ArtistSimple],
    tags=["Tags"],
    summary="Artistes associés à un tag"
)
def get_artists_by_tag_id(
    tag_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Récupère tous les artistes associés à un tag"""
    tag = qh.get_tag_by_id(db, tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} introuvable"
        )
    
    return qh.get_artists_by_tag(db, tag.tagValue, skip=skip, limit=limit)


# =============================================================================
# SECTION : ÉCOUTES (USER-ARTIST)
# =============================================================================

@app.post(
    "/listens/",
    response_model=schemas.UserArtistResponse,
    tags=["Listens"],
    status_code=status.HTTP_201_CREATED,
    summary="Enregistrer une écoute"
)
def create_listen(listen: schemas.UserArtistCreate, db: Session = Depends(get_db)):
    """Enregistre ou met à jour le nombre d'écoutes d'un artiste par un utilisateur"""
    result = qh.create_user_artist(db, listen.userID, listen.artistID, listen.weight)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artiste introuvable"
        )
    return result


@app.put(
    "/listens/{user_id}/{artist_id}",
    response_model=schemas.UserArtistResponse,
    tags=["Listens"],
    summary="Mettre à jour une écoute"
)
def update_listen(
    user_id: int,
    artist_id: int,
    listen_update: schemas.UserArtistUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour le nombre d'écoutes"""
    result = qh.update_user_artist(db, user_id, artist_id, listen_update.weight)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Écoute introuvable"
        )
    return result


@app.delete(
    "/listens/{user_id}/{artist_id}",
    tags=["Listens"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une écoute"
)
def delete_listen(user_id: int, artist_id: int, db: Session = Depends(get_db)):
    """Supprime une relation d'écoute"""
    success = qh.delete_user_artist(db, user_id, artist_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Écoute introuvable"
        )
    return None


# =============================================================================
# SECTION : TAGS APPLIQUÉS
# =============================================================================

@app.post(
    "/tagged-artists/",
    response_model=schemas.UserTaggedArtistResponse,
    tags=["Tagged Artists"],
    status_code=status.HTTP_201_CREATED,
    summary="Appliquer un tag à un artiste"
)
def create_tagged_artist(
    tagged: schemas.UserTaggedArtistCreate,
    db: Session = Depends(get_db)
):
    """Un utilisateur applique un tag à un artiste"""
    result = qh.create_user_tagged_artist(
        db,
        tagged.userID,
        tagged.artistID,
        tagged.tagID,
        tagged.day,
        tagged.month,
        tagged.year,
        tagged.timestamp
    )
    return result


@app.get(
    "/tagged-artists/",
    response_model=List[schemas.UserTaggedArtistWithDetails],
    tags=["Tagged Artists"],
    summary="Lister les tags appliqués"
)
def list_tagged_artists(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    artist_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    tag_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère les tags appliqués avec filtres optionnels"""
    tagged = qh.get_user_tagged_artists(
        db,
        skip=skip,
        limit=limit,
        artist_id=artist_id,
        user_id=user_id,
        tag_id=tag_id
    )
    
    return [
        {
            "timestamp": t.timestamp,
            "day": t.day,
            "month": t.month,
            "year": t.year,
            "artist": {
                "id": t.artist.id,
                "name": t.artist.name,
                "url": t.artist.url,
                "pictureURL": t.artist.pictureURL
            },
            "tag": {
                "tagID": t.tag.tagID,
                "tagValue": t.tag.tagValue
            }
        }
        for t in tagged
    ]


# =============================================================================
# SECTION : AMITIÉS
# =============================================================================

@app.post(
    "/friendships/",
    response_model=schemas.UserFriendResponse,
    tags=["Friendships"],
    status_code=status.HTTP_201_CREATED,
    summary="Créer une amitié"
)
def create_friendship(friendship: schemas.UserFriendCreate, db: Session = Depends(get_db)):
    """Crée une relation d'amitié entre deux utilisateurs"""
    result = qh.create_friendship(
        db,
        friendship.userID,
        friendship.friendID,
        friendship.bidirectional
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'amitié existe déjà"
        )
    return result


@app.delete(
    "/friendships/{user_id}/{friend_id}",
    tags=["Friendships"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une amitié"
)
def delete_friendship(
    user_id: int,
    friend_id: int,
    bidirectional: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Supprime une relation d'amitié"""
    success = qh.delete_friendship(db, user_id, friend_id, bidirectional)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Amitié introuvable"
        )
    return None


# =============================================================================
# SECTION : ANALYTICS & STATISTIQUES
# =============================================================================

@app.get(
    "/analytics/global",
    response_model=schemas.GlobalStats,
    tags=["Analytics"],
    summary="Statistiques globales"
)
def get_global_stats(db: Session = Depends(get_db)):
    """Retourne les statistiques globales de la base de données"""
    return qh.get_global_statistics(db)


@app.get(
    "/analytics/popular-artists",
    response_model=List[schemas.PopularArtist],
    tags=["Analytics"],
    summary="Artistes les plus populaires"
)
def get_popular_artists(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retourne les artistes avec le plus d'écoutes cumulées"""
    popular = qh.get_most_popular_artists(db, limit=limit)
    return [
        {"id": artist_id, "name": name, "total_weight": weight}
        for artist_id, name, weight in popular
    ]


@app.get(
    "/analytics/popular-tags",
    response_model=List[schemas.PopularTag],
    tags=["Analytics"],
    summary="Tags les plus utilisés"
)
def get_popular_tags(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retourne les tags les plus utilisés"""
    popular = qh.get_most_popular_tags(db, limit=limit)
    return [
        {"tagID": tag_id, "tagValue": tag_value, "usage_count": count}
        for tag_id, tag_value, count in popular
    ]


@app.get(
    "/analytics/active-users",
    response_model=List[schemas.ActiveUser],
    tags=["Analytics"],
    summary="Utilisateurs les plus actifs"
)
def get_active_users(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retourne les utilisateurs avec le plus d'artistes écoutés"""
    active = qh.get_most_active_users(db, limit=limit)
    return [
        {"userID": user_id, "listen_count": count}
        for user_id, count in active
    ]


@app.get(
    "/analytics/similar-users/{user_id}",
    response_model=List[schemas.SimilarUser],
    tags=["Analytics"],
    summary="Utilisateurs similaires"
)
def get_similar_users(
    user_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Trouve des utilisateurs avec des goûts musicaux similaires"""
    similar = qh.get_similar_users(db, user_id, limit=limit)
    return [
        {"userID": uid, "common_artists": count}
        for uid, count in similar
    ]


# =============================================================================
# SECTION : RECHERCHE AVANCÉE
# =============================================================================

@app.get(
    "/search/artists",
    response_model=List[schemas.ArtistSimple],
    tags=["Search"],
    summary="Rechercher des artistes par tags"
)
def search_artists_by_tags(
    tags: List[str] = Query(..., description="Liste de tags (l'artiste doit avoir TOUS ces tags)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Recherche des artistes qui ont TOUS les tags spécifiés.
    
    Exemple : /search/artists?tags=rock&tags=alternative
    """
    return qh.search_artists_by_tag(db, tags, skip=skip, limit=limit)


# =============================================================================
# ROOT & HEALTH CHECK
# =============================================================================

@app.get("/", tags=["Root"])
def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Bienvenue sur l'API Last.fm",
        "version": "3.0.0",
        "documentation": "/docs",
        "endpoints": {
            "artists": "/artists/",
            "users": "/users/",
            "tags": "/tags/",
            "analytics": "/analytics/global"
        }
    }


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Vérifie l'état de l'API et de la base de données"""
    try:
        # Tester la connexion à la DB
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {str(e)}"
        )

