document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.save-photo').forEach(card => {
        card.addEventListener('click', function() {
            const fotoPath = this.dataset.foto;
            const planoTipo = this.dataset.plano;
            
            if (planoTipo === "impulsione") {
                fetch(saveToGalleryUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams({
                        'foto': fotoPath
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (!card.querySelector('.saved-label')) {
                            const savedLabel = document.createElement('div');
                            savedLabel.classList.add('saved-label');
                            savedLabel.textContent = 'Foto salva';
                            card.appendChild(savedLabel);
                        }
                        card.classList.add('saved');
                        console.log("Foto salva na galeria:", fotoPath);
                    } else {
                        if (data.message === "Foto já existe na galeria") {
                            if (!card.querySelector('.saved-label')) {
                                const savedLabel = document.createElement('div');
                                savedLabel.classList.add('saved-label');
                                savedLabel.textContent = 'Foto salva';
                                card.appendChild(savedLabel);
                            }
                            card.classList.add('saved');
                            console.log("Foto já existente na galeria:", fotoPath);
                        } else {
                            console.error("Erro ao salvar foto na galeria:", data.message);
                        }
                    }
                })
                .catch(error => console.error('Erro:', error));
            } else {
                console.log("Plano não é Impulsione, redirecionar para pagamento.");
            }
        });
    });
});
