document.getElementById('submit').addEventListener('click', function() {
    let text = $('#summernote').summernote('code');
    let url = `http://127.0.0.1:5000/predict?email=${encodeURIComponent(text)}`;

    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('result').textContent = data.is_phishing ? "PHISHING" : "NOT PHISHING";
        document.getElementById('result').className = data.is_phishing ? "red-bold" : "green-bold";
        document.getElementById('confidence').textContent = data.probability;
        
        if (data.is_phishing) {
            newUrl = `http://127.0.0.1:5000/highlight-phishing-indicators?email=${encodeURIComponent(text)}`;
            fetch(newUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {

                // Extract the email value
                let email = data.highlighted_email;
                $('#summernote').summernote('code', email)
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

$(document).ready(function() {
    $('#summernote').summernote({
        height: 400,
        toolbar: false,
    });
});
