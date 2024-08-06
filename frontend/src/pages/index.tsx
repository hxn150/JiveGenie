import React, { useState, useRef, useEffect } from 'react';
import { Slider } from '@nextui-org/slider';
import { PlusCircle, X } from 'lucide-react';
import { useSwipeable } from 'react-swipeable';
import axios from "axios";
import ReactPlayer from 'react-player';
import { TailSpin } from 'react-loader-spinner'
import logo from '../components/jg.png';
import '@/pages/styles.css';

export const openInNewTab = (url: string): void => {
  const newWindow = window.open(url, '_blank', 'noopener,noreferrer')
  if (newWindow) newWindow.opener = null
}

export const onClickUrl = (url: string): (() => void) => () => openInNewTab(url)


const SongCard = ({ onClick, song, onDelete, onSelect, isSelected }) => {
  const [offset, setOffset] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  const handlers = useSwipeable({
    onSwiping: (eventData) => {
      if (eventData.dir === 'Left') {
        setOffset(Math.min(eventData.deltaX, 0));
      }
    },
    onSwipedLeft: (eventData) => {
      if (eventData.deltaX < -10) {
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
      className={`relative bg-gray-100 p-2 rounded transition-all duration-300 ease-out ${isDeleting ? 'opacity-0' : ''
        } ${isSelected ? 'border-2 border-blue-500' : ''}`}
      style={{ transform: `translateX(${offset}px)` }}
      onClick={() => onSelect(song)}
    >
      <div className="absolute right-0 top-0 bottom-0 w-16 bg-red-500 flex items-center justify-center">
        <X className="text-white" />
      </div>
      <div className="relative bg-white">
        <p className="font-semibold">{song}</p>
        {/* <p className="text-sm text-gray-600">{song.album}, {song.artist}</p> */}
      </div>
    </div>
  );
};

const JiveGenie = () => {
  const [songs, setSongs] = useState([]);
  const [speed, setSpeed] = useState(1);
  const [firstLoad, setFirstLoad] = useState(true)
  const [currSong, setCurrSong] = useState(-1)
  const [currentSongIndex, setCurrentSongIndex] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false)
  const fileInputRef = useRef(null);
  const url = 'http://127.0.0.1:8080/'

  const fetchSongs = () => {
    axios({
      method: "GET",
      url: url+"get_songs",
    })
      .then((response) => {
        setSongs(response.data)
      }).catch((error) => {
        if (error.response) {
          console.log(error.response)
          console.log(error.response.status)
          console.log(error.response.headers)
        }
      })
  }
  if (firstLoad) {
    fetchSongs()
    if (songs.length > 0) {
      setCurrSong(0)
    }
    setFirstLoad(false)
  }


  const handleUpload = (event) => {
    const file = event.target.files?.[0];
    console.log(file)
    const data = new FormData()
    data.append('file', file)
    data.append('filename', file.name)

    axios({
      method: "POST",
      url: url+"upload",
      data: data
    })
      .then((response) => {
        const res = response.data
        console.log(res)
        fetchSongs()

      }).catch((error) => {
        if (error.response) {
          console.log(error.response)
          console.log(error.response.status)
          console.log(error.response.headers)
        }
      })
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result;
        if (typeof result === 'string') {
          const audio = new Audio(result);
          audio.onloadedmetadata = () => {
            let name = file.name;
            let artist = 'Unknown';
            let album = 'Unknown';

            if ('mediaSession' in navigator && navigator.mediaSession.metadata) {
              const metadata = navigator.mediaSession.metadata;
              name = metadata.title || name;
              artist = metadata.artist || artist;
              album = metadata.album || album;
            }

            if (name === file.name) {
              const parts = file.name.split('-').map(part => part.trim());
              if (parts.length >= 2) {
                artist = parts[0];
                name = parts[1].split('.')[0];
              }
            }
            const newSong = name;
            setSongs(prevSongs => {
              const newSongs = [...prevSongs, newSong];
              setCurrentSongIndex(newSongs.length - 1);
              return newSongs;
            });
          };
        } else {
          console.error('FileReader result is not a string');
        }
      };
      reader.readAsDataURL(file);
    }


  };

  function generate_dance(index) {
    setIsLoading(true);
    axios({
      method: "POST",
      url: url+"generate_dance",
      data: { name: songs[index] }
    })
      .then((response) => {
        const res = response.data
        console.log(res)
        setIsLoading(false);
      }).catch((error) => {
        if (error.response) {
          console.log(error.response)
          console.log(error.response.status)
          console.log(error.response.headers)
        }
        setIsLoading(false);

      })

  }

  const handleDeleteSong = (index) => {
    axios({
      method: "POST",
      url: url+"delete_song",
      data: { name: songs[index] }
    })
      .then((response) => {
        const res = response.data
        console.log(res)
        fetchSongs()

      }).catch((error) => {
        if (error.response) {
          console.log(error.response)
          console.log(error.response.status)
          console.log(error.response.headers)
        }
      })
    setSongs(prevSongs => {
      const newSongs = prevSongs.filter((_, i) => i !== index);
      setCurrentSongIndex(prevIndex => {
        if (prevIndex === index) {
          return newSongs.length > 0 ? 0 : null;
        } else if (prevIndex !== null && prevIndex > index) {
          return prevIndex - 1;
        }
        return prevIndex;
      });
      return newSongs;
    });
  };

  const handleSelectSong = (song) => {
    const index = songs.findIndex(s => s === song);
    setCurrentSongIndex(index);
  };

  const currentSong = currentSongIndex !== null ? songs[currentSongIndex] : null;

  const handleFileInputClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  }

  return (
    <div className="flex flex-col p-4 w-full mx-auto">
      <header className="flex items-center mb-4">
        <img src={logo} alt="JiveGenie Logo" className="h-12 w-auto mr-4" />
        <h1 className="text-4xl font-normal" style={{ fontFamily: "Monoton" }}>JiveGenie</h1>
      </header>
      <div className="flex flex-col sm:flex-row gap-4 flex-grow overflow-hidden">
        <div className="flex-1 flex flex-col bg-gray-200 rounded-lg p-4">
          <div className="aspect-video max-h-screen bg-gray-300 rounded-lg mb-4">
            {currSong !== -1 && !isLoading &&
              <ReactPlayer
                className='react-player fixed-bottom'
                url={`outputs/test_${songs[currSong]}_sound.mp4`}
                width='100%'
                height='100%'
                controls={true}
              />
            }
          </div>
          <div className="flex justify-between items-center">
            <div>
              <p className="font-semibold">{currentSong ? currentSong.name : 'No song selected'}</p>
              <p className="text-sm text-gray-600">
                {currentSong ? currentSong.artist : 'Select a song to start'}
              </p>
            </div>
            {!isLoading && <button className="bg-blue-500 text-white px-4 py-2 rounded" onClick={() => generate_dance(currentSongIndex)} disabled={!currentSong}>Animate</button>}
            <TailSpin
              visible={isLoading}
            />
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
                    onSelect={handleSelectSong}
                    isSelected={currentSongIndex === index}
                  />
                ))}
              </ul>
            )}
          </div>

          <div className="bg-white rounded-lg p-4 flex-1 flex flex-col">
            <h2 className="font-semibold mb-2">Controls</h2>
            <div className="flex items-center justify-between mb-4">
              <span>Upload Music</span>
              <button
                className="p-1 rounded-full bg-gray-200 hover:bg-gray-300"
                onClick={handleFileInputClick}
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
            <div className="flex items-center justify-between mb-4">
              <span>Feedback</span>
              <button
                className="p-1 rounded-full bg-gray-200 hover:bg-gray-300"
                onClick={onClickUrl('https://forms.gle/MjADDNBe2CphWZRN7')}
              >
                <PlusCircle className="h-6 w-6" />
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-8">
          <header className="text-4xl font-bold mb-8">Dance Inspiration Gallery ⭐</header>
          <div className="grid grid-cols-3 gap-8">
          <iframe
            src="https://www.tiktok.com/player/v1/7352968566578236705?_r=1&_t=8noW3IxOEIR"
            className="w-full aspect-video"
            frameBorder="0"
            allow="autoplay; fullscreen"
            allowFullScreen
          />
          <iframe
            src="https://www.tiktok.com/player/v1/7338052786082434305?_r=1&_t=8oKbkrhmdSh"
            className="w-full aspect-video"
            frameBorder="0"
            allow="autoplay; fullscreen"
            allowFullScreen
        />
        <iframe
            src="https://www.tiktok.com/player/v1/7393135674880265515?lang=en"
            className="w-full aspect-video"
            frameBorder="0"
            allow="autoplay; fullscreen"
            allowFullScreen
        />
        <iframe
            src="https://www.tiktok.com/player/v1/7385297562040929579?lang=en"
            className="w-full aspect-video"
            frameBorder="0"
            allow="autoplay; fullscreen"
            allowFullScreen
        />
        <iframe
            src="https://www.tiktok.com/player/v1/7345421284068789509?lang=en&q=dance&t=1721957195756"
            className="w-full aspect-video"
            frameBorder="0"
            allow="autoplay; fullscreen"
            allowFullScreen
          />
        <iframe
            src="https://www.tiktok.com/player/v1/7342665531939458309?lang=en&q=shidaa%20and%20nolen&t=1721957268394"
            className="w-full aspect-video"
            frameBorder="0"
            allow="autoplay; fullscreen"
            allowFullScreen
        />
        </div>
      </div>
    </div>
  );
};

export default JiveGenie;