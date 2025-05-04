// Configuration du graphique
const ctx0 = document.getElementById('chart-tp-0').getContext('2d');
const ctx1 = document.getElementById('chart-tp-1').getContext('2d');
const ctx2 = document.getElementById('chart-tp-2').getContext('2d');
const ctx3 = document.getElementById('chart-tp-3').getContext('2d');
const ctx6 = document.getElementById('chart-tp-6').getContext('2d');

socket.emit('request_stat_update', {"type": 0});
socket.emit('request_stat_update', {"type": 1});
socket.emit('request_stat_update', {"type": 2});
socket.emit('request_stat_update', {"type": 3});
socket.emit('request_stat_update', {"type": 6});

socket.on('stat_update', (data) => {
    if( data.type == 0) {
        const myChart = new Chart(ctx0, data.data);
    }
    else if(data.type == 1) {
        const myChart = new Chart(ctx1, data.data);
    }
    else if(data.type == 2) {
        const myChart = new Chart(ctx2, data.data);
    }
    else if(data.type == 3) {
        const myChart = new Chart(ctx3, data.data);
    }
    else if(data.type == 6) {
        const myChart = new Chart(ctx6, data.data);
    }
});