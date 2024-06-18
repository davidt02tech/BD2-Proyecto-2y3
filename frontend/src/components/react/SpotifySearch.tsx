import React, { useState, useEffect, useRef } from 'react';
import { Button, Input, Table, TableBody, TableCell, TableColumn, TableHeader, TableRow, Image } from "@nextui-org/react";
import type { Track } from "../../models/SpotifyTrack.ts";
import type { Album } from "../../models/SpotifyAlbum.ts";
import { motion, AnimatePresence } from 'framer-motion';

async function getToken() {
  const clientId = "cdce14d45a9642a6a218e361e63a1c92";
  const clientSecret = "9b86e1effcc641e492fbc44a2fc81b15";
  const response = await fetch("https://accounts.spotify.com/api/token", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      grant_type: "client_credentials",
      client_id: clientId,
      client_secret: clientSecret,
    }),
  });
  const data = await response.json();
  return data.access_token;
}

async function fetchSpotifyTrack(accessToken: string, trackId: string): Promise<Track> {
  const response = await fetch(`https://api.spotify.com/v1/tracks/${trackId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const data = await response.json();
  return data;
}

async function fetchAlbumTracks(accessToken: string, albumId: string): Promise<Track[]> {
  const response = await fetch(`https://api.spotify.com/v1/albums/${albumId}/tracks`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const data = await response.json();
  return data.items;
}

async function fetchAlbumDetails(accessToken: string, albumId: string): Promise<Album> {
  const response = await fetch(`https://api.spotify.com/v1/albums/${albumId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const data = await response.json();
  return data;
}


export default function SpotifyApp() {
  const [inputTrackId, setInputTrackId] = useState("7FJRTNO2iN43J3B7nO5tD5?si=26f2a0a4347d4807");
  const [trackId, setTrackId] = useState(inputTrackId);
  const [track, setTrack] = useState<Track | null>(null);
  const [album, setAlbum] = useState<Album | null>(null);
  const [tracks, setTracks] = useState<Track[]>([]);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    async function fetchTokenAndTrack() {
      const token = await getToken();
      setAccessToken(token);
      const trackData = await fetchSpotifyTrack(token, trackId);
      setTrack(trackData);
      const albumData = await fetchAlbumDetails(token, trackData.album.id);
      setAlbum(albumData);
      const tracksData = await fetchAlbumTracks(token, trackData.album.id);
      setTracks(tracksData);
    }

    fetchTokenAndTrack();
  }, [trackId]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputTrackId(event.target.value);
  };

  const handleButtonClick = () => {
    setTrackId(inputTrackId);
  };

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = 0.3; 
    }
  }, [track]);

  return (
    <div className="grid grid-cols-2">
      <div>
        <div className="mt-5 max-w-max">
          {track ? (
            <>
              <img src={track.album.images[0].url} className="max-w-sm" />
              <div className="mt-5">{track.name}</div>
              <div className="opacity-70 text-sm">{track.artists[0].name}</div>
              
            </>
          ) : (
            <p>Loading...</p>
          )}
        </div>
        <div>
        {track ? (
            <>
              <div className="mt-5">
              {track.preview_url ? (
                <audio ref={audioRef} key={track.preview_url} controls>
                <source src={track.preview_url} type="audio/mpeg" />
                Your browser does not support the audio element.
                </audio>
              ) : (
                <p>No preview available</p>
              )}
            </div>
            </>
          ) : (
            <> </>
          )}
        </div>
        <div className="mt-5">
          <Input 
            placeholder="Enter Track ID" 
            value={inputTrackId} 
            onChange={handleInputChange} 
            className='mb-2 max-w-xl'
          />
          <Button onClick={handleButtonClick}>Fetch Track</Button>
        </div>
      </div>
      <div>
        <h1 className='text-3xl text-green-500 font-semibold'>Album:</h1>
        {album && (
          <div className="mt-5">
            <h2 className="text-xl">{album.name}</h2>
            <div className="opacity-70 text-sm mb-5">{album.artists.map(artist => artist.name).join(", ")}</div>
            <Table aria-label="Album Tracks" selectionMode="none">
              <TableHeader>
                <TableColumn>#</TableColumn>
                <TableColumn>Title</TableColumn>
                <TableColumn>Artist(s)</TableColumn>
                <TableColumn>Id</TableColumn>
              </TableHeader>
              <TableBody>
                {tracks.map(track_ => (
                  <TableRow key={track_.id}>
                    <TableCell>{track_.track_number}</TableCell>
                    <TableCell>{track_.name}</TableCell>
                    <TableCell>{track_.artists.map(artist => artist.name).join(", ")}</TableCell>
                    <TableCell>{track_.id}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </div>
  );
}
