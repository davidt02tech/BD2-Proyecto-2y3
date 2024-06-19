CREATE TABLE spotify_table (
    track_id TEXT PRIMARY KEY,
    track_name TEXT,
	track_artist TEXT,
	lyrics TEXT,
	track_popularity FLOAT,
	track_album_id TEXT,
	track_album_name TEXT,
	track_album_release_date TEXT,
	playlist_name TEXT,
	playlist_id TEXT,
	playlist_genre TEXT,
	playlist_subgenre TEXT,
	danceability FLOAT,
	energy FLOAT,
	key FLOAT,
	loudness FLOAT,
	mode FLOAT,
	speechiness FLOAT,
	acousticness FLOAT,
	instrumentalness FLOAT,
	liveness FLOAT,
	valence FLOAT,
	tempo FLOAT,
	duration_ms FLOAT,
	language TEXT
);


COPY spotify_table
FROM 'C:\Program Files\PostgreSQL\13\data\spotify_songs.csv'
DELIMITER ','
CSV HEADER;


ALTER TABLE spotify_table ADD COLUMN author_lyrics_tsvector tsvector;


UPDATE spotify_table 
SET author_lyrics_tsvector = setweight(to_tsvector('english', track_artist), 'A') 
	|| setweight(to_tsvector('english', track_name), 'B') 
	|| setweight(to_tsvector('english', lyrics), 'C');


CREATE INDEX idx_gin_author_lyrics ON spotify_table USING GIN (author_lyrics_tsvector);

