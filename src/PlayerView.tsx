import React, { useEffect, useRef, useState, useMemo } from 'react';
import { Match, Channel } from '../types';
import { ArrowLeft, ExternalLink, AlertCircle, PlayCircle, Settings, Sun, Volume2, Activity, Tv2, Radio, Heart, Cpu, Smartphone } from 'lucide-react';
import Hls from 'hls.js';
// @ts-ignore
import videojs from 'video.js';
// @ts-ignore
import DPlayer from 'dplayer';

type EngineType = 'native' | 'videojs' | 'dplayer';

interface PlayerViewProps {
  match: Match | null;
  onBack: () => void;
  onEnterPiP: () => void;
  onShowMoreLinks: () => void;
  relatedChannels: Channel[];
  onSelectRelated: (channel: Channel) => void;
  isFavorite?: boolean;
  onToggleFavorite?: () => void;
}

const PlayerView: React.FC<PlayerViewProps> = ({
  match, onBack, onEnterPiP, onShowMoreLinks, relatedChannels, onSelectRelated, isFavorite, onToggleFavorite
}) => {
  // Player DOM Refs
  const videoRef = useRef<HTMLVideoElement>(null);
  const vjsContainerRef = useRef<HTMLDivElement>(null);
  const dpContainerRef = useRef<HTMLDivElement>(null);

  // Player Instance Refs
  const hlsRef = useRef<Hls | null>(null);
  const vjsPlayerRef = useRef<any>(null);
  const dpPlayerRef = useRef<any>(null);
  
  // Audio Booster Refs
  const audioCtxRef = useRef<AudioContext | null>(null);
  const gainNodeRef = useRef<GainNode | null>(null);

  // Core States
  const [activeEngine, setActiveEngine] = useState<EngineType>('native');
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  
  // Feature States
  const [brightness, setBrightness] = useState(100);
  const [volume, setVolume] = useState(100); 
  const [qualities, setQualities] = useState<any[]>([]);
  const [currentQuality, setCurrentQuality] = useState<number>(-1);

  // 🛠️ FIX: Safe splitting for team name to avoid crash
  const similarChannels = useMemo(() => {
    if (!match || !match.team1) return [];
    try {
        const baseName = match.team1.split(' ')[0]?.toLowerCase() || ""; 
        return relatedChannels.filter(c => c.name?.toLowerCase().includes(baseName) && c.id !== match.id).slice(0, 10);
    } catch (e) {
        return [];
    }
  }, [match, relatedChannels]);

  // Safely destroy all running players
  const destroyAllPlayers = () => {
    try {
        if (hlsRef.current) { hlsRef.current.destroy(); hlsRef.current = null; }
        if (vjsPlayerRef.current) { vjsPlayerRef.current.dispose(); vjsPlayerRef.current = null; }
        if (dpPlayerRef.current) { dpPlayerRef.current.destroy(); dpPlayerRef.current = null; }
        if (videoRef.current) { 
            videoRef.current.pause();
            videoRef.current.removeAttribute('src'); 
            videoRef.current.load(); 
        }
    } catch (e) {
        console.log("Cleanup warning:", e);
    }
  };

  useEffect(() => {
    // 🛠️ FIX: Check if match exists AND has a streamUrl
    if (!match || !match.streamUrl) return;
    
    setError(null);
    setWarning(null);
    destroyAllPlayers();

    const streamUrl = match.streamUrl;

    // 👇 FANCODE 404 BYPASS LOGIC 👇
    const applyUniqueBypass = (xhr: any, url: string) => {
      try {
        if (url.includes('dai.google.com') || url.includes('fancode')) {
           xhr.open('GET', url, true);
           return;
        }
        const myUniqueId = Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
        const newUrl = new URL(url);
        newUrl.searchParams.append('uid', myUniqueId);
        xhr.open('GET', newUrl.toString(), true);
      } catch (e) {
        xhr.open('GET', url, true);
      }
    };

    // ----------------------------------------------------
    // ENGINE 1: NATIVE HLS
    // ----------------------------------------------------
    if (activeEngine === 'native' && videoRef.current) {
      const video = videoRef.current;
      if (Hls.isSupported()) {
        const hls = new Hls({
          maxBufferLength: 30,
          maxMaxBufferLength: 600,
          enableWorker: true,
          lowLatencyMode: true,
          xhrSetup: applyUniqueBypass 
        });

        hlsRef.current = hls;
        hls.loadSource(streamUrl);
        hls.attachMedia(video);

        hls.on(Hls.Events.MANIFEST_PARSED, (event, data) => {
          setQualities(data.levels);
          video.play().catch(() => console.log("Autoplay blocked"));
        });

        hls.on(Hls.Events.ERROR, (event, data) => {
          if (data.fatal) {
            if (data.type === Hls.ErrorTypes.NETWORK_ERROR) hls.startLoad();
            else if (data.type === Hls.ErrorTypes.MEDIA_ERROR) hls.recoverMediaError();
            else setError("Stream blocked. Try switching Engine in settings.");
          }
        });
      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = streamUrl;
        video.play().catch(() => {});
      }
    }

    // ----------------------------------------------------
    // ENGINE 2: VIDEO.JS
    // ----------------------------------------------------
    else if (activeEngine === 'videojs' && vjsContainerRef.current) {
      vjsContainerRef.current.innerHTML = `
        <video class="video-js vjs-default-skin w-full h-full object-contain" playsinline controls preload="auto"></video>
      `;
      const videoElement = vjsContainerRef.current.querySelector('video');

      if (videoElement) {
          vjsPlayerRef.current = videojs(videoElement, {
            autoplay: true,
            controls: true,
            fluid: false,
            sources: [{ src: streamUrl, type: 'application/x-mpegURL' }],
            html5: { vhs: { overrideNative: true } }
          });
      }
    }

    // ----------------------------------------------------
    // ENGINE 3: DPLAYER
    // ----------------------------------------------------
    else if (activeEngine === 'dplayer' && dpContainerRef.current) {
      try {
          dpPlayerRef.current = new DPlayer({
            container: dpContainerRef.current,
            autoplay: true,
            video: {
                url: streamUrl,
                type: 'customHls',
                customType: {
                    customHls: (video: any) => {
                        const hls = new Hls({ xhrSetup: applyUniqueBypass });
                        hls.loadSource(video.src);
                        hls.attachMedia(video);
                        hlsRef.current = hls;
                    }
                }
            }
          });
      } catch (e) {
          setError("DPlayer failed to load.");
      }
    }

    return () => destroyAllPlayers();
  }, [match?.streamUrl, activeEngine]); // 🛠️ FIX: Depend only on streamUrl string

  const handleVolumeChange = (val: number) => {
    setVolume(val);
    if (activeEngine !== 'native' || !videoRef.current) return; 
    
    // Audio Context Init Logic (kept same as your code)
    if (!audioCtxRef.current) {
      try {
        const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
        const ctx = new AudioContextClass();
        const gainNode = ctx.createGain();
        const source = ctx.createMediaElementSource(videoRef.current);
        source.connect(gainNode);
        gainNode.connect(ctx.destination);
        audioCtxRef.current = ctx;
        gainNodeRef.current = gainNode;
      } catch (e) {}
    }
    if (val <= 100) {
      videoRef.current.volume = val / 100;
      if (gainNodeRef.current) gainNodeRef.current.gain.value = 1;
    } else {
      videoRef.current.volume = 1;
      if (gainNodeRef.current) gainNodeRef.current.gain.value = val / 100;
    }
  };

  // 🛠️ FIX: Guard Clause - If no match, show loading instead of crashing
  if (!match) {
      return (
        <div className="flex items-center justify-center h-screen bg-black text-white">
            <div className="text-center">
                <p className="animate-pulse text-lg font-bold">Loading Stream Details...</p>
                <button onClick={onBack} className="mt-4 px-4 py-2 bg-red-600 rounded">Go Back</button>
            </div>
        </div>
      );
  }

  return (
    <div className="flex flex-col h-full bg-[#0f1115] overflow-hidden">
      {/* HEADER */}
      <div className="sticky top-0 z-50 bg-[#0f1115] shadow-2xl">
        <div className="flex items-center justify-between p-3 md:p-4 bg-[#12141a] border-b border-gray-800">
          <div className="flex items-center gap-3 md:gap-4 flex-1 min-w-0">
            <button onClick={onBack} className="p-2 hover:bg-gray-800 rounded-full transition shrink-0">
              <ArrowLeft className="w-5 h-5 md:w-6 md:h-6 text-white" />
            </button>
            <div className="flex flex-col truncate">
              <h1 className="text-sm md:text-lg font-bold text-white truncate">{match.team1 || "Live Stream"}</h1>
              <span className="text-[10px] text-green-500 font-black uppercase tracking-widest flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-ping"></span> {activeEngine.toUpperCase()}
              </span>
            </div>
          </div>
          <div className="flex items-center gap-1 md:gap-2 shrink-0">
            <button onClick={onToggleFavorite} className="p-2 rounded-full transition hover:bg-gray-800 hidden sm:block">
              <Heart className={`w-5 h-5 transition-colors ${isFavorite ? 'text-red-500 fill-red-500' : 'text-gray-300'}`} />
            </button>
            <button onClick={() => setShowSettings(!showSettings)} className={`p-2 rounded-full transition ${showSettings ? 'bg-green-500 text-black' : 'hover:bg-gray-800 text-gray-300'}`}>
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* VIDEO CONTAINER */}
        <div className="relative w-full aspect-video bg-black flex flex-col items-center justify-center">
          
          {warning && !error && activeEngine === 'native' && (
              <div className="absolute top-0 left-0 right-0 bg-yellow-500/90 text-black text-[10px] md:text-xs font-bold px-4 py-2 z-30 flex items-center justify-between">
                  <span>{warning}</span>
                  <button onClick={() => setActiveEngine('videojs')} className="underline font-black hover:text-white">Switch to Video.js</button>
              </div>
          )}

          {error ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center p-4 md:p-6 text-center bg-[#1a1d23] gap-4 z-20">
              <AlertCircle className="w-10 h-10 md:w-12 md:h-12 text-red-500" />
              <p className="text-red-400 text-xs md:text-sm font-semibold max-w-sm">{error}</p>
            </div>
          ) : (
            <div className="w-full h-full relative" style={brightness !== 100 ? { filter: `brightness(${brightness}%)` } : {}}>
                <video ref={videoRef} className={`w-full h-full object-contain ${activeEngine === 'native' ? 'block' : 'hidden'}`} controls playsInline />
                <div ref={vjsContainerRef} className={`w-full h-full absolute inset-0 ${activeEngine === 'videojs' ? 'block' : 'hidden'}`} />
                <div ref={dpContainerRef} className={`w-full h-full absolute inset-0 ${activeEngine === 'dplayer' ? 'block' : 'hidden'}`} />
            </div>
          )}
        </div>

        {/* SETTINGS PANEL */}
        {showSettings && (
          <div className="bg-[#1a1d23] border-b border-gray-800 p-4 absolute w-full z-40 shadow-2xl animate-in slide-in-from-top-2">
            <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-[10px] md:text-xs font-bold text-gray-400 uppercase tracking-wider">
                  <Cpu size={14}/> Engine
                </label>
                <select 
                    value={activeEngine} 
                    onChange={(e) => setActiveEngine(e.target.value as EngineType)} 
                    className="w-full bg-[#0f1115] border border-white/10 text-white rounded-lg p-2 text-xs font-bold focus:border-green-500 outline-none"
                >
                  <option value="native">Native HLS</option>
                  <option value="videojs">Video.js</option>
                  <option value="dplayer">DPlayer</option>
                </select>
              </div>

              {activeEngine === 'native' && (
                  <>
                    <div className="space-y-2">
                      <label className="flex items-center justify-between text-[10px] md:text-xs font-bold text-gray-400 uppercase"><span className="flex items-center gap-2"><Volume2 size={14}/> Vol Boost</span><span className={volume > 100 ? 'text-red-400' : 'text-green-400'}>{volume}%</span></label>
                      <input type="range" min="0" max="300" value={volume} onChange={(e) => handleVolumeChange(Number(e.target.value))} className="w-full accent-green-500" />
                    </div>
                    <div className="space-y-2">
                      <label className="flex items-center justify-between text-[10px] md:text-xs font-bold text-gray-400 uppercase"><span className="flex items-center gap-2"><Sun size={14}/> Brightness</span><span className="text-blue-400">{brightness}%</span></label>
                      <input type="range" min="20" max="200" value={brightness} onChange={(e) => setBrightness(Number(e.target.value))} className="w-full accent-blue-500" />
                    </div>
                    {qualities.length > 0 && (
                        <div className="space-y-2">
                          <label className="flex items-center justify-between text-[10px] md:text-xs font-bold text-gray-400 uppercase"><span className="flex items-center gap-2"><Activity size={14}/> Quality</span></label>
                          <select value={currentQuality} onChange={(e) => {
                              if (hlsRef.current) {
                                  hlsRef.current.currentLevel = Number(e.target.value);
                                  setCurrentQuality(Number(e.target.value));
                              }
                          }} className="w-full bg-[#0f1115] border border-white/10 text-white rounded-lg p-2 text-xs font-bold focus:border-green-500 outline-none">
                            <option value={-1}>Auto</option>
                            {qualities.map((level, index) => <option key={index} value={index}>{level.height ? `${level.height}p` : `Level ${index + 1}`}</option>)}
                          </select>
                        </div>
                    )}
                  </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* RELATED CHANNELS */}
      <div className="flex-1 overflow-y-auto bg-[#0f1115] scrollbar-hide pb-24 md:pb-6">
        {similarChannels.length > 0 && (
          <div className="p-4 md:p-6 border-b border-white/5">
            <h2 className="text-xs font-black text-blue-500 uppercase tracking-widest mb-4 flex items-center gap-2">
              <Tv2 size={16} /> Similar
            </h2>
            <div className="flex md:grid md:grid-cols-3 gap-3 overflow-x-auto snap-x snap-mandatory scrollbar-hide pb-2">
              {similarChannels.map((channel, idx) => (
                <button key={`sim-${idx}`} onClick={() => onSelectRelated(channel)} className="flex-shrink-0 w-64 md:w-auto flex items-center gap-3 p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl hover:border-blue-500 hover:bg-blue-500/20 transition-all text-left snap-start group">
                  <img src={channel.logo} className="w-8 h-8 rounded-lg object-contain bg-white/5 p-1" alt="" onError={(e) => { e.currentTarget.src = `https://ui-avatars.com/api/?name=TV&background=random` }} />
                  <span className="text-xs font-bold text-blue-100 truncate flex-1">{channel.name}</span>
                  <Radio className="w-4 h-4 text-blue-500 shrink-0" />
                </button>
              ))}
            </div>
          </div>
        )}
        <div className="p-4 md:p-6">
          <h2 className="text-xs font-black text-gray-500 uppercase tracking-widest mb-4">All Channels</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {relatedChannels.map((channel, idx) => (
              <button key={idx} onClick={() => onSelectRelated(channel)} className={`flex items-center gap-4 p-3 border rounded-xl transition-all text-left group ${match.id === channel.id ? 'bg-green-500/10 border-green-500/30' : 'bg-[#1a1d23] border-white/5 hover:border-green-500/50 hover:bg-[#252a33]'}`}>
                <div className="w-12 h-12 rounded-lg bg-white/5 p-2 flex-shrink-0 flex items-center justify-center">
                  <img src={channel.logo} alt="" className="w-full h-full object-contain" onError={(e) => { e.currentTarget.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(channel.name)}&background=random` }} />
                </div>
                <div className="flex-1 min-w-0">
                  <span className={`text-sm font-bold truncate block ${match.id === channel.id ? 'text-green-400' : 'text-gray-200'}`}>{channel.name}</span>
                  {match.id === channel.id && <span className="text-[9px] text-green-500 uppercase font-black">Playing</span>}
                </div>
                {match.id !== channel.id && <PlayCircle className="w-6 h-6 text-gray-700 group-hover:text-green-500 transition-colors shrink-0" />}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlayerView;