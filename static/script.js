//NOT AI

function _(query){
	return document.querySelector(query);
}
function _all(query){
	return document.querySelectorAll(query);
}

search_result = [];

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
    is_playing: data.is_playing,
    artist: data.artist,
    s_title: data.s_title
    };

	return dict; 
}




function get_s_data(data) {
	//console.log(s_dict)
	var list1  = Object.keys(data)
	var results = [];

	for (const element of list1) {
  		//console.log(element);
  		object = { 
		index: element,
		song: data[element].Song_Title,
    	artist: data[element].Artist,
    	length: data[element].Length,
    	track: data[element].Track_ID,
    	disk: data[element].Disc_ID
    	};

    	results.push(object);
	}

     //console.log(results[1].song)
	return results; 
}


async function stat() {
	var url = '/stat'  ;
	const response = await fetch(url);
	const data = await response.json();
	d_stat =  get_stat(data);
	value_seek = value_seek; //d_stat.time; changed dc

	if(d_stat.is_playing == 0){
			show_play_button()}
	if(d_stat.is_playing == 1){
			show_pause_button()}
	if(d_stat.is_playing == -1){
			show_paused_button()}

	update_runtime(d_stat.artist, d_stat.s_title, d_stat.length-d_stat.time);

	setTimeout(stat, 10000)
	
	return d_stat
};

function pause() {
	fetch('/pause')
	.then (data => data.json())
	.then ( data => {

	dict = {
	disk: data.Album,
	artist: data.Artist,
    length: data.length,
    time: data.time,
    is_playing: data.is_playing
    }});

return dict	
};


async function search(query) {
	if (query==""){
		return 0;
	} 
	var url = '/searchDB/'+query
	//console.log(url)
	const response = await fetch(url);
	const data = await response.json();
	//console.log(Object.keys(data));
	search_result =  get_s_data(data);
	update_sList();
	return search_result
};



function show_pause_button() {
				// display the pause button.
			play_pause_css.style.setProperty('--show_play','none');
			play_pause_css.style.setProperty('--show_pause','block');
			play_pause_css.style.setProperty('--show_paused','none');
return
};
function show_play_button() {
				// display the play button.
			play_pause_css.style.setProperty('--show_play','block');
			play_pause_css.style.setProperty('--show_pause','none');
			play_pause_css.style.setProperty('--show_paused','none');
return
};
function show_paused_button(){
				// display the paused buttin.
			play_pause_css.style.setProperty('--show_play','none');
			play_pause_css.style.setProperty('--show_pause','none');
			play_pause_css.style.setProperty('--show_paused','block');
return
};

function update_runtime(artist, s_title, runTime){

  document.getElementById("runStat").innerHTML = artist + " - "+s_title + " - "+runTime+" secs";

};

// Search list update to HTML/Browser.
function update_sList(){
let sList = document.querySelector(".search .box .search-list .sList");
let exerciseItems = "";
for (let i=0;i<search_result.length;i++){

  exerciseItems += "<li id='"+i+"'><p>" + search_result[i].artist + "</p> <h2>" + search_result[i].song + "</h2>" +"</li>";

}
 // console.log(exerciseItems);
sList.innerHTML = exerciseItems;

for (let i=0;i<search_result.length;i++) {
   document.getElementById(i).addEventListener("click", selSong);
}
};

function selSong(e) {

	//use   .removeEventListener("click", selSong) to prevent multiple button presses.
	for (let i=0;i<search_result.length;i++) {
   document.getElementById(i).removeEventListener("click", selSong);
}

	nId= e.target.parentElement.id; 

	document.getElementById(nId).style.background = 'Orange'; //.h2.style.backgroundColor);
	sInx = parseInt(nId);
	Ind= parseInt(search_result[sInx].disk)+100;
	sSng = search_result[sInx].track-1;

	 console.log(Ind,sSng)

	 requestSong(Ind,sSng);
};



//document.addEventListener("DOMContentLoaded", async () => {
// Work in  progress.
//});
var songIndex = 0;
var diskIndex = 40;
var value_seek = 40;
var  status = {};
var play_pause_css = document.querySelector(':root');


// Load from dataframe function.
async function loadDB_DF() {
	var url = '/loadDatabase/'  ;
	const response = await fetch(url+diskIndex);
	const data = await response.json();
	songList =[];
	tk = data.length;
	//console.log(data.length);
	var i = 0;
	
	//update = ".player .player-list .list"
	while (i<(tk)) {
		const artistname = data[i]['Artist'];
		const album = data[i]['Album'];
		const title = data[i]['Song_Title'];
		const length = data[i]['Length'];
		//console.log(title);
		//const {title, length} = data[1][i].recording;
		object = {
			thumbnail:"Bright_Future.jpg",
			audio:"Gin Soaked Boy - The Divine Comedy.mp3",
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
	};



//loadDB();
loadDB_DF();

 
let player = _(".player"),
	toggleSongList = _(".player .toggle-list");

let main = {
	audio:_(".player .main audio"),
	thumbnail:_(".player .main img"),
	seekbar:_(".player .main input"),
	runStat:(".player .main .details h5"),
	songname:_(".player .main .details h2"),
	album:_(".player .main .details h3"),
	artistname:_(".player .main .details p"),
	prevDisk:_(".player .main .controls .prev-disc-control"),
	prevControl:_(".player .main .controls .prev-control"),
	playPauseControl:_(".player .main .controls .play-pause-control"),
	nextDisk:_(".player .main .controls .next-disc-control"),
	nextControl:_(".player .main .controls .next-control"),
	searchButton:_(".player .main .search button")
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

 	console.log('Disk Index '+typeof(diskIndex)+" SongIndx "+typeof(diskIndex))
	const requestUrl = '/requestSong/';
	const requestData = {
		Index: diskIndex, 
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
	console.log('Index ',diskIndex, 'Song ',songIndex);
	let song = songList[songIndex];
	main.thumbnail.setAttribute("src","./static/"+song.thumbnail);
	document.body.style.background = `linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.8)), url("./static/${song.thumbnail}") center no-repeat`;
	document.body.style.backgroundSize = "cover";	
	main.songname.innerText = song.songname;
	main.artistname.innerText = song.artistname;
	//main.audio.setAttribute("src","./static/"+song.audio);
}

main.prevDisk.addEventListener("click",function(){
	if(diskIndex > 1){
		diskIndex = diskIndex-1;
		value_seek = diskIndex;
		//currentSongIndex=0
		console.log('Index ',diskIndex, 'Song ',songIndex);
		
	}
	loadDB_DF();
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
		value_seek = diskIndex;
		//currentSongIndex = 0
		console.log('Index ',diskIndex, 'Song ',songIndex);
	}
	loadDB_DF();
});


main.playPauseControl.addEventListener("click",play_button)
function play_button() {
		//  d_stat   0 = stopped     1 - playing    -1 = paused
	if(d_stat.is_playing == 0){
		requestSong(diskIndex, songIndex);
		show_pause_button();
		d_stat.is_playing == 1;
		}
	 if(d_stat.is_playing == 1){
	 	pause();
	 	show_paused_button();
	 	d_stat.is_playing == -1;
	 	}
	 if(d_stat.is_playing == -1){
	 	pause();
	 	show_pause_button();
	 	d_stat.is_playing == 1;
	 	}


};

main.searchButton.addEventListener("click", function(){
	window.location = '/search';


});



main.seekbar.addEventListener("change",function(){
	main.seekbar.setAttribute("min",1);
	main.seekbar.setAttribute("max",81);
	diskIndex = main.seekbar.value.toString();
	loadDB_DF();
});

loadSong(songIndex);

stat();
