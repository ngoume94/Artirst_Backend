from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    userID = Column(Integer, primary_key=True, index=True)
    
    listened_artists = relationship(
        "UserArtist", 
        back_populates="user"
    )
    tagged_artists = relationship(
        "UserTaggedArtist", 
        back_populates="user"
    )
    
    friendships_initiated = relationship(
        "UserFriend",
        foreign_keys="[UserFriend.userID]",
        back_populates="user"
    )
    friendships_received = relationship(
        "UserFriend",
        foreign_keys="[UserFriend.friendID]",
        back_populates="friend"
    )
    
    def get_all_friends_ids(self):
        """Retourne tous les IDs d'amis (bidirectionnel)"""
        friends_ids = set()
        for friendship in self.friendships_initiated:
            friends_ids.add(friendship.friendID)
        for friendship in self.friendships_received:
            friends_ids.add(friendship.userID)
        return friends_ids
    
    def __repr__(self):
        return f"<User(userID={self.userID})>"


class Artist(Base):
    __tablename__ = "artists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String)
    pictureURL = Column(String)
    
    listeners = relationship(
        "UserArtist", 
        back_populates="artist"
    )
    tags_received = relationship(
        "UserTaggedArtist", 
        back_populates="artist"
    )
    
    def __repr__(self):
        return f"<Artist(id={self.id}, name='{self.name}')>"


class Tag(Base):
    __tablename__ = "tags"
    
    tagID = Column(Integer, primary_key=True, index=True)
    tagValue = Column(String, nullable=False)
    
    artist_usages = relationship(
        "UserTaggedArtist", 
        back_populates="tag"
    )
    
    def __repr__(self):
        return f"<Tag(tagID={self.tagID}, tagValue='{self.tagValue}')>"


class UserArtist(Base):
    __tablename__ = "user_artists"
    
    userID = Column(Integer, ForeignKey("users.userID", ondelete="CASCADE"), primary_key=True)
    artistID = Column(Integer, ForeignKey("artists.id", ondelete="CASCADE"), primary_key=True)
    weight = Column(Integer, nullable=False)
    
    user = relationship("User", back_populates="listened_artists")
    artist = relationship("Artist", back_populates="listeners")
    
    def __repr__(self):
        return f"<UserArtist(userID={self.userID}, artistID={self.artistID}, weight={self.weight})>"


class UserTaggedArtist(Base):
    __tablename__ = "user_taggedartists"
    
    userID = Column(Integer, ForeignKey("users.userID", ondelete="CASCADE"), primary_key=True)
    artistID = Column(Integer, ForeignKey("artists.id", ondelete="CASCADE"), primary_key=True)
    tagID = Column(Integer, ForeignKey("tags.tagID", ondelete="CASCADE"), primary_key=True)
    # IMPORTANT: timestamp ne peut pas être NULL car c'est une clé primaire
    timestamp = Column(Integer, primary_key=True, nullable=False) 
    
    day = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)
    
    user = relationship("User", back_populates="tagged_artists")
    artist = relationship("Artist", back_populates="tags_received")
    tag = relationship("Tag", back_populates="artist_usages")
    
    def __repr__(self):
        return f"<UserTaggedArtist(userID={self.userID}, artistID={self.artistID}, tagID={self.tagID})>"


class UserFriend(Base):
    __tablename__ = "user_friends"
    
    userID = Column(Integer, ForeignKey("users.userID", ondelete="CASCADE"), primary_key=True)
    friendID = Column(Integer, ForeignKey("users.userID", ondelete="CASCADE"), primary_key=True)
    
    user = relationship(
        "User", 
        foreign_keys=[userID], 
        back_populates="friendships_initiated"
    )
    friend = relationship(
        "User", 
        foreign_keys=[friendID], 
        back_populates="friendships_received"
    )
    
    def __repr__(self):
        return f"<UserFriend(userID={self.userID}, friendID={self.friendID})>"