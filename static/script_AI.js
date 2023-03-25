//AI!

const getElement = query => document.querySelector(query);
const getElements = query => document.querySelectorAll(query);

let searchResult = [];

let songList = [
    {
        thumbnail: "Bright_Future.jpg",
        audio: "Gin Soaked Boy - The Divine Comedy.mp3",
        songname: "Smells Like A Placeholder",
        album: "filler",
        artistname: "Nirvana"
    }
];

const getStat = data => ({ 
    disk: data.disk,
    song: data.song,
    length: data.length,
    time: data.time,
    is_playing: data.is_playing
});

const getSongData = data => {
    const results = Object.keys(data).map(element => ({
        index: element,
        song: data[element].Song_Title,
        artist: data[element].Artist,
        length: data[element].Length,
        track: data[element].Track_ID
    }));
    return results;
};

const stat = async () => {
    const url = '/stat';
    const response = await fetch(url);
    const data = await response.json();
    const dStat = getStat(data);
    const valueSeek = valueSeek; //d_stat.time; changed dc
    switch (dStat.is_playing) {
        case 0:
            showPlayButton();
            break;
        case 1:
            showPauseButton();
            break;
        case -1:
            showPausedButton();
            break;
        default:
            break;
    }
    updateRuntime(dStat.length - dStat.time);
    setTimeout(stat, 5000);
    return dStat;
};

const pause = () => {
    const url = '/pause';
    fetch(url)
        .then(data => data.json())
        .then(data => ({
            disk: data.Album,
            artist: data.Artist,
            length: data.length,
            time: data.time,
            is_playing: data.is_playing
        }));
};

const search = async query => {
    const url = `/search/${query}`;
    const response = await fetch(url);
    const data = await response.json();
    const searchResult = getSongData(data);
    return searchResult;
};

const showPauseButton = () => {
    playPauseCss.style.setProperty('--show_play', 'none');
    playPauseCss.style.setProperty('--show_pause', 'block');
    playPauseCss.style.setProperty('--show_paused', 'none');
};

const showPlayButton = () => {
    playPauseCss.style.setProperty('--show_play', 'block');
    playPauseCss.style.setProperty('--show_pause', 'none');
    playPauseCss.style.setProperty('--show_paused', 'none');
};

const showPausedButton = () => {
    playPauseCss.style.setProperty('--show_play', 'none');
    playPauseCss.style.setProperty('--show_pause', 'none');
    playPauseCss.style.setProperty('--show_paused', 'block');
};

const updateRuntime = runTime => {
    document.getElementById('runTime').innerHTML = `${runTime} secs`;
};

const loadDatabase = async () => {
    const url = '/loadDatabase/';
    const response = await fetch(`${url}${diskIndex}`);
    const data = await response.json();
    songList = data.map(({ Artist, Album, Song_Title, Length }) => ({
        thumbnail: 'Bright_Future.jpg',
        audio: 'Frog Princess -- The Divine Comedy.mp3',
        songname: Song_Title,
        artistname: Artist,
        album: Album,
        song_length: Length
    }));
    updateSongs();
};

const player = getElement('.player');
const toggleSong
