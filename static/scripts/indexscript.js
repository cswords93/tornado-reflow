var profileTable;
var profileSelect;

window.onload = loadDoc;

function loadDoc(){
	profileTable = document.getElementById("my-table");
	profileSelect = document.getElementById("profile-select");
}

function resetStatusTable(){
	stats = document.getElementsByClassName("ovenStatus");
	var all = stats.length;
	for(i = 0; i < all ; i++){
		stats[i].innerHTML = "--";
	}
}

function loadProfile(profile) {
	var xhttp = new XMLHttpRequest();
	
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			console.log(this.responseText);
			var myJSON = JSON.parse(this.responseText);
			var data = myJSON.data;
			var preheat = myJSON.preheat;
			var duration = data[data.length - 1][0];
			
			plot(data, preheat);
			clearProfile();
			//displayProfile(times,temps);
			displayDuration(duration);
	   }
	};
	xhttp.open("GET", "load_profile?profile=" + profile, true);
	xhttp.send(); 
}


/* Takes an array of times and an array of temperatures and displays
 * them in a table */
function displayProfile(times,temps){
	var num_times = times.length;
	
	for(i = 0 ; i < num_times ; i++){
		var num_rows = profileTable.rows.length;
		var row = profileTable.insertRow(num_rows);
		
		var cell1 = row.insertCell(0);
		cell1.innerHTML = times[i];
		
		var cell2 = row.insertCell(1);
		cell2.innerHTML = temps[i];
	}
}

function displayDuration(duration){
	var durationSpan = document.getElementById("duration").innerHTML =
	duration;
}

/* Clears the currently displayed profile of one exists */ 
function clearProfile(){
	var num_rows = profileTable.rows.length;
	if (num_rows != 1){
		while (num_rows > 1) {
			profileTable.deleteRow(num_rows);
			num_rows = profileTable.row.length;
		}
	}
}

function startTimer(duration){
	
	var start = new Date().getTime();
	var countDownTime = start + duration * 1000;
	var id = window.setInterval(timer, 1000);
	
	var ovenRunTime = document.getElementById("ovenRunTime");
	var progressBar = document.getElementById("myProgressBar");	
	
	ovenRunTime.innerHTML = duration;
	progressBar.style.width = '0%';
	
	function timer(){
		var now = new Date().getTime();
		var distance = new Date(countDownTime - now);
		var remainingSeconds = Math.floor(distance.getTime() / 1000);
		var percentageDone = 100 - (remainingSeconds / duration * 100);
		
		if(remainingSeconds <= 0){
			window.clearInterval(id);
			ovenRunTime.innerHTML = "0";
		}
		
		ovenRunTime.innerHTML = remainingSeconds;
		progressBar.style.width = percentageDone.toPrecision(4) + '%';
	}
}
