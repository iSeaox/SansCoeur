// Function to display WebSocket connections
function displayConnections(data) {
    const connectionsList = document.getElementById('connections-list');
    connectionsList.innerHTML = '';

    let hasConnections = false;

    // Loop through each namespace
    for (const namespace in data) {
        // Loop through each user in the namespace
        for (const username in data[namespace]) {
            hasConnections = true;
            const userConnection = data[namespace][username];

            const row = document.createElement('tr');

            // Namespace
            const namespaceCell = document.createElement('td');
            namespaceCell.textContent = namespace;
            row.appendChild(namespaceCell);

            // Username
            const usernameCell = document.createElement('td');
            usernameCell.textContent = username;
            row.appendChild(usernameCell);

            // SID Socket.io
            const sidCell = document.createElement('td');
            sidCell.textContent = userConnection.sid_socketio || '-';
            sidCell.className = 'text-truncate';
            sidCell.style.maxWidth = '150px';
            row.appendChild(sidCell);

            // EIO Socket.io
            const eioCell = document.createElement('td');
            eioCell.textContent = userConnection.eio_socketio || '-';
            eioCell.className = 'text-truncate';
            eioCell.style.maxWidth = '150px';
            row.appendChild(eioCell);

            // Status
            const statusCell = document.createElement('td');
            if (userConnection.status) {
                statusCell.innerHTML = '<span class="badge bg-success">Connecté</span>';
            } else {
                statusCell.innerHTML = '<span class="badge bg-danger">Déconnecté</span>';
            }
            row.appendChild(statusCell);

            // IP Address
            const ipCell = document.createElement('td');
            ipCell.textContent = userConnection.ip_address || '-';
            row.appendChild(ipCell);

            // User Agent
            const uaCell = document.createElement('td');
            uaCell.textContent = userConnection.user_agent || '-';
            uaCell.className = 'text-truncate';
            uaCell.style.maxWidth = '200px';
            uaCell.title = userConnection.user_agent;
            row.appendChild(uaCell);

            // Rooms
            const roomsCell = document.createElement('td');
            if (userConnection.rooms && userConnection.rooms.length) {
                const roomsList = document.createElement('ul');
                roomsList.className = 'list-unstyled mb-0';
                userConnection.rooms.forEach(room => {
                    const roomItem = document.createElement('li');
                    roomItem.textContent = room;
                    roomsList.appendChild(roomItem);
                });
                roomsCell.appendChild(roomsList);
            } else {
                roomsCell.textContent = '-';
            }
            row.appendChild(roomsCell);

            connectionsList.appendChild(row);
        }
    }

    if (!hasConnections) {
        const emptyRow = document.createElement('tr');
        const emptyCell = document.createElement('td');
        emptyCell.colSpan = 8;
        emptyCell.textContent = 'Aucune connexion disponible';
        emptyCell.className = 'text-center';
        emptyRow.appendChild(emptyCell);
        connectionsList.appendChild(emptyRow);
    }
}