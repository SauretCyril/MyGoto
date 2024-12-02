function askQuestion() {
    const question = document.getElementById('question-input').value;
    const isPdfSource = document.getElementById('pdf-source').checked;
    const responseArea = document.getElementById('responseArea');
   
   

    if (isPdfSource) {
        const pdfPath = document.getElementById('file-input').value;
        eel.extract_text_from_pdf(pdfPath)().then(Extract_text => {
        eel.get_answer(question, Extract_text)()
            .then(answer => {
                responseArea.textContent = answer;
            })
            .catch(error => {
                responseArea.textContent = "Une erreur s'est produite: " + error;
            });
        });
    } else {
        const url = document.getElementById('url-input-field').value;
        if (!url) {
            responseArea.textContent = "Veuillez entrer une URL valide";
            return;
        }
        eel.extract_text_from_url(url)()
            .then(Extract_text => {
                eel.get_answer(question, Extract_text)()
                .then(answer => {
                    responseArea.textContent = answer;
                })
                .catch(error => {
                    responseArea.textContent = "Une erreur s'est produite: " + error;
                });
            })
            .catch(error => {
                responseArea.textContent = "Une erreur s'est produite: " + error;
            });
    }
}

//document.getElementById('Ask').onclick = askQuestion;



