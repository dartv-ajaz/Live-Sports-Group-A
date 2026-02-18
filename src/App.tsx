import React, { useState, useEffect, useCallback } from 'react';
import { View, Match, Category, Channel } from './types';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import BottomNav from './components/BottomNav';
import LiveEventsView from './views/LiveEvents';
import CategoriesView from './views/CategoriesView';
import ChannelListView from './views/ChannelList';
import PlayerView from './views/PlayerView';
import LinkModal from './components/LinkModal';
import FloatingPlayer from './components/FloatingPlayer';
import AboutView from './views/AboutView';
import PrivacyPolicyView from './views/PrivacyPolicyView';
import { CATEGORIES } from './constants';
import { WifiOff, RefreshCw } from 'lucide-react';

// AAPKE M3U LINKS

const DEFAULT_M3U = 'https://raw.githubusercontent.com/FunctionError/PiratesTv/refs/heads/main/combined_playlist.m3u';
const MASTER_JSON_URL = 'https://raw.githubusercontent.com/FunctionError/PiratesTv/refs/heads/main/master_playlists.json';

// 🚀 DAR TEVE API LINKS 🚀
// 🚀 // Ye wala link abhi aapne banaya hai (Group A):
const GROUP_A_URL = 'https://raw.githubusercontent.com/dartv-ajaz/Live-Sports-Group-A/main/live_matches_A.json';

// Ye wala link tab banega jab aap Step 1 (Group B) pura karenge:
const GROUP_B_URL = 'https://raw.githubusercontent.com/dartv-ajaz/Live-Sports-Group-B/main/live_matches_B.json';
const App: React.FC = () => {
  const [activeView, setActiveView] = useState<View>('live-events');
  const [lastMainView, setLastMainView] = useState<View>('live-events');
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  
  const [matches, setMatches] = useState<Match[]>([]);
  const [allChannels, setAllChannels] = useState<Channel[]>([]);
  const [categoryChannels, setCategoryChannels] = useState<Channel[]>([]);
  const [playlistCache, setPlaylistCache] = useState<Record<string, Channel[]>>({});
  
  const [favorites, setFavorites] = useState<Channel[]>([]);
  const [globalSearchQuery, setGlobalSearchQuery] = useState('');
  
  const [cloudCategories, setCloudCategories] = useState<Category[]>([]);
  const [customCategories, setCustomCategories] = useState<Category[]>([]);

  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const [floatingMatch, setFloatingMatch] = useState<Match | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [showLinkModal, setShowLinkModal] = useState(false);
  
  const [isLoading, setIsLoading] = useState(true);
  const [isCategoryLoading, setIsCategoryLoading] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);

  useEffect(() => {
    const savedFavs = localStorage.getItem('cricpk_favorites');
    if (savedFavs) {
      try { setFavorites(JSON.parse(savedFavs)); } catch (e) {}
    }
    const savedCustom = localStorage.getItem('cricpk_custom_playlists');
    if (savedCustom) {
      try { setCustomCategories(JSON.parse(savedCustom)); } catch (e) {}
    }
  }, []);

  const toggleFavorite = (channel: Channel) => {
    setFavorites(prev => {
      const isFav = prev.some(c => c.id === channel.id);
      const newFavs = isFav ? prev.filter(c => c.id !== channel.id) : [...prev, channel];
      localStorage.setItem('cricpk_favorites', JSON.stringify(newFavs));
      return newFavs;
    });
  };

  const handleAddCustomPlaylist = (name: string, url: string) => {
    const newCat: Category = { id: `custom-${Date.now()}`, name, playlistUrl: url };
    const updated = [...customCategories, newCat];
    setCustomCategories(updated);
    localStorage.setItem('cricpk_custom_playlists', JSON.stringify(updated));
  };

  const handleDeleteCustomPlaylist = (id: string) => {
    const updated = customCategories.filter(c => c.id !== id);
    setCustomCategories(updated);
    localStorage.setItem('cricpk_custom_playlists', JSON.stringify(updated));
  };

  const fetchM3UText = async (url: string) => {
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error('Direct fetch blocked');
      return await res.text();
    } catch (e) {
      console.warn("Direct fetch blocked by CORS. Tunneling via proxy...");
      const proxyUrl = `https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(url)}`;
      const proxyRes = await fetch(proxyUrl);
      if (!proxyRes.ok) throw new Error('Proxy fetch failed');
      return await proxyRes.text();
    }
  };

  const fetchInitialData = useCallback(async () => {
    setIsLoading(true);
    setFetchError(null);
    try {
      // 1. Load Default M3U
      const text = await fetchM3UText(DEFAULT_M3U);
      if (!text) throw new Error("Empty playlist received");
      
      const parsed = parseM3U(text, 'cat-combined');
      let currentMatches = parsed.matches;
      let currentChannels = parsed.channels;
      
      let newCache: Record<string, Channel[]> = { 'cat-combined': parsed.channels };
      let newCloudCats: Category[] = [];

      // 2. Load Master JSON
      try {
        const cloudDataText = await fetchM3UText(MASTER_JSON_URL);
        newCloudCats = JSON.parse(cloudDataText);
      } catch (e) { console.log("Cloud master not found."); }

      // 3. 🚀 FETCH DAR TEVE APIs (Group A & B) 🚀
      const apiConfigs = [
        { id: 'cat-group-a', name: 'FanCode & Jio Live', url: GROUP_A_URL },
        { id: 'cat-group-b', name: 'Hotstar & Prime VIP', url: GROUP_B_URL }
      ];

      for (const config of apiConfigs) {
        try {
            const apiText = await fetchM3UText(config.url);
            const apiData = JSON.parse(apiText);
            
            if (apiData && apiData.matches) {
                const apiChannels: Channel[] = apiData.matches.map((m: any, index: number) => ({
                    id: `ch-${config.id}-${m.id || index}`,
                    name: m.title || `${m.team_1} vs ${m.team_2}`,
                    logo: m.team_1_flag || m.banner || `https://ui-avatars.com/api/?name=${encodeURIComponent(m.platform)}&background=random`,
                    categoryId: config.id,
                    streamUrl: m.url,
                    // Storing extra DRM info if needed for player
                    isDrm: m.is_drm,
                    licenseUrl: m.license_url
                }));

                newCache[config.id] = apiChannels;
                
                // Add to Categories
                newCloudCats = [{ id: config.id, name: config.name, playlistUrl: 'internal-api' }, ...newCloudCats];

                // Add to Matches (Home Screen)
                const liveMatches: Match[] = apiData.matches.map((m: any, idx: number) => ({
                    id: m.id || `live-${config.id}-${idx}`,
                    sport: m.sport || 'Sports',
                    league: m.platform,
                    team1: m.team_1,
                    team2: m.team_2,
                    team1Logo: m.team_1_flag || m.banner,
                    team2Logo: m.team_2_flag || m.banner,
                    status: 'Live',
                    time: 'Live Now',
                    isHot: true,
                    streamUrl: m.url,
                    groupTitle: config.name,
                    // DRM Fields
                    type: m.is_drm ? "DRM" : "HLS",
                    license_url: m.license_url,
                    is_drm: m.is_drm
                }));
                currentMatches = [...liveMatches, ...currentMatches];
            }
        } catch (err) {
            console.warn(`Failed to load ${config.name}`, err);
        }
      }

      setMatches(currentMatches);
      setAllChannels(currentChannels);
      setCloudCategories(newCloudCats);
      setPlaylistCache(newCache);

    } catch (error: any) {
      setFetchError(error.message || "Broadcaster synchronization failed.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetchInitialData(); }, [fetchInitialData]);

  const parseM3U = (text: string, categoryId: string) => {
    const lines = text.split('\n');
    const matches: Match[] = [];
    const channels: Channel[] = [];
    let currentInfo: any = null;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.startsWith('#EXTINF:')) {
        const logoMatch = line.match(/tvg-logo="([^"]+)"/);
        const groupMatch = line.match(/group-title="([^"]+)"/);
        const nameSplit = line.split(',');
        const name = nameSplit.length > 1 ? nameSplit.pop()?.trim() || 'Unknown Channel' : 'Unknown Channel';
        
        currentInfo = {
          name,
          logo: logoMatch ? logoMatch[1] : `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random`,
          group: groupMatch ? groupMatch[1] : 'General'
        };
      } else if (line.startsWith('http') && currentInfo) {
        const channel: Channel = {
          id: `ch-${categoryId}-${channels.length}`,
          name: currentInfo.name,
          logo: currentInfo.logo,
          categoryId: categoryId,
          streamUrl: line
        };
        channels.push(channel);

        const groupLower = currentInfo.group.toLowerCase();
        const nameLower = currentInfo.name.toLowerCase();
        
        if (groupLower.includes('sport') || nameLower.includes('sport') || nameLower.includes('cricket') || categoryId === 'cat-wc2026') {
          matches.push({
            id: `m-${categoryId}-${matches.length}`,
            sport: nameLower.includes('cricket') ? 'Cricket' : (nameLower.includes('football') ? 'Football' : 'Other'),
            league: currentInfo.group,
            team1: currentInfo.name,
            team2: 'Live Broadcast',
            team1Logo: currentInfo.logo,
            team2Logo: currentInfo.logo,
            status: 'Live',
            time: 'Live Now',
            isHot: true,
            streamUrl: line,
            groupTitle: currentInfo.group
          });
        }
        currentInfo = null;
      }
    }
    return { channels, matches };
  };

  const handleCategorySelect = async (category: Category) => {
    setSelectedCategory(category);
    setActiveView('channel-detail');
    
    if (category.id === 'cat-favorites') {
      setCategoryChannels(favorites);
      return;
    }

    if (playlistCache[category.id]) {
      setCategoryChannels(playlistCache[category.id]);
    } else {
      setIsCategoryLoading(true);
      try {
        const text = await fetchM3UText(category.playlistUrl);
        if (!text || text.trim().length === 0) {
            alert("This playlist link is empty or dead.");
            setCategoryChannels([]);
            return;
        }
        const { channels } = parseM3U(text, category.id);
        setCategoryChannels(channels);
        setPlaylistCache(prev => ({ ...prev, [category.id]: channels }));
      } catch (err) {
        setCategoryChannels([]);
      } finally {
        setIsCategoryLoading(false);
      }
    }
  };

  const handleMatchSelect = (match: Match) => {
    // 🚀 USE SMART ROUTER IF GLOBAL FUNCTION EXISTS (For DRM Redirection) 🚀
    if ((window as any).playMatch && (match.type === 'DRM' || match.is_drm)) {
        (window as any).playMatch({
            url: match.streamUrl,
            type: match.type || 'HLS',
            license_url: match.license_url,
            is_drm: match.is_drm
        });
        return;
    }

    // Default Internal Player for standard streams
    setLastMainView('live-events');
    setSelectedMatch(match);
    setActiveView('player');
  };

  const handleLinkSelect = (linkName: string) => {
    setShowLinkModal(false);
    setFloatingMatch(null);
    setActiveView('player');
  };

  const playChannel = (ch: Channel) => {
    const matchData: Match = {
      id: ch.id, team1: ch.name, team2: 'Network Mirror', team1Logo: ch.logo, team2Logo: ch.logo,
      league: selectedCategory?.name || 'Live TV', status: 'Live', time: 'Live', sport: 'Other', streamUrl: ch.streamUrl
    };
    setSelectedMatch(matchData);
    setFloatingMatch(null);
    setActiveView('player');
  };

  const renderView = () => {
    if (isLoading) return <div className="flex flex-col items-center justify-center h-full gap-4"><div className="w-10 h-10 border-4 border-green-500/20 border-t-green-500 rounded-full animate-spin" /></div>;
    if (fetchError) return <div className="flex flex-col items-center justify-center h-full p-8 text-center gap-6"><WifiOff className="w-10 h-10 text-red-500" /><p className="text-white">{fetchError}</p><button onClick={fetchInitialData} className="bg-white text-black px-8 py-4 rounded-2xl"><RefreshCw className="w-4 h-4 inline" /> Reconnect</button></div>;

    if (globalSearchQuery.trim().length > 0) {
      const searchResults = allChannels.filter(c => c.name.toLowerCase().includes(globalSearchQuery.toLowerCase())).slice(0, 100);
      return <ChannelListView channels={searchResults} category={{ id: 'search', name: `Search Results`, playlistUrl: '' }} loading={false} onBack={() => setGlobalSearchQuery('')} onSelectChannel={(ch) => { setGlobalSearchQuery(''); setLastMainView('categories'); playChannel(ch); }} />;
    }

    switch (activeView) {
      case 'about': return <AboutView />;
      case 'privacy': return <PrivacyPolicyView />;
      case 'live-events': return <LiveEventsView matches={matches} onSelectMatch={handleMatchSelect} />;
      case 'categories': return <CategoriesView onSelectCategory={handleCategorySelect} favoritesCount={favorites.length} cloudCategories={cloudCategories} customCategories={customCategories} onAddCustom={handleAddCustomPlaylist} onDeleteCustom={handleDeleteCustomPlaylist} />;
      case 'channel-detail': return <ChannelListView channels={categoryChannels} category={selectedCategory} loading={isCategoryLoading} onBack={() => setActiveView('categories')} onSelectChannel={(ch) => { setLastMainView('channel-detail'); playChannel(ch); }} />;
      case 'player':
        const related = categoryChannels.length > 0 ? categoryChannels.slice(0, 40) : allChannels.slice(0, 40);
        return <PlayerView match={selectedMatch} onBack={() => setActiveView(lastMainView)} onEnterPiP={() => { setFloatingMatch(selectedMatch); setActiveView(lastMainView); }} onShowMoreLinks={() => setShowLinkModal(true)} relatedChannels={related} onSelectRelated={playChannel} isFavorite={favorites.some(f => f.id === selectedMatch?.id)} onToggleFavorite={() => { if (selectedMatch) toggleFavorite({ id: selectedMatch.id, name: selectedMatch.team1, logo: selectedMatch.team1Logo, categoryId: 'fav', streamUrl: selectedMatch.streamUrl }); }} />;
      default: return <LiveEventsView matches={matches} onSelectMatch={handleMatchSelect} />;
    }
  };

  const isFullPlayer = activeView === 'player';

  return (
    <div className="flex flex-row h-screen overflow-hidden bg-[#0f1115] text-white">
      {!isFullPlayer && <Sidebar isOpen={isSidebarOpen} onClose={() => setSidebarOpen(false)} activeView={activeView} onNavigate={(v) => { setActiveView(v); setLastMainView(v); setSidebarOpen(false); }} />}
      <div className="flex flex-col flex-1 relative min-w-0">
        {!isFullPlayer && (
          <Header 
            title={activeView === 'categories' ? 'Playlists' : activeView === 'channel-detail' ? (selectedCategory?.name || 'Channels') : activeView === 'about' ? 'About Us' : activeView === 'privacy' ? 'Privacy Policy' : 'DAR TEVE'} 
            onOpenSidebar={() => setSidebarOpen(true)} showBack={activeView === 'channel-detail'} onBack={() => setActiveView('categories')} searchQuery={globalSearchQuery} onSearchChange={setGlobalSearchQuery} 
          />
        )}
        <main className={`flex-1 overflow-y-auto scrollbar-hide ${!isFullPlayer ? 'pb-24 md:pb-6' : ''}`}>
          <div className={`${!isFullPlayer ? 'max-w-[1600px] mx-auto' : 'w-full h-full'}`}>{renderView()}</div>
        </main>
        {!isFullPlayer && <BottomNav activeView={activeView === 'channel-detail' ? 'categories' : activeView} onViewChange={(v) => { setActiveView(v); setLastMainView(v); }} />}
      </div>
      {floatingMatch && <FloatingPlayer match={floatingMatch} onExpand={() => { setSelectedMatch(floatingMatch); setFloatingMatch(null); setActiveView('player'); }} onClose={() => setFloatingMatch(null)} />}
      {showLinkModal && <LinkModal match={selectedMatch} onClose={() => setShowLinkModal(false)} onSelect={handleLinkSelect} />}
    </div>
  );
};

export default App;