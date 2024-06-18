import React, { useState } from 'react';
import type { TrackData } from "../../models/TrackData";
import { sanitizeTrackData } from "../../models/TrackData.ts";
import { Input, Button } from '@nextui-org/react';
import { Select, SelectItem } from "@nextui-org/react";
import { animals } from "../data2.js";

export const SeachApi1: React.FC = () => {
  const [trackData, setTrackData] = useState<TrackData | null>(null);
  const [query, setQuery] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [selectedtype, setType] = useState<string | null>(null);
  
  const fetchTrackData = async (searchQuery: string) => {
    try {
      const response = await fetch(`http://54.156.105.2:8000/ginIndexSearch/?q=2Pac`, {
        headers: {
          'accept': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data1 = await response;

      const data: TrackData = await response.json();
      const sanitizedData = sanitizeTrackData(data); 
      setTrackData(sanitizedData);
      setError(null);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to fetch data. Please try again.');
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    fetchTrackData(query);
  };

  return (
    <>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <Input
          type="text"
          placeholder="Search your favourite song"
          className='max-w-sm'
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <Button type="submit">Search</Button>
        <Select
          items={animals}
          label="Type"
          placeholder="Select a type"
          className="max-w-sm"
          onSelectionChange={(type) => setType(type as string)}
        >
          {(animal) => <SelectItem key={animal.key}>{animal.label}</SelectItem>}
        </Select>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {trackData ? (
        <div className='space-y-2'>
          <p><strong className='text-gray-500'>Song Name:</strong> {trackData.track_name}</p>
          <p><strong className='text-gray-500'>Artist:</strong> {trackData.track_artist}</p>
          <p><strong className='text-gray-500'>Album:</strong> {trackData.track_album_name} ({trackData.track_album_release_date})</p>
          <p><strong className='text-gray-500'>Popularity:</strong> {trackData.track_popularity}</p>
          <p><strong className='text-gray-500'>Genre:</strong> {trackData.playlist_genre}</p>
          <p><strong className='text-gray-500'>Subgenre:</strong> {trackData.playlist_subgenre}</p>
          <p><strong className='text-gray-500'>Duration:</strong> {Math.floor(trackData.duration_ms / 60000)}:{Math.floor((trackData.duration_ms % 60000) / 1000).toFixed(0)} minutes</p>
          <p><strong className='text-gray-500'>Id:</strong> {trackData.track_id}</p>
          <p><strong className='text-gray-500'>Lyrics:</strong> {trackData.lyrics}</p>
          {selectedtype && <p><strong>Search type:</strong> {selectedtype}</p>}
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </>
  );
};

export default SeachApi1;
