import React, { useState, useEffect, useRef } from 'react';
import { Input, Button, Table, TableBody, TableCell, TableColumn, TableHeader, TableRow, Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, useDisclosure } from '@nextui-org/react';
import { Select, SelectItem } from "@nextui-org/react";
import { animals } from "../data2.js";
import type { Track } from "../../models/SpotifyTrack.ts";
import type { Album } from "../../models/SpotifyAlbum.ts";

export interface TrackData {
  track_id: string;
  track_name: string;
  track_artist: string;
  lyrics: string;
}

const getToken = async () => {
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
};

const fetchSpotifyTrack = async (accessToken: string, trackId: string): Promise<Track> => {
  const response = await fetch(`https://api.spotify.com/v1/tracks/${trackId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const data = await response.json();
  return data;
};

const fetchAlbumTracks = async (accessToken: string, albumId: string): Promise<Track[]> => {
  const response = await fetch(`https://api.spotify.com/v1/albums/${albumId}/tracks`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const data = await response.json();
  return data.items;
};

const fetchAlbumDetails = async (accessToken: string, albumId: string): Promise<Album> => {
  const response = await fetch(`https://api.spotify.com/v1/albums/${albumId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const data = await response.json();
  return data;
};

const fetchTrackDetails = async (trackData: TrackData[], accessToken: string) => {
  const updatedTrackData = await Promise.all(trackData.map(async (track) => {
    const spotifyTrack = await fetchSpotifyTrack(accessToken, track.track_id);
    return {
      ...track,
      track_name: spotifyTrack.name,
      track_artist: spotifyTrack.artists.map(artist => artist.name).join(", ")
    };
  }));
  return updatedTrackData;
};

const SeachApi1: React.FC = () => {
  const [trackData, setTrackData] = useState<TrackData[]>([]);
  const [query, setQuery] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [selectedType, setType] = useState<string | null>(null);
  const [k, setK] = useState<number>(2);  // Nuevo estado para k
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [selectedLyrics, setSelectedLyrics] = useState<string | null>(null);
  const [selectedTrackId, setSelectedTrackId] = useState<string | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [spotifyTrack, setSpotifyTrack] = useState<Track | null>(null);
  const [album, setAlbum] = useState<Album | null>(null);
  const [tracks, setTracks] = useState<Track[]>([]);
  const audioRef = useRef<HTMLAudioElement>(null);

  const fetchTrackData = async (searchQuery: string, indexType: string, kValue: number) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/multiDimensionalSearch?q=${searchQuery}&k=${kValue}&indexType=${indexType}`, {
        headers: {
          'accept': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const token = await getToken();
      setAccessToken(token);
      const updatedData = await fetchTrackDetails(data.results, token);
      setTrackData(updatedData);
      setError(null);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to fetch data. Please try again.');
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const formattedQuery = query.replace(/\s+/g, '_');
    fetchTrackData(formattedQuery, 'default', k);
  };

  const handleRowClick = async (lyrics: string, trackId: string) => {
    setSelectedLyrics(lyrics);
    setSelectedTrackId(trackId);
    const trackData = await fetchSpotifyTrack(accessToken!, trackId);
    setSpotifyTrack(trackData);
    const albumData = await fetchAlbumDetails(accessToken!, trackData.album.id);
    setAlbum(albumData);
    const tracksData = await fetchAlbumTracks(accessToken!, trackData.album.id);
    setTracks(tracksData);
    onOpen();
  };

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = 0.3; 
    }
  }, [spotifyTrack]);

  return (
    <>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <Input
          type="text"
          placeholder="Insert your ID song"
          className='max-w-sm'
          size='lg'
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <Input
          type="number"
          placeholder="Enter k value"
          className='max-w-sm'
          size='lg'
          value={k.toString()}
          onChange={(e) => setK(parseInt(e.target.value))}
        />
        <Select
          items={animals}
          label="Type"
          placeholder="Select a type"
          size='sm'
          className="max-w-sm"
          onSelectionChange={(type) => setType(type as string)}
        >
          {(animal) => <SelectItem key={animal.key}>{animal.label}</SelectItem>}          
        </Select>
        <Button type="submit" size='lg'>Search</Button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {trackData.length > 0 ? (
        <Table aria-label="Track Results" selectionMode="none">
          <TableHeader>
            <TableColumn>Song Name</TableColumn>
            <TableColumn>Artist</TableColumn>
            <TableColumn>Id</TableColumn>
          </TableHeader>
          <TableBody>
            {trackData.map((track) => (
              <TableRow key={track.track_id} onClick={() => handleRowClick(track.lyrics, track.track_id)}>
                <TableCell>{track.track_name}</TableCell>
                <TableCell>{track.track_artist}</TableCell>
                <TableCell>{track.track_id}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      ) : (
        <p>Loading...</p>
      )}
     

      <Modal isOpen={isOpen} onOpenChange={onOpenChange}>
        <ModalContent className="max-w-7xl mx-auto p-4">
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1 text-green-500">Song Details</ModalHeader>
              <ModalBody className="overflow-auto max-h-[500px]">
                {spotifyTrack ? (
                  <>
                    <div className='flex'>
                      <div>
                        <img src={spotifyTrack.album.images[0].url} className="max-w-xs" />
                        <div className="mt-5">{spotifyTrack.name}</div>
                        <div className="opacity-70 text-sm">{spotifyTrack.artists[0].name}</div>
                        <div className="mt-5">
                          {spotifyTrack.preview_url ? (
                            <audio ref={audioRef} key={spotifyTrack.preview_url} controls>
                              <source src={spotifyTrack.preview_url} type="audio/mpeg" />
                              Your browser does not support the audio element.
                            </audio>
                          ) : (
                            <p>No preview available</p>
                          )}
                        </div>
                      </div>
                      <div className='ml-5'>
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
                  </>
                ) : (
                  <p>Loading...</p>
                )}
                <div className='text-xl text-green-500 font-bold'>
                  Lyrics
                </div>
                <p>{selectedLyrics}</p>
              </ModalBody>
              <ModalFooter>
                <Button color="danger" variant="light" onPress={onClose}>
                  Close
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
};

export default SeachApi1;
