import React, { useState, useRef } from 'react';
import { Slider } from '@nextui-org/slider';
import { PlusCircle, X } from 'lucide-react';
import { useSwipeable } from 'react-swipeable';
import axios from "axios";
import ReactPlayer from 'react-player';


const SongCard = ({ onClick, song, onDelete }) => {
  const [offset, setOffset] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  const handlers = useSwipeable({
    onSwiping: (eventData) => {
      if (eventData.dir === 'Left') {
        setOffset(Math.min(eventData.deltaX, 0));
      }
    },
    onSwipedLeft: (eventData) => {
      if (eventData.deltaX < -100) {
        setIsDeleting(true);
        setTimeout(() => onDelete(), 300);
      } else {
        setOffset(0);
      }
    },
    onSwipedRight: () => setOffset(0),
    trackMouse: true,
    onTap: () => onClick()
  });

  return (
      <div
          {...handlers}
          className={`relative bg-gray-100 p-2 rounded transition-all duration-300 ease-out ${
              isDeleting ? 'opacity-0' : ''
          }`}
          style={{ transform: `translateX(${offset}px)` }}
      >
        <div className="absolute right-0 top-0 bottom-0 w-16 bg-red-500 flex items-center justify-center">
          <X className="text-white" />
        </div>
        <div className="relative bg-white">
          <p className="font-semibold">{song.name}</p>
          <p className="text-sm text-gray-600">{song.album}, {song.artist}</p>
        </div>
      </div>
  );
};

const JiveGenie = () => {
  const [songs, setSongs] = useState([]);
  const [speed, setSpeed] = useState(1);
  const [currSong, setCurrSong] = useState(-1)
  const fileInputRef = useRef(null);

  const handleUpload = (event) => {
    const file = event.target.files[0];
    console.log(file)
    const data = new FormData()
    data.append('file', file)
    data.append('filename', file.name)
    
    axios({
      method: "POST",
      url: "http://localhost:5000/upload",
      data: data
    })
    .then((response) => {
      const res = response.data
      console.log(res)
    }).catch((error) => {
      if (error.response) {
        console.log(error.response)
        console.log(error.response.status)
        console.log(error.response.headers)
        }
    })

    if (file) {
      setSongs([...songs, { name: file.name, album: 'Unknown', artist: 'Unknown' }]);
    }
  

  };

  function generate_dance() {
    axios({
      method: "POST",
      url:"http://localhost:5000/generate_dance",
    })
    .then((response) => {
      const res = response.data
      console.log(res)
    }).catch((error) => {
      if (error.response) {
        console.log(error.response)
        console.log(error.response.status)
        console.log(error.response.headers)
        }
    })}

  const handleDeleteSong = (index) => {
    setSongs(songs.filter((_, i) => i !== index));
  };

  return (
      <div className="flex flex-col p-4 w-full mx-auto">
        <h1 className="text-3xl font-bold mb-4">Jive Genie</h1>
        <div className="flex flex-col sm:flex-row gap-4 flex-grow overflow-hidden">
          <div className="flex-1 flex flex-col bg-gray-200 rounded-lg p-4">
          <div className="aspect-video max-h-screen bg-gray-300 rounded-lg mb-4">
            {(currSong !== -1) &&
              <ReactPlayer
                className='react-player fixed-bottom'
                url={`outputs/test_${songs[currSong]['name'].slice(0,-4)}_sound.mp4`}
                width='100%'
                height='100%'
                controls={true}
              />
            } 
            </div>
            <div className="flex justify-between items-center">
              <div>
                <p className="font-semibold">Song Name</p>
                <p className="text-sm text-gray-600">Album Name, Artist</p>
              </div>
              <button className="bg-blue-500 text-white px-4 py-2 rounded" onClick={() => generate_dance()}>Animate</button>
            </div>
          </div>

          <div className="w-64 space-y-4">
            <div className="bg-white rounded-lg p-4">
              <h2 className="font-semibold mb-2">Your Jives</h2>
              {songs.length === 0 ? (
                  <p className="text-gray-500">Upload songs to start dancing!</p>
              ) : (
                  <ul className="space-y-2">
                    {songs.map((song, index) => (
                        <SongCard
                            key={index}
                            song={song}
                            onClick={() => setCurrSong(index)}
                            onDelete={() => handleDeleteSong(index)}
                        />
                    ))}
                  </ul>
              )}
            </div>

            <div className="bg-white rounded-lg p-4">
              <h2 className="font-semibold mb-2">Controls</h2>
              <div className="flex items-center justify-between mb-4">
                <span>Upload Music</span>
                <button
                    className="p-1 rounded-full bg-gray-200 hover:bg-gray-300"
                    onClick={() => fileInputRef.current.click()}
                >
                  <PlusCircle className="h-6 w-6" />
                </button>
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleUpload}
                    className="hidden"
                    accept="audio/*"
                />
              </div>
              {/* <div>
                <span>Speed</span>
                <Slider
                    value={[speed]}
                    onValueChange={(value) => setSpeed(value[0])}
                    max={2}
                    step={0.1}
                    className="mt-2"
                />
              </div> */}
            </div>
          </div>
        </div>
      </div>
  );
};

export default JiveGenie;