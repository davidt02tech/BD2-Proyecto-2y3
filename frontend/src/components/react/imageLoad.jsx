// components/react/RotatingImage.tsx
import React from 'react';
import { motion } from 'framer-motion';

const RotatingImage = () => {
  return (
    <motion.img
      src="https://upload.wikimedia.org/wikipedia/commons/8/84/Spotify_icon.svg"
      className="w-auto h-48"
      alt="Rotating Spotify Icon"
      animate={{ rotate: 360 }}
      transition={{ repeat: Infinity, duration: 30 , ease: "linear" }}
    />
  );
};

export default RotatingImage;
