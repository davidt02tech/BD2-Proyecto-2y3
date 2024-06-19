import React, { useState } from 'react';
import { Input, Button, Table, TableBody, TableCell, TableColumn, TableHeader, TableRow, Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, useDisclosure } from '@nextui-org/react';
import { Select, SelectItem } from "@nextui-org/react";
import { animals } from "../data2.js";

export interface TrackData {
  track_id: string;
  track_name: string;
  track_artist: string;
  lyrics: string;
}

export const SeachApi1: React.FC = () => {
  const [trackData, setTrackData] = useState<TrackData[]>([]);
  const [query, setQuery] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [selectedType, setType] = useState<string | null>(null);
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const [selectedLyrics, setSelectedLyrics] = useState<string | null>(null);

  const fetchTrackData = async (searchQuery: string) => {
    try {
      const response = await fetch(`http://54.156.105.2:8000/ginIndexSearch/?q=${searchQuery}`, {
        headers: {
          'accept': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTrackData(data.results);
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

  const handleRowClick = (lyrics: string) => {
    setSelectedLyrics(lyrics);
    onOpen();
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
      {trackData.length > 0 ? (
        <Table aria-label="Track Results" selectionMode="none">
          <TableHeader>
            <TableColumn>Song Name</TableColumn>
            <TableColumn>Artist</TableColumn>
            <TableColumn>Id</TableColumn>
          </TableHeader>
          <TableBody>
            {trackData.map((track) => (
              <TableRow key={track.track_id} onClick={() => handleRowClick(track.lyrics)}>
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
      {selectedType && <p><strong>Search type:</strong> {selectedType}</p>}

      <Modal isOpen={isOpen} onOpenChange={onOpenChange}>
        <ModalContent className="max-w-7xl mx-auto p-4">
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1 text-green-500">Lyrics</ModalHeader>
              <ModalBody>
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
