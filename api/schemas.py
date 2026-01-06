"""
Schémas Pydantic pour l'API Last.fm
"""
from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List
from datetime import datetime

# =============================================================================
# 1. BASES (Attributs partagés)
# =============================================================================

class ArtistBase(BaseModel):
    """Schéma de base pour un artiste"""
    name: str = Field(..., min_length=1, max_length=500, description="Nom de l'artiste")
    url: Optional[str] = Field(None, max_length=500, description="URL Last.fm de l'artiste")
    pictureURL: Optional[str] = Field(None, max_length=500, description="URL de l'image de l'artiste")


class UserBase(BaseModel):
    """Schéma de base pour un utilisateur"""
    userID: int = Field(..., gt=0, description="ID unique de l'utilisateur")


class TagBase(BaseModel):
    """Schéma de base pour un tag"""
    tagValue: str = Field(..., min_length=1, max_length=100, description="Valeur du tag")


# =============================================================================
# 2. CRUD - SCHÉMAS D'ENTRÉE (CREATE / UPDATE)
# =============================================================================

# --- Artist CRUD ---

class ArtistCreate(ArtistBase):
    """Schéma pour créer un artiste"""
    pass


class ArtistUpdate(BaseModel):
    """Schéma pour mettre à jour un artiste (tous les champs optionnels)"""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    url: Optional[str] = Field(None, max_length=500)
    pictureURL: Optional[str] = Field(None, max_length=500)


# --- User CRUD ---

class UserCreate(UserBase):
    """Schéma pour créer un utilisateur"""
    pass


# --- Tag CRUD ---

class TagCreate(TagBase):
    """Schéma pour créer un tag"""
    pass


class TagUpdate(BaseModel):
    """Schéma pour mettre à jour un tag"""
    tagValue: str = Field(..., min_length=1, max_length=100)


# --- Relations CRUD (Écoutes, Tags, Amis) ---

class UserArtistCreate(BaseModel):
    """Schéma pour ajouter/mettre à jour une écoute"""
    userID: int = Field(..., gt=0, description="ID de l'utilisateur")
    artistID: int = Field(..., gt=0, description="ID de l'artiste")
    weight: int = Field(..., ge=0, description="Nombre d'écoutes")


class UserArtistUpdate(BaseModel):
    """Schéma pour mettre à jour le poids d'une écoute"""
    weight: int = Field(..., ge=0, description="Nouveau nombre d'écoutes")


class UserTaggedArtistCreate(BaseModel):
    """Schéma pour appliquer un tag à un artiste"""
    userID: int = Field(..., gt=0, description="ID de l'utilisateur")
    artistID: int = Field(..., gt=0, description="ID de l'artiste")
    tagID: int = Field(..., gt=0, description="ID du tag")
    timestamp: Optional[int] = Field(None, description="Timestamp en millisecondes (auto-généré si omis)")
    day: Optional[int] = Field(None, ge=1, le=31, description="Jour (1-31)")
    month: Optional[int] = Field(None, ge=1, le=12, description="Mois (1-12)")
    year: Optional[int] = Field(None, ge=2000, le=2100, description="Année")
    
    @validator('timestamp', always=True)
    def set_timestamp(cls, v):
        """Génère automatiquement un timestamp si non fourni"""
        return v or int(datetime.now().timestamp() * 1000)


class UserFriendCreate(BaseModel):
    """Schéma pour créer une amitié"""
    userID: int = Field(..., gt=0, description="ID de l'utilisateur")
    friendID: int = Field(..., gt=0, description="ID de l'ami")
    bidirectional: bool = Field(True, description="Créer l'amitié dans les deux sens")
    
    @validator('friendID')
    def friend_not_self(cls, v, values):
        """Vérifie qu'un utilisateur ne peut pas être ami avec lui-même"""
        if 'userID' in values and v == values['userID']:
            raise ValueError("Un utilisateur ne peut pas être ami avec lui-même")
        return v


# =============================================================================
# 3. SCHÉMAS DE RÉPONSE SIMPLES (LECTURE)
# =============================================================================

class ArtistSimple(ArtistBase):
    """Réponse simple pour un artiste"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class UserSimple(UserBase):
    """Réponse simple pour un utilisateur"""
    
    model_config = ConfigDict(from_attributes=True)


class TagSimple(TagBase):
    """Réponse simple pour un tag"""
    tagID: int
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# 4. SCHÉMAS D'ASSOCIATION (POUR LES LISTES IMBRIQUÉES)
# =============================================================================

class UserArtistResponse(BaseModel):
    """Réponse pour une relation utilisateur-artiste"""
    userID: int
    artistID: int
    weight: int
    
    model_config = ConfigDict(from_attributes=True)


class UserArtistWithDetails(BaseModel):
    """Relation utilisateur-artiste avec détails de l'artiste"""
    weight: int
    artist: ArtistSimple
    
    model_config = ConfigDict(from_attributes=True)


class ArtistListenerWithDetails(BaseModel):
    """Relation artiste-auditeur avec détails de l'utilisateur"""
    weight: int
    user: UserSimple
    
    model_config = ConfigDict(from_attributes=True)


class UserTaggedArtistResponse(BaseModel):
    """Réponse pour un tag appliqué"""
    userID: int
    artistID: int
    tagID: int
    timestamp: int
    day: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserTaggedArtistWithDetails(BaseModel):
    """Tag appliqué avec détails complets"""
    timestamp: int
    day: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None
    artist: ArtistSimple
    tag: TagSimple
    
    model_config = ConfigDict(from_attributes=True)


class ArtistTagSummary(BaseModel):
    """Résumé des tags pour un artiste avec comptage"""
    tagValue: str
    count: int


class UserFriendResponse(BaseModel):
    """Réponse pour une amitié"""
    userID: int
    friendID: int
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# 5. SCHÉMAS DÉTAILLÉS (VUES COMPLÈTES)
# =============================================================================

class UserDetailed(UserSimple):
    """Vue complète d'un utilisateur avec toutes ses relations"""
    listened_artists: List[UserArtistWithDetails] = Field(default_factory=list)
    tagged_artists: List[UserTaggedArtistWithDetails] = Field(default_factory=list)
    friends_count: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class ArtistDetailed(ArtistSimple):
    """Vue complète d'un artiste avec statistiques"""
    total_listens: Optional[int] = None
    listener_count: Optional[int] = None
    top_tags: List[ArtistTagSummary] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


class TagDetailed(TagSimple):
    """Vue complète d'un tag avec statistiques d'usage"""
    usage_count: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# 6. ANALYTICS & STATISTIQUES
# =============================================================================

class GlobalStats(BaseModel):
    """Statistiques globales de la base de données"""
    total_artists: int = Field(..., description="Nombre total d'artistes")
    total_users: int = Field(..., description="Nombre total d'utilisateurs")
    total_tags: int = Field(..., description="Nombre total de tags")
    total_listens: int = Field(..., description="Nombre total d'écoutes")
    total_tagged: int = Field(..., description="Nombre total de tags appliqués")
    total_friendships: int = Field(..., description="Nombre total d'amitiés")


class ArtistStats(BaseModel):
    """Statistiques détaillées pour un artiste"""
    artistID: int
    name: str
    total_listens: int = Field(..., description="Nombre total d'écoutes cumulées")
    listener_count: int = Field(..., description="Nombre d'auditeurs uniques")
    tags_count: int = Field(..., description="Nombre de tags appliqués")
    top_tags: List[ArtistTagSummary] = Field(default_factory=list, description="Top tags pour cet artiste")


class UserStats(BaseModel):
    """Statistiques détaillées pour un utilisateur"""
    userID: int
    artists_listened: int = Field(..., description="Nombre d'artistes écoutés")
    tags_created: int = Field(..., description="Nombre de tags créés")
    friends_count: int = Field(..., description="Nombre d'amis")
    total_listens: Optional[int] = Field(None, description="Nombre total d'écoutes")


class TagStats(BaseModel):
    """Statistiques pour un tag"""
    tagID: int
    tagValue: str
    usage_count: int = Field(..., description="Nombre de fois que le tag a été utilisé")


class PopularArtist(BaseModel):
    """Artiste populaire avec son score"""
    id: int
    name: str
    total_weight: int = Field(..., description="Poids total d'écoutes")


class PopularTag(BaseModel):
    """Tag populaire avec son nombre d'utilisations"""
    tagID: int
    tagValue: str
    usage_count: int


class ActiveUser(BaseModel):
    """Utilisateur actif avec son score d'activité"""
    userID: int
    listen_count: int = Field(..., description="Nombre d'artistes écoutés")


class SimilarUser(BaseModel):
    """Utilisateur similaire avec score de similarité"""
    userID: int
    common_artists: int = Field(..., description="Nombre d'artistes en commun")


class RecommendedArtist(BaseModel):
    """Artiste recommandé avec score"""
    artist: ArtistSimple
    score: int = Field(..., description="Score de recommandation basé sur les utilisateurs similaires")


# =============================================================================
# 7. SCHÉMAS DE RECHERCHE ET FILTRAGE
# =============================================================================

class ArtistSearchParams(BaseModel):
    """Paramètres de recherche pour les artistes"""
    name: Optional[str] = Field(None, description="Rechercher par nom (partiel)")
    tags: Optional[List[str]] = Field(None, description="Filtrer par tags")
    skip: int = Field(0, ge=0, description="Nombre d'éléments à sauter")
    limit: int = Field(100, ge=1, le=1000, description="Nombre max d'éléments à retourner")


class UserSearchParams(BaseModel):
    """Paramètres de recherche pour les utilisateurs"""
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class TagSearchParams(BaseModel):
    """Paramètres de recherche pour les tags"""
    tag_value: Optional[str] = Field(None, description="Rechercher par valeur (partiel)")
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


# =============================================================================
# 8. SCHÉMAS DE RÉPONSE PAGINÉE
# =============================================================================

class PaginatedResponse(BaseModel):
    """Réponse paginée générique"""
    total: int = Field(..., description="Nombre total d'éléments")
    skip: int = Field(..., description="Nombre d'éléments sautés")
    limit: int = Field(..., description="Limite d'éléments par page")
    items: List = Field(..., description="Liste des éléments")


class PaginatedArtists(BaseModel):
    """Liste paginée d'artistes"""
    total: int
    skip: int
    limit: int
    items: List[ArtistSimple]


class PaginatedUsers(BaseModel):
    """Liste paginée d'utilisateurs"""
    total: int
    skip: int
    limit: int
    items: List[UserSimple]


class PaginatedTags(BaseModel):
    """Liste paginée de tags"""
    total: int
    skip: int
    limit: int
    items: List[TagSimple]


# =============================================================================
# 9. SCHÉMAS DE RÉPONSE D'ERREUR
# =============================================================================

class ErrorResponse(BaseModel):
    """Réponse d'erreur standardisée"""
    error: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message d'erreur détaillé")
    details: Optional[dict] = Field(None, description="Détails additionnels")


class SuccessResponse(BaseModel):
    """Réponse de succès standardisée"""
    success: bool = True
    message: str
    data: Optional[dict] = None