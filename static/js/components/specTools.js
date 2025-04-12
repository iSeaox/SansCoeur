const specToolsSection = document.getElementById('spec-tools-section');

socket.on('load-spec-tools', () => {
    console.log("Vous êtes un spec")
    specToolsSection.className = specToolsSection.className.replace(/\bd-none\b/g, 'd-flex');
});