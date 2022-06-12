function _(query){
	return document.querySelector(query);
}
function _all(query){
	return document.querySelectorAll(query);
}


let songList = [
	{
		thumbnail:"Bright_Future.jpg",
		audio:"Gin Soaked Boy - The Divine Comedy.mp3",
		songname:"Smells Like A Placeholder",
		album:"filler",
		artistname:"Nirvana"
	}
];
 

function get_stat(data) {
	dict = { 
	disk: data.disk,
	song: data.song,
    length: data.length,
    time: data.time,
    is_playing: data.is_playing
    };

	return dict; 
}
async function stat() {
	var url = '/stat'  ;
	const response = await fetch(url);
	const data = await response.json();
	d_stat = await get_stat(data);
	value_seek = d_stat.time;

};

function pause() {
	fetch('/pause')
	.then (data => data.json())
	.then ( data => {

	dict = { 
	disk: data.disk,
	song: data.song,
    length: data.length,
    time: data.time,
    is_playing: data.is_playing
    }});

return dict	
};


//document.addEventListener("DOMContentLoaded", async () => {
// Work in  progress.
//});
var songIndex = 0;
var diskIndex = 3;
var value_seek = 0;
var  status = {};
var play_pause_css = document.querySelector(':root');


// Query server for tracks list from disc in url. response is a list of dicts in json form.
async function loadDB() {
	var url = '/loadDatabase/'  ;
	const response = await fetch(url+diskIndex);
	const data = await response.json();
	songList =[]
	var tk= data[0].tracks;
	//console.log(tk);
	var i = 0
	//update = ".player .player-list .list"
	while (i<(tk)) {
		const artistname = data[2].artistname;
		const album = data[3].album;
		console.log(album);
		const {title, length} = data[1][i].recording;
		object = {
			thumbnail:"Bright_Future.jpg",
			audio:"Frog Princess -- The Divine Comedy.mp3",
			songname: title,
			artistname: artistname,
			album: album,
			song_length: length
			};

		songList.push(object);		
		
		i = i + 1;
		main.songname.innerText = songList[0].songname;
		main.artistname.innerText = songList[0].artistname;
		main.album.innerText = songList[0].album;
		
};
	updateSongs();
	
	}

loadDB();

 
let player = _(".player"),
	toggleSongList = _(".player .toggle-list");

let main = {
	audio:_(".player .main audio"),
	thumbnail:_(".player .main img"),
	seekbar:_(".player .main input"),
	songname:_(".player .main .details h2"),
	album:_(".player .main .details h3"),
	artistname:_(".player .main .details p"),
	prevDisk:_(".player .main .controls .prev-disc-control"),
	prevControl:_(".player .main .controls .prev-control"),
	playPauseControl:_(".player .main .controls .play-pause-control"),
	nextDisk:_(".player .main .controls .next-disc-control"),
	nextControl:_(".player .main .controls .next-control")
}
 
toggleSongList.addEventListener("click", function(){
	toggleSongList.classList.toggle("active");
	player.classList.toggle("activeSongList");
});


//load album details into album song list in index,html
function updateSongs(){
_(".player .player-list .list").innerHTML = (songList.map(function(song,songIndex){
	return `
		<div class="item" songIndex="${songIndex}">
			<div class="thumbnail">
				<img src="./static/${song.thumbnail}">
			</div>
			<div class="details">
				<h2>${song.songname}</h2>
				<p>${song.artistname}</p>
			</div>
		</div>
	`;
}).join(""));

let songListItems = _all(".player .player-list .list .item");
for(let i=0;i<songListItems.length;i++){
	songListItems[i].addEventListener("click",function(){
		currentSongIndex = parseInt(songListItems[i].getAttribute("songIndex"));
		//loadSong(currentSongIndex); //not sure why this is here. 
		player.classList.remove("activeSongList");
	});
}
}


 function requestSong(diskIndex, currentSongIndex){
	const requestUrl = '/requestSong/';
	const requestData = {
		Disk: diskIndex, 
		Song: currentSongIndex 
	}
	const request = new Request (requestUrl, 
	{
	method:'POST',
	body : JSON.stringify(requestData),
	headers: new Headers({'Content-Type': 'application/json'})
	});
	fetch(request);
}


function loadSong(songIndex){
	console.log('Disk ',diskIndex, 'Song ',songIndex);
	let song = songList[songIndex];
	main.thumbnail.setAttribute("src","./static/"+song.thumbnail);
	document.body.style.background = `linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.8)), url("./static/${song.thumbnail}") center no-repeat`;
	document.body.style.backgroundSize = "cover";	
	main.songname.innerText = song.songname;
	main.artistname.innerText = song.artistname;
	//main.audio.setAttribute("src","./static/"+song.audio);
}


setInterval(function(){
	main.seekbar.value = value_seek; //parseInt(main.audio.currentTime);
	if (d_stat.is_playing){
		value_seek = value_seek + 2;
	}

	if (value_seek > d_stat.length) {
		value_seek = 0;
		d_stat.is_playing = false;
		play_pause_css.style.setProperty('--show_play','block');
		play_pause_css.style.setProperty('--show_pause','none');
	} 
	//console.log(value_seek);
},2000);



main.prevDisk.addEventListener("click",function(){
	if(diskIndex > 1){
		diskIndex = diskIndex-1;
		//currentSongIndex=0
		console.log('Disk ',diskIndex, 'Song ',songIndex);
		
	}
	loadDB();
});
	
 
main.prevControl.addEventListener("click",function(){
	songIndex--;
	if(songIndex < 0){
		songIndex = songList.length + songIndex;
	}
	loadSong(songIndex);
});
main.nextControl.addEventListener("click",function(){
	songIndex = (songIndex+1) % songList.length;
	loadSong(songIndex);
});

main.nextDisk.addEventListener("click",function(){
	if(diskIndex < 99){
		diskIndex = diskIndex+1;
		//currentSongIndex = 0
		console.log('Disk ',diskIndex, 'Song ',songIndex);
	}
	loadDB();
});


main.playPauseControl.addEventListener("click",play_button)
function play_button() {

		// console.log(d_stat.is_playing );

	if(d_stat.is_playing == false){
			requestSong(diskIndex, songIndex);

			// display the pause button.
			play_pause_css.style.setProperty('--show_play','none');
			play_pause_css.style.setProperty('--show_pause','block');

			// delay 15secs to allow Pioneer cd player time to access cd.
			setTimeout(stat, 15000);
			setTimeout(function(){
				main.seekbar.setAttribute("min",0);
				main.seekbar.setAttribute("max",d_stat.length); 
				value_seek = d_stat.time;
				//console.log('length: ' + d_stat.length);
			}, 20000);
			
		} 
	}
	//if(d_stat.is_playing == true){
	//	main.playPauseControl.classList.add("paused");
	//	pause();
	//	console.log('is_playing now paused');
	//	//main.audio.pause();
	//}
	//if(d_stat.is_playing == 'Paused'){
	//	main.playPauseControl.classList.remove("paused");
	//	pause();
	//	console.log('is_playing set as playing');

//main.seekbar.addEventListener("change",function(){
//	main.audio.currentTime = main.seekbar.value;
//});

loadSong(songIndex);

stat();
